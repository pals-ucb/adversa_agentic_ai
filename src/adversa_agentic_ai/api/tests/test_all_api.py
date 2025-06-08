"""
run_all_tests.py

Standalone test runner for SimModel and PromptTemplate CRUD endpoints.
No pytest required—simply execute this script with the correct PYTHONPATH.
"""

import argparse
import uuid
import sys
import traceback
import requests
import time

# reuse your existing constants
BASE_SIM = "/aaa/sim/models"
BASE_PROMPT = "/aaa/prompt/templates"

def parse_args():
    parser = argparse.ArgumentParser(
        description="Smoke-test the Agentic AI API Server"
    )
    parser.add_argument("--base-url", required=False, default="http://127.0.0.1:8080",
        help="Base URL of the API under test"
    )
    return parser.parse_args()

class APIClient:
    def __init__(self, base_url: str):
        # strip trailing slash if given
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def get(self, path: str, **kwargs):
        url = f"{self.base_url}{path}"
        return self.session.get(url, **kwargs)

    def post(self, path: str, json=None, **kwargs):
        url = f"{self.base_url}{path}"
        return self.session.post(url, json=json, **kwargs)

    def put(self, path: str, json=None, **kwargs):
        url = f"{self.base_url}{path}"
        return self.session.put(url, json=json, **kwargs)

    def delete(self, path: str, json=None, **kwargs):
        url = f"{self.base_url}{path}"
        return self.session.delete(url, json=json, **kwargs)



def print_result(test_name, success, detail=""):
    status = "PASS" if success else "FAIL"
    print(f"[{status}] {test_name}{': ' + detail if detail else ''}")


def test_health_check(client):
    name = "Health check"
    try:
        resp = client.get("/health")
        assert resp.status_code == 200, f"Status code {resp.status_code}"
        assert resp.json() == {"status": "ok"}, f"Response body: {resp.text}"
        print_result(name, True)
    except AssertionError as e:
        print_result(name, False, str(e))


def test_sim_model_crud(client):
    base = BASE_SIM
    model_id = str(uuid.uuid4())
    payload = {
        "id": model_id,
        "name": "ER Simulation",
        "description": "A test simulation for emergency room triage",
        "nodes": [
            {
                "id": "node1",
                "name": "Pharmacy",
                "properties": [],
                "services": [],
                "resources": [],
                "vulnerabilities": [],
                "firewalls": [],
                "children": []
            }
        ]
    }

    # 0) Create a persistent model
    test_name = "SimModel: Create Persistent model"
    try:
        persist_mid = str(uuid.uuid4())
        payload["id"] = persist_mid
        resp = client.post(f"{base}", json=payload)
        assert resp.status_code == 200, f"Create status {resp.status_code}"
        data = resp.json()
        assert data["id"] == persist_mid
        print_result(test_name, True)
        payload["id"] = model_id
    except AssertionError as e:
        print_result(test_name, False, str(e))

    # 1) Create
    test_name = "SimModel: Create"
    try:
        resp = client.post(f"{base}", json=payload)
        assert resp.status_code == 200, f"Create status {resp.status_code}"
        data = resp.json()
        assert data["id"] == model_id
        print_result(test_name, True)
    except AssertionError as e:
        print_result(test_name, False, str(e))

    # 2) Get
    test_name = "SimModel: Get"
    try:
        resp = client.get(f"{base}/{model_id}")
        assert resp.status_code == 200, f"Get status {resp.status_code}"
        data = resp.json()
        assert data["id"] == model_id
        print_result(test_name, True)
    except AssertionError as e:
        print_result(test_name, False, str(e))

    # 3) Update
    test_name = "SimModel: Update"
    try:
        payload["name"] = "ER Simulation Updated"
        payload["description"] = "Updated description"
        resp = client.put(f"{base}/{model_id}", json=payload)
        assert resp.status_code == 200, f"Update status {resp.status_code}"
        data = resp.json()
        assert data["name"] == "ER Simulation Updated", "Name did not update"
        assert data["description"] == "Updated description", "Description did not update"
        print_result(test_name, True)
    except AssertionError as e:
        print_result(test_name, False, str(e))

    # 4) Delete
    test_name = "SimModel: Delete"
    try:
        resp = client.delete(f"{base}/{model_id}")
        assert resp.status_code == 200, f"Delete status {resp.status_code}"
        data = resp.json()
        assert data == {"status": "deleted"}, f"Unexpected delete response {data}"
        print_result(test_name, True)
        time.sleep(1)
    except AssertionError as e:
        print_result(test_name, False, str(e))

    # 5) Get after Delete (should 404)
    test_name = "SimModel: Get after Delete"
    try:
        resp = client.get(f"{base}/{model_id}")
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"
        print_result(test_name, True)
    except AssertionError as e:
        print_result(test_name, False, str(e))

    # 6) Update non-existent (404)
    test_name = "SimModel: Update non-existent"
    try:
        fake_id = str(uuid.uuid4())
        fake_payload = {
            "id": fake_id,
            "name": "Nonexistent",
            "description": "Should not exist",
            "nodes": []
        }
        resp = client.put(f"{base}/{fake_id}", json=fake_payload)
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"
        print_result(test_name, True)
    except AssertionError as e:
        print_result(test_name, False, str(e))

    # 7) Delete non-existent (404)
    test_name = "SimModel: Delete non-existent"
    try:
        fake_id = str(uuid.uuid4())
        resp = client.delete(f"{base}/{fake_id}")
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"
        print_result(test_name, True)
    except AssertionError as e:
        print_result(test_name, False, str(e))


