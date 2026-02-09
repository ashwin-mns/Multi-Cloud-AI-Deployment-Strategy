from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import time
import random
import os

app = FastAPI(title="Multi-Cloud AI Deployment Service")

class PredictionRequest(BaseModel):
    text: str

class PredictionResponse(BaseModel):
    sentiment: str
    confidence: float
    processing_time_ms: float
    provider: str = "Unknown"

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    start_time = time.perf_counter()
    
    # Simulate some ML processing logic
    # In a real scenario, this would load a model and run inference
    text = request.text.lower()
    
    # Simple rule-based sentiment for demonstration
    positive_words = ["good", "great", "excellent", "happy", "love", "amazing"]
    negative_words = ["bad", "sad", "awful", "terrible", "hate", "worst"]
    
    score = 0
    for word in positive_words:
        if word in text:
            score += 1
    for word in negative_words:
        if word in text:
            score -= 1
            
    if score > 0:
        sentiment = "Positive"
        confidence = 0.7 + (random.random() * 0.25)
    elif score < 0:
        sentiment = "Negative"
        confidence = 0.7 + (random.random() * 0.25)
    else:
        sentiment = "Neutral"
        confidence = 0.5 + (random.random() * 0.2)
        
    # Simulate variable processing time to mimic different cloud infrastructures
    time.sleep(0.05 + (random.random() * 0.1)) 
    
    end_time = time.perf_counter()
    duration_ms = (end_time - start_time) * 1000
    
    provider = os.getenv("CLOUD_PROVIDER", "Unknown")
    
    print(f"[{provider}] Prediction for text: '{request.text[:30]}...' processed in {duration_ms:.2f}ms")

    return PredictionResponse(
        sentiment=sentiment,
        confidence=round(confidence, 4),
        processing_time_ms=round(duration_ms, 2),
        provider=provider
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
