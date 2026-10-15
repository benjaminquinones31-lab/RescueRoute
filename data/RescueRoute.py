#Rescue Route - Surplus Food Matching & Pickup Planner
import json
from datetime import datetime
from math import ceil

#Read Donations File
with open("data/donations.json", "r") as file:
    donations_data = json.load(file)

#Read Recipients File
with open("data/recipients.json", "r") as file:
    recipients_data = json.load(file)

#Read Volunteers File
with open("data/volunteers.json", "r") as file:
    volunteers_data = json.load(file)

print("Recipients loaded:", len(recipients_data))

#FIFO Baseline Algorithm
def FIFO(d_data, r_data, v_data):
    matches = []
    unmatched = []

    food_quantity_rescued = 0
    food_quantity_at_risk = 0

    # Track remaining recipient capacity and volunteer pickups
    recipient_used = {r["recipient_id"]: 0 for r in r_data}

    volunteer_pickups = {v["volunteer_id"]: 0 for v in v_data}

    # Current time, used to identify expired donations
    now = datetime.now()

    # Process donations in arrival order
    for donation in d_data:
        recipient_found = None
        volunteer_found = None

        r_reason = ""
        v_reason = ""

        # Find first feasible recipient
        for recipient in r_data:
            food_matches = (donation["food_type"] in recipient["accepted_food_types"])

            remaining_capacity = (recipient["capacity"] - recipient_used[recipient["recipient_id"]])

            enough_capacity = (donation["quantity"] <= remaining_capacity)

            before_closing = (donation["expiration_time"] <= recipient["closing_time"])

            if (food_matches and enough_capacity and before_closing):
                recipient_found = recipient
                break
                
            if(not food_matches):
                r_reason = "food_matches"
            if(not enough_capacity):
                r_reason = "enough_capacity"
            if(not before_closing):
                r_reason = "before_closing"
            
        # Find first feasible volunteer
        for volunteer in v_data:

            enough_vehicle_capacity = (donation["quantity"] <= volunteer["vehicle_capacity"])

            available_when_ready = volunteer["available_from"] <= donation["ready_time"]

            available_before_expiration = volunteer["available_until"] >= donation["ready_time"]

            has_pickup_space = (volunteer_pickups[volunteer["volunteer_id"]] < volunteer["maximum_pickups"])

            if (enough_vehicle_capacity and available_when_ready and available_before_expiration and has_pickup_space):
                volunteer_found = volunteer
                break
            if(not enough_vehicle_capacity):
                v_reason = "enough_vehicle_capacity"
            if(not available_when_ready):
                v_reason = "available_when_ready"
            if(not available_before_expiration):
                v_reason = "available_before_expiration"
            if(not has_pickup_space):
                v_reason = "has_pickup_space"

        # If both were found, record the match
        if recipient_found and volunteer_found:
            quantity = donation["quantity"]
            food_quantity_rescued += (donation["quantity"])

            recipient_used[recipient_found["recipient_id"]] += quantity

            volunteer_pickups[volunteer_found["volunteer_id"]] += 1

            matches.append({
                "donation_id": donation["donation_id"],
                "recipient_id": recipient_found["recipient_id"],
                "volunteer_id": volunteer_found["volunteer_id"],
                "quantity": quantity
            })

        # Otherwise, record the unmatched donation ID
        else:
            unmatched.append({
                "donation_id": donation["donation_id"],
                "quantity": donation["quantity"]
            })

            food_quantity_at_risk += donation["quantity"]

    #Output
    total_recipient_capacity = sum(recipient["capacity"] for recipient in r_data)
    total_volunteer_capacity = sum(volunteer["vehicle_capacity"] for volunteer in v_data)

    if total_recipient_capacity > 0:
        recipient_utilization = (food_quantity_rescued / total_recipient_capacity* 100)
    else:
        recipient_utilization = 0

    if total_volunteer_capacity > 0:
        volunteer_utilization = (food_quantity_rescued / total_volunteer_capacity * 100)
    else:
        volunteer_utilization = 0

    urgent_total = 0
    urgent_assigned = 0

    earliest_expiration = min(donation["expiration_time"] for donation in d_data)

    for donation in d_data:
        if donation["expiration_time"] == earliest_expiration:
            urgent_total += 1

        for match in matches:
            if donation["donation_id"] == match["donation_id"]:
                urgent_assigned += 1
                break
    
    # Calculate the percentage of urgent donations assigned
    if urgent_total > 0:
        urgent_rescue_rate = (urgent_assigned / urgent_total) * 100
    else:
        urgent_rescue_rate = 0
    
    print("--- Rescue Route ---\n")

    print("Total Donation records processed:", len(matches) + len(unmatched))
    print("Food quantity rescued:", food_quantity_rescued)
    print("Food quantity at risk:", food_quantity_at_risk)
    print(f"Urgent rescue rate: {urgent_rescue_rate:.2f}%")

    print(f"Recipient capacity utilization: "f"{recipient_utilization:.2f}%")
    print(f"Volunteer capacity utilization: "f"{volunteer_utilization:.2f}%")

    print("\nMatches:", len(matches))
    for match in matches:
        print(match["donation_id"], "was assigned to recipient", match["recipient_id"], "with volunteer", match["volunteer_id"])
    
    print("Unmatched:", len(unmatched))
    for donation_id in unmatched:
        print(donation_id["donation_id"], "was not assigned because no recipient had", r_reason, "and no volunteer had", v_reason)

FIFO(donations_data, recipients_data, volunteers_data)