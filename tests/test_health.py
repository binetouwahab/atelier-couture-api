from fastapi.testclient import TestClient

from app.main import app
from app.db.session import get_db


def test_health_retourne_ok_si_db_disponible():

    class FausseBaseDeDonnees:
        def execute(self, requete):
            return 1

    def remplacer_get_db():
        yield FausseBaseDeDonnees()

    app.dependency_overrides[get_db] = remplacer_get_db

    try:
        client = TestClient(app)

        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    finally:
        app.dependency_overrides.pop(get_db, None)