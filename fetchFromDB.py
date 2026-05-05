from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

# ---------- DB setup ----------
DATABASE_URL = "postgresql://postgres:DBPassword001@localhost/puckdoku_clone"  # nahraď svojou URI

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class Word(Base):
    __tablename__ = 'hangman_words'
    id = Column(Integer, primary_key=True)
    content = Column(String)

# Base.metadata.create_all(bind=engine)  # odkomentuj ak chceš vytvoriť tabuľku

# ---------- App setup ----------
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ---------- Dependency ----------
def get_db():
    db = SessionLocal()
    try:
        return db.query(Word).all()
    finally:
        db.close()

# ---------- Route ----------
router = APIRouter()

@router.get("/hangman/penalties", response_class=HTMLResponse)
def hangman_penalties(request: Request):
    db = next(get_db())
    words = db.query(Word).all()
    
    print("Im here")
    print(words)
    if not words:
        print("No data found!")
    else:
        for w in words:
            print(w.content)
    
    return templates.TemplateResponse(
        "hangman.html",
        {"request": request, "words": words}
    )