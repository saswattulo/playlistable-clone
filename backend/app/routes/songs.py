# app/routes/songs.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
import models
import schemas
from database import get_db
from typing import Optional, List, Dict, Any


router = APIRouter(prefix="/songs", tags=["Songs"])

# CREATE a song
@router.post("/", response_model=schemas.SongResponse)
def create_song(song: schemas.SongCreate, db: Session = Depends(get_db)):
    # Extract mood_ids and context_ids before creating the song object
    song_data = song.dict(exclude={"mood_ids", "context_ids"})
    db_song = models.Song(**song_data)

    # Handle moods if provided
    if song.mood_ids:
        moods = db.query(models.Mood).filter(models.Mood.id.in_(song.mood_ids)).all()
        db_song.moods = moods

    # Handle contexts if provided
    if song.context_ids:
        contexts = db.query(models.Context).filter(models.Context.id.in_(song.context_ids)).all()
        db_song.contexts = contexts

    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song


# READ all songs
@router.get("/", response_model=list[schemas.SongResponse])
def get_all_songs(db: Session = Depends(get_db)):
    return db.query(models.Song).all()


@router.get("/search/", response_model=list[schemas.SongResponse])
def search_songs(
    query: Optional[str] = Query(None, min_length=1, description="Search query for song name, artist, or album"),
    mood_ids: Optional[List[int]] = Query(None, description="List of mood IDs to filter by (songs must have ALL specified moods)"),
    context_ids: Optional[List[int]] = Query(None, description="List of context IDs to filter by (songs must have ALL specified contexts)"),
    db: Session = Depends(get_db)
):
    """
    Search for songs by song_name, artist, or album, optionally filtered by moods and/or contexts.
    If mood_ids and/or context_ids are provided, only songs associated with ALL specified filters are returned.
    If no query, mood_ids, or context_ids are provided, returns an empty list.
    """
    if not query and not mood_ids and not context_ids:
        # Return empty list if no search criteria are provided
        return []

    # Start with a base query
    db_query = db.query(models.Song)

    # Apply text search filter if query is provided
    if query:
        search_pattern = f"%{query}%"  # Use wildcard for partial matching
        db_query = db_query.filter(
            or_(
                models.Song.song_name.ilike(search_pattern),  # Updated from title to song_name
                models.Song.artist.ilike(search_pattern),
                models.Song.album.ilike(search_pattern)
            )
        )

    # Apply mood filter if mood_ids are provided
    if mood_ids:
        # Filter by multiple moods (AND condition)
        db_query = db_query.join(models.song_mood_table).join(models.Mood)
        db_query = db_query.filter(models.Mood.id.in_(mood_ids))
        db_query = db_query.group_by(models.Song.id)
        db_query = db_query.having(func.count(models.Mood.id) == len(set(mood_ids)))  # Use set to handle duplicate mood_ids

    # Apply context filter if context_ids are provided
    if context_ids:
        # If we already filtered by moods, we need a subquery to maintain the previous results
        if mood_ids:
            # Get the IDs from previous query to maintain those filters
            filtered_song_ids = [song.id for song in db_query.all()]
            # Reset the query but keep the filtered songs
            db_query = db.query(models.Song).filter(models.Song.id.in_(filtered_song_ids))
        
        # Apply context filtering
        db_query = db_query.join(models.song_context_table).join(models.Context)
        db_query = db_query.filter(models.Context.id.in_(context_ids))
        db_query = db_query.group_by(models.Song.id)
        db_query = db_query.having(func.count(models.Context.id) == len(set(context_ids)))

    # Execute the query and return results
    songs = db_query.all()
    return songs


