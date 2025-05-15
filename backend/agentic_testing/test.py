# backend/agentic_testing/test.py
import sys
import os

# # Add the parent directory to Python path to enable app imports
# # This is the crucial fix - adding the parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

print("Current Working Directory:", os.getcwd())
print("Script Directory:", os.path.dirname(os.path.abspath(__file__)))
print("Updated Python Path (sys.path):")
for p in sys.path:
    print(p)

import asyncio
import json
from typing import List, Dict, Any, Optional
from autogen_core import CancellationToken
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from app.models import *
from app.database import SessionLocal
# Import the model client and the core search logic from helper functions
# Assuming search_songs is defined in helper_functions and takes db, query, mood_tag_ids
from helper_functions import *

# # Define a wrapper for your database functions
# def db_function_wrapper(func):
#     """
#     Decorator to handle database session creation and closing for functions.
#     Returns the result of the wrapped function on success,
#     or a dictionary {"error": ..., "message": ...} on exception.
#     """
#     def wrapper(*args, **kwargs):
#         # Create a new session for this function call
#         db = SessionLocal()
#         try:
#             # Call the original function with db as the first argument
#             # Assuming it expects 'db' as the first positional argument:
#             result = func(db, *args, **kwargs)
#             return result
#         except Exception as e:
#             # Log the error or handle it as needed
#             print(f"Database function error in {func.__name__}: {e}")
#             # Return an error structure that the caller can handle
#             # Return a dictionary with 'error' and 'message' keys
#             return {"error": str(e), "message": f"Database operation failed for {func.__name__}."}
#         finally:
#             db.close()
#     return wrapper

# # Original database function to get all tags
# # Note: This function is now wrapped by db_function_wrapper below
# def get_all_tags_db(db: SessionLocal) -> List[Mood]:
#     """
#     Fetches all tags from the database.

#     Args:
#         db: The SQLAlchemy database session.

#     Returns:
#         A list of all Mood model instances.
#     """
#     return db.query(Mood).all()

# # Wrapped version of get_all_tags for the agent tool
# @db_function_wrapper
# def get_all_tags_wrapped(db: SessionLocal) -> List[dict]:
#     """
#     Tool function to fetch all tags from the database and return as dictionaries.
#     Handles database session via decorator.

#     Args:
#         db: The SQLAlchemy database session (provided by decorator).

#     Returns:
#         A list of dictionaries, each with 'id' and 'name' for available tags.
#     """
#     tags = get_all_tags_db(db) # Call the original DB function
#     # Convert Mood objects to dictionaries with id and name
#     return [{"id": tag.id, "name": tag.name} for tag in tags]

# # --- Wrap the imported search_songs function ---
# # Apply the decorator to the imported search_songs function
# @db_function_wrapper
# def search_songs_wrapped(db: SessionLocal, query: Optional[str] = None, mood_tag_ids: Optional[List[int]] = None) -> List[Dict[str, Any]]:
#     """
#     Wrapped version of the search_songs function from helper_functions.
#     Handles database session via decorator.

#     Args:
#         db: The SQLAlchemy database session (provided by decorator).
#         query: Optional text query for title, artist, or album.
#         mood_tag_ids: Optional list of tag IDs. If provided, songs must have ALL specified tags.

#     Returns:
#         A list of dictionaries representing matching songs (title, artist, etc.).
#         Returns a dictionary {"error": ..., "message": ...} on failure.
#     """
#     # Ensure mood_tag_ids is a list if provided, handle potential single int or None
#     if isinstance(mood_tag_ids, int):
#          mood_tag_ids = [mood_tag_ids]
#     elif mood_tag_ids is None:
#          mood_tag_ids = []
#     elif not isinstance(mood_tag_ids, list):
#          # Handle unexpected types if necessary, maybe log a warning
#          print(f"Warning: Unexpected type for mood_tag_ids: {type(mood_tag_ids)}. Defaulting to empty list.")
#          mood_tag_ids = [] # Default to empty list if format is wrong

