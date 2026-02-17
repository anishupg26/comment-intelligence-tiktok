from pydantic import BaseModel
from typing import Optional, Any


class UploadResponse(BaseModel):
    dataset_id: str


class ProcessResponse(BaseModel):
    job_id: str


class JobStatus(BaseModel):
    status: str
    progress: Optional[float] = None


class ResultsResponse(BaseModel):
    data: Any
