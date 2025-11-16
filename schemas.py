"""
Database Schemas for BlazinVibe

Each Pydantic model represents a MongoDB collection.
Collection name is the lowercase of the class name.
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Literal
from datetime import datetime

# Core event info
class Eventinfo(BaseModel):
    name: str = Field(..., description="Event name")
    tagline: Optional[str] = Field(None, description="Short tagline")
    date_iso: str = Field(..., description="Event ISO date string, e.g., 2025-08-23T18:00:00Z")
    venue: str = Field(..., description="Venue name")
    address: str = Field(..., description="Venue address")
    city: str = Field(..., description="City")
    country: str = Field(..., description="Country")
    ticket_url: Optional[HttpUrl] = Field(None, description="External ticketing URL")
    socials: Optional[dict] = Field(default_factory=dict, description="Map of social links")

# Artists / creators
class Artist(BaseModel):
    name: str
    role: Literal['DJ', 'Live Band', 'Visual Artist', 'Performer'] = 'DJ'
    bio: Optional[str] = None
    image: Optional[str] = Field(None, description="Image URL")
    headliner: bool = False
    links: Optional[dict] = Field(default_factory=dict)

# Immersive zones / experiences
class Experiencezone(BaseModel):
    title: str
    kind: Literal['Live Set', 'Installation', 'Chill', 'VIP'] = 'Live Set'
    description: Optional[str] = None
    image: Optional[str] = None

# Ticket tiers
class Tickettier(BaseModel):
    name: Literal['Early Bird', 'General Admission', 'VIP', 'Backstage'] = 'General Admission'
    price: float
    currency: str = 'USD'
    includes: List[str] = Field(default_factory=list)
    available: bool = True

# FAQ entries
class Faq(BaseModel):
    question: str
    answer: str
    category: Optional[str] = None

# Testimonials / social proof
class Testimonial(BaseModel):
    author: str
    role: Optional[str] = None
    quote: str
    avatar: Optional[str] = None

# Media gallery items
class Mediaitem(BaseModel):
    kind: Literal['photo', 'video'] = 'photo'
    url: str
    alt: Optional[str] = None
    thumb: Optional[str] = None

# Creator applications
class Application(BaseModel):
    name: str
    discipline: Literal['DJ', 'Live Band', 'Visual Artist', 'Performer', 'Other'] = 'Other'
    portfolio: Optional[str] = None
    bio: Optional[str] = None
    instagram: Optional[str] = None
    tiktok: Optional[str] = None
    twitter: Optional[str] = None
    email: str
    status: Literal['submitted', 'reviewed', 'accepted', 'rejected'] = 'submitted'

# Newsletter signups
class Newsletter(BaseModel):
    email: str
    name: Optional[str] = None
    source: Optional[str] = 'website'

"""
Note: The Flames admin uses these schemas for validation and collection setup.
Collections created:
- eventinfo
- artist
- experiencezone
- tickettier
- faq
- testimonial
- mediaitem
- application
- newsletter
"""
