
import httpx
from fastapi import Request
async def get_user_info_from_request(request: Request):
    """
    Extract user information from the request headers.
    This function assumes that the user information is stored in the headers.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    if not token:
        return None
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://localhost:8000/api/auth/me", headers={"Authorization": f"Bearer {token}"})
            if response.status_code == 200:
                return response.json()
            else:
                return None
    except httpx.RequestError as e:
        print(f"An error occurred while fetching user info: {e}")
        return None
    raise HTTPException(status_code=400, detail="Get user info failed")