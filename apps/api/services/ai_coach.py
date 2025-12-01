"""
AI Recovery Coach using Claude

This service analyzes health metrics from Oura Ring and generates
personalized recovery recommendations using Anthropic's Claude.
"""

import anthropic
import os
from datetime import date
from typing import Optional
from models import SleepData, ReadinessData, ActivityData, RecoveryRecommendation


class AICoachError(Exception):
    """Custom exception for AI Coach errors"""
    pass


class RecoveryCoach:
    """
    AI-powered recovery coach that analyzes health metrics
    and provides personalized recommendations
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI coach with Anthropic API key

        Args:
            api_key: Anthropic API key. If not provided, reads from ANTHROPIC_API_KEY env var
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key is required. "
                "Set ANTHROPIC_API_KEY environment variable or pass to constructor."
            )

        self.client = anthropic.Anthropic(api_key=self.api_key)

    def analyze_recovery(
        self,
        sleep_data: SleepData,
        readiness_data: ReadinessData,
        activity_data: ActivityData
    ) -> RecoveryRecommendation:
        """
        Analyze health metrics and generate recovery recommendations

        Args:
            sleep_data: Sleep metrics from Oura
            readiness_data: Readiness metrics from Oura
            activity_data: Activity metrics from Oura

        Returns:
            RecoveryRecommendation with AI-generated advice
        """

        # Build the analysis prompt for Claude
        prompt = self._build_analysis_prompt(sleep_data, readiness_data, activity_data)

        try:
            # Call Claude API
            # Note: Using Haiku for faster/cheaper responses. Upgrade to Sonnet/Opus for better analysis
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract the response
            response_text = message.content[0].text

            # Parse the response and create recommendation
            recommendation = self._parse_ai_response(
                response_text,
                sleep_data.date,
                sleep_data,
                readiness_data,
                activity_data
            )

            return recommendation

        except anthropic.APIError as e:
            raise AICoachError(f"Claude API error: {str(e)}")
        except Exception as e:
            raise AICoachError(f"Error generating recommendation: {str(e)}")

    def _build_analysis_prompt(
        self,
        sleep_data: SleepData,
        readiness_data: ReadinessData,
        activity_data: ActivityData
    ) -> str:
        """
        Build a detailed prompt for Claude to analyze health data

        Returns:
            Formatted prompt string
        """

        # Convert durations from seconds to hours for readability
        total_sleep_hrs = sleep_data.total_sleep_duration / 3600
        deep_sleep_hrs = sleep_data.deep_sleep_duration / 3600
        rem_sleep_hrs = sleep_data.rem_sleep_duration / 3600
        light_sleep_hrs = sleep_data.light_sleep_duration / 3600

        prompt = f"""You are an expert recovery coach and sports scientist analyzing health data from an Oura Ring.

**Today's Date:** {sleep_data.date}

**SLEEP METRICS:**
- Sleep Score: {sleep_data.sleep_score}/100
- Total Sleep: {total_sleep_hrs:.1f} hours
- Deep Sleep: {deep_sleep_hrs:.1f} hours ({(deep_sleep_hrs/total_sleep_hrs*100):.0f}% of total)
- REM Sleep: {rem_sleep_hrs:.1f} hours ({(rem_sleep_hrs/total_sleep_hrs*100):.0f}% of total)
- Light Sleep: {light_sleep_hrs:.1f} hours ({(light_sleep_hrs/total_sleep_hrs*100):.0f}% of total)
- Sleep Efficiency: {sleep_data.sleep_efficiency}%
- Restfulness: {sleep_data.restfulness}/100

**READINESS METRICS:**
- Readiness Score: {readiness_data.readiness_score}/100
- Resting Heart Rate: {readiness_data.resting_heart_rate} bpm
- HRV Balance: {readiness_data.hrv_balance}/100
- Temperature Deviation: {readiness_data.temperature_deviation}°C from baseline
- Recovery Index: {readiness_data.recovery_index}/100
- Sleep Balance: {readiness_data.sleep_balance}/100
- Activity Balance: {readiness_data.activity_balance}/100

**ACTIVITY METRICS (Previous Day):**
- Activity Score: {activity_data.activity_score}/100
- Steps: {activity_data.steps:,}
- Total Calories: {activity_data.total_calories}
- Active Calories: {activity_data.active_calories}
- Training Volume: {activity_data.training_volume} minutes

**CONTEXT & GUIDELINES:**
- Deep sleep optimal: 1.5-2 hours (15-25% of total sleep)
- REM sleep optimal: 1.5-2.5 hours (20-25% of total sleep)
- Resting HR baseline: 55-65 bpm (varies by individual)
- Temperature deviation >0.5°C may indicate stress, illness, or overtraining
- Readiness <70 = prioritize recovery, 70-85 = light-moderate activity, >85 = ready for hard training

**YOUR TASK:**
Analyze this data and provide a recovery recommendation. Format your response EXACTLY as follows:

RECOMMENDATION_TYPE: [choose ONE: rest_day, light_recovery, moderate_activity, training_ready, peak_performance]

KEY_FACTORS:
- [Factor 1: brief observation about the data]
- [Factor 2: another key insight]
- [Factor 3: another key insight]

MESSAGE:
[2-3 sentences with your main recommendation for today. Be specific and actionable. Mention the most important metrics.]

