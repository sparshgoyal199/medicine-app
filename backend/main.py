from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routers import auth, checkin, photos, symptoms, medicine, timeline, notifications
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Regrowth OS API",
    description="Backend API for Regrowth OS - A hair treatment tracking app for Man Matters products",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routers
app.include_router(auth.router)
app.include_router(checkin.router)
app.include_router(photos.router)
app.include_router(symptoms.router)
app.include_router(medicine.router)
app.include_router(timeline.router)
app.include_router(notifications.router)


# ─── API health endpoints ────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Redirect root to the frontend app"""
    return FileResponse(Path(__file__).parent.parent / "frontend" / "index.html")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Regrowth OS API"}


# ─── Serve frontend static files ─────────────────────────────────────────────
# Mount at the very END so API routes take priority

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

if FRONTEND_DIR.exists():
    # Serve /css, /js, /assets, /pages as static directories
    app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
    app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")
    app.mount("/pages", StaticFiles(directory=FRONTEND_DIR / "pages", html=True), name="pages")

    # Serve index.html at root
    @app.get("/index.html")
    async def serve_index():
        return FileResponse(FRONTEND_DIR / "index.html")

else:
    print(f"WARNING: Frontend directory not found at {FRONTEND_DIR}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
