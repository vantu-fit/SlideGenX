import os
from fastapi import APIRouter, Depends, HTTPException, Request, Body
from fastapi.responses import JSONResponse, FileResponse
from fastapi import status
from service.slide import SlideService
from db.session import get_db, Session
from util.auth import get_user_info_from_request

router = APIRouter()
def get_slide_service(db: Session = Depends(get_db)):
    return SlideService(db)

@router.get("/list_templates", response_model=list[str])
async def list_templates(    request: Request,
    service: SlideService = Depends(get_slide_service)):
    """List available slide templates. 
    Returns a list of template names."""
    try:
        templates = service.list_templates()
        return JSONResponse(content=templates, status_code=status.HTTP_200_OK)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.get("/get_template", response_model=str)
async def get_template(
    request: Request,
    template_name: str,
    service: SlideService = Depends(get_slide_service)
):
    """Get the full path to a specific template."""
    try:
        template_path = service.get_template(template_name)
        return FileResponse(template_path, 
                            media_type='application/vnd.openxmlformats-officedocument.presentationml.presentation',
                            filename=f"{template_name}.pptx")
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

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
    
@router.post("/save_slide", response_model=dict)
async def save_slide(
    request: Request,
    session_id: str = Body(..., embed=True),
    service: SlideService = Depends(get_slide_service)
):
    """Save the slide information to the database."""
    user_info = await get_user_info_from_request(request)
    import logging
    logging.error(f"Session ID: {session_id}, User Info: {user_info}")
    if not user_info:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")
    
    try:
        slide_info = service.save_slide(session_id, user_info['username'])
        return JSONResponse(content=slide_info, status_code=status.HTTP_201_CREATED)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.get("/get_slide_ids_by_username", response_model=list[str])
async def get_slides_by_username(
    request: Request,
    service: SlideService = Depends(get_slide_service)
):
    """Get slides created by a specific user."""
    user_info = await get_user_info_from_request(request)
    if not user_info:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")
    
    try:
        slides = service.get_slide_session_ids_by_username(user_info['username'])
        return JSONResponse(content=slides, status_code=status.HTTP_200_OK)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.get("/get_slide_by_session_id/{session_id}", response_class=FileResponse)
async def get_slide_by_session_id(
    session_id: str,
    request: Request,
    service: SlideService = Depends(get_slide_service)
):
    username = await get_user_info_from_request(request)
    if service.check_slide_belongs_to_user(session_id, username['username']):
        slide_path = f"slides/{session_id}"
        if os.path.exists(slide_path):
            pptx_files = [f for f in os.listdir(slide_path) if f.endswith('.pptx')]
            if pptx_files:
                return FileResponse(os.path.join(slide_path, pptx_files[0]),
                                    media_type='application/vnd.openxmlformats-officedocument.presentationml.presentation',
                                    filename=pptx_files[0])
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No slides found for this session")
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this slide")
    