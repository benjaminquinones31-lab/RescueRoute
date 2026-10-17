import json
from pathlib import Path


def FIFO(d_data, r_data, v_data):
    assignments = []
    recipient_used = {r["recipient_id"]: 0 for r in r_data}
    volunteer_pickups = {v["volunteer_id"]: 0 for v in v_data}

    for donation in d_data:
        recipient_found = None
        volunteer_found = None

        for recipient in r_data:
            remaining = (
                recipient["capacity"]
                - recipient_used[recipient["recipient_id"]]
            )
            if (
                donation["food_type"] in recipient["accepted_food_types"]
                and donation["quantity"] <= remaining
                and donation["ready_time"] <= recipient["closing_time"]
            ):
                recipient_found = recipient
                break

        for volunteer in v_data:
            if (
                donation["quantity"] <= volunteer["vehicle_capacity"]
                and donation["pickup_location"] == volunteer["location"]
                and volunteer["available_from"]
                <= donation["ready_time"]
                <= volunteer["available_until"]
                and volunteer_pickups[volunteer["volunteer_id"]]
                < volunteer["maximum_pickups"]
            ):
                volunteer_found = volunteer
                break

        record = {
            "donation_id": donation["donation_id"],
            "recipient_id": None,
            "volunteer_id": None,
            "scheduled_time": None,
            "status": "unassigned",
            "decision_reason": "",
        }

        if recipient_found is not None and volunteer_found is not None:
            rid = recipient_found["recipient_id"]
            vid = volunteer_found["volunteer_id"]
            recipient_used[rid] += donation["quantity"]
            volunteer_pickups[vid] += 1

            record.update({
                "recipient_id": rid,
                "volunteer_id": vid,
                "scheduled_time": donation["ready_time"],
                "status": "assigned",
                "decision_reason": (
                    f"{recipient_found['organization_name']} accepts the food, "
                    "has capacity, and is open at the ready time. "
                    f"{vid} is available in the pickup area, can carry "
                    "the quantity, and has a pickup remaining."
                ),
            })
        else:
            reasons = []
            if recipient_found is None:
                reasons.append(
                    "No recipient meets all food-type, remaining-capacity, "
                    "and closing-time checks."
                )
            if volunteer_found is None:
                reasons.append(
                    "No volunteer meets all vehicle-capacity, pickup-area, "
                    "availability, and pickup-limit checks."
                )
            record["decision_reason"] = " ".join(reasons)

        assignments.append(record)

    assigned_ids = {
        a["donation_id"] for a in assignments if a["status"] == "assigned"
    }
    rescued = sum(
        d["quantity"] for d in d_data if d["donation_id"] in assigned_ids
    )
    earliest = min((d["expiration_time"] for d in d_data), default=None)
    urgent_ids = {
        d["donation_id"] for d in d_data if d["expiration_time"] == earliest
    }
    recipient_capacity = sum(r["capacity"] for r in r_data)
    volunteer_capacity = sum(v["vehicle_capacity"] for v in v_data)

    metrics = {
        "donations_received": len(d_data),
        "donations_assigned": len(assigned_ids),
        "donations_unassigned": len(d_data) - len(assigned_ids),
        "food_quantity_rescued": rescued,
        "food_quantity_at_risk": sum(d["quantity"] for d in d_data) - rescued,
        "urgent_rescue_rate": (
            100 * len(urgent_ids & assigned_ids) / len(urgent_ids)
            if urgent_ids else 0
        ),
        "recipient_capacity_utilization": (
            100 * rescued / recipient_capacity if recipient_capacity else 0
        ),
        "volunteer_capacity_utilization": (
            100 * rescued / volunteer_capacity if volunteer_capacity else 0
        ),
    }

    print("\n--- FIFO ---")
    for name, value in metrics.items():
        print(f"{name}: {value}")
    for record in assignments:
        print(
            record["donation_id"],
            record["status"],
            "-", record["decision_reason"]
        )

    path = Path(__file__).parent / "data" / "assignment.json"
    with open(path, "w", encoding="utf-8") as file:
        json.dump(assignments, file, indent=4)

    return {"assignments": assignments, "metrics": metrics}