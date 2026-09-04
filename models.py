from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field

class Source(BaseModel):
    name: str
    url: str

class Startup(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schemaVersion: str = "1.0"
    recordType: str = "STARTUP"
    source: Source
    content: dict[str, Any]
    collectedAt: datetime

class Product(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schemaVersion: str = "1.0"
    recordType: str = "PRODUCT"
    source: Source
    content: dict[str, Any]
    collectedAt: datetime

class ResearchPaper(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schemaVersion: str = "1.0"
    recordType: str = "RESEARCH_PAPER"
    source: Source
    content: dict[str, Any]
    collectedAt: datetime

class Job(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schemaVersion: str = "1.0"
    recordType: str = "JOB"
    source: Source
    content: dict[str, Any]
    collectedAt: datetime

class News(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schemaVersion: str = "1.0"
    recordType: str = "NEWS"
    source: Source
    content: dict[str, Any]
    collectedAt: datetime

class EntityMapping(BaseModel):
    raw_name: str
    canonical_name: str
    entity_type: str
    method: str
    score: float
