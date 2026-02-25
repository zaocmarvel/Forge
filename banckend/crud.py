from sqlalchemy.orm import Session
import models, schemas

def get_story(db: Session, story_id: int):
    return db.query(models.Story).filter(models.Story.id == story_id).first()

def get_stories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Story).order_by(models.Story.created_at.desc()).offset(skip).limit(limit).all()

def create_story(db: Session, story: schemas.StoryCreate):
    db_story = models.Story(
        title=story.title,
        genre=story.genre,
        prompt=story.prompt,
        full_story=""
    )
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    return db_story

def add_chapter(db: Session, story_id: int, chapter_data: dict, chapter_number: int):
    # Create Chapter
    db_chapter = models.Chapter(
        story_id=story_id,
        chapter_number=chapter_number,
        title=chapter_data["title"],
        content=chapter_data["content"]
    )
    db.add(db_chapter)
    
    # Update Story full text
    story = get_story(db, story_id)
    story.full_story += f"\n\nChapter {chapter_number}: {chapter_data['title']}\n\n{chapter_data['content']}"
    
    db.commit()
    db.refresh(db_chapter)
    db.refresh(story)
    return db_chapter