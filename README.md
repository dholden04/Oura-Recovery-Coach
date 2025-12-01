# Oura Ring AI Recovery Coach
AI-powered personalized health insights and recovery recommendations based on your Oura Ring data

#Overview
As an avid Oura Ring user, I found the default dashboard lacked the depth and AI-powered insights needed to truly optimize recovery. This project bridges that gap by combining real-time biometric data from the Oura Ring with Claude AI to deliver personalized, actionable health recommendations.
The application analyzes sleep quality, activity levels, and readiness metrics to provide context-aware coaching that adapts to your daily health patterns.
Features

#AI-Powered Analysis 
- Claude AI interprets your health metrics and provides personalized recovery recommendations
Comprehensive Dashboard - Detailed breakdowns of sleep stages, activity metrics, and readiness scores
Secure OAuth2 Integration - Industry-standard authentication with the Oura API
Real-Time Insights - Fetch and analyze your latest health data instantly
Multi-Metric Analysis - Combines sleep, activity, and readiness data for holistic recommendations

#Tech Stack


Python 3.11+ - Core language
FastAPI - Modern async web framework
httpx - Async HTTP client for API calls
Pydantic - Data validation and settings management
python-dotenv - Environment variable management

#APIs & Services

Oura Ring API v2 - Health and fitness data
Anthropic Claude API - AI-powered analysis and recommendations

#Authentication

OAuth2 Authorization Code Flow - Secure, token-based authentication
Environment-based secrets management

#Data Flow
1. User Authentication

/oauth/start triggers Oura authorization
User grants permissions (daily, sleep, personal, heartrate scopes)
/oauth/callback receives authorization code
Exchange code for access_token and refresh_token
Store tokens securely in environment

2. Data Retrieval

User requests recommendations for specific date
Backend makes parallel async calls to Oura API:

/sleep endpoint for duration breakdowns
/daily_sleep endpoint for sleep score
/daily_activity endpoint for steps, calories, activity score
/daily_readiness endpoint for HRV, resting HR, recovery metrics


Combine and validate data with Pydantic models

3. AI Analysis

Format health metrics into structured prompt
Send to Claude API with context and constraints
Parse AI response into recommendation model
Return to user with confidence scores

4. Response Delivery

JSON response with:

Recommendation type (recovery, light_activity, full_activity)
Personalized message
Key contributing factors
Confidence score



#Key Components
1. main.py - API Gateway

Defines all REST endpoints
Handles OAuth2 flow
Coordinates between services
Error handling and logging

2. oura_client.py - Oura API Integration

Manages authentication headers
Makes async requests to multiple Oura endpoints
Handles date range logic for different data types
Merges responses from /sleep and /daily_sleep endpoints

3. ai_coach.py - AI Service Layer

Constructs prompts with health metrics
Interfaces with Anthropic Claude API
Parses and validates AI responses
Applies business logic for recommendations

4. models.py - Data Models

Pydantic schemas for type safety
Validation rules for health data
Response models for API contracts


#Prerequisites