#     # Call the original search_songs function from helper_functions,
#     # passing the db session provided by the decorator.
#     # This call is now within the try block of the decorator's wrapper
#     songs = search_songs(db, query=query, mood_tag_ids=mood_tag_ids)

#     # Format the song results for presentation
#     # Assuming search_songs returns a list of Song objects
#     return [
#         {
#             "title": song.song_name,
#             "artist": song.artist,
#             "album": song.album,
#             # Include other relevant fields you want to present
#             "mood_annotation": song.mood_annotation,
#         }
#         for song in songs
#     ]
# # --- End Wrapping ---


# # --- System Message for the Agent (Focus on Mood Identification) ---
# system_message = """
# You are a music recommendation assistant. Your primary task is to understand the user's music preferences and identify the most relevant tags from the available list.

# Your process should be:
# 1. When the user describes the kind of music they want, ALWAYS CALL the `get_tags_tool()` first to see the available MOOD tag.
# 2. Analyze the user's request and the list of available tags to identify the most relevant tag IDs and names.
# 3. DO NOT search for songs yourself. Your only job is to identify the relevant MOOD tag.
# 4. DO NOT write any Python code in your response.
# 5. ONLY return a JSON object with the selected tags in the following format:
#    {"selected_tags": [{"id": tag_id_1, "name": "tag_name_1"}, {"id": tag_id_2, "name": "tag_name_2"}, ...]}
# 6. The JSON response should contain ONLY tag IDs and names that exist in the database and match the user's preferences.
# 7. If no relevant tags are found based on the user's input, return an empty list in the JSON: {"selected_tags": []}.
# 8. Do not include any other text or explanation outside the JSON object in your final response.
# """

# # --- Main Async Function ---
# async def main() -> None:
#     """
#     Main function to run the agent interaction loop.
#     """
#     # Define the tag recommendation tool using the wrapped function
#     # This is the ONLY tool the agent will have access to now
#     async def get_tags_tool() -> List[dict]:
#         """
#         Get all available music tags from the database.

#         Returns:
#             A list of dictionaries, each with 'id' and 'name' for available tags.
#         """
#         print("\n--- Calling Tool: get_tags_tool ---")
#         result = get_all_tags_wrapped() # Call the wrapped function
#         print(f"--- Tool Result (first 5): {result[:5]}... ---") # Print partial result if list is long
#         return result

#     assistant = AssistantAgent(
#         name="music_tag_identifier", # Renamed to reflect its role
#         system_message=system_message,
#         model_client=model_client,
#         # ONLY register the tag tool
#         tools=[get_tags_tool],
#         # Configure the assistant to potentially call tools
#         reflect_on_tool_use=True, # Helps understand agent's reasoning
#     )

#     print("Music Mood Identifier Agent Ready. Tell me what kind of music you're looking for (e.g., 'energetic pop' or 'mellow jazz'). Type 'exit' to quit.")

#     while True:
#         user_input = input("User: ")
#         if user_input.lower() == "exit":
#             break

#         # Send the user message to the assistant
#         # Autogen handles the tool call (get_tags_tool) and the agent's final response
#         response = await assistant.on_messages([TextMessage(content=user_input, source="user")], CancellationToken())

#         # Process the assistant's final response
#         if response.chat_message.content:
#             output_text = response.chat_message.to_text()
#             print("Assistant's final response:\n", output_text)

#             # --- Extract Mood IDs and Search for Songs ---
#             try:
#                 # Find the first occurrence of '{' and try to parse from there
#                 json_start = output_text.find('{')
#                 if json_start != -1:
#                     json_str = output_text[json_start:]
#                     # Attempt to parse the JSON output
#                     data = json.loads(json_str)