# READ a specific song by ID
@router.get("/{song_id}", response_model=schemas.SongResponse)
def get_song(song_id: int, db: Session = Depends(get_db)):
    song = db.query(models.Song).filter(models.Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song


# UPDATE a song
@router.put("/{song_id}", response_model=schemas.SongResponse)
def update_song(song_id: int, song_update: schemas.SongCreate, db: Session = Depends(get_db)):
    # Filter by integer ID
    song = db.query(models.Song).filter(models.Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    # Update song attributes excluding mood_ids and context_ids
    for attr, value in song_update.dict(exclude={"mood_ids", "context_ids"}).items():
        setattr(song, attr, value)

    # Update moods if mood_ids are provided
    if song_update.mood_ids is not None:
        moods = db.query(models.Mood).filter(models.Mood.id.in_(song_update.mood_ids)).all()
        song.moods = moods

    # Update contexts if context_ids are provided
    if song_update.context_ids is not None:
        contexts = db.query(models.Context).filter(models.Context.id.in_(song_update.context_ids)).all()
        song.contexts = contexts

    db.commit()
    db.refresh(song)
    return song


# DELETE a song
@router.delete("/{song_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_song(song_id: int, db: Session = Depends(get_db)):
    song = db.query(models.Song).filter(models.Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    db.delete(song)
    db.commit()
    return

# Mood annotation endpoints
@router.post("/{song_id}/moods/{mood_id}", status_code=status.HTTP_200_OK)
def add_mood_to_song(song_id: int, mood_id: int, db: Session = Depends(get_db)):
    """
    Assign a mood to a song.
    """
    # Check if the song exists
    song = db.query(models.Song).filter(models.Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    # Check if the mood exists
    mood = db.query(models.Mood).filter(models.Mood.id == mood_id).first()
    if not mood:
        raise HTTPException(status_code=404, detail="Mood not found")
    
    # Check if the relationship already exists
    if mood in song.moods:
        return {"message": f"Mood '{mood.name}' is already assigned to song '{song.song_name}'"}
    
    # Add the mood to the song
    song.moods.append(mood)
    db.commit()
    
    return {"message": f"Mood '{mood.name}' successfully assigned to song '{song.song_name}'"}

@router.delete("/{song_id}/moods/{mood_id}", status_code=status.HTTP_200_OK)
def remove_mood_from_song(song_id: int, mood_id: int, db: Session = Depends(get_db)):
    """
    Remove a mood from a song.
    """
    # Check if the song exists
    song = db.query(models.Song).filter(models.Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    # Check if the mood exists
    mood = db.query(models.Mood).filter(models.Mood.id == mood_id).first()
    if not mood:
        raise HTTPException(status_code=404, detail="Mood not found")
    
    # Check if the relationship exists
    if mood not in song.moods:
        raise HTTPException(status_code=404, detail=f"Mood '{mood.name}' is not assigned to song '{song.song_name}'")
    
    # Remove the mood from the song
    song.moods.remove(mood)
    db.commit()
    
    return {"message": f"Mood '{mood.name}' successfully removed from song '{song.song_name}'"}

# Context annotation endpoints
@router.post("/{song_id}/contexts/{context_id}", status_code=status.HTTP_200_OK)
def add_context_to_song(song_id: int, context_id: int, db: Session = Depends(get_db)):
    """
    Assign a context to a song.
    """
    # Check if the song exists
    song = db.query(models.Song).filter(models.Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    # Check if the context exists
    context = db.query(models.Context).filter(models.Context.id == context_id).first()
    if not context:
        raise HTTPException(status_code=404, detail="Context not found")
    
    # Check if the relationship already exists
    if context in song.contexts:
        return {"message": f"Context '{context.name}' is already assigned to song '{song.song_name}'"}
    
    # Add the context to the song
    song.contexts.append(context)
    db.commit()
    
    return {"message": f"Context '{context.name}' successfully assigned to song '{song.song_name}'"}

@router.delete("/{song_id}/contexts/{context_id}", status_code=status.HTTP_200_OK)
def remove_context_from_song(song_id: int, context_id: int, db: Session = Depends(get_db)):
    """
    Remove a context from a song.
    """
    # Check if the song exists
    song = db.query(models.Song).filter(models.Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    # Check if the context exists
    context = db.query(models.Context).filter(models.Context.id == context_id).first()
    if not context:
        raise HTTPException(status_code=404, detail="Context not found")
    
    # Check if the relationship exists
    if context not in song.contexts:
        raise HTTPException(status_code=404, detail=f"Context '{context.name}' is not assigned to song '{song.song_name}'")
    
    # Remove the context from the song
    song.contexts.remove(context)
    db.commit()
    
    return {"message": f"Context '{context.name}' successfully removed from song '{song.song_name}'"}

# Batch annotation endpoints for moods and contexts
@router.post("/{song_id}/annotations/batch", status_code=status.HTTP_200_OK)
def batch_annotate_song(
    song_id: int, 
    annotations: Dict[str, List[int]] = Body(..., example={"mood_ids": [1, 2], "context_ids": [3, 4]}),
    db: Session = Depends(get_db)
):
    """
    Batch assign moods and contexts to a song.
    Provide mood_ids and/or context_ids in the request body.
    """
    # Check if the song exists
    song = db.query(models.Song).filter(models.Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    results = {"added_moods": [], "added_contexts": [], "already_assigned_moods": [], "already_assigned_contexts": []}
    
    # Process mood annotations
    if "mood_ids" in annotations and annotations["mood_ids"]:
        moods = db.query(models.Mood).filter(models.Mood.id.in_(annotations["mood_ids"])).all()
        mood_map = {mood.id: mood for mood in moods}
        
        for mood_id in annotations["mood_ids"]:
            if mood_id not in mood_map:
                continue  # Skip non-existent moods
                
            mood = mood_map[mood_id]
            if mood in song.moods:
                results["already_assigned_moods"].append({"id": mood.id, "name": mood.name})
            else:
                song.moods.append(mood)
                results["added_moods"].append({"id": mood.id, "name": mood.name})
    
    # Process context annotations
    if "context_ids" in annotations and annotations["context_ids"]:
        contexts = db.query(models.Context).filter(models.Context.id.in_(annotations["context_ids"])).all()
        context_map = {context.id: context for context in contexts}
        
        for context_id in annotations["context_ids"]:
            if context_id not in context_map:
                continue  # Skip non-existent contexts
                
            context = context_map[context_id]
            if context in song.contexts:
                results["already_assigned_contexts"].append({"id": context.id, "name": context.name})
            else:
                song.contexts.append(context)
                results["added_contexts"].append({"id": context.id, "name": context.name})
    
    db.commit()
    
    return results