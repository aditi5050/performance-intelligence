from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import redis
import json
import uuid
import os

from dotenv import load_dotenv
import google.generativeai as genai

# ==============================
# LOAD ENV
# ==============================

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

# ==============================
# APP INIT
# ==============================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# connect redis
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# ==============================
# REQUEST MODELS
# ==============================

class AuditRequest(BaseModel):
    url: str

class ExplainRequest(BaseModel):
    job_id: str
    question: str

# ==============================
# GEMINI AI ENGINE
# ==============================

def generate_reasoned_answer(data, question):

    try:

        model = genai.GenerativeModel("models/gemini-2.5-flash")

        prompt = f"""
You are a senior website performance engineer AI.

User Question:
{question}

Website Lighthouse Audit Data:
{json.dumps(data, indent=2)}

Explain clearly:

1) What is wrong
2) What takes the most time
3) Root cause of performance issues
4) What happens if traffic increases
5) Best prioritized fixes
6) Provide example code fixes if useful

Answer in simple but technical language.
"""

        response = model.generate_content(prompt)

        return response.text

    except Exception as e:

        print("GEMINI ERROR:", e)

        # SAFE FALLBACK (app never breaks)
        lcp = data.get("lcp", 0)
        tbt = data.get("tbt", 0)

        if lcp > tbt:
            return f"LCP ({lcp} ms) is main performance bottleneck."
        else:
            return f"JavaScript blocking time ({tbt}) causes delay."

# ==============================
# CREATE AUDIT JOB
# ==============================

@app.post("/audit")
def run_audit(data: AuditRequest):

    job_id = str(uuid.uuid4())

    job_data = {
        "id": job_id,
        "url": data.url
    }

    r.rpush("audit_queue", json.dumps(job_data))

    return {
        "message": "Job added",
        "job_id": job_id
    }

# ==============================
# GET RESULT
# ==============================

@app.get("/result/{job_id}")
def get_result(job_id: str):

    result = r.get(f"result:{job_id}")

    if result:
        return json.loads(result)

    return {"status": "processing"}

# ==============================
# GET HISTORY
# ==============================

@app.get("/history")
def get_history(url: str):

    history = r.lrange(f"history:{url}", 0, -1)

    return [json.loads(h) for h in history]

# ==============================
# AI EXPLANATION ENDPOINT
# ==============================

@app.post("/explain")
def explain(req: ExplainRequest):

    result = r.get(f"result:{req.job_id}")

    if not result:
        return {"error": "job not found"}

    data = json.loads(result)

    answer = generate_reasoned_answer(data, req.question)

    return {"answer": answer}
