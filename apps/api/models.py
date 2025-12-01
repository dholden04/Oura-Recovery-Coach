"""
Data models for Oura Ring health metrics
"""

from pydantic import BaseModel
from typing import Optional
from datetime import date


class SleepData(BaseModel):
    """Sleep metrics from Oura Ring"""
    date: date
    total_sleep_duration: int  # seconds
    deep_sleep_duration: int  # seconds
    rem_sleep_duration: int  # seconds
    light_sleep_duration: int  # seconds
    sleep_score: int  # 0-100
    restfulness: Optional[int] = None  # 0-100
    sleep_efficiency: Optional[int] = None  # percentage


class ReadinessData(BaseModel):
    """Readiness metrics from Oura Ring"""
    date: date
    readiness_score: int  # 0-100
    temperature_deviation: Optional[float] = None  # celsius
    resting_heart_rate: Optional[int] = None  # bpm
    hrv_balance: Optional[int] = None  # 0-100
    recovery_index: Optional[int] = None  # 0-100
    previous_night_score: Optional[int] = None  # 0-100
    sleep_balance: Optional[int] = None  # 0-100
    activity_balance: Optional[int] = None  # 0-100


class ActivityData(BaseModel):
    """Activity metrics from Oura Ring"""
    date: date
    activity_score: int  # 0-100
    steps: int
    total_calories: int
    active_calories: int
    target_calories: int
    training_frequency: Optional[int] = None
    training_volume: Optional[int] = None
    recovery_time: Optional[int] = None  # hours


class RecoveryRecommendation(BaseModel):
    """AI-generated recovery recommendation"""
    date: date
    recommendation_type: str  # "rest", "light_activity", "moderate_training", "high_intensity"
    message: str
    confidence: float  # 0.0-1.0
    key_factors: list[str]
