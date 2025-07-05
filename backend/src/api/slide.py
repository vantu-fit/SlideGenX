import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Body
from fastapi.responses import JSONResponse, FileResponse
from fastapi import status
from service.slide import SlideService
from db.session import get_db, Session
from util.auth import get_user_info_from_request

router = APIRouter()
def get_slide_service(db: Session = Depends(get_db)):
    return SlideService(db)

@router.post("/generate_slide", response_class=FileResponse)
async def generate_slide(
    request: Request,
    title: str = Body(..., embed=True),
    content: str = Body(..., embed=True),
    duration: int = Body(..., embed=True),
    purpose: str = Body(..., embed=True),
    output_file_name: str = Body(..., embed=True),
    template: str = Body(None, embed=True),
    service: SlideService = Depends(get_slide_service)
):
    try:
        response = service.generate_slide(title, content, duration, purpose, output_file_name, template)
        import logging
        logging.error(f"File name: {output_file_name}, Session ID: {response['session_id']}")
        return FileResponse(response['output_path'], 
                            media_type='application/vnd.openxmlformats-officedocument.presentationml.presentation',
                            headers={"Session-ID": response['session_id']},
                            filename=f"{output_file_name}.pptx"
                            )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))