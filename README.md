# Playlistable-clone

This project is a music annotation and recommendation system. It allows users to annotate songs with tags and contexts, and then get recommendations based on these annotations.

## Technologies Used

### Backend

- Python
- FastAPI
- SQLAlchemy
- Autogen
- Groq API for recommendations

### Frontend

- React
- Vite
- Tailwind CSS
- React Query

## Project Structure

The project is divided into two main parts: a `backend` and a `frontend`.

- **`backend`**: A FastAPI application that provides a RESTful API for managing songs, tags, contexts, and recommendations. It uses SQLAlchemy for the database and the Groq API with Autogen for generating recommendations.

- **`frontend`**: A React application built with Vite that provides the user interface for annotating songs and viewing recommendations.

## Setup and Installation

### Backend

1.  **Navigate to the `backend` directory:**
    ```bash
    cd backend
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    ```

3.  **Activate the virtual environment:**
    -   On macOS and Linux:
        ```bash
        source .venv/bin/activate
        ```
    -   On Windows:
        ```bash
        .venv\Scripts\activate
        ```

4.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Create a `.env` file** in the `backend` directory and add your Groq API key:
    ```
    GROQ_API_KEY=your_groq_api_key
    ```

### Frontend

1.  **Navigate to the `frontend` directory:**
    ```bash
    cd frontend
    ```

2.  **Install the required dependencies:**
    ```bash
    npm install
    ```

## Running the Application

### Backend

1.  **Navigate to the `backend` directory:**
    ```bash
    cd backend
    ```

2.  **Start the FastAPI server:**
    ```bash
    uvicorn app.main:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000`.

### Frontend

1.  **Navigate to the `frontend` directory:**
    ```bash
    cd frontend
    ```

2.  **Start the development server:**
    ```bash
    npm run dev
    ```
    The application will be available at `http://localhost:5173`.
