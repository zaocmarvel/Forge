from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChapterBase(BaseModel):
    title: str
    content: str
    chapter_number: int

class ChapterCreate(ChapterBase):
    pass

class Chapter(ChapterBase):
    id: int
    story_id: int

    class Config:
        from_attributes = True

class StoryBase(BaseModel):
    title: str
    genre: str
    prompt: str

class StoryCreate(StoryBase):
    pass

class Story(StoryBase):
    id: int
    full_story: str
    created_at: datetime
    chapters: List[Chapter] = []

    class Config:
        from_attributes = True

class GenerateRequest(BaseModel):
    title: str
    genre: str
    prompt: str

class ContinueRequest(BaseModel):
    story_id: int
    instructions: Optional[str] = "Continue the story seamlessly."