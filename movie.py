# movie.py
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from bson import ObjectId
from datetime import datetime
from typing import List

from model import MovieCreate, MovieUpdate, MovieResponse
from database import get_db
from auth import get_current_user

movie_router = APIRouter()


@movie_router.post(
    "", response_model=MovieResponse, status_code=status.HTTP_201_CREATED
)
async def add_movie(movie: MovieCreate, current_user: dict = Depends(get_current_user)):
    """Add a new movie"""
    print(f"Adding movie: {movie.dict()}")
    print(f"Current user: {current_user['username']} (ID: {current_user['id']})")

    db = get_db()

    movie_dict = movie.dict()
    movie_dict["user_id"] = str(current_user["_id"])
    movie_dict["created_at"] = datetime.utcnow()
    movie_dict["updated_at"] = datetime.utcnow()

    try:
        result = await db.movies.insert_one(movie_dict)
        print(f"Movie inserted with ID: {result.inserted_id}")

        created_movie = await db.movies.find_one({"_id": result.inserted_id})
        created_movie["id"] = str(created_movie["_id"])

        return created_movie
    except Exception as e:
        print(f"Error adding movie: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding movie: {str(e)}",
        )


@movie_router.get("", response_model=List[MovieResponse])
async def get_movies(current_user: dict = Depends(get_current_user)):
    """Get all movies for current user"""
    print(f"Getting movies for user: {current_user.get('username', 'Unknown')}")
    print(f"Current user id: {current_user.get('id', 'Unknown')}")
    print(f"Current user _id: {current_user.get('_id', 'Unknown')}")

    db = get_db()

    try:
        # Ensure we're using strings for comparison
        user_id_str = str(current_user.get("_id", ""))
        print(f"Looking for movies with user_id string: {user_id_str}")

        movies = []
        cursor = db.movies.find({"user_id": user_id_str})

        async for movie in cursor:
            # Convert _id to string for response
            movie["id"] = str(movie["_id"])
            movies.append(movie)

        print(f"Found {len(movies)} movies")
        return movies
    except Exception as e:
        print(f"Error getting movies: {str(e)}")
        # Return empty list instead of error for debugging
        return []


@movie_router.get("/{id}", response_model=MovieResponse)
async def get_movie_by_id(id: str, current_user: dict = Depends(get_current_user)):
    """Get a movie by ID"""
    db = get_db()

    try:
        movie = await db.movies.find_one(
            {"_id": ObjectId(id), "user_id": str(current_user["_id"])}
        )
    except Exception as e:
        print(f"Error finding movie by ID: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid movie ID format"
        )

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with ID {id} not found",
        )

    movie["id"] = str(movie["_id"])
    return movie


@movie_router.put("/{id}", response_model=MovieResponse)
async def update_movie(
    id: str, movie: MovieUpdate, current_user: dict = Depends(get_current_user)
):
    """Update a movie"""
    db = get_db()

    # Ensure movie exists and belongs to current user
    try:
        existing_movie = await db.movies.find_one(
            {"_id": ObjectId(id), "user_id": str(current_user["_id"])}
        )
    except Exception as e:
        print(f"Error finding movie for update: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid movie ID format"
        )

    if not existing_movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with ID {id} not found",
        )

    # Update movie
    update_data = movie.dict()
    update_data["updated_at"] = datetime.utcnow()

    await db.movies.update_one({"_id": ObjectId(id)}, {"$set": update_data})

    # Get updated movie
    updated_movie = await db.movies.find_one({"_id": ObjectId(id)})
    updated_movie["id"] = str(updated_movie["_id"])

    return updated_movie


@movie_router.delete("/{id}")
async def delete_movie(id: str, current_user: dict = Depends(get_current_user)):
    """Delete a movie"""
    db = get_db()

    # Ensure movie exists and belongs to current user
    try:
        existing_movie = await db.movies.find_one(
            {"_id": ObjectId(id), "user_id": str(current_user["_id"])}
        )
    except Exception as e:
        print(f"Error finding movie for deletion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid movie ID format"
        )

    if not existing_movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with ID {id} not found",
        )

    # Delete movie
    await db.movies.delete_one({"_id": ObjectId(id)})

    return {"message": f"Movie with ID {id} deleted successfully"}


@movie_router.put("/{id}/toggle-watched")
async def toggle_watched(id: str, current_user: dict = Depends(get_current_user)):
    """Toggle movie watched status"""
    db = get_db()

    # Ensure movie exists and belongs to current user
    try:
        existing_movie = await db.movies.find_one(
            {"_id": ObjectId(id), "user_id": str(current_user["_id"])}
        )
    except Exception as e:
        print(f"Error finding movie for toggle watched: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid movie ID format"
        )

    if not existing_movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with ID {id} not found",
        )

    # Toggle watched status
    new_status = not existing_movie["watched"]
    await db.movies.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"watched": new_status, "updated_at": datetime.utcnow()}},
    )

    return {"message": f"Movie with ID {id} watched status toggled to {new_status}"}
