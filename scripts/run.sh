SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR/..

export PROJECT_ID="nth-passage-113523"

uvicorn main:app --reload
