# Instructions


### Task 1

**Write a script in Python that prints the numbers from 1 to 75.**

But for multiples of four print "Mission" instead of the number and for the multiples of five print "Control". For numbers which are multiples of both four and seven print "Mission Control".


### Task 2

**Data handling and basic visualization test:**

Download json GOES 16 proton data from services.swpc.noaa.gov
https://services.swpc.noaa.gov/json/goes/primary/differential-protons-1-day.json
Put it into Pandas Dataframe Plot a 20 minute moving average against the raw inputs for p1

### Task 3

**Create a single RESTful endpoint in Flask for delivering spwx data:**

Download https://services.swpc.noaa.gov/json/rtsw/rtsw_mag_1m.json to form a SQLite3 table.
Have the endpoint use query string to allow you to select a time period of up to an hour. Where the data is grouped into periods of 5 minute averages and returned via json.

### Task 4

**Kerbal mission:**

Create a rocket in the Kerbal Space Program and have it dock with the International Space Station. Look online for help tutorials and videos. Send a video or screenshot of your spacecraft after you have done it successfully.


# Notes

### Compiling

Before trying to compile my code, run this to install all dependencies:

> pip install -r requirements.txt

### Running my code

**Challenge 1**

1. Simply run:

> python challenge1.py

**Challenge 2**

1. Simply run:

>python challenge2.py

**Challenge 3**

1. Run:

>python challenge3.py

2. Go to the locally hosted URL (e.g. http://127.0.0.1:5000).
3. Input a time window and select enter.
4. A json of 5-minute averages should be returned to you.

