from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import requests


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/create_quiz")
async def create_quiz(
    topic: str = Body(...),
    instructions: str = Body(default=None)
):
    try:
        questions = get_questions_from_llm(topic, instructions)
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_questions_from_llm(topic, instructions):
    url = "https://gemma.us.gaianet.network/v1/chat/completions"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    system_content = "You are an axpert in all the fields of knowledge. You are proficient at all different types of topics and are an expert at crafting flashcards. Follow this output format to create questions and answers { \"questions\": \"```json\\\\n[\\\\n  {\\\\'number\\\\': \\\\'1\\\\', \\\\'question\\\\': \\\\'string\\\\', \\\\'answer\\\\': \\\\'string\\\\'}\\\\n]\\\\n```\" } Provide a 15-question and answers flashcards. The output should be of valid json format strictly."
    
    user_content = f"This is the topic of the flashcards: {topic} Create 15 flashcards with question and answers relevant to the topic. The output should be of JSON format."
    
    if instructions:
        user_content += f" Also, please consider this special note added by the user: {instructions}."
    else:
        user_content += " There are no special instructions to consider."

    data = {
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ],
        "model": "gemma"
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print(response.json()["choices"][0]["message"]["content"])
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Error: Unable to fetch questions from LLM. Status code: {response.status_code}")
