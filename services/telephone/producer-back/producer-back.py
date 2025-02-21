from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import boto3
import os


app = FastAPI()

SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ENDPOINT= os.getenv("AWS_ENDPOINT", None)

sqs_client = boto3.client("sqs", region_name=AWS_REGION, endpoint_url=AWS_ENDPOINT)

origins = [
    "http://localhost:8080",
    "https://producer-front.esuarez.info"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MessageModel(BaseModel):
    message: str

@app.post("/send")
async def send_message(msg: MessageModel):
    try:
        response = sqs_client.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=msg.message
        )
        return {"message_id": response["MessageId"], "status": "Message sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
