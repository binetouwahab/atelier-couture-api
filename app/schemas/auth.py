from pydantic import BaseModel, EmailStr, Field


class ConnexionRequest(BaseModel):
    email: EmailStr
    mot_de_passe: str = Field(min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int