Python 3.11 or higher
Oura Ring with active account
Oura API credentials (https://cloud.ouraring.com/oauth/applications)
Anthropic API key (https://console.anthropic.com/)

Installation
1. Clone the repository
bashgit clone https://github.com/dholden04/Oura-Recovery-Coach.git
cd Oura-Recovery-Coach
2. Install dependencies
bashcd apps/api
pip install -r requirements.txt
3. Set up environment variables
Create .env file in apps/api directory:
env# Oura OAuth Credentials
OURA_CLIENT_ID=your_oura_client_id
OURA_CLIENT_SECRET=your_oura_client_secret
OURA_REDIRECT_URI=http://localhost:8000/oauth/callback

# Oura Access Tokens (obtained through OAuth flow)
OURA_ACCESS_TOKEN=your_access_token
OURA_REFRESH_TOKEN=your_refresh_token

# Anthropic API
ANTHROPIC_API_KEY=your_anthropic_api_key
4. Run the OAuth flow to get tokens
bash# Start the server
uvicorn main:app --reload

# Visit in browser
http://localhost:8000/oauth/start

# Authorize the app on Oura's page
# Copy the access_token and refresh_token from the callback response
# Add them to your .env file
5. Restart the server
bashuvicorn main:app --reload
Usage
Check API health:
bashcurl http://localhost:8000/api/health
Get sleep data:
bashcurl http://localhost:8000/api/oura/sleep/2025-11-20
Get activity data:
bashcurl http://localhost:8000/api/oura/activity/2025-11-20
Get readiness data:
bashcurl http://localhost:8000/api/oura/readiness/2025-11-20
Get AI recommendations:
bashcurl -X POST http://localhost:8000/api/recommendations/2025-11-20
```

**Access interactive API documentation:**
```
http://localhost:8000/docs
API Reference
Authentication Endpoints
GET /oauth/start
Initiates OAuth2 authorization flow with Oura.
Response: Redirects to Oura authorization page
Scopes requested:

daily - Daily summary data
personal - User profile information
heartrate - Heart rate data
sleep - Detailed sleep data


GET /oauth/callback
Handles OAuth2 callback and exchanges authorization code for tokens.
Query Parameters:

code (string, required) - Authorization code from Oura

Response:
json{
  "message": "Success!",
  "access_token": "_0XBPWQQ_...",
  "refresh_token": "_1XBPWQQ_..."
}
Health Data Endpoints
GET /api/oura/sleep/{date}
Retrieves comprehensive sleep data for a specific date.
Parameters:

date (string, required) - Date in YYYY-MM-DD format

Response:
json{
  "date": "2025-11-20",
  "total_sleep_duration": 28800,
  "deep_sleep_duration": 7200,
  "rem_sleep_duration": 6480,
  "light_sleep_duration": 15120,
  "sleep_score": 82,
  "restfulness": 2,
  "sleep_efficiency": 94
}

GET /api/oura/activity/{date}
Retrieves activity metrics for a specific date.
Parameters:

date (string, required) - Date in YYYY-MM-DD format

Response:
json{
  "date": "2025-11-20",
  "activity_score": 73,
  "steps": 9314,
  "active_calories": 432,
  "total_calories": 2918,
  "target_calories": 350,
  "equivalent_walking_distance": 6800,
  "high_activity_time": 0,
  "medium_activity_time": 2340,
  "low_activity_time": 13680
}

GET /api/oura/readiness/{date}
Retrieves readiness score and contributing factors.
Parameters:

date (string, required) - Date in YYYY-MM-DD format

Response:
json{
  "date": "2025-11-20",
  "readiness_score": 78,
  "temperature_deviation": -0.2,
  "resting_heart_rate": 52,
  "hrv_balance": 8,
  "recovery_index": 85,
  "sleep_balance": 72,
  "activity_balance": 80
}

POST /api/recommendations/{date}
Generates AI-powered recovery recommendations based on all health metrics.
Parameters:

date (string, required) - Date in YYYY-MM-DD format

Response:
json{
  "date": "2025-11-20",
  "recommendation_type": "light_recovery",
  "message": "Your sleep quality was good with 8 hours total, but your HRV balance is slightly low at 8/10. Your body is showing moderate recovery with a readiness score of 78. Consider light activity today like walking or yoga, and prioritize sleep consistency tonight.",
  "confidence": 0.85,
  "key_factors": [
    "Low HRV balance (8/10)",
    "Good sleep duration (8.0 hours)",
    "Moderate activity yesterday (73 score)",
    "Slightly elevated RHR (52 bpm)"
  ]
}
Recommendation Types:

full_rest - Complete recovery day recommended
light_recovery - Light activity okay (walking, stretching)
moderate_activity - Moderate training permitted
full_activity - Full intensity training cleared

Technical Challenges & Solutions
Challenge 1: OAuth2 Migration Mid-Development
Problem: Oura deprecated Personal Access Tokens during development, requiring a complete authentication overhaul.
Solution:

Implemented full OAuth2 authorization code flow
Created /oauth/start and /oauth/callback endpoints
Managed token lifecycle with refresh capability
Configured granular scopes for different data types

Key Learning: OAuth2 provides better security and user control through revocable access, granular permissions, and token expiration with refresh capability.

Challenge 2: Inconsistent API Endpoint Behaviors
Problem: Different Oura endpoints returned different data:

/daily_sleep provided scores but no duration data
/sleep provided durations but no scores
Activity data required date+1 boundary for "closed" days

Solution:
python# Call BOTH endpoints and merge responses
detailed_response = await self._make_request("sleep", params)
daily_response = await self._make_request("daily_sleep", params)

# Combine best of both
return SleepData(
    total_sleep_duration=detailed_response["data"][0]["total_sleep_duration"],
    sleep_score=daily_response["data"][0]["score"]
)
Key Insight: Activity data is continuous (accumulates throughout the day) while sleep data is event-based (finalized after sleep session). Activity needs date+1 to mark the day as "closed."

Challenge 3: Pydantic Validation Errors
Problem: Sleep score field was None causing validation errors because the detailed /sleep endpoint doesn't include scores.
Solution:
python# Made fields optional in model
class SleepData(BaseModel):
    sleep_score: Optional[int] = None  # Can be None
    
# Then populated from second endpoint call
Key Learning: Real APIs don't always match documentation perfectly. Need defensive programming with optional fields, default values, and validation that allows for API variations.

Challenge 4: Date Range Handling
Problem: Single-date queries returned empty results for activity data.
Solution:
python# Activity needs next-day boundary
end_date = (target_date + timedelta(days=1)).isoformat()
params = {
    "start_date": date_str,
    "end_date": end_date  # Date+1
}
Root Cause: Continuous data streams need boundaries to "close" the data collection period. This mirrors how databases handle time-series data.
What I Learned
Backend Engineering

OAuth2 Implementation - Built authorization code flow from scratch, understanding the four-actor model (user, client, authorization server, resource server)
Async Programming - Used asyncio.gather() for parallel API calls, reducing latency by 3x
API Integration - Handled rate limits, error responses, and undocumented edge cases
Error Handling - Implemented custom exceptions with proper HTTP status codes

System Design

Data Modeling - Designed Pydantic models for type safety and validation
Service Architecture - Separated concerns (routes, services, clients, models)
Event-based vs Continuous Data - Understood how different data collection patterns affect API design

Production Practices

Security - Never exposed API keys, used environment variables, implemented secure token storage
Debugging - Systematic debugging through logging at every layer
Documentation - Wrote comprehensive API docs and inline comments

Problem-Solving Approach

Start simple, iterate - Got basic endpoints working before adding OAuth
Debug systematically - Added logging to isolate failure points
Question assumptions - Asked "why" to understand root causes (like the activity date+1 requirement)
Read the response, not just the docs - Tested actual API behavior vs. documentation

Future Enhancements

Historical Trend Analysis - Track metrics over weeks/months to identify patterns
Data Caching Layer - Redis integration to reduce API calls and improve performance
Workout Correlation - Analyze how different workout types affect recovery
Mobile App - React Native frontend for iOS/Android
Multi-User Support - User authentication and database for multiple accounts
Webhook Integration - Real-time updates when new Oura data is available
Automated Recommendations - Daily notifications with recovery advice
Goal Tracking - Set and monitor health objectives
Export Features - Download reports as PDF or CSV
