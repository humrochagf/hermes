from fastapi import status
from fastapi.testclient import TestClient


def test_demo_pod(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == status.HTTP_200_OK
