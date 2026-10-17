import unittest
from copy import deepcopy

from fifo import FIFO
from greedy import Greedy


class TestComparison(unittest.TestCase):
    def test_urgent_donation_competes_for_capacity(self):
        donations = [
            {
                "donation_id": "D-LATE",
                "donor_name": "Cafe",
                "food_type": "bread",
                "quantity": 10,
                "ready_time": "2026-10-01T12:00:00",
                "expiration_time": "2026-10-01T18:00:00",
                "pickup_location": "Campus",
            },
            {
                "donation_id": "D-URGENT",
                "donor_name": "Bakery",
                "food_type": "bread",
                "quantity": 10,
                "ready_time": "2026-10-01T12:00:00",
                "expiration_time": "2026-10-01T13:00:00",
                "pickup_location": "Campus",
            },
        ]

        recipients = [{
            "recipient_id": "R-1",
            "organization_name": "Shelter",
            "accepted_food_types": ["bread"],
            "capacity": 10,
            "location": "Campus",
            "closing_time": "2026-10-01T20:00:00",
        }]

        volunteers = [{
            "volunteer_id": "V-1",
            "vehicle_capacity": 10,
            "location": "Campus",
            "available_from": "2026-10-01T11:00:00",
            "available_until": "2026-10-01T20:00:00",
            "maximum_pickups": 2,
        }]

        # Prevent FIFO's output file from overwriting your sample results.
        from unittest.mock import mock_open, patch

        with patch("fifo.open", mock_open()):
            fifo_result = FIFO(
                deepcopy(donations),
                deepcopy(recipients),
                deepcopy(volunteers),
            )

        greedy_ids = Greedy(
            deepcopy(donations),
            deepcopy(recipients),
            deepcopy(volunteers),
        )

        fifo_ids = {
            a["donation_id"]
            for a in fifo_result["assignments"]
            if a["status"] == "assigned"
        }

        self.assertEqual(fifo_ids, {"D-LATE"})
        self.assertEqual(greedy_ids, {"D-URGENT"})
        self.assertEqual(fifo_result["metrics"]["urgent_rescue_rate"], 0)


if __name__ == "__main__":
    unittest.main()