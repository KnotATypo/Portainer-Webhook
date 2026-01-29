import datetime
import os

import jwt
import requests
from flask import Flask, request, jsonify
from requests import Response
from waitress import serve

PORTAINER_TOKEN = ""
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
API_URL = os.getenv("PORTAINER_API") + "/api"

app = Flask(__name__)
app.logger.setLevel(LOG_LEVEL)
# Prevent double-logging of messages
app.logger.propagate = False


@app.route("/deploy/<stack_name>", methods=["POST"])
def webhook(stack_name: str) -> tuple[Response, int]:
    app.logger.debug(f"Hook received for {stack_name}")
    # Ensure request is authenticated
    if "Secret-Token" not in request.headers or request.headers["Secret-Token"] != os.getenv("HOOK_SECRET"):
        return jsonify({"status": "unauthorized"}), 401

    # Token should only be empty on first request
    if PORTAINER_TOKEN == "":
        get_new_token()

    # Check token hasn't expired
    timestamp = jwt.decode(PORTAINER_TOKEN, options={"verify_signature": False})["exp"]
    if datetime.datetime.fromtimestamp(int(timestamp)) < datetime.datetime.now():
        get_new_token()

    # Run update/deploy
    stack_id = get_stack_id(stack_name)
    app.logger.debug(f"Received stack id {stack_id}")
    update_stack(stack_id)

    app.logger.info(f"Successfully deployed stack {stack_name} ({stack_id})")

    return jsonify({"status": "ok"}), 200


def get_new_token():
    app.logger.debug("Generating new token")
    response = requests.post(
        f"{API_URL}/auth",
        json={"username": os.getenv("PORTAINER_USERNAME"), "password": os.getenv("PORTAINER_PASSWORD")},
    )
    log_response(response)

    global PORTAINER_TOKEN
    PORTAINER_TOKEN = response.json()["jwt"]


def get_stack_id(stack_name: str) -> int:
    response = portainer_get(f"{API_URL}/stacks")
    return [x["Id"] for x in response.json() if x["Name"] == stack_name][0]


def update_stack(stack_id: int):
    file = portainer_get(f"{API_URL}/stacks/{stack_id}/file").json()
    file_content = file["StackFileContent"]

    stack_info = portainer_get(f"{API_URL}/stacks/{stack_id}").json()
    endpoint_id = stack_info["EndpointId"]
    env = stack_info["Env"]

    response = requests.put(
        f"{API_URL}/stacks/{stack_id}?endpointId={endpoint_id}",
        headers={"Authorization": f"Bearer {PORTAINER_TOKEN}", "Content-Type": "application/json"},
        json={"pullImage": True, "env": env, "stackFileContent": file_content},
    )
    log_response(response)


def portainer_get(url: str) -> Response:
    response = requests.get(url, headers={"Authorization": f"Bearer {PORTAINER_TOKEN}"})
    log_response(response)
    return response


def log_response(response: Response):
    app.logger.debug(f"Status code: {response.status_code}")
    app.logger.debug(f"Headers: {response.headers}")
    app.logger.debug(f"Body: {response.text}")


def start():
    app.logger.info("Starting deployment")
    serve(app, host="0.0.0.0", port=5500)


if __name__ == "__main__":
    start()
