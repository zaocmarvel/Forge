import re
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from typing import List
import database, schemas, crud
from services import gemini_service

router = APIRouter(
    prefix="/stories",
    tags=["stories"]
)

@router.post("/", response_model=schemas.Story)
async def create_story(request: schemas.GenerateRequest, db: Session = Depends(database.get_db)):
    story_in = schemas.StoryCreate(title=request.title, genre=request.genre, prompt=request.prompt)
    db_story = crud.create_story(db, story_in)
    
    try:
        chapter_data = await gemini_service.generate_initial_chapter(
            request.title, 
            request.genre, 
            request.prompt
        )
        crud.add_chapter(db, db_story.id, chapter_data, 1)
        
        db.refresh(db_story)
        return db_story
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{story_id}/chapters", response_model=schemas.Chapter)
async def generate_next_chapter(story_id: int, request: schemas.ContinueRequest, db: Session = Depends(database.get_db)):
    db_story = crud.get_story(db, story_id)
    if not db_story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    last_chapter_num = len(db_story.chapters)
    
    try:
        chapter_data = await gemini_service.generate_next_chapter(
            db_story.full_story, 
            last_chapter_num, 
            request.instructions
        )
        
        new_chapter = crud.add_chapter(db, story_id, chapter_data, last_chapter_num + 1)
        return new_chapter
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[schemas.Story])
def read_stories(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return crud.get_stories(db, skip=skip, limit=limit)

@router.get("/{story_id}", response_model=schemas.Story)
def read_story(story_id: int, db: Session = Depends(database.get_db)):
    db_story = crud.get_story(db, story_id)
    if not db_story:
        raise HTTPException(status_code=404, detail="Story not found")
    return db_story

@router.get("/{story_id}/download")
def download_story(story_id: int, db: Session = Depends(database.get_db)):
    db_story = crud.get_story(db, story_id)
    if not db_story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    # Strip special characters and replace spaces for a clean, OS-safe filename
    safe_title = re.sub(r'[^\w\s-]', '', db_story.title).strip()
    filename = f"{safe_title.replace(' ', '_')}.txt"
    
    content = f"Title: {db_story.title}\nGenre: {db_story.genre}\n\n{db_story.full_story}"
    
    return PlainTextResponse(
        content, 
        media_type="text/plain", 
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )