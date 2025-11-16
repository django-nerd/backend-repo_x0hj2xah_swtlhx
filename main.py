import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents

app = FastAPI(title="BlazinVibe API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helpers
class ObjectIdStr(str):
    @classmethod
    def validate(cls, v):
        try:
            ObjectId(v)
            return v
        except Exception:
            raise ValueError("Invalid ObjectId")

# Public endpoints
@app.get("/")
def root():
    return {"name": "BlazinVibe", "status": "ok"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:20]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# Content endpoints
@app.get("/api/artists")
async def list_artists(role: Optional[str] = None, headliner: Optional[bool] = None):
    if db is None:
        return []
    filt = {}
    if role:
        filt["role"] = role
    if headliner is not None:
        filt["headliner"] = headliner
    docs = get_documents("artist", filt)
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs

@app.get("/api/experiences")
async def list_experiences():
    if db is None:
        return []
    docs = get_documents("experiencezone")
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs

@app.get("/api/tickets")
async def list_tickets():
    if db is None:
        return []
    docs = get_documents("tickettier")
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs

@app.get("/api/faqs")
async def list_faqs():
    if db is None:
        return []
    docs = get_documents("faq")
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs

@app.get("/api/testimonials")
async def list_testimonials():
    if db is None:
        return []
    docs = get_documents("testimonial")
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs

@app.get("/api/media")
async def list_media():
    if db is None:
        return []
    docs = get_documents("mediaitem")
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs

# Forms
class ApplicationIn(BaseModel):
    name: str
    discipline: str
    portfolio: Optional[str] = None
    bio: Optional[str] = None
    instagram: Optional[str] = None
    tiktok: Optional[str] = None
    twitter: Optional[str] = None
    email: str

@app.post("/api/apply")
async def submit_application(payload: ApplicationIn):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    data = payload.model_dump()
    data["status"] = "submitted"
    inserted_id = create_document("application", data)
    return {"ok": True, "id": inserted_id, "message": "Thanks for applying — we’ll get back to you soon."}

class NewsletterIn(BaseModel):
    email: str
    name: Optional[str] = None

@app.post("/api/newsletter")
async def subscribe_newsletter(payload: NewsletterIn):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    inserted_id = create_document("newsletter", payload.model_dump())
    return {"ok": True, "id": inserted_id, "message": "Thanks for joining the vibe!"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
