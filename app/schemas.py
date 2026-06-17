from pydantic import BaseModel


class AgeCheckResponse(BaseModel):
    module: str
    is_above_threshold: bool
    decision: str
    confidence: float
    latency_ms: float