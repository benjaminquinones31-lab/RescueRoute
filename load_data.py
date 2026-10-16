import json
import re
from datetime import datetime
from pathlib import Path

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

RULES = {
    "donations": {
        "id": "donation_id",
        "text": ["donation_id", "donor_name", "food_type", "pickup_location"],
        "numbers": {"quantity": 1},
        "times": ["ready_time", "expiration_time"],
    },
    "recipients": {
        "id": "recipient_id",
        "text": ["recipient_id", "organization_name", "location"],
        "numbers": {"capacity": 0},
        "times": ["closing_time"],
    },
    "volunteers": {
        "id": "volunteer_id",
        "text": ["volunteer_id", "location"],
        "numbers": {"vehicle_capacity": 0, "maximum_pickups": 0},
        "times": ["available_from", "available_until"],
    },
}


def validate_records(records, kind):
    errors = []
    rules = RULES[kind]
    seen_ids = set()
    required = rules["text"] + list(rules["numbers"]) + rules["times"]
    if kind == "recipients":
        required.append("accepted_food_types")

    if not isinstance(records, list):
        return [f"{kind}: the file must contain a list inside square brackets."]

    for row, record in enumerate(records, start=1):
        label = f"{kind}, record {row}"
        if not isinstance(record, dict):
            errors.append(f"{label}: each record must be an object inside braces.")
            continue

        missing = [field for field in required if field not in record]
        if missing:
            errors.append(f"{label}: missing fields: {', '.join(missing)}.")
            continue

        for field in rules["text"]:
            value = record[field]
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{label}: {field} must be nonempty text.")
            elif value != value.strip():
                errors.append(f"{label}: remove spaces at the ends of {field}.")

        record_id = record[rules["id"]]
        if isinstance(record_id, str) and record_id.strip():
            if record_id in seen_ids:
                errors.append(f"{label}: duplicate ID {record_id}.")
            seen_ids.add(record_id)

        for field, minimum in rules["numbers"].items():
            value = record[field]
            if type(value) is not int or value < minimum:
                errors.append(
                    f"{label}: {field} must be a whole number of at least {minimum}."
                )

        if kind == "recipients":
            foods = record["accepted_food_types"]
            if not isinstance(foods, list) or not foods:
                errors.append(f"{label}: accepted_food_types must be a nonempty list.")
            else:
                seen_foods = set()
                for food in foods:
                    if not isinstance(food, str) or not food.strip():
                        errors.append(f"{label}: each accepted food type must be nonempty text.")
                    elif food != food.strip():
                        errors.append(f"{label}: remove spaces at the ends of food types.")
                    elif food in seen_foods:
                        errors.append(f"{label}: repeated accepted food type {food}.")
                    else:
                        seen_foods.add(food)

        parsed_times = {}
        for field in rules["times"]:
            value = record[field]
            try:
                if not isinstance(value, str) or not re.fullmatch(
                    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}", value
                ):
                    raise ValueError
                parsed_times[field] = datetime.strptime(value, TIME_FORMAT)
            except ValueError:
                errors.append(
                    f"{label}: {field} must be a real date/time like 2026-10-01T17:00:00."
                )

        if kind == "donations":
            start, end = "ready_time", "expiration_time"
        elif kind == "volunteers":
            start, end = "available_from", "available_until"
        else:
            continue

        if start in parsed_times and end in parsed_times:
            if parsed_times[start] >= parsed_times[end]:
                errors.append(f"{label}: {start} must be earlier than {end}.")

    return errors


def load_all_data(data_folder):
    data = {}
    errors = []

    for kind in RULES:
        path = Path(data_folder) / f"{kind}.json"
        try:
            with open(path, encoding="utf-8-sig") as file:
                records = json.load(file)
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            errors.append(f"{path.name}: could not read the file: {error}")
            continue

        errors.extend(validate_records(records, kind))
        data[kind] = records

    if errors:
        raise ValueError("Validation failed:\n- " + "\n- ".join(errors))

    return data


def main():
    data_folder = Path(__file__).parent / "data"
    try:
        data = load_all_data(data_folder)
    except ValueError as error:
        print(error)
        return

    for kind, records in data.items():
        print(f"{kind.capitalize()} loaded: {len(records)}")
    print("All data passed validation.")


if __name__ == "__main__":
    main()