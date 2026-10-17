#Schedule donations with the least remaining shelf life first
#If they have equal shelf life, prioritize the one with the most quantity
#If they have the same quantity, prioritize the one with the earlier ready time
#If they have the same ready time, prioritize any prepared meals first

import json
import heapq

#Read Donations File
with open("donations.json", "r") as file:
    donations_data = json.load(file)

#Read Recipients File
with open("recipients.json", "r") as file:
    recipients_data = json.load(file)

#Read Volunteers File
with open("volunteers.json", "r") as file:
    volunteers_data = json.load(file)

#Greedy Algorithm
def Greedy(d_data, r_data, v_data):

    donation_heap = []
    final_return_list = []

    #Manage variables of each donation into a heap
    for donation in d_data:
        priority = (
             donation["expiration_time"],
            -donation["quantity"],
             donation["ready_time"],
             0 if donation["food_type"] == "prepared_meals" else 1,
             donation["donation_id"],
             donation["pickup_location"]
        )

        heapq.heappush(donation_heap, (priority, donation))

    while donation_heap:
        priority, donation = heapq.heappop(donation_heap)
        assigned(donation, r_data, v_data, final_return_list)

    print("\n\n".join(final_return_list))
                            

def assigned(donation, r_data, v_data, final_return_list):
    recipient_found = None
    volunteer_found = None

    #Find first feasible recipient
    for recipient in r_data:
        food_matches = (donation["food_type"] in recipient["accepted_food_types"])

        enough_capacity = (donation["quantity"] <= recipient["capacity"])

        before_closing = (donation["expiration_time"] <= recipient["closing_time"])

        if (food_matches
            and enough_capacity
            and before_closing
        ):
            recipient_found = recipient
            break

    #Find first feasible volunteer
    for volunteer in v_data:
        enough_vehicle_capacity = (donation["quantity"] <= volunteer["vehicle_capacity"])

        location_matches = (donation["pickup_location"] == volunteer["location"])

        available_when_ready = (volunteer["available_from"] <= donation["ready_time"])

        available_before_expiration = (volunteer["available_until"] >= donation["expiration_time"])

        if (
            enough_vehicle_capacity
            and location_matches
            and available_when_ready
            and available_before_expiration
        ):
            volunteer_found = volunteer
            break

    if recipient_found and volunteer_found:
        assigned = "Donation " + donation["donation_id"] + " was assigned to the " + recipient_found["organization_name"] + " with volunteer " + volunteer_found["volunteer_id"] + " because the recipient is easily able to accept the food and the volunteer has enough capacity and time to get it there before the food expires."

    elif recipient_found == None and volunteer_found:
        assigned = "Donation " + donation["donation_id"] + " could not be assigned due to constraints with any available recipients."

    elif recipient_found and volunteer_found == None:
        assigned = "Donation " + donation["donation_id"] + " could not be assigned due to constraints with any available volunteers."

    else:
        assigned = "Donation " + donation["donation_id"] + " could not be assigned because no recipient or volunteer could meet the requirements necessary for the donation."

    final_return_list.append(assigned)


Greedy(donations_data, recipients_data, volunteers_data)