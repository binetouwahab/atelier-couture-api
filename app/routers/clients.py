from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.services.client_service import (
    creer_client,
    obtenir_client,
    lister_clients
)


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

@router.get("/")
def lister_les_clients(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    return lister_clients(db, limit, offset)