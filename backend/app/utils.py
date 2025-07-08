# app/agentic-testing/helper_functions.py
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional
from models import Mood,Song,Context,song_mood_table,song_context_table

mood_agent_system_message = """
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

# System Message for the Context Agent
context_agent_system_message = """
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
# Function to fetch all tags
def get_all_moods(db: Session) -> List[Mood]:
    """
    Fetches all tags from the database.

    Args:
        db: The SQLAlchemy database session.

    Returns:
        A list of all Tag model instances.
    """
    return db.query(Mood).all()

def get_all_contexts(db: Session) -> List[Context]:
    """
    Fetches all tags from the database.

    Args:
        db: The SQLAlchemy database session.

    Returns:
        A list of all Tag model instances.
    """
    return db.query(Context).all()

# Function to fetch all songs
def get_all_songs(db: Session) -> List[Song]:
    """
    Fetches all songs from the database.

    Args:
        db: The SQLAlchemy database session.

    Returns:
        A list of all Song model instances.
    """
    return db.query(Song).all()
def search_songs(
    db: Session,
    query: Optional[str] = None,
    mood_ids: Optional[List[int]] = None,
    context_ids: Optional[List[int]] = None # Added context_ids parameter
) -> List[Song]:
    """
    Searches for songs by title, artist, or album, optionally filtered by mood and context IDs.
    - Text query uses OR condition on title, artist, album.
    - Mood IDs filter uses OR condition (song must have ANY of the specified moods).
    - Context IDs filter uses OR condition (song must have ANY of the specified contexts).
    - Filters (query, moods, contexts) are combined with AND logic:
      A song matches if it meets the query criteria AND (if mood_ids provided) has >=1 matching mood
      AND (if context_ids provided) has >=1 matching context.

    Args:
        db: The SQLAlchemy database session.
        query: Optional text query for title, artist, or album.
        mood_ids: Optional list of mood IDs. If provided, songs must have ANY of the specified moods.
        context_ids: Optional list of context IDs. If provided, songs must have ANY of the specified contexts.

    Returns:
        A list of Song model instances matching the criteria.
    """
    # If no filters are provided at all, return empty
    if not query and (not mood_ids or len(mood_ids) == 0) and (not context_ids or len(context_ids) == 0):
        return []

    # Start with a base query for songs
    db_query = db.query(Song)

    # Apply text search filter if query is provided
    if query:
        search_pattern = f"%{query}%" # Use wildcard for partial matching
        db_query = db_query.filter(
            or_(
                Song.song_name.ilike(search_pattern), # ilike for case-insensitive match
                Song.artist.ilike(search_pattern),
                Song.album.ilike(search_pattern)
            )
        )

    # Apply mood filter if mood_ids are provided (OR condition within moods)
    # Combined with text query using AND (another filter() call implicitly uses AND)
    if mood_ids and len(mood_ids) > 0:
        # Join with the song_mood_association table and filter by mood IDs
        db_query = db_query.join(song_mood_table).filter(song_mood_table.c.mood_id.in_(mood_ids))
        # We'll add distinct() later if needed after all joins

    # Apply context filter if context_ids are provided (OR condition within contexts)
    # Combined with previous filters (query, moods) using AND
    if context_ids and len(context_ids) > 0:
        # Join with the song_context_association table and filter by context IDs
        # Use a separate join for contexts
        db_query = db_query.join(song_context_table).filter(song_context_table.c.context_id.in_(context_ids))
        # We'll add distinct() later if needed after all joins


    # Add distinct() if multiple joins might produce duplicate Song objects
    # This is needed if a song matches multiple moods or multiple contexts or both moods and contexts
    if (mood_ids and len(mood_ids) > 0) or (context_ids and len(context_ids) > 0):
         db_query = db_query.distinct()


    # Execute the query and return results
    songs = db_query.all()

    return songs

from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
import os
# Load from .env file
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
model_client = OpenAIChatCompletionClient(
        model="llama-3.3-70b-versatile",
        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": "unknown",
            "structured_output": True
        },
        base_url="https://api.groq.com/openai/v1",
        api_key=GROQ_API_KEY,
        # response_format={"type": "json_object"},
    )
def db_function_wrapper(func):
    """
    Decorator to handle database session creation and closing for functions.
    Returns the result of the wrapped function on success,
    or a dictionary {"error": ..., "message": ...} on exception.
    """
    def wrapper(*args, **kwargs):
        db = SessionLocal()
        try:
            # Call the original function with db as the first argument
            result = func(db, *args, **kwargs)
            return result
        except Exception as e:
            print(f"Database function error in {func.__name__}: {e}")
            return {"error": str(e), "message": f"Database operation failed for {func.__name__}."}
        finally:
            db.close()
    wrapper.__name__ = func.__name__ # Preserve original function name for tool calls
    wrapper.__doc__ = func.__doc__ # Preserve original docstring for tool description
    return wrapper