# app/seed.py 

from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import pandas as pd
import os

import models as models
from database import SessionLocal

EXCEL_FILE_PATH = "/home/saswat/Projects/Playlistable-clone/backend/agentic_testing/dataset.xlsx"

def extract_mood_context_lists(dataset_path):
    """
    Extract unique moods and contexts from an Excel file.
    
    Args:
        dataset_path (str): Path to the Excel file
    
    Returns:
        tuple: A tuple containing two lists (mood_list, context_list)
    """
    # Read the Excel file
    df = pd.read_excel(dataset_path)
    
    mood_list = []
    context_list = []
    
    # Iterate through each row
    for mood, context in zip(df['mood'], df['context']):
        # Split by comma and strip whitespace
        mood_list.extend([m.strip().lower() for m in str(mood).split(',') if m.strip()])
        context_list.extend([c.strip() .lower()for c in str(context).split(',') if c.strip()])
    
    # Return unique values only
    return list(set(mood_list)), list(set(context_list))

DEFAULT_MOOD_NAMES, DEFAULT_CONTEXT_NAMES = extract_mood_context_lists(EXCEL_FILE_PATH)

def seed_data_from_excel_single_sheet():
    db: Session = SessionLocal()

    if not os.path.exists(EXCEL_FILE_PATH):
        print(f"❌ Error: Excel file not found at {EXCEL_FILE_PATH}")
        return

    try:
        # Delete existing data (in reverse dependency order)
        print("Clearing existing data...")
        db.query(models.Annotation).delete()
        db.query(models.UserSongInteraction).delete()
        db.execute(models.song_mood_table.delete())
        db.execute(models.song_context_table.delete())
        db.query(models.Song).delete()
        db.query(models.Mood).delete()
        db.query(models.Context).delete()
        db.query(models.User).delete()
        db.commit()
        print("✅ Existing data cleared.")

        # Add default moods and contexts
        print("Seeding moods and contexts...")
        mood_lookup = {}
        context_lookup = {}

        for name in DEFAULT_MOOD_NAMES:
            mood = models.Mood(name=name)
            db.add(mood)
            mood_lookup[name.lower()] = mood

        for name in DEFAULT_CONTEXT_NAMES:
            context = models.Context(name=name)
            db.add(context)
            context_lookup[name.lower()] = context

        db.commit()

        for mood in db.query(models.Mood).all():
            mood_lookup[mood.name.lower()] = mood
        for context in db.query(models.Context).all():
            context_lookup[context.name.lower()] = context

        print(f"✅ Seeded {len(mood_lookup)} moods and {len(context_lookup)} contexts.")

        # Add default user
        print("Adding default user...")
        user = db.query(models.User).filter_by(username="testuser").first()
        if not user:
            user = models.User(
                username="testuser",
                email="test@example.com",
                password_hash="not_really_hashed"  # Replace with actual hashed password in production
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print("✅ Default user 'testuser' added.")
        else:
            print("ℹ️ Default user already exists.")

        # Load Excel
        print(f"Loading songs from: {EXCEL_FILE_PATH}")
        df = pd.read_excel(EXCEL_FILE_PATH, sheet_name=0)

        print(f"Found columns: {df.columns.tolist()}")

        for index, row in df.iterrows():
            song_name = str(row.get('song name', '')).strip()
            if not song_name:
                print(f"⚠️ Skipping row {index} due to empty song name.")
                continue

            song = models.Song(
                song_name=song_name,
                link=str(row.get('link', '')).strip() or None,
                image=str(row.get('Image', '')).strip() or None,
                artist=str(row.get('artist', '')).strip() if 'artist' in df.columns else None,
                album=str(row.get('album', '')).strip() if 'album' in df.columns else None,
                release_date=row.get('release_date').date() if isinstance(row.get('release_date'), datetime) else None,
                duration_ms=int(row.get('duration_ms', 0)) if 'duration_ms' in df.columns else 0,
                explicit=str(row.get('explicit', '')).strip().lower() if 'explicit' in df.columns else None,
                danceability=float(row.get('danceability', 0.0)) if 'danceability' in df.columns else 0.0,
                energy=float(row.get('energy', 0.0)) if 'energy' in df.columns else 0.0,
                key=int(row.get('key', -1)) if 'key' in df.columns else -1,
                loudness=float(row.get('loudness', 0.0)) if 'loudness' in df.columns else 0.0,
                mode=int(row.get('mode', -1)) if 'mode' in df.columns else -1,
                speechiness=float(row.get('speechiness', 0.0)) if 'speechiness' in df.columns else 0.0,
                acousticness=float(row.get('acousticness', 0.0)) if 'acousticness' in df.columns else 0.0,
                instrumentalness=float(row.get('instrumentalness', 0.0)) if 'instrumentalness' in df.columns else 0.0,
                liveness=float(row.get('liveness', 0.0)) if 'liveness' in df.columns else 0.0,
                valence=float(row.get('valence', 0.0)) if 'valence' in df.columns else 0.0,
                tempo=float(row.get('tempo', 0.0)) if 'tempo' in df.columns else 0.0,
                time_signature=int(row.get('time_signature', -1)) if 'time_signature' in df.columns else -1,
                popularity=int(row.get('popularity', 0)) if 'popularity' in df.columns else 0,
                mood_annotation=str(row.get('mood_annotation', '')).strip() if 'mood_annotation' in df.columns else None
            )

            # Link moods
            if 'mood' in df.columns:
                for mood_name in str(row.get('mood', '')).strip().split(','):
                    mood_name = mood_name.strip().lower()
                    if mood_name and mood_name in mood_lookup:
                        song.moods.append(mood_lookup[mood_name])
                    elif mood_name:
                        print(f"⚠️ Mood '{mood_name}' not found for song '{song_name}'.")

            # Link contexts
            if 'context' in df.columns:
                for context_name in str(row.get('context', '')).strip().split(','):
                    context_name = context_name.strip().lower()
                    if context_name and context_name in context_lookup:
                        song.contexts.append(context_lookup[context_name])
                    elif context_name:
                        print(f"⚠️ Context '{context_name}' not found for song '{song_name}'.")

            db.add(song)

        db.commit()
        print("✅ Songs seeded successfully.")

    except Exception as e:
        db.rollback()
        print(f"❌ Error occurred: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_data_from_excel_single_sheet()
