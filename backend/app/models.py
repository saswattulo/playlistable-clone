# app/models.py
from sqlalchemy import (
    Column, String, Integer, Float, Date, Text, ForeignKey, Table, Boolean, DateTime
)

from sqlalchemy.orm import relationship
import datetime
from database import Base

# Association Table: Many-to-Many (Song <-> Mood)
song_mood_table = Table(
    "song_mood_association",
    Base.metadata,
    Column("song_id", Integer, ForeignKey("songs.id"), primary_key=True),
    Column("mood_id", Integer, ForeignKey("moods.id"), primary_key=True)
)

# Association Table: Many-to-Many (Song <-> Context)
song_context_table = Table(
    "song_context_association",
    Base.metadata,
    Column("song_id", Integer, ForeignKey("songs.id"), primary_key=True),
    Column("context_id", Integer, ForeignKey("contexts.id"), primary_key=True)
)

class User(Base):
    """
    Represents a user in the application.
    Stores user authentication and profile information.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="Unique identifier for the user")
    username = Column(String, unique=True, nullable=False, comment="Unique username for the user")
    email = Column(String, unique=True, nullable=False, comment="Unique email address for the user")
    password_hash = Column(String, nullable=False, comment="Hashed password for security")
    created_at = Column(DateTime, default=datetime.datetime.utcnow, comment="Timestamp of user creation")

    # Relationships remain the same, referencing the model names
    interactions = relationship("UserSongInteraction", back_populates="user")
    annotations = relationship("Annotation", back_populates="user")

    def __repr__(self):
        return f"<User(username='{self.username}')>"

class Song(Base):
    """
    Represents a song with its metadata and audio features.
    """
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="Unique identifier for the song")
    song_name = Column(String, nullable=False, comment="Title of the song")
    artist = Column(String, nullable=True, comment="Artist(s) of the song")
    album = Column(String, comment="Album the song belongs to")
    release_date = Column(Date, comment="Release date of the song")
    duration_ms = Column(Integer, comment="Duration of the song in milliseconds")
    explicit = Column(String, comment="Explicit content flag (e.g., 'yes', 'no', 'restricted')")

    danceability = Column(Float, comment="How suitable a track is for dancing (0.0 to 1.0)")
    energy = Column(Float, comment="Perceptual measure of intensity and activity (0.0 to 1.0)")
    key = Column(Integer, comment="Key the track is in (0-11, representing pitches)")
    loudness = Column(Float, comment="Overall loudness of a track in decibels (dB)")
    mode = Column(Integer, comment="Indicates the modality (major or minor) of a track (0 for minor, 1 for major)")
    speechiness = Column(Float, comment="Presence of spoken words in the track (0.0 to 1.0)")
    acousticness = Column(Float, comment="Confidence measure of whether the track is acoustic (0.0 to 1.0)")
    instrumentalness = Column(Float, comment="Predicts whether a track contains no vocals (0.0 to 1.0)")
    liveness = Column(Float, comment="Detects the presence of an audience in the recording (0.0 to 1.0)")
    valence = Column(Float, comment="Musical positiveness conveyed by the track (0.0 to 1.0)")
    tempo = Column(Float, comment="Estimated overall tempo of a track in beats per minute (BPM)")
    time_signature = Column(Integer, comment="Estimated overall time signature of a track")
    popularity = Column(Integer, comment="Popularity of the track (e.g., 0-100)")

    # URLs remain the same
    link = Column(String, comment="URL to the song file or streaming link")
    image = Column(String, comment="URL to the album art image")

    mood_annotation = Column(Text, comment="A general text annotation about the song's mood")

    # Updated relationships to reference moods instead of tags
    moods = relationship("Mood", secondary=song_mood_table, back_populates="songs")
    # New relationship for contexts
    contexts = relationship("Context", secondary=song_context_table, back_populates="songs")
    interactions = relationship("UserSongInteraction", back_populates="song")
    annotations = relationship("Annotation", back_populates="song")

    def __repr__(self):
        return f"<Song(title='{self.song_name}', artist='{self.artist}')>"

class Mood(Base):
    """
    Represents a mood that can be applied to songs for categorization or filtering.
    """
    __tablename__ = "moods"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="Unique identifier for the mood")
    name = Column(String, unique=True, nullable=False, comment="Name of the mood (e.g., 'happy', 'sad', 'energetic')")

    # Updated relationship to reference songs
    songs = relationship("Song", secondary=song_mood_table, back_populates="moods")

    def __repr__(self):
        return f"<Mood(name='{self.name}')>"

class Context(Base):
    """
    Represents a context that can be applied to songs for categorization or filtering.
    (e.g., 'workout', 'studying', 'party', 'relaxation')
    """
    __tablename__ = "contexts"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="Unique identifier for the context")
    name = Column(String, unique=True, nullable=False, comment="Name of the context")
    description = Column(Text, comment="Optional description of the context")

    # Relationship with songs (many-to-many)
    songs = relationship("Song", secondary=song_context_table, back_populates="contexts")

    def __repr__(self):
        return f"<Context(name='{self.name}')>"

class UserSongInteraction(Base):
    """
    Records interactions between a user and a specific song,
    such as likes and play counts.
    """
    __tablename__ = "user_song_interactions"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="Unique identifier for the interaction record")
    user_id = Column(Integer, ForeignKey("users.id"), comment="Foreign key to the interacting user")
    song_id = Column(Integer, ForeignKey("songs.id"), comment="Foreign key to the interacted song")
    liked = Column(Boolean, default=False, comment="Boolean indicating if the user liked the song")
    play_count = Column(Integer, default=0, comment="Number of times the user has played the song")
    last_played = Column(DateTime, default=datetime.datetime.utcnow, comment="Timestamp of the last time the user played the song")

    # Relationships remain the same, referencing the model names
    user = relationship("User", back_populates="interactions")
    song = relationship("Song", back_populates="interactions")

    def __repr__(self):
        return f"<Interaction(user={self.user_id}, song={self.song_id}, liked={self.liked})>"

class Annotation(Base):
    """
    Represents a user-generated text annotation on a specific song.
    """
    __tablename__ = "annotations"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="Unique identifier for the annotation")
    user_id = Column(Integer, ForeignKey("users.id"), comment="Foreign key to the user who made the annotation")
    song_id = Column(Integer, ForeignKey("songs.id"), comment="Foreign key to the song being annotated")
    content = Column(Text, nullable=False, comment="The text content of the annotation")
    created_at = Column(DateTime, default=datetime.datetime.utcnow, comment="Timestamp of annotation creation")

    # Relationships remain the same, referencing the model names
    user = relationship("User", back_populates="annotations")
    song = relationship("Song", back_populates="annotations")

    def __repr__(self):
        return f"<Annotation(user={self.user_id}, song={self.song_id})>"