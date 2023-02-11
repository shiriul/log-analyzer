from fastapi import FastAPI

import target

app = FastAPI()

app.include_router(target.targetRouter)

@app.get("/")
async def root():
    return {"message": "Hello World"}
