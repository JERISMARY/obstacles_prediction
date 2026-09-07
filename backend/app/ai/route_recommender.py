"""
Route Recommender
-----------------
Compares current route against alternative routes and recommends
the best one based on a combined score of travel time + traffic + risk.

⚠ DEMO MODE DISCLAIMER:
  All routes, ETAs, and traffic data here are simulated/predefined.
  This is clearly labelled as DEMO ROUTE DATA throughout.
  In production, replace _fetch_route_options() with calls to:
    - OSRM (open-source, free)
    - GraphHopper
    - OpenRouteService
    - Google Maps Directions API
  The interface (input/output schema) is already compatible with those APIs.

Route Score = weighted combination of:
  - Estimated travel time (lower = better)
  - Traffic level (lower = better)
  - Incident risk score (lower = better)
  - Road condition factor
"""
from typing import Dict, List, Optional


# ── Demo route database (Madurai city) ──────────────────────────────
# In production: replace with routing API calls
DEMO_ROUTES = {
    "BUS-101": {
        "current": {
            "name": "Route A",
            "description": "Madurai Central → Anna Nagar via Main Road",
            "eta_min": 28,
            "distance_km": 8.2,
            "traffic": "high",
            "risk_score": 65,
            "waypoints": [(9.9252, 78.1198), (9.9318, 78.1280), (9.9345, 78.1310)],
        },
        "alternatives": [
            {
                "name": "Route B",
                "description": "Via Bypass Road",
                "eta_min": 22,
                "distance_km": 9.8,
                "traffic": "moderate",
                "risk_score": 35,
                "waypoints": [(9.9252, 78.1198), (9.9210, 78.1190), (9.9345, 78.1310)],
            },
            {
                "name": "Route C",
                "description": "Via Ring Road",
                "eta_min": 31,
                "distance_km": 11.1,
                "traffic": "low",
                "risk_score": 20,
                "waypoints": [(9.9252, 78.1198), (9.9180, 78.1160), (9.9345, 78.1310)],
            },
        ],
    },
    "BUS-102": {
        "current": {
            "name": "Route A",
            "description": "Meenakshi Temple → Kochadai via Town Hall Road",
            "eta_min": 28,
            "distance_km": 6.4,
            "traffic": "severe",
            "risk_score": 80,
            "waypoints": [(9.9195, 78.1193), (9.9238, 78.1230), (9.9295, 78.1288)],
        },
        "alternatives": [
            {
                "name": "Route B",
                "description": "Via South Bypass",
                "eta_min": 20,
                "distance_km": 8.1,
                "traffic": "moderate",
                "risk_score": 30,
                "waypoints": [(9.9195, 78.1193), (9.9180, 78.1160), (9.9295, 78.1288)],
            },
        ],
    },
    "BUS-103": {
        "current": {
            "name": "Route A",
            "description": "Mattuthavani → Goripalayam Direct",
            "eta_min": 18,
            "distance_km": 5.1,
            "traffic": "low",
            "risk_score": 20,
            "waypoints": [(9.9310, 78.1180), (9.9248, 78.1232), (9.9200, 78.1270)],
        },
        "alternatives": [],
    },
    "BUS-104": {
        "current": {
            "name": "Route A",
            "description": "Madurai Junction → Vilangudi via City Centre",
            "eta_min": 35,
            "distance_km": 9.3,
            "traffic": "severe",
            "risk_score": 85,
            "waypoints": [(9.9279, 78.1148), (9.9342, 78.1222), (9.9368, 78.1252)],
        },
        "alternatives": [
            {
                "name": "Route B",
                "description": "Via North Ring Road",
                "eta_min": 27,
                "distance_km": 11.2,
                "traffic": "moderate",
                "risk_score": 40,
                "waypoints": [(9.9279, 78.1148), (9.9310, 78.1180), (9.9368, 78.1252)],
            },
        ],
    },
    "BUS-105": {
        "current": {
            "name": "Route A",
            "description": "Bypass Road Circuit",
            "eta_min": 40,
            "distance_km": 12.0,
            "traffic": "low",
            "risk_score": 15,
            "waypoints": [(9.9180, 78.1160), (9.9255, 78.1230), (9.9180, 78.1160)],
        },
        "alternatives": [],
    },
}

# ── Scoring weights ──────────────────────────────────────────────────
TRAFFIC_SCORE = {"low": 0, "moderate": 15, "high": 30, "severe": 50}

def _route_combined_score(route: Dict) -> float:
    """Lower = better route."""
    eta = route.get("eta_min", 30)
    traffic = TRAFFIC_SCORE.get(route.get("traffic", "low"), 0)
    risk = route.get("risk_score", 50) * 0.4
    return eta + traffic + risk


class RouteRecommender:
    """
    Compares current vs alternative routes and returns recommendation.
    All data is clearly labelled DEMO when using built-in route database.
    """

    def recommend(
        self,
        bus_id: str,
        current_traffic_level: Optional[str] = None,
        current_risk_score: Optional[float] = None,
    ) -> Dict:
        """
        Returns route recommendation for a bus.
        Optionally overrides traffic/risk from live detection.

        Returns:
        {
            "current_route": {...},
            "alternatives": [...],
            "recommended": {...} | None,
            "time_saving_min": int | None,
            "should_recommend": bool,
            "reason": str,
            "is_demo": True,
        }
        """
        routes = DEMO_ROUTES.get(bus_id)
        if not routes:
            return {
                "current_route": None,
                "alternatives": [],
                "recommended": None,
                "should_recommend": False,
                "reason": "No route data available for this bus",
                "is_demo": True,
            }

        current = dict(routes["current"])
        alternatives = [dict(a) for a in routes.get("alternatives", [])]

        # Override with live detection data if available
        if current_traffic_level:
            current["traffic"] = current_traffic_level
        if current_risk_score is not None:
            current["risk_score"] = current_risk_score

        current_score = _route_combined_score(current)

        # Find best alternative
        best_alt = None
        best_alt_score = current_score

        for alt in alternatives:
            alt_score = _route_combined_score(alt)
            if alt_score < best_alt_score:
                best_alt = alt
                best_alt_score = alt_score

        should_recommend = (
            best_alt is not None
            and current.get("traffic") in ("high", "severe")
            and best_alt_score < current_score * 0.85  # at least 15% better
        )

        time_saving = None
        reason = "Current route is optimal"
        if should_recommend and best_alt:
            time_saving = current["eta_min"] - best_alt["eta_min"]
            reason = (
                f"Current route has {current['traffic']} traffic. "
                f"{best_alt['name']} has {best_alt['traffic']} traffic "
                f"and saves approximately {time_saving} minutes."
            )

        return {
            "current_route": current,
            "alternatives": alternatives,
            "recommended": best_alt if should_recommend else None,
            "time_saving_min": time_saving if should_recommend else None,
            "should_recommend": should_recommend,
            "reason": reason,
            "is_demo": True,  # always True until real routing API is integrated
        }
