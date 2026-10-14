"""Convert natural-language preferences into a small safe routing schema.

This module deliberately does not produce steering or acceleration commands.  Its
output is constrained to planner preferences and can therefore be validated before
it crosses into the deterministic routing stack.
"""

from __future__ import annotations

from dataclasses import dataclass

from mountainpilot.planning import DrivingProfile


@dataclass(frozen=True, slots=True)
class RoutePreference:
    profile: DrivingProfile
    avoid_high_risk: bool
    request_text: str
    explanation: str


def interpret_route_request(text: str) -> RoutePreference:
    normalized = text.strip().lower()
    if not normalized:
        raise ValueError("route request cannot be empty")
    if len(normalized) > 200:
        raise ValueError("route request must not exceed 200 characters")

    eco_words = ("省电", "节能", "续航", "eco", "energy")
    fast_words = ("最快", "赶时间", "快速", "fast", "quick")
    comfort_words = ("舒适", "平稳", "不晕车", "comfort", "smooth")
    risk_words = ("安全", "避开危险", "避开复杂", "safe", "low risk")

    if any(word in normalized for word in eco_words):
        profile = DrivingProfile.ECO
        explanation = "Selected ECO to prioritize estimated traction energy."
    elif any(word in normalized for word in fast_words):
        profile = DrivingProfile.FAST
        explanation = "Selected FAST to prioritize estimated travel time."
    elif any(word in normalized for word in comfort_words):
        profile = DrivingProfile.COMFORT
        explanation = "Selected COMFORT to penalize curvature and risk."
    else:
        profile = DrivingProfile.COMFORT
        explanation = "No explicit mode found; selected the conservative COMFORT default."

    avoid_high_risk = any(word in normalized for word in risk_words)
    return RoutePreference(profile, avoid_high_risk, text.strip(), explanation)
