from fastapi import FastAPI 
from pydantic import BaseModel 

import requests 
import random   
import traceback 
from dotenv import load_dotenv
import os

load_dotenv()  

app = FastAPI() 

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("API key was not found")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

MODELS = [
    "meta-llama/llama-3-8b-instruct:free",
    "openchat/openchat-7b:free"
]


class Prompt(BaseModel):
    text: str           
    mode: str = "chat"  


@app.get("/")   
def home():
    return {"status": "Free AI server running "} 

def build_prompt(text: str, mode: str):

    if mode == "translate":
        return f"Translate to English:\n{text}"

    elif mode == "code":
        return f"Write code and explain briefly:\n{text}"

    return text

def get_random_model():
    return random.choice(MODELS)

def call_model(model_name, prompt):
    return requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        },
        timeout=60
    )

@app.post("/ask")
def ask_ai(prompt: Prompt):
    try:
        print("\n==============================")
        print(" INPUT:", prompt.text)

        model_name = "openrouter/auto"
        print(" MODEL AUTO")

        full_prompt = build_prompt(prompt.text, prompt.mode)

        r = call_model(model_name, full_prompt)

        print(" STATUS:", r.status_code)

        if r.status_code != 200:
            print(" Model auto lỗi, thử fallback...")
            r = call_model("openchat/openchat-7b", full_prompt)

        if r.status_code != 200:
            print(" ERROR:", r.text)
            return {"error": r.text}

        data = r.json()
        result = data["choices"][0]["message"]["content"].strip()

        return 
        {
            "model": model_name,
            "result": result
        }

    except requests.exceptions.Timeout:
        return {"error": " AI timeout"}

    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}

#local run
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
