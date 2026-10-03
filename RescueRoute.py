#Rescue Route - Surplus Food Matching & Pickup Planner
import json

#Read Donations File
with open("donations.json", "r") as file:
    donations_data = json.load(file)

#Read Recipients File
with open("recipients.json", "r") as file:
    recipients_data = json.load(file)

#Read Volunteers File
with open("volunteers.json", "r") as file:
    volunteers_data = json.load(file)

#FIFO Baseline Algorithm
def FIFO(d_data, r_data, v_data):
    matches = []
    unmatched = []

    food_quantity_rescued = 0
    food_quantity_at_risk = 0

    for donation in d_data:
        recipient_found = None
        volunteer_found = None

        # Find first feasible recipient
        for recipient in r_data:
            food_matches = (
                donation["food_type"] in recipient["accepted_food_types"]
            )

            enough_capacity = (
                donation["quantity"] <= recipient["capacity"]
            )

            location_matches = (
                donation["pickup_location"] == recipient["location"]
            )

            before_closing = (
                donation["expiration_time"] <= recipient["closing_time"]
            )

            if (food_matches and enough_capacity and location_matches and before_closing):
                recipient_found = recipient
            elif(not food_matches):
                r_reason = "food_matches"
            elif(not enough_capacity):
                r_reason = "enough_capacity"
            elif(not location_matches):
                r_reason = "location_matches"
            elif(not before_closing):
                r_reason = "before_closing"
            
        # Find first feasible volunteer
        for volunteer in v_data:

            enough_vehicle_capacity = (
                donation["quantity"] <= volunteer["vehicle_capacity"]
            )

            location_matches = (
                donation["pickup_location"] == volunteer["location"]
            )

            available_when_ready = (
                volunteer["available_from"] <= donation["ready_time"]
            )

            available_before_expiration = (
                volunteer["available_until"] >= donation["expiration_time"]
            )

            if (enough_vehicle_capacity and location_matches and available_when_ready and available_before_expiration):
                volunteer_found = volunteer
            elif(not enough_vehicle_capacity):
                v_reason = "enough_vehicle_capacity"
            elif(not location_matches):
                v_reason = "location_matches"
            elif(not available_when_ready):
                v_reason = "available_when_ready"
            elif(not available_before_expiration):
                v_reason = "available_before_expiration"

        # If both were found, record the match
        if recipient_found and volunteer_found:
            food_quantity_rescued = (donation["quantity"])
            matches.append({
                "donation_id": donation["donation_id"],
                "recipient_id": recipient_found["recipient_id"],
                "volunteer_id": volunteer_found["volunteer_id"]
            })

        # Otherwise, record the unmatched donation ID
        else:
            unmatched.append({
                "donation_id": donation["donation_id"]
            })

    #Output
    print("--- Rescue Route ---\n")

    print("Total Donation records processed:", len(matches) + len(unmatched))
    print("Food quantity rescued:", food_quantity_rescued)

    print("\nMatches:", len(matches))
    for match in matches:
        print(match["donation_id"], "was assigned to recipient", match["recipient_id"], "with volunteer", match["volunteer_id"])
    
    print("Unmatched:", len(unmatched))
    for donation_id in unmatched:
        print(donation_id["donation_id"], "was not assigned because the recipient did not have", r_reason, "and the volunteer did not have", v_reason)

FIFO(donations_data, recipients_data, volunteers_data)