#                     # Check if the expected key is in the JSON and it's a list
#                     if "selected_tags" in data and isinstance(data["selected_tags"], list):
#                         selected_tag_ids = [tag_info.get("id") for tag_info in data["selected_tags"] if isinstance(tag_info.get("id"), int)]
#                         selected_tag_names = [tag_info.get("name") for tag_info in data["selected_tags"] if tag_info.get("name")]

#                         print(f"\nIdentified Mood IDs: {selected_tag_ids}")
#                         print(f"Identified Mood Names: {selected_tag_names}")


#                         if selected_tag_ids:
#                             print("\n--- Searching for songs with these tags ---")
#                             # Call the *wrapped* search_songs function directly
#                             # This function now handles getting the DB session internally
#                             matching_songs_data = search_songs_wrapped(mood_tag_ids=selected_tag_ids) # Call the wrapped function

#                             print("\n--- Recommended Songs ---")
#                             # --- FIX: Check if matching_songs_data is the error dict first ---
#                             if isinstance(matching_songs_data, dict) and matching_songs_data.get("error"):
#                                 print(f"Error fetching songs: {matching_songs_data['message']}")
#                             # --- End FIX ---
#                             elif isinstance(matching_songs_data, list) and matching_songs_data:
#                                 # If it's a list and not empty, process the songs
#                                 for song in matching_songs_data:
#                                     # Ensure each item in the list is a dictionary before using .get()
#                                     if isinstance(song, dict):
#                                         title = song.get("title", "Unknown Title")
#                                         artist = song.get("artist", "Unknown Artist")
#                                         print(f"- {title} by {artist}")
#                                     else:
#                                         print(f"- Unexpected song data format: {song}")
#                             else:
#                                 # If it's an empty list or not a list/dict (shouldn't happen with wrapper)
#                                 print("No songs found matching the selected tags.")

#                         else:
#                             print("\nNo relevant tags identified by the agent.")

#                     else:
#                          print("\nAssistant did not return the expected JSON format with 'selected_tags' list.")

#             except json.JSONDecodeError:
#                 print("\nAssistant's final response was not valid JSON.")
#             except Exception as e:
#                 print(f"\nError processing assistant's final response or searching songs: {e}")

#         else:
#             print("Assistant provided an empty response.")


#     await model_client.close() # Close the model client connection

# if __name__ == "__main__":
#     # Ensure tables are created and seeded before running the agent
#     # You might want to run seed.py separately or include table creation here
#     # from app.database import engine
#     # from app.models import Base
#     # print("Ensuring database tables exist...")
#     # Base.metadata.create_all(bind=engine)
#     # print("Database table check complete.")
#     # Note: Seeding should be done once before running the agent repeatedly.

#     asyncio.run(main())
# backend/agentic_testing/test.py

# --- Remove the sys.path modification code ---
# It is no longer needed when running with `python -m app.agentic_testing.test`
# ... (removed lines) ...
# --- End Removal ---

# Define a wrapper for your database functions
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

@db_function_wrapper
def get_all_moods_tool(db: Session) -> List[dict]: # Accepts db
    """
    Tool function to fetch all moods from the database and return as dictionaries.

    Returns:
        A list of dictionaries, each with 'id' and 'name' for available moods.
    """
    moods = get_all_moods(db)
    return [{"id": mood.id, "name": mood.name} for mood in moods]

@db_function_wrapper
def get_all_contexts_tool(db: Session) -> List[dict]: # Accepts db
    """
    Tool function to fetch all contexts from the database and return as dictionaries.

    Returns:
        A list of dictionaries, each with 'id', 'name', and 'description' for available contexts.
    """
    contexts = get_all_contexts(db)
    return [{"id": context.id, "name": context.name, "description": context.description} for context in contexts]

