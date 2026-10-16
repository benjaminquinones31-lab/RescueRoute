import unittest
from load_data import validate_records


class TestDonationValidation(unittest.TestCase):
    def test_valid_donation(self):
        donation = {
            "donation_id": "D-1001",
            "donor_name": "Campus Cafe",
            "food_type": "prepared_meals",
            "quantity": 10,
            "expiration_time": "2026-10-01T17:00:00",
            "pickup_location": "Campus",
            "ready_time": "2026-10-01T14:00:00",
        }

        errors = validate_records([donation], "donations")

        self.assertEqual(errors, [])

    def test_negative_quantity(self):
        donation = {
            "donation_id": "D-1002",
            "donor_name": "Campus Cafe",
            "food_type": "prepared_meals",
            "quantity": -10,
            "expiration_time": "2026-10-01T17:00:00",
            "pickup_location": "Campus",
            "ready_time": "2026-10-01T14:00:00",
        }

        errors = validate_records([donation], "donations")

        self.assertTrue(
            any("quantity" in error for error in errors)
        )

    def test_duplicate_donation_ids(self):
        donation = {
            "donation_id": "D-1001",
            "donor_name": "Campus Cafe",
            "food_type": "prepared_meals",
            "quantity": 10,
            "expiration_time": "2026-10-01T17:00:00",
            "pickup_location": "Campus",
            "ready_time": "2026-10-01T14:00:00",
        }

        errors = validate_records(
            [donation, donation.copy()], "donations"
        )

        self.assertTrue(
            any("duplicate ID" in error for error in errors)
        )

    def test_missing_food_type(self):
        donation = {
            "donation_id": "D-1001",
            "donor_name": "Campus Cafe",
            "quantity": 10,
            "expiration_time": "2026-10-01T17:00:00",
            "pickup_location": "Campus",
            "ready_time": "2026-10-01T14:00:00",
        }

        errors = validate_records([donation], "donations")

        self.assertTrue(
            any(
                "missing fields" in error and "food_type" in error
                for error in errors
            )
        )

    def test_empty_donation_list(self):
        errors = validate_records([], "donations")

        self.assertEqual(errors, [])

    def test_expiration_before_ready_time(self):
        donation = {
            "donation_id": "D-1001",
            "donor_name": "Campus Cafe",
            "food_type": "prepared_meals",
            "quantity": 10,
            "expiration_time": "2026-10-01T13:00:00",
            "pickup_location": "Campus",
            "ready_time": "2026-10-01T14:00:00",
        }

        errors = validate_records([donation], "donations")

        self.assertTrue(
            any(
                "ready_time must be earlier than expiration_time" in error
                for error in errors
            )
        )    

    def test_negative_recipient_capacity(self):
        recipient = {
            "recipient_id": "R-1001",
            "organization_name": "Community Shelter",
            "accepted_food_types": ["prepared_meals", "bread"],
            "capacity": -5,
            "location": "Campus",
            "closing_time": "2026-10-01T20:00:00",
        }

        errors = validate_records([recipient], "recipients")

        self.assertTrue(
            any("capacity" in error for error in errors)
        )

    def test_invalid_volunteer_availability(self):
        volunteer = {
            "volunteer_id": "V-1001",
            "vehicle_capacity": 20,
            "location": "Campus",
            "available_from": "2026-10-01T18:00:00",
            "available_until": "2026-10-01T13:00:00",
            "maximum_pickups": 2,
        }

        errors = validate_records([volunteer], "volunteers")

        self.assertTrue(
            any(
                "available_from must be earlier than available_until" in error
                for error in errors
            )
        )

    def test_negative_pickup_limit(self):
        volunteer = {
            "volunteer_id": "V-1001",
            "vehicle_capacity": 20,
            "location": "Campus",
            "available_from": "2026-10-01T13:00:00",
            "available_until": "2026-10-01T18:00:00",
            "maximum_pickups": -1,
        }

        errors = validate_records([volunteer], "volunteers")

        self.assertTrue(
            any("maximum_pickups" in error for error in errors)
        )

    def test_invalid_expiration_date(self):
        donation = {
            "donation_id": "D-1001",
            "donor_name": "Campus Cafe",
            "food_type": "prepared_meals",
            "quantity": 10,
            "expiration_time": "2026-02-30T17:00:00",
            "pickup_location": "Campus",
            "ready_time": "2026-02-28T14:00:00",
        }

        errors = validate_records([donation], "donations")

        self.assertTrue(
            any(
                "expiration_time must be a real date/time" in error
                for error in errors
            )
        )   

if __name__ == "__main__":
    unittest.main()