import redis
import json
import subprocess

# connect redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

print("Worker started...")

while True:

    # wait for job
    job = r.blpop("audit_queue")

    if job:

        data = json.loads(job[1])

        job_id = data["id"]
        url = data["url"]

        print("Running audit for:", url)

        result = subprocess.run(
            ["node", "runAudit.js", url],
            capture_output=True,
            text=True
        )

        print("NODE OUTPUT:", result.stdout)
        print("NODE ERROR:", result.stderr)

        # save result
        r.set(f"result:{job_id}", result.stdout)

        print("Saved result for job:", job_id)
