from typing import Optional
from pydantic import BaseModel


class Location(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
