import datetime
from pydantic import BaseModel


class Version(BaseModel):
    version: str
    release_date: datetime
