from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
import os


app = FastAPI()

SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL", "YOUR_SQS_QUEUE_URL")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

sqs_client = boto3.client("sqs", region_name=AWS_REGION)

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
