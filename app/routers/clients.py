from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.client_service import obtenir_client

from app.db.session import get_db
from app.schemas.client import ClientCreate, ClientRead
from app.services.client_service import creer_client


router = APIRouter(
    prefix="/clients",
    tags=["Clients"]
)


@router.post("/", response_model=ClientRead, status_code=201)
def creer_un_client(
    donnees: ClientCreate,
    db: Session = Depends(get_db)
):
    nouveau_client = creer_client(db, donnees)

    db.commit()
    db.refresh(nouveau_client)

    return nouveau_client

@router.get("/{client_id}", response_model=ClientRead)
def consulter_un_client(
    client_id: int,
    db: Session = Depends(get_db)
):
    return obtenir_client(db, client_id)