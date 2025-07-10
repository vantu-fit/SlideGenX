from fastapi import HTTPException, status, Depends, APIRouter, Body, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from service.auth import AuthService
from db.session import get_db
from util.auth import get_user_info_from_request

def get_auth_service(db  = Depends(get_db)):
    return AuthService(db)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.get("/me", response_model=dict)
def get_current_user(token: str = Depends(oauth2_scheme), service: AuthService = Depends(get_auth_service)):
    try:
        user = service.get_user_from_token(token)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "username": user.username
            }
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/register", response_model=dict)
def register_user(
    username: str = Body(..., embed=True),
    email: str = Body(..., embed=True),
    password: str = Body(..., embed=True),
    full_name: str = Body(None, embed=True),
    service: AuthService = Depends(get_auth_service)
):
    try:
        user = service.register_user(username, email, password, full_name)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=dict)
def login_user(
    username: str = Body(None, embed=True),
    password: str = Body(..., embed=True),
    service: AuthService = Depends(get_auth_service)
):
    try:
        access_token = service.login_user(username, password)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"access_token": access_token, "token_type": "bearer"}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/change-password", response_model=dict)
async def change_password(
    request: Request,
    old_password: str = Body(..., embed=True),
    new_password: str = Body(..., embed=True),
    service: AuthService = Depends(get_auth_service),
):
    try:
        info = await get_user_info_from_request(request)
        if not info:
            raise HTTPException(status_code=401, detail="Not authenticated")
        username = info.get("username")
        success = service.change_password(username, old_password, new_password)
        if success:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": "Password changed successfully"}
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to change password")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/update-profile", response_model=dict)
async def update_profile(
    request: Request,
    full_name: str = Body(None, embed=True),
    email: str = Body(None, embed=True),
    service: AuthService = Depends(get_auth_service),
):
    try:
        info = await get_user_info_from_request(request)
        if not info:
            raise HTTPException(status_code=401, detail="Not authenticated")
        username = info.get("username")
        user = service.update_user(username=username, full_name=full_name, email=email)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "username": user.username,
                "full_name": user.full_name
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))