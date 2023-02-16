import jinja2
import tempfile

from urllib import response
from fastapi import APIRouter, Path, Body
from typing import List, Optional
from pydantic import BaseModel
from confluent_kafka.admin import AdminClient, NewTopic, ConsumerGroupMetadata

topicRouter = APIRouter(
    prefix="/topics",
    tags=["Topics"],
    responses={404: {"description": "Not found"}},
)

class Consumer(BaseModel):
    group_id: str
    topic: str
    consumer_id:str
    host: str
    client_id: str

class ConsumerList(Consumer):
    consumers: List[Consumer] = []

# kafka broker 설정
bootstrap_servers = "localhost:9092"
kafka_client = AdminClient({"bootstrap.servers": bootstrap_servers})

@topicRouter.get("/topics")
async def list_topics():
    topics = kafka_client.list_topics().topics.keys()
    return {"topics": list(topics)}

@topicRouter.post("/topics/{topic_name}")
async def create_topic(topic_name: str):
    num_partitions = 1
    replication_factor = 1
    topic = NewTopic(topic_name, num_partitions, replication_factor)

    futures = kafka_client.create_topics([topic])
    for topic, future in futures.items():
        try:
            future.result()
            return {"message": "Topic {} created".format(topic_name)}
        except Exception as e:
            return {"message": "Failed to create topic {}".format(topic_name)}

@topicRouter.delete("/topics/{topic_name}")
async def delete_topic(topic_name: str):
    try:
        kafka_client.delete_topics([topic_name], timeout_ms=5000)
        return {"message": "Topic {} deleted".format(topic_name)}
    except Exception as e:
        return {"message": "Failed to delete topic {}".format(topic_name)}

@topicRouter.get("/topics/{topic_name}/consumers")
async def list_consumers_for_topic(topic_name: str):
    consumer_groups = kafka_client.list_consumer_groups()
    
    response_consumers = ConsumerList()
    for group in consumer_groups:
        group_metadata = kafka_client.describe_consumer_group(group.id)
        for member_metadata in group_metadata.members:
            if topic_name in member_metadata.assignment:
                consumer = Consumer()
                    group_id: group.id,
                    topic: topic_name,
                    consumer_id: member_metadata.client_id,
                    host: member_metadata.client_host,
                    client_id: member_metadata.member_id,
                )
                response_consumers.consumers.append(consumer)
    
    return response_consumers
