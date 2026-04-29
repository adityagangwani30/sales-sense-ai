from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.services.dataset_service import load_dataset, validate_dataset


router = APIRouter(tags=["dataset"])


class DatasetRequest(BaseModel):
    dataset: str = Field(..., examples=["dataset_1"])


@router.post("/load-dataset")
def load_dataset_route(payload: DatasetRequest) -> dict:
    dataset_name = validate_dataset(payload.dataset)
    return load_dataset(dataset_name)
