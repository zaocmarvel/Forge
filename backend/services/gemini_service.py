import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# Configuration for response control
generation_config = genai.types.GenerationConfig(
    candidate_count=1,
    max_output_tokens=4000, # Limits response size to prevent timeouts/overspending
    temperature=0.8,        # Slightly higher creative freedom for storytelling
)

async def generate_initial_chapter(title: str, genre: str, prompt: str) -> dict:
    """
    Generates the first chapter with a specific focus on a strong hook 
    and establishing the world/characters.
    """
    system_prompt = (
        f"You are a best-selling {genre} author. "
        f"Write the FIRST chapter of a new story titled '{title}'.\n\n"
        f"CORE CONCEPT: {prompt}\n\n"
        "GUIDELINES:\n"
        "1. Start with a compelling hook that immediately grabs the reader.\n"
        "2. Introduce the protagonist and the central conflict clearly.\n"
        "3. Establish the setting effectively.\n"
        "4. End the chapter on a minor cliffhanger or an intriguing note.\n\n"
        "FORMATTING:\n"
        "Return the response strictly as:\n"
        "Chapter Title\n"
        "The story content..."
    )
    
    try:
        response = model.generate_content(
            system_prompt, 
            generation_config=generation_config
        )
        
        text = response.text.strip()
        lines = text.split('\n')
        
        # intelligent parsing to handle "Chapter 1: Title" vs just "Title"
        raw_title = lines[0].strip()
        chapter_title = raw_title.split(':')[-1].strip() if ':' in raw_title else raw_title
        
        content = "\n".join(lines[1:]).strip()
        
        return {
            "title": chapter_title,
            "content": content
        }
    except Exception as e:
        # Fallback for error handling
        print(f"Gemini Error: {e}")
        raise Exception("Failed to generate story. Please try again.")

async def generate_next_chapter(full_story_history: str, last_chapter_number: int, instructions: str) -> dict:
    """
    Generates the next chapter by feeding the FULL story context to ensure 
    character memory and plot continuity.
    """
    next_chapter_num = last_chapter_number + 1
    
    # We utilize Gemini 1.5's large context window by passing the entire story history.
    # This ensures the AI "remembers" obscure details from Chapter 1 when writing Chapter 10.
    system_prompt = (
        f"You are continuing an ongoing story. You must maintain perfect consistency with the text below.\n\n"
        f"=== STORY SO FAR ===\n"
        f"{full_story_history}\n"
        f"=== END OF CONTEXT ===\n\n"
        f"TASK: Write Chapter {next_chapter_num}.\n"
        f"USER INSTRUCTIONS: {instructions}\n\n"
        "GUIDELINES:\n"
        "1. Maintain the existing tone, writing style, and character voices.\n"
        "2. Ensure continuity: characters should remember previous events.\n"
        "3. Advance the plot logically based on previous chapters.\n"
        "4. First line must be the Chapter Title.\n"
    )

    try:
        response = model.generate_content(
            system_prompt,
            generation_config=generation_config
        )
        
        text = response.text.strip()
        lines = text.split('\n')
        
        raw_title = lines[0].strip()
        chapter_title = raw_title.replace(f"Chapter {next_chapter_num}:", "").strip()
        content = "\n".join(lines[1:]).strip()

        return {
            "title": chapter_title,
            "content": content
        }
    except Exception as e:
        raise Exception(f"Gemini API Error: {str(e)}")