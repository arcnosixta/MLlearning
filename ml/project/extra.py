"""Run with python -m uvicorn extra:app; use the form at /docs."""

from functools import lru_cache

from fastapi import FastAPI
from pydantic import BaseModel, Field

from lab import FEATURES, train

app = FastAPI(title='ML 3305 synthetic churn demo')


class Customer(BaseModel):
    days_active: int = Field(ge=0, le=30)
    tickets: int = Field(ge=0, le=20)
    monthly_fee: float = Field(ge=0, le=200, allow_inf_nan=False)


@lru_cache(maxsize=1)
def model():
    return train()


@app.post('/predict')
def predict(customer: Customer):
    row = [getattr(customer, feature) for feature in FEATURES]
    probability = float(model().predict_proba([row])[0, 1])
    return {'probability': probability, 'prediction': int(probability >= .5), 'version': 'demo-1'}
