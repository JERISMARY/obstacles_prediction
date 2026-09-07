"""
Warning Generator
-----------------
Converts RiskEngine output into natural-language voice warnings.

Design principles:
  1. Combine multiple hazards into a SINGLE message (no speech spam).
  2. Prioritize by risk level.
  3. Use conservative, safe language (slow down / caution).
  4. Never instruct dangerous maneuvers (swerve, overtake, cross lane).
  5. Low confidence → softer language ("possible hazard").
  6. Clear priority levels: CRITICAL > HIGH > MEDIUM > LOW.
"""
from typing import Dict, List, Optional


# ── Warning priority levels ──────────────────────────────────────────
PRIORITY_CRITICAL = 4
PRIORITY_HIGH     = 3
PRIORITY_MEDIUM   = 2
PRIORITY_LOW      = 1
PRIORITY_NONE     = 0

PRIORITY_LABELS = {
    PRIORITY_CRITICAL: "critical",
    PRIORITY_HIGH:     "high",
    PRIORITY_MEDIUM:   "medium",
    PRIORITY_LOW:      "low",
    PRIORITY_NONE:     "none",
}

# ── Risk level → priority ────────────────────────────────────────────
RISK_TO_PRIORITY = {
    "critical": PRIORITY_CRITICAL,
    "warning":  PRIORITY_HIGH,
    "caution":  PRIORITY_MEDIUM,
    "safe":     PRIORITY_LOW,
}


class WarningGenerator:
    """
    Generates natural-language warnings from RiskEngine output.
    """

    def generate(
        self,
        risk_assessment: Dict,
        route_recommendation: Optional[Dict] = None,
    ) -> Optional[Dict]:
        """
        Generate a warning from a risk assessment.

        Returns None if no warning is needed (safe + no traffic issue).
        Returns:
        {
            "message": str,          # voice + display text
            "priority": int,
            "priority_label": str,
            "type": str,             # primary hazard type
            "speak": bool,           # should TTS be triggered?
            "risk_score": float,
            "risk_level": str,
        }
        """
        risk_level = risk_assessment.get("risk_level", "safe")
        hazards = risk_assessment.get("hazards", [])
        oncoming = risk_assessment.get("oncoming_vehicles", [])
        traffic_level = risk_assessment.get("traffic_level", "low")
        risk_score = risk_assessment.get("risk_score", 0)

        priority = RISK_TO_PRIORITY.get(risk_level, PRIORITY_LOW)

        # Collect hazard phrases
        hazard_phrases = []
        primary_type = "general"

        # ── Road defects in path ─────────────────────────────────────
        for h in hazards:
            if not h.get("in_path") and h["object"] not in ("pothole", "road_damage", "waterlogging"):
                continue  # only warn about side hazards for defects

            obj = h["object"]
            pos = h["position"]
            dist = h.get("distance", "medium")
            conf = h.get("confidence", 0.5)
            is_oncoming = h.get("is_oncoming", False)

            if obj == "pothole":
                if conf >= 0.70:
                    phrase = f"pothole {'ahead' if pos == 'center' else 'on the ' + pos}"
                else:
                    phrase = "possible road hazard ahead"
                hazard_phrases.append(phrase)
                primary_type = "pothole"

            elif obj == "road_damage":
                phrase = "damaged road ahead" if pos == "center" else f"road damage on the {pos}"
                hazard_phrases.append(phrase)
                if primary_type == "general":
                    primary_type = "road_damage"

            elif obj == "waterlogging":
                phrase = "waterlogged road section ahead"
                hazard_phrases.append(phrase)
                if primary_type == "general":
                    primary_type = "waterlogging"

            elif obj == "person":
                phrase = "pedestrian in the road"
                hazard_phrases.append(phrase)
                if primary_type == "general":
                    primary_type = "pedestrian"

            elif is_oncoming:
                phrase = "oncoming vehicle ahead"
                hazard_phrases.append(phrase)
                if primary_type == "general":
                    primary_type = "oncoming_vehicle"

        # ── Oncoming vehicles (flagged by tracker) ────────────────────
        if oncoming and "oncoming vehicle" not in " ".join(hazard_phrases):
            if oncoming[0].get("confidence", 0) >= 0.60:
                hazard_phrases.append("oncoming vehicle ahead")
                if primary_type == "general":
                    primary_type = "oncoming_vehicle"
            else:
                hazard_phrases.append("vehicle ahead")
                if primary_type == "general":
                    primary_type = "vehicle"

        # ── Traffic congestion ────────────────────────────────────────
        traffic_warning = None
        if traffic_level in ("high", "severe"):
            traffic_warning = "heavy traffic ahead"
            if primary_type == "general":
                primary_type = "traffic_congestion"

        # ── No significant hazards ────────────────────────────────────
        if not hazard_phrases and not traffic_warning and risk_level == "safe":
            return None

        # ── Build combined message ────────────────────────────────────
        message = self._build_message(
            risk_level=risk_level,
            hazard_phrases=hazard_phrases,
            traffic_warning=traffic_warning,
            route_recommendation=route_recommendation,
            primary_type=primary_type,
        )

        # Speak for medium+ priority
        speak = priority >= PRIORITY_MEDIUM

        return {
            "message": message,
            "priority": priority,
            "priority_label": PRIORITY_LABELS[priority],
            "type": primary_type,
            "speak": speak,
            "risk_score": risk_score,
            "risk_level": risk_level,
        }

    def _build_message(
        self,
        risk_level: str,
        hazard_phrases: List[str],
        traffic_warning: Optional[str],
        route_recommendation: Optional[Dict],
        primary_type: str,
    ) -> str:
        """Build a clean, combined natural-language warning."""

        # Prefix based on risk level
        prefix_map = {
            "critical": "Warning.",
            "warning":  "Warning.",
            "caution":  "Caution.",
            "safe":     "",
        }
        prefix = prefix_map.get(risk_level, "Caution.")

        parts = []

        # Combine hazard phrases (max 2 to keep it short)
        if hazard_phrases:
            combined_hazards = " and ".join(hazard_phrases[:2])
            combined_hazards = combined_hazards[0].upper() + combined_hazards[1:]
            parts.append(f"{prefix} {combined_hazards}.")

        # Safe action recommendation
        action = self._safe_action(primary_type, risk_level)
        if action:
            parts.append(action)

        # Traffic + route
        if traffic_warning:
            if not parts:
                parts.append(f"{traffic_warning[0].upper() + traffic_warning[1:]}.")
            else:
                parts.append(f"Also, {traffic_warning}.")

        if route_recommendation and route_recommendation.get("recommended"):
            rec = route_recommendation["recommended"]
            saving = route_recommendation.get("time_saving_min")
            route_name = rec.get("name", "alternate route")
            if saving:
                parts.append(
                    f"Alternate {route_name} may save approximately {saving} minutes."
                )
            else:
                parts.append(f"Alternate {route_name} is available.")

        return " ".join(parts).strip()

    def _safe_action(self, primary_type: str, risk_level: str) -> str:
        """Returns a safe, non-aggressive recommended action."""
        actions = {
            "pothole":          "Slow down.",
            "road_damage":      "Slow down and proceed with caution.",
            "waterlogging":     "Reduce speed. Risk of skidding.",
            "pedestrian":       "Slow down. Pedestrian in road.",
            "oncoming_vehicle": "Maintain your lane.",
            "vehicle":          "Maintain safe following distance.",
            "traffic_congestion": "",
            "general":          "Exercise caution.",
        }
        if risk_level in ("critical", "warning") and primary_type not in actions:
            return "Reduce speed and maintain your lane."
        return actions.get(primary_type, "")
