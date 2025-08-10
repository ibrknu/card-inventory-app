from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .db import Base, engine
from .routes import items as items_routes
from .routes import scan as scan_routes


PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = PROJECT_ROOT / "app" / "static"
INDEX_HTML = STATIC_DIR / "index.html"

app = FastAPI(title="Card Inventory")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items_routes.router)
app.include_router(scan_routes.router)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return FileResponse(INDEX_HTML)


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")