
from fastapi import FastAPI # đem class FastAPI từ thư viện fastapi để dùng, mục đích là để thông qua API
#giao tiếp với server
from pydantic import BaseModel # dùng để định nghĩa dữ liệu sẽ giao tiếp với API sẽ ra sao

import requests # giúp code python có thể GET(nhận data) và POST(gửi data), có thể dùng PUT để cập nhật data
# và DELETE để xóa dữ liệu
import random    # sử dụng để sinh số ngẫu nhiên
import traceback # thư viện để xem chi tiết lỗi
from dotenv import load_dotenv
import os

load_dotenv()  # đọc file .env

#gán đối tượng fastAPI vào đối tượng app 
app = FastAPI() 

#tạo biến lưu chuỗi api key vào đây
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("❌ Không tìm thấy API KEY bro")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

#list các model free
MODELS = [
    "mistralai/mistral-7b-instruct",
    "openchat/openchat-7b",
    "meta-llama/llama-3-8b-instruct"
]

#tạo format dữ liệu chuẩn để gửi/nhận trong quá trình giao tiếp
#lớp Promt kế thừa từ class BaseModel để định nghĩa dữ liệu
class Prompt(BaseModel):
    text: str           #mặc định text phải là chuỗi, còn dạng khác hên xui vẫn convert được :))
    mode: str = "chat"  #mặc định 


@app.get("/")    # nếu server gửi request GET lên fastAPI thì tại đường dẫn / 
#tạo một hàm trả về trạng thái với form json để chứng tỏ server đang hoạt động
def home():
    return {"status": "Free AI server running 😎"} #tóm lại, server tao vẫn sống nha bây

# ===== BUILD PROMPT =====
def build_prompt(text: str, mode: str):

    if mode == "translate":
        return f"Translate to English:\n{text}"

    elif mode == "code":
        return f"Write code and explain briefly:\n{text}"

    return text

# ===== CHỌN MODEL RANDOM =====
def get_random_model():
    return random.choice(MODELS)

# ===== MAIN API =====
@app.post("/ask")
def ask_ai(prompt: Prompt):
    try:
        print("\n==============================")
        print("📩 INPUT:", prompt.text)

        model_name = get_random_model()
        print("🎲 MODEL:", model_name)

        full_prompt = build_prompt(prompt.text, prompt.mode)

        r = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model_name,
                "messages": [
                    {"role": "user", "content": full_prompt}
                ]
            },
            timeout=60
        )

        print("📡 STATUS:", r.status_code)

        if r.status_code != 200:
            print("❌ ERROR:", r.text)
            return {"error": r.text}

        data = r.json()

        result = data["choices"][0]["message"]["content"].strip()

        return {
            "model": model_name,
            "result": result
        }

    except requests.exceptions.Timeout:
        return {"error": "⏳ AI timeout"}

    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)