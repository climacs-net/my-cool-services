from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

OPA_URL = "https://malamig-na-serbisyo.climacs.net/v1/data/authz/allow"

# In-memory storage for users
users = []

# Function to check OPA authorization
def check_opa_authz(input_data):
    response = requests.post(OPA_URL, json={"input": input_data})
    return response.json().get('result', False)

@app.route('/api/users', methods=['GET'])
def get_users():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Unauthorized"}), 401
    if check_opa_authz({"method": "GET", "token": token}):
        return jsonify(users), 200
    else:
        return jsonify({"error": "Forbidden"}), 403

@app.route('/api/users', methods=['POST'])
def create_user():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Unauthorized"}), 401
    if check_opa_authz({"method": "POST", "token": token}):
        data = request.json
        users.append({"name": data["name"], "email": data["email"]})
        return jsonify({"message": "User created"}), 201
    else:
        return jsonify({"error": "Forbidden"}), 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
