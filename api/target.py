import jinja2
import tempfile

from urllib import response
from fastapi import APIRouter, Path, Body
from bson import ObjectId
from pymongo import MongoClient
from typing import List, Optional
from pydantic import BaseModel

targetRouter = APIRouter(
    prefix="/targets",
    tags=["Targets"],
    responses={404: {"description": "Not found"}},
)

client = MongoClient("mongodb://localhost:27017/")
db = client["targets_db"]
targets_collection = db["targets"]

class Target(BaseModel):
    id: Optional[str]
    target_system: str
    server_list: List[str]
    log_path: str

@targetRouter.get("/")
async def get_targets():
    response_targets = []
    targets = list(targets_collection.find({}))
    for target in targets:
        response_target = Target(
            id = str(target["id"]),
            target_system = target["target_system"],
            server_list = target["server_list"],
            log_path = target["log_path"]
        )
        response_targets.append(response_target)
    return response_targets

@targetRouter.get("/{id}", response_model=Target)
async def get_target(id: str):
    object_id = ObjectId(id)
    target = targets_collection.find_one({"id": object_id})
    if target:
        response_target = Target(
            id = str(target["id"]),
            target_system = target["target_system"],
            server_list = target["server_list"],
            log_path = target["log_path"]
        )
        return response_target
    else:
        return {"message": "Target with id {} not found".format(id)}

@targetRouter.post("/")
async def create_target(target: Target = Body(...)):
    target_dict = target.__dict__
    target_dict["id"] = ObjectId()

    #TODO
    data = {}
    with open("test.yaml.j2", "r") as file:
        template = jinja2.Template(file.read())

    playbook = template.render(data)

    # Write the playbook to a temporary file
    with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False) as f:
        f.write(playbook)
        playbook_file = f.name
    








    targets_collection.insert_one(target_dict)
    return {"message": "Target with id {} was created".format(target_dict["id"])}

@targetRouter.put("/{id}")
async def update_target(id: str, target: Target = Body(...)):
    target_dict = target.__dict__
    target_dict["id"] = id
    result = targets_collection.replace_one({"id": id}, target_dict)
    if result.matched_count:
        return {"message": "Target with id {} was updated".format(id)}
    else:
        return {"message": "Target with id {} not found".format(id)}

@targetRouter.delete("/{id}")
async def delete_target(id: str):
    object_id = ObjectId(id)
    result = targets_collection.delete_one({"id": object_id})
    if result.deleted_count:
        return {"message": "Target with id {} was deleted".format(id)}
    else:
        return {"message": "Target with id {} not found".format(id)}
