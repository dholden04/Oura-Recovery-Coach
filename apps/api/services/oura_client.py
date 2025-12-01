"""
Oura Ring API Client

This service integrates with the Oura Ring API v2 to fetch real health data.
API Documentation: https://cloud.ouraring.com/v2/docs
"""

import httpx
from datetime import date, datetime, timedelta
from typing import Optional
from models import SleepData, ReadinessData, ActivityData
import os


class OuraAPIError(Exception):
    """Custom exception for Oura API errors"""
    pass


class OuraClient:
    """
    Client for interacting with Oura Ring API v2

    Rate Limits: 5,000 requests per day per user
    """

    BASE_URL = "https://api.ouraring.com/v2/usercollection"

    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize Oura API client

        Args:
            access_token: Personal access token from Oura Cloud
                         If not provided, will try to get from OURA_ACCESS_TOKEN env var
        """
        self.access_token = access_token or os.getenv("OURA_ACCESS_TOKEN")
        
        if not self.access_token:
            raise ValueError(
                "Oura access token is required. "
                "Set OURA_ACCESS_TOKEN environment variable or pass to constructor."
            )

        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    async def _make_request(self, endpoint: str, params: dict) -> dict:
        """
        Make an async HTTP request to Oura API

        Args:
            endpoint: API endpoint (e.g., "sleep", "daily_readiness")
            params: Query parameters

        Returns:
            JSON response from API

        Raises:
            OuraAPIError: If request fails
        """
        url = f"{self.BASE_URL}/{endpoint}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    raise OuraAPIError("Invalid or expired Oura access token")
                elif e.response.status_code == 429:
                    raise OuraAPIError("Rate limit exceeded. Try again later.")
                else:
                    raise OuraAPIError(f"Oura API error: {e.response.status_code} - {e.response.text}")

            except httpx.RequestError as e:
                raise OuraAPIError(f"Network error connecting to Oura API: {str(e)}")

   
    async def get_sleep_data(self, target_date: date) -> SleepData:
            date_str = target_date.isoformat()
            end_date = (target_date + timedelta(days=1)).isoformat()
            
    
            params = {
                "start_date": date_str,
                "end_date": end_date
            }
            

            detailed_response = await self._make_request("sleep", params)
            daily_response = await self._make_request("daily_sleep", params)
            if not detailed_response.get("data") or not daily_response.get("data"):
                raise OuraAPIError(
            f"No data available on {date_str}. "
            f"Check Oura app to see if ring is connected."
        )
    
            detailed_record = detailed_response["data"][0]
            daily_record = daily_response["data"][0]
    
    # Combine data from both endpoints
            return SleepData(
                date=target_date,
                total_sleep_duration=detailed_record.get("total_sleep_duration", 0),
                deep_sleep_duration=detailed_record.get("deep_sleep_duration", 0),
                rem_sleep_duration=detailed_record.get("rem_sleep_duration", 0),
                light_sleep_duration=detailed_record.get("light_sleep_duration", 0),
                sleep_score=daily_record.get("score"),  # ← From daily_sleep
                restfulness=detailed_record.get("restless_periods"),
                sleep_efficiency=detailed_record.get("efficiency")
            )
    async def get_readiness_data(self, target_date: date) -> ReadinessData:
        """
        Get readiness data for a specific date

        Args:
            target_date: Date to fetch readiness data for

        Returns:
            ReadinessData model with readiness metrics
        """
        date_str = target_date.isoformat()

        params = {
            "start_date": date_str,
            "end_date": date_str
        }

        response = await self._make_request("daily_readiness", params)

        if not response.get("data"):
           raise OuraAPIError(
                f"No data available on {date_str}."
                f"Check Oura app to see if ring is connected."
            )

        readiness_record = response["data"][0]
        contributors = readiness_record.get("contributors", {})
       
        # Map Oura API response to our ReadinessData model
        return ReadinessData(
            date=target_date,
            readiness_score=readiness_record.get("score"),
            temperature_deviation=contributors.get("body_temperature"),
            resting_heart_rate=contributors.get("resting_heart_rate"),
            hrv_balance=contributors.get("hrv_balance"),
            recovery_index=contributors.get("recovery_index"),
            previous_night_score=contributors.get("previous_night"),
            sleep_balance=contributors.get("sleep_balance"),
            activity_balance=contributors.get("activity_balance")
        )

    async def get_activity_data(self, target_date: date) -> ActivityData:
        """
        Get activity data for a specific date

        Args:
            target_date: Date to fetch activity data for

        Returns:
            ActivityData model with activity metrics
        """
        date_str = target_date.isoformat()
        end_date = (target_date + timedelta(days=1)).isoformat()
        params = {
            "start_date": date_str,
            "end_date": end_date
        }

        response = await self._make_request("daily_activity", params)
        
        if not response.get("data"):
           
            raise OuraAPIError(
                f"No data available on {date_str}."
                f"Check Oura app to see if ring is connected."
            )

        activity_record = response["data"][0]

    
        contributors = activity_record.get("contributors", {})
      

        # Map Oura API response to our ActivityData model
        return ActivityData(
            date=target_date,
            activity_score=activity_record.get("score"),
            steps=activity_record.get("steps", 0),
            total_calories=activity_record.get("total_calories", 0),
            active_calories=activity_record.get("active_calories", 0),
            target_calories=activity_record.get("target_calories", 0),
            training_frequency=contributors.get("training_frequency"),
            training_volume=contributors.get("training_volume"),
            recovery_time=activity_record.get("rest_mode_state")
        )

    async def get_personal_info(self) -> dict:
        """
        Get user's personal information

        Returns:
            Dictionary with user info (age, weight, height, biological sex)
        """
        response = await self._make_request("personal_info", {})
        return response

    #
# Singleton instance for reuse across the application
_oura_client: Optional[OuraClient] = None


def get_oura_client() -> OuraClient:
    """
    Get or create the Oura client singleton

    Returns:
        OuraClient instance
    """
    global _oura_client
    if _oura_client is None:
        _oura_client = OuraClient()
    return _oura_client
