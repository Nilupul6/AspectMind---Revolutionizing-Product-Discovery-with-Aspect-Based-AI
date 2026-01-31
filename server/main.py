from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys
import traceback

# FORCE OFFLINE MODE
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'

# Add current dir to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from recommender import ProductRecommender

app = FastAPI(title="Product Recommender API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
recommender = None
startup_error = None

@app.on_event("startup")
def startup_event():
    global recommender, startup_error
    print("🚀 Starting Server & Loading Models...")
    try:
        recommender = ProductRecommender()
        print("✅ Model loaded successfully!")
    except Exception as e:
        startup_error = traceback.format_exc()
        print(f"❌ Error loading recommender:\n{startup_error}")

@app.get("/")
def read_root():
    if startup_error:
        return {"status": "error", "message": "Server failed to start correctly", "detail": startup_error}
    return {"status": "active", "message": "Product Recommender API is running"}

@app.get("/search")
def search(
    q: str,
    category: str = None,
    min_sentiment: float = None,
    sort_by: str = "relevance"
):
    if startup_error:
         raise HTTPException(status_code=500, detail=f"Server startup failed: {startup_error}")
    
    if not recommender:
        raise HTTPException(status_code=503, detail="Model is still loading...")
    
    try:
        results = recommender.recommend(
            q, 
            category_filter=category,
            min_sentiment_score=min_sentiment,
            sort_by=sort_by
        )
        return results
    except Exception as e:
        print(f"Search Error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

class FeedbackRequest(BaseModel):
    product_id: str
    feedback: str

class AnalysisRequest(BaseModel):
    text: str

class CompareRequest(BaseModel):
    product_ids: list[str]

@app.post("/feedback")
def submit_feedback(data: FeedbackRequest):
    if not recommender:
        raise HTTPException(status_code=503, detail="Model service unavailable")
    
    result = recommender.add_feedback(data.product_id, data.feedback)
    return result

@app.post("/analyze")
def analyze_text(data: AnalysisRequest):
    if not recommender:
        raise HTTPException(status_code=503, detail="Model service unavailable")
    
    return recommender.analyze_text_only(data.text)

@app.get("/analytics")
def get_analytics():
    """Get analytics data for dashboard"""
    if startup_error:
        raise HTTPException(status_code=500, detail=f"Server startup failed: {startup_error}")
    
    if not recommender:
        raise HTTPException(status_code=503, detail="Model is still loading...")
    
    try:
        analytics = recommender.get_analytics()
        return analytics
    except Exception as e:
        print(f"Analytics Error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compare")
def compare_products(data: CompareRequest):
    """Compare multiple products side-by-side"""
    if not recommender:
        raise HTTPException(status_code=503, detail="Model service unavailable")
    
    try:
        comparison = recommender.compare_products(data.product_ids)
        return comparison
    except Exception as e:
        print(f"Comparison Error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
