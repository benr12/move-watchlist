# main.py
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse, RedirectResponse
from fastapi.responses import JSONResponse

from movie import movie_router
from auth_router import auth_router
from database import connect_to_mongo, close_mongo_connection

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Event handlers for database connection
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()


# Exception handler for authentication errors
@app.exception_handler(401)
async def unauthorized_exception_handler(request: Request, exc):
    return JSONResponse(
        status_code=401,
        content={"detail": "Authentication required"},
    )


# Include routers
app.include_router(auth_router, tags=["Authentication"], prefix="/auth")
app.include_router(movie_router, tags=["Movies"], prefix="/movies")

# Mount static files
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


# Root route
# Root route
@app.get("/")
async def read_index():
    # Redirect to login page by default
    return RedirectResponse(url="/frontend/login.html")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