def test_prompt_template_crud(client):
    base = BASE_PROMPT
    prompt_id = str(uuid.uuid4())
    payload = {
        "id": prompt_id,
        "name": "Basic Triage Prompt",
        "description": "Template for triage decisions",
        "template": "Given symptoms: {symptoms}, what is the likely diagnosis?",
        "placeholders": [
            {"name": "symptoms", "description": "List of symptoms", "optional": False}
        ]
    }

    # 1) Create
    test_name = "PromptTemplate: Create"
    try:
        resp = client.post(f"{base}", json=payload)
        assert resp.status_code == 200, f"Create status {resp.status_code}"
        data = resp.json()
        assert data["id"] == prompt_id
        print_result(test_name, True)
    except AssertionError as e:
        print_result(test_name, False, str(e))

    # 2) Get
    test_name = "PromptTemplate: Get"
    try:
        resp = client.get(f"{base}/{prompt_id}")
        assert resp.status_code == 200, f"Get status {resp.status_code}"
        data = resp.json()
        assert data["id"] == prompt_id
        print_result(test_name, True)
    except AssertionError as e:
        print_result(test_name, False, str(e))

    # 3) Update
    test_name = "PromptTemplate: Update"
    try:
        payload["description"] = "Updated description"
        resp = client.put(f"{base}/{prompt_id}", json=payload)
        assert resp.status_code == 200, f"Update status {resp.status_code}"
        data = resp.json()
        assert data["description"] == "Updated description"
        print_result(test_name, True)
    except AssertionError as e:
        print_result(test_name, False, str(e))

    # 4) Delete
    test_name = "PromptTemplate: Delete"
    try:
        resp = client.delete(f"{base}/{prompt_id}")
        assert resp.status_code == 200, f"Delete status {resp.status_code}"
        data = resp.json()
        # Assuming delete returns {"status": "deleted"} or similar
        assert "deleted" in data.get("status", "")
        print_result(test_name, True)
        time.sleep(2)
    except AssertionError as e:
        print_result(test_name, False, str(e))

    # 5) Get after Delete
    test_name = "PromptTemplate: Get after Delete"
    try:
        resp = client.get(f"{base}/{prompt_id}")
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"
        print_result(test_name, True)
    except AssertionError as e:
        print_result(test_name, False, str(e))


def main():
    args = parse_args()
    client = APIClient(args.base_url)

    print("\n--- Running ApiServer Health check Tests ---")
    test_health_check(client)
    print("\n--- Running SimModel CRUD Tests ---")
    test_sim_model_crud(client)
    print("\n--- Running PromptTemplate CRUD Tests ---")
    test_prompt_template_crud(client)
    print("\n--- All tests complete ---\n")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
    else:
        sys.exit(0)
