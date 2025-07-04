from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from beanie import PydanticObjectId

from app.schemas.auth import OperatorCreate, OperatorLogin, Token
from app.database.models.operator import Operator
from app.utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_operator
)

auth_router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)


@auth_router.post("/register", response_model=Token)
async def register_operator(operator_data: OperatorCreate):
    """
    Registra un nuevo operador en el sistema
    """
    # Verificar si el email ya existe
    if await Operator.find_one({"email": operator_data.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )

    # Crear el operador
    operator = Operator(
        email=operator_data.email,
        hashed_password=get_password_hash(operator_data.password),
        full_name=operator_data.full_name
    )
    await operator.save()

    # Generar token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(operator.id)},
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@auth_router.post("/login", response_model=Token)
async def login(operator_data: OperatorLogin):
    """
    Inicia sesión de un operador
    """
    # Buscar operador por email
    operator = await Operator.find_one({"email": operator_data.email})
    if not operator or not verify_password(operator_data.password, operator.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar si el operador está activo
    if not operator.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operador inactivo"
        )

    # Generar token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(operator.id)},
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
