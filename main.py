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

    system_content = "You are a teacher at a top school or university, with deep knowledge in all types of subjects at different levels, like school, university and PhD level. You are proficient at all different types of topics and are an expert at crafting flashcards. Provide a 20-question and answers flashcards.Each question and it's answer will be seperated by a comma. And each question answer pair will be seperated by a new line. Only return 10 flashcards that will be numbered from 1 to 20."
    
    user_content = f"This is the topic of the flashcards: {topic}. The output should be of this format always- {{\"questions\": \"Here are 20 math flashcards, numbered 1 to 20:\\n\\n**1.**  **Term:** Area     **Definition:** The amount of space inside a two-dimensional shape.\\n**2.** **Term:** Perimeter   **Definition:** The total distance around the outside of a two-dimensional shape.\\n**3.** **Term:** Volume   **Definition:** The amount of space a three-dimensional object takes up.\\n**4.**  **Term:** Prime Number   **Definition:** A whole number greater than 1 that has only two divisors: 1 and itself.\\n**5.** **Equation:** 2 + 3 x 4 = ?  **Answer:** 14\\n**6.** **Term:** Fraction   **Definition:** A part of a whole, written as a numerator over a denominator.\\n**7.** **Term:** Decimal   **Definition:** A number that uses digits and a decimal point to represent parts of a whole.\\n**8.**  **Equation:** 12 ÷ 3 = ? **Answer:** 4\\n**9.** **Term:** Integer    **Definition:** A whole number (positive, negative, or zero).\\n**10.** **Term:**  Exponent   **Definition:**  A number that indicates how many times a base number is multiplied by itself.\"}}"
    
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
