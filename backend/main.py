from time import time

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn


class GreetingResponse(BaseModel):
    message: str
    timestamp: int


app = FastAPI(title="Python Backend Starter", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/greeting", response_model=GreetingResponse)
def greeting(name: str = Query(default="World")) -> GreetingResponse:
    return GreetingResponse(message=f"Hello, {name}!", timestamp=int(time() * 1000))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
