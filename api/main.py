from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
from google.cloud import aiplatform
import snowflake.connector
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Recommendation Engine API",
    description="API for serving personalized recommendations",
    version="1.0.0"
)

# Initialize Vertex AI
aiplatform.init(
    project=os.getenv('GCP_PROJECT_ID'),
    location=os.getenv('GCP_REGION')
)

# Initialize Snowflake connection
def get_snowflake_connection():
    return snowflake.connector.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        database=os.getenv('SNOWFLAKE_DATABASE'),
        schema=os.getenv('SNOWFLAKE_SCHEMA')
    )

# Models
class RecommendationRequest(BaseModel):
    user_id: str
    limit: Optional[int] = 10

class RecommendationResponse(BaseModel):
    user_id: str
    recommendations: List[dict]
    latency_ms: float

# Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """Get recommendations for a user."""
    start_time = time.time()
    
    try:
        # Get Vertex AI endpoint
        endpoint = aiplatform.Endpoint(
            endpoint_name=os.getenv('VERTEX_AI_ENDPOINT')
        )
        
        # Get predictions from Vertex AI
        predictions = endpoint.predict(
            instances=[{"user_id": request.user_id}]
        )
        
        # Get additional metadata from Snowflake
        with get_snowflake_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    r.ITEM_ID,
                    r.RECOMMENDATION_SCORE,
                    i.UNIQUE_USERS,
                    i.TOTAL_INTERACTIONS
                FROM RECOMMENDATIONS_V r
                JOIN ITEM_POPULARITY_MV i
                    ON r.ITEM_ID = i.ITEM_ID
                WHERE r.USER_ID = %s
                LIMIT %s
            """, (request.user_id, request.limit))
            
            results = cursor.fetchall()
        
        # Format recommendations
        recommendations = [
            {
                "item_id": row[0],
                "score": float(row[1]),
                "popularity": {
                    "unique_users": row[2],
                    "total_interactions": row[3]
                }
            }
            for row in results
        ]
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        return RecommendationResponse(
            user_id=request.user_id,
            recommendations=recommendations,
            latency_ms=latency_ms
        )
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting recommendations: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 