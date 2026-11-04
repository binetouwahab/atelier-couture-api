
def test_health_retourne_ok_si_db_disponible(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
