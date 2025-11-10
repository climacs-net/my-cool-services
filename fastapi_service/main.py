import os
from fastapi import FastAPI, Depends, HTTPException, status, Header
from pydantic import BaseModel
import requests

app = FastAPI()

class User(BaseModel):
    name: str
    email: str

def verify_token(token: str, method: str):
    opa_url = os.getenv("OPA_URL", "http://opa-service.opa.svc.cluster.local/v1/data/authz/allow")
    response = requests.post(opa_url, json={"input": {"token": token, "method": method}})
    if response.json().get("result"):
        return True
    return False

@app.get("/api/users")
def read_users(token: str = Header(None)):
    if not verify_token(token, "GET"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return [{"name": "John Doe", "email": "john@example.com"}]

@app.post("/api/users")
def create_user(user: User, token: str = Header(None)):
    if not verify_token(token, "POST"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return user
