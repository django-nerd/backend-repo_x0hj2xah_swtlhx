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
@app.get("/api/eventinfo")
async def get_event_info():
    """Return the latest event info document if available"""
    if db is None:
        return {}
    doc = db["eventinfo"].find_one(sort=[("_id", -1)])
    if not doc:
        return {}
    doc["id"] = str(doc.pop("_id"))
    return doc

class EventInfoIn(BaseModel):
    name: str
    tagline: Optional[str] = None
    date_iso: str
    venue: str
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    ticket_url: Optional[str] = None
    socials: Optional[dict] = None

@app.post("/api/eventinfo")
async def upsert_event_info(payload: EventInfoIn):
    """Create or update the singleton event info document to activate countdown and ticket links."""
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    data = payload.model_dump()
    db["eventinfo"].replace_one({}, data, upsert=True)
    return {"ok": True}

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

# Utilities: seed demo content for quick start
@app.post("/api/seed")
async def seed_demo_content():
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")

    created = {"eventinfo": False, "artist": 0, "experiencezone": 0, "tickettier": 0, "faq": 0, "mediaitem": 0}

    # Event info (set real-looking sample details)
    if db["eventinfo"].count_documents({}) == 0:
        create_document("eventinfo", {
            "name": "BlazinVibe",
            "tagline": "Feel the Beat. Live the Vibe.",
            # Set to a near-future real date to activate countdown
            "date_iso": "2025-08-23T18:00:00Z",
            "venue": "Neon Docks",
            "address": "Pier 7, Riverfront",
            "city": "Riverfront City",
            "country": "USA",
            # External ticketing link (replace with your live link anytime)
            "ticket_url": "https://tickets.blazinvibe.io",
            "socials": {"instagram": "https://instagram.com/blazinvibe", "twitter": "https://twitter.com/blazinvibe"}
        })
        created["eventinfo"] = True

    # Artists
    if db["artist"].count_documents({}) == 0:
        artists = [
            {"name": "NovaPulse", "role": "DJ", "bio": "Bass-heavy cosmic journeys.", "headliner": True},
            {"name": "Synesthesia", "role": "Live Band", "bio": "Synthwave meets indie electronica."},
            {"name": "VJ Lumen", "role": "Visual Artist", "bio": "Projection mapping wizard."},
            {"name": "Flux Dancers", "role": "Performer", "bio": "Immersive choreographies and LED suits."},
            {"name": "Echo Drift", "role": "DJ", "bio": "Hypnotic house and rolling techno."},
            {"name": "Orbitals", "role": "Live Band", "bio": "Modular synths and drum machines live."},
            {"name": "PrismArt", "role": "Visual Artist", "bio": "Holographic sculptures and lasers."},
            {"name": "Aerial Flux", "role": "Performer", "bio": "Aerial silk performers in neon."},
            {"name": "Deep Current", "role": "DJ", "bio": "Submerged basslines and liquid DnB."}
        ]
        for a in artists:
            create_document("artist", a)
            created["artist"] += 1

    # Experiences
    if db["experiencezone"].count_documents({}) == 0:
        zones = [
            {"title": "Main Stage", "kind": "Live Set", "description": "Headliner sets with full-spectrum lasers."},
            {"title": "Neon Garden", "kind": "Installation", "description": "Interactive light trails and art."},
            {"title": "Chill Harbor", "kind": "Chill", "description": "Low-tempo grooves and ambient visuals."},
            {"title": "Creator Playground", "kind": "Workshop", "description": "DIY visuals, beat labs, and collab corners."},
            {"title": "VIP Skydeck", "kind": "Lounge", "description": "Panoramic views, exclusive bar, concierge."}
        ]
        for z in zones:
            create_document("experiencezone", z)
            created["experiencezone"] += 1

    # Tickets
    if db["tickettier"].count_documents({}) == 0:
        tiers = [
            {"name": "Early Bird", "price": 49, "currency": "USD", "includes": ["General entry", "Installations"]},
            {"name": "General Admission", "price": 79, "currency": "USD", "includes": ["All stages", "Installations", "Creator Playground"]},
            {"name": "VIP", "price": 149, "currency": "USD", "includes": ["VIP lounge", "Priority entry", "Exclusive bar"]},
            {"name": "Group 4-Pack", "price": 280, "currency": "USD", "includes": ["4x GA passes", "Merch discount"]}
        ]
        for t in tiers:
            create_document("tickettier", t)
            created["tickettier"] += 1

    # FAQs
    if db["faq"].count_documents({}) == 0:
        faqs = [
            {"question": "What time do doors open?", "answer": "Doors open at 6:00 PM."},
            {"question": "Is there re-entry?", "answer": "Yes, with wristband and valid ID."},
            {"question": "Is the event all-ages?", "answer": "18+ with valid ID."},
            {"question": "Will there be food?", "answer": "Yes, a variety of street food vendors and vegan options."}
        ]
        for f in faqs:
            create_document("faq", f)
            created["faq"] += 1

    # Media (images + video) — replace these URLs with your own later
    if db["mediaitem"].count_documents({}) == 0:
        media = [
            {"kind": "photo", "url": "https://images.unsplash.com/photo-1518972559570-7cc1309f3229", "alt": "Crowd bathed in neon lights"},
            {"kind": "photo", "url": "https://images.unsplash.com/photo-1540575467063-178a50c2df87", "alt": "DJ on stage with lasers"},
            {"kind": "photo", "url": "https://images.unsplash.com/photo-1487180144351-b8472da7d491", "alt": "Colorful light trails in dark hall"},
            {"kind": "photo", "url": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30", "alt": "Hands up in the air at concert"},
            {"kind": "photo", "url": "https://images.unsplash.com/photo-1492684223066-42c7cf8a1f7a", "alt": "Laser beams over crowd"},
            {"kind": "video", "url": "https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4", "alt": "Aftermovie clip sample"}
        ]
        for m in media:
            create_document("mediaitem", m)
            created["mediaitem"] += 1

    return {"ok": True, "created": created}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
