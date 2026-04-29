from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.routes.analytics import router as analytics_router
from backend.routes.dataset import router as dataset_router
from backend.services.dataset_service import InvalidDatasetError


app = FastAPI(title="SalesSense AI Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(InvalidDatasetError)
def invalid_dataset_handler(_: Request, __: InvalidDatasetError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"error": "Invalid dataset"})


@app.exception_handler(RequestValidationError)
def validation_handler(_: Request, __: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"error": "Invalid request"})


@app.get("/")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "SalesSense AI Backend"}


app.include_router(dataset_router)
app.include_router(analytics_router)