SPECIFIC_TIPS:
- [Specific tip #1]
- [Specific tip #2]
- [Specific tip #3]
- [Specific tip #4]

CONFIDENCE: [0.0-1.0, how confident are you in this recommendation based on data quality]

Be direct, specific, and actionable. Focus on what matters most for today's recovery."""

        return prompt

    def _parse_ai_response(
        self,
        response_text: str,
        target_date: date,
        sleep_data: SleepData,
        readiness_data: ReadinessData,
        activity_data: ActivityData
    ) -> RecoveryRecommendation:
        """
        Parse Claude's response into a structured RecoveryRecommendation

        Args:
            response_text: Raw text response from Claude
            target_date: Date of the recommendation
            sleep_data: Original sleep data (for fallback analysis)
            readiness_data: Original readiness data (for fallback analysis)
            activity_data: Original activity data (for fallback analysis)

        Returns:
            Structured RecoveryRecommendation object
        """

        try:
            # Extract recommendation type
            rec_type = "moderate_activity"  # Default
            if "RECOMMENDATION_TYPE:" in response_text:
                type_line = [line for line in response_text.split('\n') if "RECOMMENDATION_TYPE:" in line][0]
                rec_type = type_line.split(":", 1)[1].strip()

            # Extract key factors
            key_factors = []
            if "KEY_FACTORS:" in response_text:
                in_factors = False
                for line in response_text.split('\n'):
                    if "KEY_FACTORS:" in line:
                        in_factors = True
                        continue
                    if in_factors and line.strip().startswith('-'):
                        key_factors.append(line.strip('- ').strip())
                    elif in_factors and line.strip() and not line.strip().startswith('-'):
                        break

            # Extract main message
            message = ""
            if "MESSAGE:" in response_text:
                message_start = response_text.find("MESSAGE:") + len("MESSAGE:")
                message_end = response_text.find("SPECIFIC_TIPS:", message_start)
                if message_end == -1:
                    message_end = response_text.find("CONFIDENCE:", message_start)
                message = response_text[message_start:message_end].strip()

            # Extract specific tips
            specific_tips = []
            if "SPECIFIC_TIPS:" in response_text:
                in_tips = False
                for line in response_text.split('\n'):
                    if "SPECIFIC_TIPS:" in line:
                        in_tips = True
                        continue
                    if in_tips and line.strip().startswith('-'):
                        specific_tips.append(line.strip('- ').strip())
                    elif in_tips and "CONFIDENCE:" in line:
                        break

            # Combine message and tips
            full_message = message
            if specific_tips:
                full_message += "\n\nSpecific Tips:\n" + "\n".join(f"• {tip}" for tip in specific_tips)

            # Extract confidence
            confidence = 0.8  # Default
            if "CONFIDENCE:" in response_text:
                conf_line = [line for line in response_text.split('\n') if "CONFIDENCE:" in line][0]
                conf_str = conf_line.split(":", 1)[1].strip()
                try:
                    confidence = float(conf_str)
                except ValueError:
                    confidence = 0.8

            # Add key factors if not found
            if not key_factors:
                key_factors = self._generate_key_factors(sleep_data, readiness_data, activity_data)

            return RecoveryRecommendation(
                date=target_date,
                recommendation_type=rec_type,
                message=full_message,
                confidence=confidence,
                key_factors=key_factors
            )

        except Exception as e:
            # Fallback: Create a basic recommendation from the raw response
            return RecoveryRecommendation(
                date=target_date,
                recommendation_type=self._determine_recommendation_type(readiness_data),
                message=response_text[:500],  # Use first 500 chars of response
                confidence=0.7,
                key_factors=self._generate_key_factors(sleep_data, readiness_data, activity_data)
            )

    def _determine_recommendation_type(self, readiness_data: ReadinessData) -> str:
        """
        Determine recommendation type based on readiness score

        Args:
            readiness_data: Readiness metrics

        Returns:
            Recommendation type string
        """
        score = readiness_data.readiness_score

        if score >= 85:
            return "peak_performance"
        elif score >= 70:
            return "training_ready"
        elif score >= 55:
            return "moderate_activity"
        elif score >= 40:
            return "light_recovery"
        else:
            return "rest_day"

    def _generate_key_factors(
        self,
        sleep_data: SleepData,
        readiness_data: ReadinessData,
        activity_data: ActivityData
    ) -> list[str]:
        """
        Generate key factors from health metrics

        Returns:
            List of key factor strings
        """
        factors = []

        # Sleep quality
        if sleep_data.sleep_score >= 85:
            factors.append(f"Excellent sleep quality ({sleep_data.sleep_score}/100)")
        elif sleep_data.sleep_score < 70:
            factors.append(f"Poor sleep quality ({sleep_data.sleep_score}/100)")

        # Readiness
        if readiness_data.readiness_score >= 85:
            factors.append(f"High readiness score ({readiness_data.readiness_score}/100)")
        elif readiness_data.readiness_score < 70:
            factors.append(f"Low readiness score ({readiness_data.readiness_score}/100)")

        # Temperature
        if readiness_data.temperature_deviation and abs(readiness_data.temperature_deviation) > 0.5:
            factors.append(f"Elevated temperature deviation ({readiness_data.temperature_deviation}°C)")

        # HRV
        if readiness_data.hrv_balance and readiness_data.hrv_balance < 60:
            factors.append(f"Low HRV balance ({readiness_data.hrv_balance}/100)")

        # Activity
        if activity_data.steps < 5000:
            factors.append(f"Low activity yesterday ({activity_data.steps} steps)")

        return factors[:5]  # Return top 5 factors


# Singleton instance
_recovery_coach: Optional[RecoveryCoach] = None


def get_recovery_coach() -> RecoveryCoach:
    """
    Get or create the RecoveryCoach singleton

    Returns:
        RecoveryCoach instance
    """
    global _recovery_coach
    if _recovery_coach is None:
        _recovery_coach = RecoveryCoach()
    return _recovery_coach
