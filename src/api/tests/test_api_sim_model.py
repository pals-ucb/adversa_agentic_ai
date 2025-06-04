import uuid
from fastapi.testclient import TestClient
from api.api_server import app  # make sure this imports your FastAPI instance

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    print(f'Health check: passed')


def test_create_and_list_sim_models():
    # Generate a unique model ID
    sim_model_id = str(uuid.uuid4())

    # Construct SimModel payload
    sim_model_payload = {
        "id": sim_model_id,
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

    # Create the SimModel
    response = client.post("/aaa/sim/models", json=sim_model_payload)

    print("Create response:", response.status_code, response.text)

    assert response.status_code == 200
    assert response.json()["id"] == sim_model_id

    # List SimModels
    response = client.get("/aaa/sim/models")
    print("List response:", response.status_code, response.text)
    assert response.status_code == 200
    models = response.json()
    assert isinstance(models, list)
    assert any(model["id"] == sim_model_id for model in models)


def main():
    test_health_check()
    test_create_and_list_sim_models()

if __name__ == "__main__":
    main()