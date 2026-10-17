import unittest
from contextlib import redirect_stdout
from copy import deepcopy
from io import StringIO
from unittest.mock import mock_open, patch

from fifo import FIFO
from greedy import Greedy


class TestScheduling(unittest.TestCase):
    def setUp(self):
        self.donations = [{
            "donation_id": "D-1",
            "donor_name": "Cafe",
            "food_type": "bread",
            "quantity": 10,
            "ready_time": "2026-10-01T12:00:00",
            "expiration_time": "2026-10-01T18:00:00",
            "pickup_location": "Campus",
        }]
        self.recipients = [{
            "recipient_id": "R-1",
            "organization_name": "Shelter",
            "accepted_food_types": ["bread"],
            "capacity": 20,
            "location": "Campus",
            "closing_time": "2026-10-01T20:00:00",
        }]
        self.volunteers = [{
            "volunteer_id": "V-1",
            "vehicle_capacity": 10,
            "location": "Campus",
            "maximum_pickups": 2,
            "available_from": "2026-10-01T11:00:00",
            "available_until": "2026-10-01T20:00:00",
        }]

    def check_both(self, expected_fifo, expected_greedy=None):
        if expected_greedy is None:
            expected_greedy = expected_fifo

        # Hide printed output and prevent writing assignment files.
        with redirect_stdout(StringIO()), \
                patch("fifo.open", mock_open()), \
                patch("greedy.open", mock_open()):
            fifo = FIFO(
                deepcopy(self.donations),
                deepcopy(self.recipients),
                deepcopy(self.volunteers),
            )
            greedy = Greedy(
                deepcopy(self.donations),
                deepcopy(self.recipients),
                deepcopy(self.volunteers),
            )

        fifo_ids = {
            a["donation_id"] for a in fifo["assignments"]
            if a["status"] == "assigned"
        }
        self.assertEqual(fifo_ids, expected_fifo)
        self.assertEqual(greedy, expected_greedy)

    def test_normal_match(self):
        self.check_both({"D-1"})

    def test_incompatible_food(self):
        self.recipients[0]["accepted_food_types"] = ["fruit"]
        self.check_both(set())

    def test_insufficient_recipient_capacity(self):
        self.recipients[0]["capacity"] = 5
        self.check_both(set())

    def test_insufficient_vehicle_capacity(self):
        self.volunteers[0]["vehicle_capacity"] = 5
        self.check_both(set())

    def test_unavailable_volunteer(self):
        self.volunteers[0]["available_until"] = "2026-10-01T11:30:00"
        self.check_both(set())

    def test_pickup_limit(self):
        self.volunteers[0]["maximum_pickups"] = 1
        self.donations.append(
            dict(self.donations[0], donation_id="D-2")
        )
        self.check_both({"D-1"})

    def test_empty_inputs(self):
        self.donations = []
        self.recipients = []
        self.volunteers = []
        self.check_both(set())

    def test_nearly_expired_donation(self):
        # Pickup is instantaneous in our simplified model.
        self.donations[0]["expiration_time"] = "2026-10-01T12:00:01"
        self.check_both({"D-1"})

    def test_fairness_tradeoff(self):
        self.recipients[0]["capacity"] = 10
        self.donations.append(
            dict(
                self.donations[0],
                donation_id="D-URGENT",
                expiration_time="2026-10-01T13:00:00",
            )
        )

        # FIFO favors the first arrival.
        # Greedy considers D-1 later and consumes capacity on D-URGENT.
        self.check_both({"D-1"}, {"D-URGENT"})


if __name__ == "__main__":
    unittest.main()