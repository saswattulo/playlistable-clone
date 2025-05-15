# app/schemas.py
from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, List
from datetime import date, datetime

### ---- Mood ---- ###
class MoodBase(BaseModel):
    name: str

class MoodCreate(MoodBase):
    pass

class MoodResponse(MoodBase):
    id: int
    
    class Config:
        orm_mode = True

class MoodUpdate(BaseModel):
    name: str

### ---- Context ---- ###
class ContextBase(BaseModel):
    name: str
    description: Optional[str] = None

class ContextCreate(ContextBase):
    pass

class ContextResponse(ContextBase):
    id: int
    
    class Config:
        orm_mode = True

class ContextUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

### ---- Song ---- ###
class SongBase(BaseModel):
    song_name: str  # Updated from title to match the model
    artist: Optional[str]
    album: Optional[str] = None
    release_date: Optional[date] = None
    duration_ms: Optional[int] = None
    explicit: Optional[str] = None
    
    # Spotify features
    danceability: Optional[float] = None
    energy: Optional[float] = None
    key: Optional[int] = None
    loudness: Optional[float] = None
    mode: Optional[int] = None
    speechiness: Optional[float] = None
    acousticness: Optional[float] = None
    instrumentalness: Optional[float] = None
    liveness: Optional[float] = None
    valence: Optional[float] = None
    tempo: Optional[float] = None
    time_signature: Optional[int] = None
    popularity: Optional[int] = None
    
    # URLs
    # Using Optional[str] for URLs as HttpUrl requires validation which might not be needed here,
    # and the model stores them as String. Can change back to HttpUrl if validation is desired.
    link: Optional[str] = None  # Updated from song_url to match the model
    image: Optional[str] = None  # Updated from album_art_url to match the model
    
    # Annotation
    mood_annotation: Optional[str] = None

class SongCreate(SongBase):
    mood_ids: Optional[List[int]] = []  # Updated from tag_ids to mood_ids
    context_ids: Optional[List[int]] = []  # Added context_ids

class SongResponse(SongBase):
    id: int
    moods: List[MoodResponse] = []  # Updated from tags to moods
    contexts: List[ContextResponse] = []  # Added contexts
    
    class Config:
        orm_mode = True

### ---- User ---- ###
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str  # Plaintext for now; hash before saving

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

### ---- Annotation ---- ###
class AnnotationBase(BaseModel):
    content: str

class AnnotationCreate(AnnotationBase):
    user_id: int
    song_id: int

class AnnotationResponse(AnnotationBase):
    id: int
    user: UserResponse
    song_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

### ---- UserSongInteraction ---- ###
class InteractionBase(BaseModel):
    liked: bool
    play_count: int

class InteractionCreate(InteractionBase):
    user_id: int
    song_id: int

class InteractionResponse(InteractionBase):
    id: int
    user: UserResponse
    song_id: int
    last_played: datetime
    
    class Config:
        orm_mode = True


class MusicRecommendationRequest(BaseModel):
    """Request schema for music recommendation endpoint."""
    prompt: str
    
    class Config:
        schema_extra = {
            "example": {
                "prompt": "I need some upbeat music for my workout session"
            }
        }

class SongResponseV2(BaseModel):
    """Response schema for song items."""
    id: int
    title: str
    artist: str
    album: Optional[str] = None
    link: Optional[str] = None
    image: Optional[str] = None
    mood_annotation: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Eye of the Tiger",
                "artist": "Survivor",
                "album": "Rocky III Soundtrack",
                "link": "https://example.com/song-link",
                "image": "https://example.com/album-cover.jpg",
                "mood_annotation": "Energetic, Motivational"
            }
        }