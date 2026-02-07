from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import redis
import json
import uuid

# ==============================
# APP INIT
# ==============================

app = FastAPI()

# enable CORS (for frontend dashboard)
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
# REQUEST MODEL
# ==============================

class AuditRequest(BaseModel):
    url: str

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

    # push job to queue
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
