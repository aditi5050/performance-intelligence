from fastapi import FastAPI
from pydantic import BaseModel
import redis
import json
import uuid

app = FastAPI()

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

class AuditRequest(BaseModel):
    url: str

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

@app.get("/result/{job_id}")
def get_result(job_id: str):

    result = r.get(f"result:{job_id}")

    if result:
        return json.loads(result)

    return {"status": "processing"}
