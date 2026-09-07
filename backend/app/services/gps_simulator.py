"""
GPS Simulator Service
---------------------
Simulates bus movement along predefined routes.

MODULAR DESIGN:
  This module exposes a GPSProvider interface. The simulator is one
  implementation. Real GPS hardware (e.g. serial NMEA, REST GPS tracker)
  can replace it by implementing GPSProvider.

Usage:
  gps = GPSSimulator("BUS-102")
  location = gps.get_next_location()
"""
import math
import time
import random
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional
from datetime import datetime


# ── Predefined Bus Routes (Madurai city, real coordinates) ──────────
BUS_ROUTES: Dict[str, Dict] = {
    "BUS-101": {
        "route_name": "Route 1 – Central to Anna Nagar",
        "route_start": "Madurai Central",
        "route_end": "Anna Nagar",
        "waypoints": [
            (9.9252, 78.1198),
            (9.9261, 78.1212),
            (9.9275, 78.1230),
            (9.9290, 78.1248),
            (9.9305, 78.1265),
            (9.9318, 78.1280),
            (9.9330, 78.1295),
            (9.9345, 78.1310),
        ],
        "speed_kmh": 25,
    },
    "BUS-102": {
        "route_name": "Route 2 – Meenakshi Temple to Kochadai",
        "route_start": "Meenakshi Temple",
        "route_end": "Kochadai",
        "waypoints": [
            (9.9195, 78.1193),
            (9.9210, 78.1205),
            (9.9225, 78.1215),
            (9.9238, 78.1230),
            (9.9252, 78.1245),
            (9.9268, 78.1260),
            (9.9282, 78.1275),
            (9.9295, 78.1288),
        ],
        "speed_kmh": 20,
    },
    "BUS-103": {
        "route_name": "Route 3 – Mattuthavani to Goripalayam",
        "route_start": "Mattuthavani",
        "route_end": "Goripalayam",
        "waypoints": [
            (9.9310, 78.1180),
            (9.9298, 78.1195),
            (9.9282, 78.1208),
            (9.9265, 78.1220),
            (9.9248, 78.1232),
            (9.9232, 78.1245),
            (9.9215, 78.1258),
            (9.9200, 78.1270),
        ],
        "speed_kmh": 30,
    },
    "BUS-104": {
        "route_name": "Route 4 – Railway Station to Vilangudi",
        "route_start": "Madurai Junction",
        "route_end": "Vilangudi",
        "waypoints": [
            (9.9279, 78.1148),
            (9.9290, 78.1162),
            (9.9302, 78.1178),
            (9.9315, 78.1193),
            (9.9328, 78.1208),
            (9.9342, 78.1222),
            (9.9355, 78.1238),
            (9.9368, 78.1252),
        ],
        "speed_kmh": 22,
    },
    "BUS-105": {
        "route_name": "Route 5 – Bypass Road Circuit",
        "route_start": "Bypass Road",
        "route_end": "Bypass Road",
        "waypoints": [
            (9.9180, 78.1160),
            (9.9195, 78.1175),
            (9.9210, 78.1190),
            (9.9225, 78.1205),
            (9.9240, 78.1218),
            (9.9255, 78.1230),
            (9.9268, 78.1242),
            (9.9280, 78.1255),
        ],
        "speed_kmh": 35,
    },
}


class GPSProvider(ABC):
    """Interface for GPS providers (simulator or real hardware)."""

    @abstractmethod
    def get_current_location(self, bus_id: str) -> Tuple[float, float]:
        ...

    @abstractmethod
    def get_next_location(self, bus_id: str) -> Tuple[float, float]:
        ...


class GPSSimulator(GPSProvider):
    """
    Simulates GPS movement along a predefined waypoint route.
    Interpolates smoothly between waypoints.
    """

    def __init__(self):
        # Track current waypoint index per bus
        self._state: Dict[str, Dict] = {}
        for bus_id, route in BUS_ROUTES.items():
            self._state[bus_id] = {
                "waypoint_idx": 0,
                "interp_t": 0.0,       # 0.0 → 1.0 between waypoints
                "current_lat": route["waypoints"][0][0],
                "current_lon": route["waypoints"][0][1],
            }

    def get_current_location(self, bus_id: str) -> Tuple[float, float]:
        state = self._state.get(bus_id)
        if not state:
            return (9.9252, 78.1198)  # default: Madurai centre
        return (state["current_lat"], state["current_lon"])

    def get_next_location(self, bus_id: str) -> Tuple[float, float]:
        """Advance bus along its route and return new coordinates."""
        if bus_id not in BUS_ROUTES or bus_id not in self._state:
            return (9.9252 + random.uniform(-0.001, 0.001),
                    78.1198 + random.uniform(-0.001, 0.001))

        route = BUS_ROUTES[bus_id]
        state = self._state[bus_id]
        waypoints = route["waypoints"]
        idx = state["waypoint_idx"]

        # Interpolation step based on speed
        step = 0.05 + random.uniform(-0.01, 0.01)
        state["interp_t"] += step

        if state["interp_t"] >= 1.0:
            state["interp_t"] = 0.0
            state["waypoint_idx"] = (idx + 1) % len(waypoints)
            idx = state["waypoint_idx"]

        next_idx = (idx + 1) % len(waypoints)
        t = state["interp_t"]
        lat = waypoints[idx][0] + t * (waypoints[next_idx][0] - waypoints[idx][0])
        lon = waypoints[idx][1] + t * (waypoints[next_idx][1] - waypoints[idx][1])

        # Add tiny GPS noise (realistic jitter)
        lat += random.gauss(0, 0.00005)
        lon += random.gauss(0, 0.00005)

        state["current_lat"] = round(lat, 6)
        state["current_lon"] = round(lon, 6)

        return (state["current_lat"], state["current_lon"])

    def get_all_locations(self) -> Dict[str, Tuple[float, float]]:
        """Return current location of all buses."""
        return {
            bus_id: self.get_current_location(bus_id)
            for bus_id in BUS_ROUTES
        }

    def get_route_info(self, bus_id: str) -> Optional[Dict]:
        return BUS_ROUTES.get(bus_id)


# Singleton instance
gps_simulator = GPSSimulator()