@db_function_wrapper
def search_songs_wrapped(db: Session, query: Optional[str] = None, mood_ids: Optional[List[int]] = None, context_ids: Optional[List[int]] = None) -> List[Dict[str, Any]]:
    """
    Wrapped version of the search_songs function for the orchestrator.
    Handles database session via decorator.

    Args:
        db: The SQLAlchemy database session (provided by decorator).
        query: Optional text query.
        mood_ids: Optional list of mood IDs.
        context_ids: Optional list of context IDs.

    Returns:
        A list of dictionaries representing matching songs.
        Returns a dictionary {"error": ..., "message": ...} on failure.
    """
    # Ensure IDs are lists, handling potential single int or None input (less likely here, but safe)
    if isinstance(mood_ids, int): mood_ids = [mood_ids]
    elif mood_ids is None: mood_ids = []
    mood_ids = [item for item in mood_ids if isinstance(item, int)] # Ensure list contains only ints

    if isinstance(context_ids, int): context_ids = [context_ids]
    elif context_ids is None: context_ids = []
    context_ids = [item for item in context_ids if isinstance(item, int)] # Ensure list contains only ints

    # Call the core search_songs function
    songs = search_songs(db, query=query, mood_ids=mood_ids, context_ids=context_ids)

    # Format results
    return [
        {
            "title": song.song_name,
            "artist": song.artist if song.artist else "Unknown Artist",
            "album": song.album if song.album else "Unknown Album",
            "link": song.link,
            "image": song.image,
            "mood_annotation": song.mood_annotation,
        }
        for song in songs
    ]


# System Message for the Mood Agent
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

