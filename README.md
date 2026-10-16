# RescueRoute
Python application that helps coordinate time-sensitive surplus food donations with compatible community organizations and volunteer drivers. 
## Data loading and validation

Sample input files are stored in the data folder:

- donations.json

- recipients.json

- volunteers.json

Run the loader from the project folder:
```
python load_data.py
```
The loader checks required fields, nonempty text, duplicate IDs, whole-number quantities and capacities, accepted-food lists, valid date/time formats, and time ordering. It reports errors and refuses to return invalid data.

Quantities use whole-number servings. Donation quantities must be positive; capacities and maximum pickup limits may be zero. Times use the format YYYY-MM-DDTHH:MM:SS in one shared local timezone.

Run the validation tests:
```
python -m unittest test_load_data -v
```
The test suite contains 10 validation tests. These cover data validation, not FIFO or greedy scheduling.

Both scheduling strategies can load validated data with:
```
from pathlib import Path
from load_data import load_all_data

data = load_all_data(Path(__file__).parent / "data")

donations = data["donations"]
recipients = data["recipients"]
volunteers = data["volunteers"]
```
Each strategy should start with fresh data so assignments from one run do not affect the other. Scheduling code is responsible for food compatibility, remaining capacity, pickup limits, and feasible assignment times.
