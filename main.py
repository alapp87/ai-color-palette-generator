import os
import logging
import json
import openai
import secrets

from typing import Annotated

from fastapi import FastAPI, Form, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

from pydantic import BaseModel

from google.cloud import secretmanager

log = logging.getLogger(__name__)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

security = HTTPBasic()

user = None


class User(BaseModel):
    username: str
    password: str


@app.on_event("startup")
def startup():
    global user

    project_id = os.environ.get("PROJECT_ID")
    openai_api_key_secret_id = os.environ.get(
        "OPENAI_API_KEY_SECRET_ID", "OPENAI_API_KEY"
    )
    username_secret_id = os.environ.get("USERNAME_SECRET_ID", "COLOR_PALETTE_AUTH_USER")
    password_secret_id = os.environ.get(
        "PASSWORD_SECRET_ID", "COLOR_PALETTE_AUTH_PASSWORD"
    )
    log_level = os.environ.get("LOG_LEVEL", "INFO")

    logging.basicConfig(level=log_level)

    username = access_secret_version(project_id, username_secret_id)
    password = access_secret_version(project_id, password_secret_id)
    user = User(username=username, password=password)

    set_openai_api_key(project_id, openai_api_key_secret_id)


def set_openai_api_key(project_id, openai_api_key_secret_id: str) -> None:
    if not openai.api_key or openai.api_key == "":
        log.info("Setting OpenAI API key...")
        openai.api_key = access_secret_version(project_id, openai_api_key_secret_id)


def get_current_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = user.username.encode("utf-8")
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = user.password.encode("utf-8")
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/")
def index(username: Annotated[str, Depends(get_current_username)]):
    log.info(username)
    return FileResponse("templates/index.html")


@app.post("/palette")
def prompt_to_palette(
    query: Annotated[str, Form()],
    username: Annotated[str, Depends(get_current_username)],
):
    log.info("Will generate color palette for query: %s", query)

    if is_query_valid(query):
        messages = initialize_messages(query)

        chat_completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )

        log.debug("Chat response : %s", chat_completion)

        colors = json.loads(chat_completion["choices"][0]["message"]["content"])

        return {"colors": colors}


def initialize_messages(query) -> list:
    return [
        {
            "role": "system",
            "content": """
                You are a color palette generating assistant that responds to text prompts for color palettes
                Your should generate color palettes that fit the theme, mood, or instructions in the prompt.
                The palettes should be between 2 and 8 colors.
                """,
        },
        {
            "role": "user",
            "content": "Convert the following verbal description of a color palette into a list of colors: The Mediterranean Sea",
        },
        {
            "role": "assistant",
            "content": '["#006699", "#66CCCC", "#F0E68C", "#008000", "#F08080"]',
        },
        {
            "role": "user",
            "content": "Convert the following verbal description of a color palette into a list of colors: sage, nature, earth",
        },
        {
            "role": "assistant",
            "content": '["#EDF1D6", "#9DC08B", "#609966", "#40513B"]',
        },
        {
            "role": "user",
            "content": f"Convert the following verbal description of a color palette into a list of colors: {query}",
        },
    ]


def is_query_valid(query: str) -> bool:
    return query and query.strip() != ""


def access_secret_version(project_id, secret_id, version_id="latest"):
    log.info("Retrieving secret %s :: version %s", secret_id, version_id)

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(name=name)

    # Return the decoded payload.
    return response.payload.data.decode("UTF-8")
