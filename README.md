# Color Palette Generation App

This is a FastAPI-based web application that generates color palettes based on text prompts. It uses the GPT-3.5 Turbo language model from OpenAI to interpret the prompts and generate corresponding color palettes. Users can input descriptions or keywords related to color themes, moods, or concepts, and the app will respond with a list of colors that fit the input.

## Prerequisites

Before you can run this application, make sure you have the following prerequisites:

1. Python 3.7 or higher
2. OpenAI API key
3. Google Cloud project with Secret Manager enabled
4. FastAPI and required Python packages (install using `pip install -r requirements.txt`)

## Getting Started

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/alapp87/ai-color-palette-generator.git
   cd ai-color-palette-generator
   ```

2. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:

   - Create a `.env` file in the project directory and add the following environment variables:

     ```dotenv
     PROJECT_ID=your-google-cloud-project-id
     OPENAI_API_KEY_SECRET_ID=your-openai-api-key-secret-id
     USERNAME_SECRET_ID=your-username-secret-id
     PASSWORD_SECRET_ID=your-password-secret-id
     LOG_LEVEL=INFO
     ```

   Replace the placeholders with your actual values.

4. Start the FastAPI server:

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

   The server will be accessible at `http://localhost:8000`.

## Endpoints

### `/`

This is the home page of the application. When accessed, it displays the main user interface for generating color palettes.

### `/palette`

This endpoint accepts POST requests with a `query` parameter representing a text prompt. The app interprets this prompt and generates a color palette accordingly.

#### Request Body

- `query`: A text description or keywords related to the desired color palette.

#### Response

The response will be a JSON object containing a list of colors that fit the input query.

```json
{
  "colors": ["#FFFFFF", "#000000", "#FF5733"]
}
```

## Important Notes

- The application uses Google Cloud Secret Manager to store sensitive data like OpenAI API keys, usernames, and passwords.
- The `get_current_username` function validates user credentials using HTTP Basic Authentication.
- The `initialize_messages` function prepares a list of messages to be used in the GPT-3.5 Turbo conversation for generating color palettes.

## Security Considerations

- Ensure that you keep your secrets and sensitive information secure.
- Use proper authentication and authorization mechanisms to protect user data.
- Follow best practices for securing your server and API endpoints.

## License

This project is licensed under the [MIT License](LICENSE).

---

Feel free to contribute, report issues, or suggest improvements by creating pull requests in this repository. Happy color palette generating! 🎨🌈
