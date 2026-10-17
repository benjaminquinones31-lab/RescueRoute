https://github.com/benjaminquinones31-lab/RescueRoute
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

## How to run it

You need Python 3. We only used built-in Python libraries, so there is nothing extra to install.

Open a terminal in the RescueRoute folder and run:

```bash
python main.py
```

This runs FIFO and greedy using separate copies of the same data. It prints the assignments, explanations, and a comparison of the results.

To run all tests:

```bash
python -m unittest discover -v
```

We have 20 tests, and all 20 passed locally.

## Files

- `main.py` runs both algorithms and compares their results.
- `load_data.py` loads and checks the JSON files.
- `fifo.py` handles donations in arrival order.
- `greedy.py` handles donations in priority order.
- `test_load_data.py` tests data validation.
- `test_comparison.py` checks a case where the algorithms choose different donations.
- `test_scheduling.py` checks matching, capacity, availability, pickup limits, empty inputs, nearly expired food, and fairness.
- `data/` contains the sample inputs and saved assignment results.

FIFO saves to `data/assignment.json`.
Greedy saves to `data/greedy_assignments.json`.

Each assignment includes the donation, recipient, volunteer, scheduled time, status, and reason. Unassigned donations have null values for the recipient, volunteer, and scheduled time.

The comparison test can overwrite the greedy output with test data. Run `python main.py` again afterward to restore the normal sample results.

## Our data

We use three JSON input files:

- Donations: ID, donor name, food type, quantity, expiration time, pickup location, and ready time.
- Recipients: ID, organization name, accepted foods, capacity, location, and closing time.
- Volunteers: ID, vehicle capacity, location, availability, and maximum pickups.

Quantities and capacities are measured in servings. All dates use the same local timezone and the format `YYYY-MM-DDTHH:MM:SS`.

## How the algorithms work

### FIFO

We treat the order of donations in the JSON file as their arrival order. FIFO checks them in that order and chooses the first recipient and volunteer that meet the requirements.

### Greedy

Greedy uses a heap to choose donations in this order:

1. Earliest expiration.
2. Largest quantity.
3. Earliest ready time.
4. Prepared meals first.
5. Donation ID and pickup location to break any remaining ties.

The idea is to prioritize food that could expire sooner. This does not mean greedy always rescues the most food or finds the best possible schedule.

### Data structures

We use dictionaries for records, tracking capacity and pickups, and storing metrics. Sets help detect duplicate IDs and track assigned donations. Lists store the donation order and assignment history. Greedy uses `heapq` for its priority queue.

## Matching rules

Both algorithms check that:

- The recipient accepts the food and has enough capacity left.
- The volunteer can carry the quantity and has pickups remaining.
- The volunteer is in the donation's pickup area.
- The volunteer is available at the ready time.
- The recipient has not closed at that time.

After a match, we subtract the donation quantity from the recipient's remaining capacity and use one volunteer pickup.

To keep the project simple, we assume pickup and delivery happen at the ready time without travel time. Recipients can be in a different area. We do not split donations or search for a later pickup time.

The loader checks that ready time comes before expiration. We use simulated dates rather than checking them against today's date. Capacities and pickup limits apply to the whole run.

## Metrics

We compare:

- Donations received, assigned, and unassigned.
- Food quantity rescued and at risk.
- Urgent rescue rate.
- Recipient capacity utilization.
- Volunteer capacity utilization.

For urgent rescue rate, we count donations tied for the earliest expiration:

Assigned urgent donations / total urgent donations × 100.

Recipient utilization is rescued servings divided by the total starting recipient capacity.

Volunteer utilization is rescued servings divided by total vehicle capacity. Since volunteers can make multiple pickups, this number can go above 100%.

We use zero when a calculation would divide by zero. The comparison shows greedy minus FIFO. Differences between percentages are percentage points.

## What we found

With our five-donation sample, both algorithms assign three donations and rescue 65 servings. They leave 55 servings at risk and have a 100% urgent rescue rate.

The results match because the sample donations are already in greedy order.

We also tested two donations competing for only 10 servings of recipient capacity:

- FIFO chooses D-LATE because it arrived first.
- Greedy chooses D-URGENT because it expires first.

Both rescue 10 servings, but FIFO has a 0% urgent rescue rate and greedy has 100%.

This shows a tradeoff: greedy helps the urgent donation, but the donation that arrived first gets considered later and loses the available capacity. In a continuing system, repeated urgent arrivals could keep pushing less urgent donations back.

## Complexity

D is the number of donations, R is recipients, and V is volunteers.

For each donation, the code can check all recipients and volunteers. FIFO therefore takes O(D × (R + V)) time.

Greedy does those same checks and adds O(D log D) for the heap.

Ignoring the length of explanation text, space use is O(D + R + V). This includes records, counters, and assignment history. Greedy also stores up to D donations in its heap.

## Limitations

This is a class prototype with simulated data, not a system ready for real food deliveries.

We do not calculate travel times, check recipient opening times, or check whether donations have expired relative to the current date. Rejection messages explain which groups of checks failed, but do not list every failed check for every candidate.

## Who worked on what

- Benjamin Quinones: initial sample data, loading and validation, validation tests, integration and scheduling tests, and documentation.
- Yannick Mangelschots: initial FIFO algorithm, resource tracking, and output/metrics work.
- Eliyas Khodr-Osman: initial greedy algorithm, heap implementation, and priority rule.

## Sources and help used

- RescueRoute project brief and assignment requirements.
- Python documentation: https://docs.python.org/3/library/
- ChatGPT/Codex for help understanding Python, writing validation code, debugging, integration, tests, and documentation.
