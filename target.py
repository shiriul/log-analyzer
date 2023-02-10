from fastapi import FastAPI, Path, Body
from bson import ObjectId
from pymongo import MongoClient

app = FastAPI()

client = MongoClient("mongodb://localhost:27017/")
db = client["targets_db"]
targets_collection = db["targets"]

class Target:
    def __init__(self, _id: ObjectId, target_system: str, server_list: list):
        self._id = _id
        self.target_system = target_system
        self.server_list = server_list

@app.get("/target/{_id}")
async def get_target(_id: ObjectId):
    target = targets_collection.find_one({"_id": _id})
    if target:
        return target
    else:
        return {"message": "Target with id {} not found".format(_id)}

@app.post("/target")
async def create_target(target: Target = Body(...)):
    target_dict = target.__dict__
    target_dict["_id"] = ObjectId()
    targets_collection.insert_one(target_dict)
    return {"message": "Target with id {} was created".format(target_dict["_id"])}

@app.put("/target/{_id}")
async def update_target(_id: ObjectId, target: Target = Body(...)):
    target_dict = target.__dict__
    target_dict["_id"] = _id
    result = targets_collection.replace_one({"_id": _id}, target_dict)
    if result.matched_count:
        return {"message": "Target with id {} was updated".format(_id)}
    else:
        return {"message": "Target with id {} not found".format(_id)}

@app.delete("/target/{_id}")
async def delete_target(_id: ObjectId):
    result = targets_collection.delete_one({"_id": _id})
    if result.deleted_count:
        return {"message": "Target with id {} was deleted".format(_id)}
    else:
        return {"message": "Target with id {} not found".format(_id)}