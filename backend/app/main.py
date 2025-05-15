from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from routes import songs,tags, contexts,recommendations
from database import engine # Import the engine
from models import Base # Import the Base metadata

app = FastAPI(title="Music Annotation API")

# Add startup event handler to create database tables
@app.on_event("startup")
def startup_event():
    """
    Create database tables when the application starts up.
    """
    print("Creating database tables...")
    # This will create tables based on the models if they don't exist
    Base.metadata.create_all(bind=engine)
    print("Database tables created (if they didn't exist).")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set to frontend URL in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(songs.router)
app.include_router(tags.router)
app.include_router(contexts.router)
app.include_router(recommendations.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Music Annotation API!"}
