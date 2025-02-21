from fastapi import FastAPI, WebSocket
import boto3
import asyncio
import os

app = FastAPI()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")
AWS_ENDPOINT= os.getenv("AWS_ENDPOINT", None)

sqs_client = boto3.client("sqs", region_name=AWS_REGION, endpoint_url=AWS_ENDPOINT)

connections = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.add(websocket)
    try:
        while True:
            await asyncio.sleep(1)
    except Exception:
        pass
    finally:
        connections.remove(websocket)

async def poll_sqs():
    while True:
        try:
            response = sqs_client.receive_message(
                QueueUrl=SQS_QUEUE_URL,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=10,
            )

            if "Messages" in response:
                print("Messages received")
                for message in response["Messages"]:
                    message_body = message["Body"]

                for connection in connections:
                    print(connections)
                    try:
                        await connection.send_text(message_body)
                    except:
                        connections.remove(connection)

                sqs_client.delete_message(
                    QueueUrl=SQS_QUEUE_URL,
                    ReceiptHandle=message["ReceiptHandle"]
                )
        except Exception as e:
            print(f"Error polling SQS: {e}")

        await asyncio.sleep(5)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(poll_sqs())
