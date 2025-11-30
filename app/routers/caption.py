from fastapi import APIRouter, UploadFile, Form, Depends, HTTPException, status, Request
from jose import JWTError, jwt
from datetime import datetime
from typing import Optional

from app.services.stt_azure import azure_transcribe
from app.services.translator_azure import azure_translate_async
from app.db.db import insert_caption_entry, fetch_captions, delete_caption_entry
from app.config import settings

router = APIRouter(prefix="/api/captions", tags=["captions"])

# -----------------------------
# Dependency to get current user
# -----------------------------
async def get_current_user(request: Request) -> str:
    auth_header: Optional[str] = request.headers.get("Authorization")
    print("DEBUG: Authorization header received:", auth_header)

    if not auth_header or not auth_header.startswith("Bearer "):
        print("DEBUG: Missing or malformed token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid token"
        )
    
    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        print("DEBUG: JWT payload:", payload)
        if user_id is None:
            print("DEBUG: No 'sub' in token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return user_id
    except JWTError as e:
        print("DEBUG: JWTError:", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


# -----------------------------
# Endpoints
# -----------------------------
@router.post("")
async def create_caption(
    audio: UploadFile,
    from_lang: str = Form(...),
    to_lang: str = Form(...),
    user_id: str = Depends(get_current_user)
):
    """
    Receives audio, performs STT, translates the text, and stores the result for the logged-in user.
    """
    audio_bytes = await audio.read()

    # Convert audio to transcript
    transcript = azure_transcribe(audio_bytes, from_lang)

    # Translate transcript
    translated = await azure_translate_async(transcript, from_lang, to_lang)

    # Save caption in DB
    caption_id = insert_caption_entry(
        transcript=transcript,
        translated_text=translated,
        from_lang=from_lang,
        to_lang=to_lang,
        processing_ms=0,
        session_id=None,
        user_id=user_id,
        created_at=datetime.utcnow(),
    )

    return {
        "id": caption_id,
        "transcript": transcript,
        "translated": translated,
    }


@router.get("")
def get_captions(user_id: str = Depends(get_current_user)):
    """
    Fetch all captions for the currently logged-in user, most recent first.
    """
    return fetch_captions(user_id=user_id)


@router.delete("/{caption_id}")
def delete_caption(caption_id: int, user_id: str = Depends(get_current_user)):
    """
    Delete a caption belonging to the logged-in user.
    """
    deleted = delete_caption_entry(caption_id, user_id=user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caption not found or not owned by user")
    return {"deleted": caption_id}
