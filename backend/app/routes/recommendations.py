from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import asyncio
import json

from autogen_core import CancellationToken
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage

from database import get_db
from models import Song
from schemas import SongResponseV2, MusicRecommendationRequest

# from app.agentic_testing.helper_functions import (get_all_contexts,get_all_songs,search_songs,model_client)
from utils import get_all_contexts, search_songs, model_client, get_all_moods

# Create router
router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"]
)

# Define wrapper for database functions
def db_function_wrapper(func):
    """
    Decorator to handle database session for functions.
    """
    def wrapper(db: Session, *args, **kwargs):
        try:
            result = func(db, *args, **kwargs)
            return result
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Database operation failed: {str(e)}"
            )
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper

# System messages for the specialized agents
MOOD_AGENT_SYSTEM_MESSAGE = """
You are a music mood identifier agent. Your SOLE task is to understand the user's music preferences related to MOOD and identify the most relevant MOOD IDs from the available list.

Your process:
1. Call `get_all_moods_tool()` FIRST to see available MOODs.
2. Analyze the user's request and the list of available MOODs to identify the most relevant MOOD IDs.
3. IGNORE any mentions of context, situation, activity, or non-mood related filtering.
4. DO NOT search for songs.
5. DO NOT write Python code.
6. ONLY return a JSON object with selected MOOD IDs: {"selected_mood_ids": [mood_id_1, mood_id_2, ...]}
7. Return only IDs that exist in the database list and match the user's mood preference.
8. If no relevant MOOD IDs are found, return {"selected_mood_ids": []}.
9. No other text outside the JSON.
"""

CONTEXT_AGENT_SYSTEM_MESSAGE = """
You are a music context identifier agent. Your SOLE task is to understand the user's music preferences related to CONTEXT or situation and identify the most relevant CONTEXT IDs from the available list.

Your process:
1. Call `get_all_contexts_tool()` FIRST to see available CONTEXTs.
2. Analyze the user's request and the list of available CONTEXTs to identify the most relevant CONTEXT IDs.
3. IGNORE any mentions of mood, feeling, emotion, or non-context related filtering.
4. DO NOT search for songs.
5. DO NOT write Python code.
6. ONLY return a JSON object with selected CONTEXT IDs: {"selected_context_ids": [context_id_1, context_id_2, ...]}
7. Return only IDs that exist in the database list and match the user's context/situation preference.
8. If no relevant CONTEXT IDs are found, return {"selected_context_ids": []}.
9. No other text outside the JSON.
"""

# Create the agents once at module level
# They will be reused across requests to avoid recreation overhead
mood_agent = None
context_agent = None

# Define the agent tool functions without FastAPI dependencies
async def get_all_moods_tool() -> List[dict]:
    """
    Tool function to fetch all moods from the database.
    
    Returns:
        A list of dictionaries, each with 'id' and 'name' for available moods.
    """
    # Create a new db session that's not exposed in the function signature
    db = next(get_db())
    try:
        moods = get_all_moods(db)
        return [{"id": mood.id, "name": mood.name} for mood in moods]
    finally:
        db.close()

async def get_all_contexts_tool() -> List[dict]:
    """
    Tool function to fetch all contexts from the database.
    
    Returns:
        A list of dictionaries, each with 'id', 'name', and 'description' for available contexts.
    """
    # Create a new db session that's not exposed in the function signature
    db = next(get_db())
    try:
        contexts = get_all_contexts(db)
        return [{"id": context.id, "name": context.name, "description": context.description} for context in contexts]
    finally:
        db.close()

def setup_agents():
    """Initialize agents if not already created"""
    global mood_agent, context_agent
    
    if mood_agent is None:
        mood_agent = AssistantAgent(
            name="mood_identifier",
            system_message=MOOD_AGENT_SYSTEM_MESSAGE,
            model_client=model_client,
            tools=[get_all_moods_tool],  # Use the new tool function without dependency
            reflect_on_tool_use=True,
        )
    
    if context_agent is None:
        context_agent = AssistantAgent(
            name="context_identifier",
            system_message=CONTEXT_AGENT_SYSTEM_MESSAGE,
            model_client=model_client,
            tools=[get_all_contexts_tool],  # Use the new tool function without dependency
            reflect_on_tool_use=True,
        )

# Main endpoint
@router.post("/recommend", response_model=List[SongResponseV2])
async def recommend_music(
    request: MusicRecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint to recommend music based on user prompt.
    Uses specialized AI agents to identify moods and contexts,
    then searches for matching songs.
    """
    # Ensure agents are set up
    setup_agents()
    
    # Extract user prompt
    user_prompt = request.prompt
    
    # 1. Get mood IDs from Mood Agent
    mood_response = await mood_agent.on_messages(
        [TextMessage(content=user_prompt, source="user")], 
        CancellationToken()
    )
    
    mood_agent_content = mood_response.chat_message.content if mood_response.chat_message else None
    selected_mood_ids = []
    
    if mood_agent_content:
        try:
            json_start = mood_agent_content.find('{')
            if json_start != -1:
                json_str = mood_agent_content[json_start:]
                data = json.loads(json_str)
                if "selected_mood_ids" in data and isinstance(data["selected_mood_ids"], list):
                    selected_mood_ids = [item for item in data["selected_mood_ids"] if isinstance(item, int)]
        except json.JSONDecodeError:
            pass
        except Exception as e:
            print(f"Error parsing mood agent response: {e}")
    
    # 2. Get context IDs from Context Agent
    context_response = await context_agent.on_messages(
        [TextMessage(content=user_prompt, source="user")], 
        CancellationToken()
    )
    
    context_agent_content = context_response.chat_message.content if context_response.chat_message else None
    selected_context_ids = []
    
    if context_agent_content:
        try:
            json_start = context_agent_content.find('{')
            if json_start != -1:
                json_str = context_agent_content[json_start:]
                data = json.loads(json_str)
                if "selected_context_ids" in data and isinstance(data["selected_context_ids"], list):
                    selected_context_ids = [item for item in data["selected_context_ids"] if isinstance(item, int)]
        except json.JSONDecodeError:
            pass
        except Exception as e:
            print(f"Error parsing context agent response: {e}")
    
    # 3. Search for songs with identified criteria
    # Handle text query if needed (optional)
    text_query = None  # Could be extracted from prompt using another agent if needed
    
    # If no filters identified at all, return empty list
    if not text_query and not selected_mood_ids and not selected_context_ids:
        return []
    
    # Perform the search
    matching_songs = search_songs(
        db=db,
        query=text_query,
        mood_ids=selected_mood_ids,
        context_ids=selected_context_ids
    )
    
    # Format and return the results
    return [
        {   
            "id": song.id,
            "title": song.song_name,
            "artist": song.artist if song.artist else "Unknown Artist",
            "album": song.album if song.album else "Unknown Album",
            "link": song.link,
            "image": song.image,
            "mood_annotation": song.mood_annotation,
        }
        for song in matching_songs
    ]

# Close model client when application shuts down
@router.on_event("shutdown")
async def shutdown_event():
    await model_client.close()