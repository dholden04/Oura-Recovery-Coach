"""
Recovery Coach API - Main Application

This is the entry point for our FastAPI backend.
FastAPI automatically generates interactive API docs at /docs
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, timedelta
from models import SleepData, ReadinessData, ActivityData, RecoveryRecommendation
from services.oura_client import get_oura_client, OuraAPIError
from services.ai_coach import get_recovery_coach, AICoachError
from dotenv import load_dotenv
import httpx
import os
from fastapi.responses import RedirectResponse
# Load environment variables from .env file
load_dotenv()


CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
OURA_REDIRECT_URI = os.getenv("OURA_REDIRECT_URI", "http://localhost:8000/oauth/callback")


# Create the FastAPI application instance
app = FastAPI(
    title="Recovery Coach API",
    description="AI-powered recovery recommendations based on health metrics",
    version="0.1.0"
)

# CORS middleware allows our frontend (running on different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#OAuth endpoints
@app.get("/oauth/start")
def start_oauth():
    CLIENT_ID = os.getenv("CLIENT_ID")
    OURA_REDIRECT_URI = os.getenv("OURA_REDIRECT_URI", "http://localhost:8000/oauth/callback")
    
    # Check if configured
    if not CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="OURA_CLIENT_ID not configured. Add it to .env file."
        )
    auth_url = (
        f"https://cloud.ouraring.com/oauth/authorize?"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={OURA_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=daily personal heartrate sleep"
    )
    return RedirectResponse(auth_url)

@app.get("/oauth/callback")
async def oauth_callback(code: str):
    # TODO: Get client_id and client_secret from environment
   
    # TODO: Make POST request to https://api.ouraring.com/oauth/token
    #       Include: grant_type, code, client_id, client_secret, redirect_uri
    async with httpx.AsyncClient() as client:
        response = await client.post(
             "https://api.ouraring.com/oauth/token",
             headers = {
                  "Content-Type": "application/x-www-form-urlencoded"
             },
             data={
                 "grant_type" : "authorization_code",
                 "code" : code,
                 "client_id" :  CLIENT_ID,
                 "client_secret": CLIENT_SECRET,
                 "redirect_uri" : OURA_REDIRECT_URI
             }
           )
        if response.status_code != 200:
            return {"error": f"Token exchange failed: {response.text}"}
        tokens = response.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]

        return {
            "message": "Success!",
            "access_token" : access_token,
            "refresh_token" : refresh_token,
        }
    
    # TODO: Parse the JSON response
    
    # TODO: Extract access_token and refresh_token
    
    # TODO: Return or display them

@app.get("/")
def read_root():
    """
    Health check endpoint - confirms API is running
    """
    return {
        "message": "Recovery Coach API is running!",
        "version": "0.1.0",
        "status": "healthy"
    }


@app.get("/api/health")
def health_check():
    """
    Detailed health check - useful for monitoring
    """
    # Check if Oura token is configured
    import os
    oura_status = "configured" if os.getenv("access_token") else "not_configured"

    return {
        "api": "healthy",
        "database": "not_connected",  
        "oura_integration": oura_status
    }


@app.get("/api/oura/sleep/{date_str}", response_model=SleepData)
async def get_sleep_data(date_str: str):
    """
    Get sleep data for a specific date from Oura Ring
    Date format: YYYY-MM-DD

    Fetches real data from Oura API v2
    """
    print(f"=== SLEEP ENDPOINT CALLED ===")
    
    try:
        query_date = date.fromisoformat(date_str)
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    try:
        oura_client = get_oura_client()
       
        sleep_data = await oura_client.get_sleep_data(query_date)
        
        return sleep_data
    except OuraAPIError as e:
        raise HTTPException(status_code=503, detail=f"Oura API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/api/oura/readiness/{date_str}", response_model=ReadinessData)
async def get_readiness_data(date_str: str):
    """
    Get readiness data for a specific date from Oura Ring
    Date format: YYYY-MM-DD

    Fetches real data from Oura API v2
    """
    try:
        query_date = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    try:
        oura_client = get_oura_client()
        readiness_data = await oura_client.get_readiness_data(query_date)
        return readiness_data
    except OuraAPIError as e:
        raise HTTPException(status_code=509, detail=f"Oura API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/api/oura/activity/{date_str}", response_model=ActivityData)
async def get_activity_data(date_str: str):
    """
    Get activity data for a specific date from Oura Ring
    Date format: YYYY-MM-DD

    Fetches real data from Oura API v2
    """
    try:
        query_date = date.fromisoformat(date_str)
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    try:
        oura_client = get_oura_client()
        activity_data = await oura_client.get_activity_data(query_date)
        return activity_data
    except OuraAPIError as e:
        raise HTTPException(status_code=503, detail=f"Oura API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.post("/api/recommendations/{date_str}", response_model=RecoveryRecommendation)
async def generate_recommendation(date_str: str):
    """
    Generate AI-powered recovery recommendation for a specific date

    This endpoint:
    1. Fetches sleep, readiness, and activity data from Oura
    2. Analyzes all metrics together using Claude AI
    3. Returns personalized recovery recommendations

    Date format: YYYY-MM-DD

    Example response:
    {
        "date": "2024-01-15",
        "recommendation_type": "light_recovery",
        "message": "Your sleep was good but HRV is low. Light activity recommended.",
        "confidence": 0.85,
        "key_factors": ["Low HRV balance", "Good sleep quality"]
    }
    """
    print(f"\n{'='*60}")
    print(f"🎯 RECOMMENDATIONS ENDPOINT CALLED FOR: {date_str}")
    print(f"{'='*60}\n")
    
    try:
        query_date = date.fromisoformat(date_str)
        print(f"✅ Date parsed: {query_date}")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    try:
        # Fetch all three types of data from Oura
        print("\n📊 Step 1: Fetching Oura data...")
        oura_client = get_oura_client()

        # Get data in parallel for efficiency
        import asyncio
        sleep_data, readiness_data, activity_data = await asyncio.gather(
            oura_client.get_sleep_data(query_date),
            oura_client.get_readiness_data(query_date),
            oura_client.get_activity_data(query_date)
        )

        print("✅ Step 1 Complete: Got all Oura data!")
        print(f"   Sleep score: {sleep_data.sleep_score}")
        print(f"   Sleep total duration: {sleep_data.total_sleep_duration}")  # ← Add this
        print(f"   Sleep deep duration: {sleep_data.deep_sleep_duration}")    # ← Add this
        print(f"   Readiness score: {readiness_data.readiness_score}")
        print(f"   Activity score: {activity_data.activity_score}")

        # Generate AI recommendation
        print("\n🤖 Step 2: Initializing AI coach...")
        coach = get_recovery_coach()
        print("✅ Step 2 Complete: AI coach initialized!")
        
        print("\n🔮 Step 3: Calling analyze_recovery()...")
        recommendation = coach.analyze_recovery(
            sleep_data=sleep_data,
            readiness_data=readiness_data,
            activity_data=activity_data
        )
        
        print("✅ Step 3 Complete: Got recommendation!")
        print(f"   Type: {recommendation.recommendation_type}")
        print(f"\n{'='*60}\n")
        
        return recommendation

    except OuraAPIError as e:
        print(f"\n❌ OURA API ERROR: {e}")
        raise HTTPException(status_code=503, detail=f"Oura API error: {str(e)}")
        
    except AICoachError as e:
        print(f"\n❌ AI COACH ERROR: {e}")
        raise HTTPException(status_code=503, detail=f"AI Coach error: {str(e)}")
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR:")
        print(f"   Message: {e}")
        print(f"   Type: {type(e).__name__}")
        
        import traceback
        print(f"\n📋 Full traceback:")
        print(traceback.format_exc())
        
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
@app.get("/test/scan-activity-data")
async def scan_activity_data():
    """Scan last 30 days to see which dates have activity in API"""
    import httpx
    from datetime import timedelta
    
    token = os.getenv("OURA_ACCESS_TOKEN")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Request 30-day range
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.ouraring.com/v2/usercollection/daily_activity",
            headers=headers,
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        )
        
        data = response.json()
        
        results = {
            "status": response.status_code,
            "date_range": f"{start_date.isoformat()} to {end_date.isoformat()}",
            "total_records": len(data.get("data", [])),
            "dates_with_data": []
        }
        
        for record in data.get("data", []):
            results["dates_with_data"].append({
                "date": record.get("day"),
                "score": record.get("score"),
                "steps": record.get("steps"),
                "calories": record.get("total_calories")
            })
        
        return results

