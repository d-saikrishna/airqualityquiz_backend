from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List
import pygsheets
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware  # Import the middleware
import os
import base64
from dotenv import load_dotenv

# Load environment variables from .env file

load_dotenv()

# Read the Base64-encoded JSON from the environment variable
base64_json = os.environ.get('SERVICE_ACCOUNT_JSON_BASE64')
if not base64_json:
    raise ValueError("SERVICE_ACCOUNT_JSON_BASE64 environment variable not set")
# Decode the Base64 string to get the JSON content
json_content = base64.b64decode(base64_json).decode('utf-8')


origins = [
    "http://localhost:3000",  # Add your frontend URL(s)
    "http://127.0.0.1:3000",  # Add your frontend URL(s)
    # Add other origins as needed (e.g., your deployed frontend URL)
    "https://urbanemissionsinfo.github.io/airqualityquiz"
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Important if you're using cookies or authentication
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Google Sheets setup (using pygsheets)
gc = pygsheets.authorize(service_account_json =json_content)  # Path to your service account key file
sh = gc.open("airqualityquiz")  # Open your Google Sheet
wks_scores = sh.worksheet("title","Scores") # Get the Scores worksheet
wks_questions_performance = sh.worksheet("title","Question_wise_performance") # Get the Questions wise worksheet

class Score(BaseModel):
    quizName: str
    score: int
    date: datetime
    question_ids: list
    responses: list

@app.get("/")  # Add a route for the root path
async def root():
    return {"message": "Welcome to the Quiz API!"}  # Or a more detailed message


@app.post("/api/saveScore")
async def save_score(request: Request, score: Score):
    try:
        client_ip = request.client.host
        # Convert datetime object to string
        new_row = [score.quizName, score.score, client_ip, score.date.isoformat()]
        wks_scores.append_table(new_row)

        responses = score.responses
        # Define the mapping of numbers to options
        replacement_map = {0: 'a', 1: 'b', 2: 'c', 3: 'd'}
        # Replace elements in the list using the map
        responses = [replacement_map.get(x, x) for x in responses]

        new_rows = [[a, b] for a, b in zip(score.question_ids, responses)]
        # Add the rows to the sheet
        wks_questions_performance.append_table(new_rows, dimension='ROWS', overwrite=False)

        return {"message": "Score saved successfully"}
    except Exception as e:
        print(f"Error saving score: {e}")
        raise HTTPException(status_code=500, detail="Error saving score")

# @app.get("/api/leaderboard/{quiz_name}", response_model=List[Score])
# async def get_leaderboard(quiz_name: str):
#     try:
#         data = wks.get_all_records()
#         scores = []
#         for row in data:
#             if row.get('quizName') == quiz_name:
#                 try:
#                     row['date'] = datetime.fromisoformat(row['date'])  # Convert back to datetime
#                     scores.append(Score(**row))
#                 except ValueError:
#                     print("Error: Date format invalid in Google Sheet")
#         scores.sort(key=lambda x: x.score, reverse=True)
#         return scores[:10]
#     except Exception as e:
#         print(f"Error fetching leaderboard: {e}")
#         raise HTTPException(status_code=500, detail="Error fetching leaderboard")


# To run the FastAPI server:
# uvicorn main:app --reload