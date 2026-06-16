from fastapi import FastAPI
from contextlib import asynccontextmanager
import redis
import json
import asyncio
from ai_engine import analyze_audio
import requests


redis_client = redis.Redis(host="localhost", port="6379", db=0, decode_responses=True)

QUEUE_NAME = 'bull:audio-analysis:wait'

async def process_queue():
    while True:
        try:

            job = redis_client.blpop(QUEUE_NAME, timeout=2)

            if job:
                queue_name, job_id = job

                job_key=f"bull:audio-analysis:{job_id}"
                raw_data = redis_client.hget(job_key, "data")

                if raw_data:

                    job_data = json.loads(raw_data)

                    file_path = job_data.get('filePath')
                    metadata_id = job_data.get('metadataId')

                    print(f"Picked up {metadata_id}.")
                    print(f"Analyzing file at: {file_path}.")

                    analysis_result = await asyncio.to_thread(analyze_audio, file_path)
                    print(f"Analysis results {metadata_id}: {analysis_result}.")

                    if analysis_result["status"] == "success":
                        webhook_payload = {
                            "metadataId": metadata_id,
                            "score": analysis_result["manipulation_score"],
                            "isManipulated": analysis_result["is_manipulated"]
                        }
                        try:
                            response = requests.post("http://localhost:3000/audio/webhook/ai-result", json=webhook_payload)
                            print(f"Webhook sent to API! Status: {response.status_code}.")
                        except Exception as e:
                            print(f"Failed to send webhook to API: {e}.")

                    redis_client.delete(job_key)
                    print(f"Deleted job data {job_key} from Redis to free memory.")
                    
                else:
                    print(f"Job {job_id} popped, but data payload was missing.")

        except Exception as ex:
            print(f"Error processing queue: {ex}.")

        await asyncio.sleep(1)


@asynccontextmanager
async def lifespan(app: FastAPI):

    asyncio.create_task(process_queue())

    yield


app = FastAPI(lifespan=lifespan)