import heapq
import json
from pathlib import Path

def Greedy(d_data, r_data, v_data):
    donation_heap = []
    final_return_list = []
    assigned_ids = set()

    for donation in d_data:
        priority = (
            donation["expiration_time"],
            -donation["quantity"],
            donation["ready_time"],
            0 if donation["food_type"] == "prepared_meals" else 1,
            donation["donation_id"],
            donation["pickup_location"],
        )
        heapq.heappush(donation_heap, (priority, donation))

    while donation_heap:
        priority, donation = heapq.heappop(donation_heap)
        if assigned(donation, r_data, v_data, final_return_list):
            assigned_ids.add(donation["donation_id"])

    for record in final_return_list:
        print(record["decision_reason"])
        print()

    path = Path(__file__).parent / "data" / "greedy_assignments.json"
    with open(path, "w", encoding="utf-8") as file:
        json.dump(final_return_list, file, indent=4)

    return assigned_ids

def assigned(donation, r_data, v_data, final_return_list):
    recipient_found = None
    volunteer_found = None

    for recipient in r_data:
        food_matches = (
            donation["food_type"] in recipient["accepted_food_types"]
        )
        enough_capacity = donation["quantity"] <= recipient["capacity"]
        before_closing = (
            donation["ready_time"] <= recipient["closing_time"]
        )

        if food_matches and enough_capacity and before_closing:
            recipient_found = recipient
            break

    for volunteer in v_data:
        enough_vehicle_capacity = (
            donation["quantity"] <= volunteer["vehicle_capacity"]
        )
        location_matches = (
            donation["pickup_location"] == volunteer["location"]
        )
        available_when_ready = (
            volunteer["available_from"]
            <= donation["ready_time"]
            <= volunteer["available_until"]
        )

        if (
            enough_vehicle_capacity
            and location_matches
            and available_when_ready
            and volunteer["maximum_pickups"] > 0
        ):
            volunteer_found = volunteer
            break

    success = recipient_found is not None and volunteer_found is not None

    if success:
        recipient_found["capacity"] -= donation["quantity"]
        volunteer_found["maximum_pickups"] -= 1
        message = (
            f'Donation {donation["donation_id"]} was assigned to '
            f'{recipient_found["organization_name"]} with volunteer '
            f'{volunteer_found["volunteer_id"]}. The recipient accepts '
            'the food, has capacity, and is open at the ready time. '
            'The volunteer passes capacity, location, availability, '
            'and pickup-limit checks.'
        )
    else:
        reasons = []
        if recipient_found is None:
            reasons.append(
                "no recipient meets all food, capacity, and closing-time checks"
            )
        if volunteer_found is None:
            reasons.append(
                "no volunteer meets all capacity, location, availability, "
                "and pickup-limit checks"
            )
        message = (
            f'Donation {donation["donation_id"]} could not be assigned: '
            + "; ".join(reasons) + "."
        )

    final_return_list.append({
        "donation_id": donation["donation_id"],
        "recipient_id": (
            recipient_found["recipient_id"] if success else None
        ),
        "volunteer_id": (
            volunteer_found["volunteer_id"] if success else None
        ),
        "scheduled_time": donation["ready_time"] if success else None,
        "decision_reason": message,
        "status": "assigned" if success else "unassigned",
    })
    return success