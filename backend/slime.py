"""
PlasmaGrid — Physarum Polycephalum Slime Mould Routing Algorithm
Based on the mathematical model published in Science (2010):
"Rules for Biologically Inspired Adaptive Network Design"
Applied to Karnataka state emergency resource routing.
"""
import math


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculates the great-circle distance between two GPS points on Earth.
    Uses the Haversine formula to account for Earth's spherical shape.
    Returns distance in kilometres.
    """
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.asin(math.sqrt(a))


def slime_allocate(nodes):
    """
    Physarum chemotaxis model applied to hospital resource routing.

    Biology:
      - Nodes with scarcity < 35 = "food sources" (surplus) → PUSH resources out
      - Nodes with scarcity > 65 = "hungry nodes" (critical) → PULL resources in
      - Conductivity = (scarcity_difference) / max(distance, 0.1)
      - Highest conductivity path selected first (greedy optimal)

    Returns a list of transfer recommendations sorted by priority score.
    """
    # Filter nodes — must have valid GPS coordinates
    valid = [n for n in nodes if n.get("lat") and n.get("lng") and n.get("scarcity") is not None]

    pushers = [n for n in valid if n["scarcity"] < 35]   # surplus nodes
    pullers = [n for n in valid if n["scarcity"] > 65]   # critical nodes

    transfers = []

    for pull in pullers:
        best = None
        best_score = 0

        for push in pushers:
            dist = haversine(
                pull["lat"], pull["lng"],
                push["lat"], push["lng"]
            )
            # Physarum conductivity formula
            score = (pull["scarcity"] - push["scarcity"]) / max(dist, 0.1)
            if score > best_score:
                best_score = score
                best = push

        if best:
            dist_km = haversine(
                pull["lat"], pull["lng"],
                best["lat"], best["lng"]
            )
            transfers.append({
                "from": best["name"],
                "from_id": best.get("id", ""),
                "from_area": best.get("area", ""),
                "from_city": best.get("city", ""),
                "to": pull["name"],
                "to_id": pull.get("id", ""),
                "to_area": pull.get("area", ""),
                "to_city": pull.get("city", ""),
                "distance_km": round(dist_km, 2),
                "priority_score": round(best_score, 4),
                "from_scarcity": best["scarcity"],
                "to_scarcity": pull["scarcity"],
                "pressure_delta": pull["scarcity"] - best["scarcity"],
            })

    # Sort by highest priority (greatest pressure delta over shortest distance)
    return sorted(transfers, key=lambda x: -x["priority_score"])