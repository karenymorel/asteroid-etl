from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class AsteroidSchema(BaseModel):
    id: str
    name: str
    absolute_magnitude: Optional[float] = None
    diameter_min_meters: Optional[float] = None
    diameter_max_meters: Optional[float] = None
    is_potentially_hazardous: bool = False
    is_sentry_object: bool = False


class CloseApproachSchema(BaseModel):
    asteroid_id: str
    approach_date: date
    velocity_kmh: float = Field(default=0.0, ge=0.0)
    miss_distance_km: float = Field(default=0.0, ge=0.0)
    orbiting_body: str = "Earth"