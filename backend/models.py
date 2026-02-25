from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Story(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    genre = Column(String, index=True) # Indexed for filtering
    prompt = Column(Text)
    full_story = Column(Text, default="")
    # Indexed for sorting by newest
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationship: One Story -> Many Chapters
    # passive_deletes=True combined with ondelete="CASCADE" in Child ensures DB handles deletion efficiently
    chapters = relationship(
        "Chapter", 
        back_populates="story", 
        cascade="all, delete-orphan", 
        passive_deletes=True
    )

class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key with Cascade Delete
    # If a Story is deleted, the DB automatically deletes these chapters
    story_id = Column(
        Integer, 
        ForeignKey("stories.id", ondelete="CASCADE"), 
        nullable=False,
        index=True # Index FK for faster joins
    )
    
    chapter_number = Column(Integer, nullable=False)
    title = Column(String)
    content = Column(Text)
    
    # Back Reference
    story = relationship("Story", back_populates="chapters")