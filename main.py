from pathlib import Path
from copy import deepcopy

from load_data import load_all_data
from fifo import FIFO
from greedy import Greedy


def main():
    try:
        data = load_all_data(Path(__file__).parent / "data")
    except ValueError as error:
        print(error)
        return

    fifo_data = deepcopy(data)
    fifo_results = FIFO(
        fifo_data["donations"],
        fifo_data["recipients"],
        fifo_data["volunteers"],
    )

    print("\n--- Greedy ---")
    greedy_data = deepcopy(data)
    assigned_ids = Greedy(
        greedy_data["donations"],
        greedy_data["recipients"],
        greedy_data["volunteers"],
    )

    donations = data["donations"]
    rescued = sum(
        d["quantity"] for d in donations
        if d["donation_id"] in assigned_ids
    )
    earliest = min(
        (d["expiration_time"] for d in donations), default=None
    )
    urgent_ids = {
        d["donation_id"] for d in donations
        if d["expiration_time"] == earliest
    }
    recipient_capacity = sum(r["capacity"] for r in data["recipients"])
    volunteer_capacity = sum(v["vehicle_capacity"] for v in data["volunteers"])

    greedy_metrics = {
        "donations_received": len(donations),
        "donations_assigned": len(assigned_ids),
        "donations_unassigned": len(donations) - len(assigned_ids),
        "food_quantity_rescued": rescued,
        "food_quantity_at_risk": sum(d["quantity"] for d in donations) - rescued,
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

    print("\n--- FIFO vs. Greedy ---")
    print("Rates/utilization are percentages. Difference = Greedy minus FIFO.")

    for metric, fifo_value in fifo_results["metrics"].items():
        greedy_value = greedy_metrics[metric]
        print(
            f"{metric}: FIFO={fifo_value:.2f}, "
            f"Greedy={greedy_value:.2f}, "
            f"Difference={greedy_value - fifo_value:+.2f}"
        )


if __name__ == "__main__":
    main()