async def main() -> None:
    """
    Main function to orchestrate the interaction with specialized agents
    and perform the final song search.
    """
    # Define the tool *definitions* that will be passed to the agents
    async def get_all_moods_tool_definition() -> List[dict]:
         print("\n--- Mood Agent Calling Tool: get_all_moods_tool ---")
         result = get_all_moods_tool() # Call the wrapped function
         print(f"--- Mood Tool Result (first 5): {result[:5]}... ---")
         if isinstance(result, dict) and result.get("error"):
             print(f"Mood Tool error: {result['message']}")
             return [] # Return empty list on error for the agent
         return result

    async def get_all_contexts_tool_definition() -> List[dict]:
         print("\n--- Context Agent Calling Tool: get_all_contexts_tool ---")
         result = get_all_contexts_tool() # Call the wrapped function
         print(f"--- Context Tool Result (first 5): {result[:5]}... ---")
         if isinstance(result, dict) and result.get("error"):
             print(f"Context Tool error: {result['message']}")
             return [] # Return empty list on error for the agent
         return result


    # Instantiate the two specialized agents
    mood_agent = AssistantAgent(
        name="mood_identifier",
        system_message=mood_agent_system_message,
        model_client=model_client,
        tools=[get_all_moods_tool_definition], # ONLY the mood tool
        reflect_on_tool_use=True,
    )

    context_agent = AssistantAgent(
        name="context_identifier",
        system_message=context_agent_system_message,
        model_client=model_client,
        tools=[get_all_contexts_tool_definition], # ONLY the context tool
        reflect_on_tool_use=True,
    )


    print("Music Filter Orchestrator Ready. Tell me what kind of music/situation you're looking for (e.g., 'energetic music for working out'). Type 'exit' to quit.")
    print("Ensure your database is running and seeded with moods and contexts (and songs linked).")


    while True:
        user_input = input("\nUser: ")
        if user_input.lower() == "exit":
            break

        # --- Orchestration Step 1: Get Mood IDs from Mood Agent ---
        print("\n--- Orchestrator sending prompt to Mood Agent ---")
        mood_response = await mood_agent.on_messages([TextMessage(content=user_input, source="user")], CancellationToken())
        mood_agent_content = mood_response.chat_message.content if mood_response.chat_message else None

        selected_mood_ids = []
        if mood_agent_content:
            print("Mood Agent final response:\n", mood_agent_content)
            try:
                json_start = mood_agent_content.find('{')
                if json_start != -1:
                    json_str = mood_agent_content[json_start:]
                    data = json.loads(json_str)
                    if "selected_mood_ids" in data and isinstance(data["selected_mood_ids"], list):
                         selected_mood_ids = [item for item in data["selected_mood_ids"] if isinstance(item, int)]
                         print(f"Orchestrator extracted Mood IDs: {selected_mood_ids}")
                    else:
                         print("Orchestrator: Mood Agent did not return expected JSON with 'selected_mood_ids'.")
            except json.JSONDecodeError:
                print("Orchestrator: Mood Agent response was not valid JSON.")
            except Exception as e:
                print(f"Orchestrator: Error parsing Mood Agent response: {e}")
        else:
            print("Orchestrator: Mood Agent provided an empty response.")


        # --- Orchestration Step 2: Get Context IDs from Context Agent ---
        print("\n--- Orchestrator sending prompt to Context Agent ---")
        # Send the same user input to the context agent
        context_response = await context_agent.on_messages([TextMessage(content=user_input, source="user")], CancellationToken())
        context_agent_content = context_response.chat_message.content if context_response.chat_message else None

        selected_context_ids = []
        if context_agent_content:
            print("Context Agent final response:\n", context_agent_content)
            try:
                json_start = context_agent_content.find('{')
                if json_start != -1:
                    json_str = context_agent_content[json_start:]
                    data = json.loads(json_str)
                    if "selected_context_ids" in data and isinstance(data["selected_context_ids"], list):
                        selected_context_ids = [item for item in data["selected_context_ids"] if isinstance(item, int)]
                        print(f"Orchestrator extracted Context IDs: {selected_context_ids}")
                    else:
                        print("Orchestrator: Context Agent did not return expected JSON with 'selected_context_ids'.")
            except json.JSONDecodeError:
                print("Orchestrator: Context Agent response was not valid JSON.")
            except Exception as e:
                print(f"Orchestrator: Error parsing Context Agent response: {e}")
        else:
             print("Orchestrator: Context Agent provided an empty response.")


        # --- Orchestration Step 3: Perform Song Search ---
        # Assuming no direct text query is identified by these specialized agents
        identified_query = None # Or modify agents/parsing to identify a query if needed

        # Only search if at least one filter is present
        if identified_query or selected_mood_ids or selected_context_ids:
            print("\n--- Orchestrator Searching for songs... ---")
            # Call the wrapped search function with collected IDs
            matching_songs_data = search_songs_wrapped(
                query=identified_query,
                mood_ids=selected_mood_ids,
                context_ids=selected_context_ids
            )

            print("\n--- Recommended Songs ---")
            if isinstance(matching_songs_data, dict) and matching_songs_data.get("error"):
                print(f"Orchestrator: Error fetching songs: {matching_songs_data['message']}")
            elif isinstance(matching_songs_data, list):
                if not matching_songs_data:
                    print("Orchestrator: No songs found matching the criteria.")
                else:
                    for song in matching_songs_data:
                         if isinstance(song, dict):
                            title = song.get("title", "Unknown Title")
                            artist = song.get("artist", "Unknown Artist")
                            link = song.get("link", "No Link")
                            image = song.get("image", "No Image")
                            print(f"- {title} by {artist}")
                            if link and link != "No Link":
                                print(f"  Link: {link}")
                            if image and image != "No Image":
                                print(f"  Image: {image}")
                         else:
                            print(f"- Orchestrator: Unexpected song data format: {song}")
            else:
                # Should ideally not be reached
                print("Orchestrator: No songs found matching the criteria.")

        else:
             print("\nOrchestrator: No relevant moods or contexts identified by either agent.")


    await model_client.close() # Close the model client connection

if __name__ == "__main__":
    print("Starting music filter orchestrator...")
    # Ensure tables are created and seeded with moods and contexts (and songs linked to them)
    # Example: python3 -m app.seed
    asyncio.run(main())
