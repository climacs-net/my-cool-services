import os
import json
from fastapi import FastAPI, Depends, HTTPException, status, Header
from pydantic import BaseModel
import requests

app = FastAPI()

class User(BaseModel):
    name: str
    email: str

# Load user data from JSON file
def load_users():
    with open('users.json', 'r') as f:
        return json.load(f)

users = load_users()

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
    return [{"name": user["name"], "email": email} for email, user in users.items()]

@app.post("/api/users")
def create_user(user: User, token: str = Header(None)):
    if not verify_token(token, "POST"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    users[user.email] = {"name": user.name, "email": user.email}
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)
    return user
