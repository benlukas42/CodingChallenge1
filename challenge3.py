'''
Challenge task 3 for Saber Astronautics.
Creates a REST endpoint that gets a time window from the user.
This time window is used to extract data, which is averaged into 5-minute periods
and returned to the user via json.

Author: Ben Lukas
'''

from flask import Flask, request, jsonify, render_template
import json
import sqlite3
import calendar

filepath = './rtsw_mag_1m.json'

app = Flask(__name__)

'''
Represents the REST endpoint.
'''
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        response = getResponse(start_time, end_time)
        return jsonify(response), 200
    else:
        return render_template('index.html')
    

'''
Ensures that a time dictionary is coherent.
'''
def ensureTimeDict(time):
    if time['minute'] >= 60:
        time['minute'] -= 60
        time['hour'] += 1
    if time['hour'] >= 24:
        time['hour'] -= 24
        time['day'] += 1
    if time['day'] > calendar.monthrange(time['year'], time['month'])[1]:
        time['day'] -= calendar.monthrange(time['year'], time['month'])
        time['month'] += 1
    if time['month'] > 12:
        time['month'] -= 12
        time['year'] += 1
    return

'''
Turns a time dictionary into a string.
Structure: 2024-04-23T23:38:00
'''
def stringify(time):
    string = ""
    string += str(time['year'])
    string += '-'
    if(len(str(time['month'])) < 2):
        string += '0'
    string += str(time['month'])
    string += '-'
    if(len(str(time['day'])) < 2):
        string += '0'
    string += str(time['day'])
    string += 'T'
    if(len(str(time['hour'])) < 2):
        string += '0'
    string += str(time['hour'])
    string += ":"
    if(len(str(time['minute'])) < 2):
        string += '0'
    string += str(time['minute'])
    string += ":"
    if(len(str(time['second'])) < 2):
        string += '0'
    string += str(time['second'])

    return string

'''
Groups data into periods of 5-minute averages.
'''
def groupAndAvg(start, minutes):
    response = []

    cycles = int(minutes / 5)

    # Run this at least once
    if cycles == 0:
        cycles += 1

    for i in range(0, cycles):
        start_thresh = i * 5
        end_thresh = start_thresh + 5
        # end thresh can't be higher than minutes
        if end_thresh > minutes:
            end_thresh = minutes

        start_time_dict = {
            'year': start['year'],
            'month': start['month'],
            'day': start['day'],
            'hour': start['hour'],
            'minute': start['minute'] + start_thresh,
            'second': start['second']
        }
        ensureTimeDict(start_time_dict)

        end_time_dict = {
            'year': start['year'],
            'month': start['month'],
            'day': start['day'],
            'hour': start['hour'],
            'minute': start['minute'] + end_thresh,
            'second': start['second']
        }
        ensureTimeDict(end_time_dict)

        start_time_string = stringify(start_time_dict)
        end_time_string = stringify(end_time_dict)

        query = queryDatabase(start_time_string, end_time_string)
        
        ## Get the average of query, add that to response
        sums = {}
        counts = {}
        for item in query:
            for key, value in item.items():
                if isinstance(value, (int, float)):
                    sums[key] = sums.get(key, 0) + value
                    counts[key] = counts.get(key, 0) + 1

        averages = {key: sums[key] / counts[key] for key in sums}
        averages['time_tag_start'] = start_time_string
        averages['time_tag_end'] = end_time_string

        response.append(averages)

        continue

    print(response)
    return response

'''
Creates a response given a start and end time.
Returns an error if the start and end time are inappropriate.
'''
def getResponse(start_time, end_time):

    # Structure: 2024-04-23T23:38:00

    # Check for basic violations
    if end_time < start_time:
        return {'Error message': 'Invalid entry: Start time is later than end time'}
    if len(end_time) < 19 or len(start_time) < 19:
        return {'Error message': 'Invalid entry: time must be formatted like "2024-04-23T23:38:00" (yyyy-mm-ddThh:mm:ss)'}

    # Form structs for easier manipulation
    start = {
        'year': int(start_time[0:4]),
        'month': int(start_time[5:7]),
        'day': int(start_time[8:10]),
        'hour': int(start_time[11:13]),
        'minute': int(start_time[14:16]),
        'second': int(start_time[17:])
    }
    end = {
        'year': int(end_time[0:4]),
        'month': int(end_time[5:7]),
        'day': int(end_time[8:10]),
        'hour': int(end_time[11:13]),
        'minute': int(end_time[14:16]),
        'second': int(end_time[17:])
    }
    difference = {
        'year': end['year'] - start['year'],
        'month': end['month'] - start['month'],
        'day': end['day'] - start['day'],
        'hour': end['hour'] - start['hour'],
        'minute': end['minute'] - start['minute'],
        'second': end['second'] - start['second']
    }
    # Fix difference
    if difference['month'] < 0 and difference['year'] > 0:
            difference['year'] -= 1
            difference['month'] += 12
    if difference['day'] < 0 and difference['month'] == 1:
        day_count = calendar.monthrange(start['year'], start['month'])[1]
        if start['day'] == day_count and end['day'] == 1:
            difference['month'] = 0
            difference['day'] = 1
    if difference['hour'] < 0 and difference['day'] > 0:
            difference['day'] -= 1
            difference['hour'] += 24
    if difference['minute'] < 0 and difference['hour'] > 0:
            difference['hour'] -=  1
            difference['minute'] += 60

    # Ensure window is only 1 hour max
    if not difference['day'] == 0:
        if difference['day'] == 1:
            if (start['hour'] == 23) and (end['hour'] == 0):
                if (difference['minute'] <= 0):
                    # OK
                    pass
                else:
                    # A day apart, but more than 60 minutes
                    return {'Error message': 'Invalid entry: window of time cannot be >1 hour'}
            else:
                # A day apart, but more than 1 hour
                return {'Error message': 'Invalid entry: window of time cannot be >1 hour'}
        else:
            # More than a day apart
            return {'Error message': 'Invalid entry: window of time cannot be >1 hour'}
    if difference['hour'] > 1:
        return {'Error message': 'Invalid entry: window of time cannot be >1 hour'}
    if difference['hour'] == 1:
        if difference['minute'] > 0:
           return {'Error message': 'Invalid entry: window of time cannot be >1 hour'} 

    minutes = difference['minute']
    if difference['hour'] == 1:
        minutes += 60

    
    response = groupAndAvg(start, minutes)

    return response


'''
Queries the database for entries between start and end time.
'''
def queryDatabase(start_time, end_time):

    # Connect to the database
    print("Querying database")
    conn = sqlite3.connect('rtsw_mag_1m.db')
    cursor = conn.cursor()

    # Form the query
    select_query = ("""
    SELECT DISTINCT *
    FROM my_table
    WHERE time_tag >= '""" + start_time +
    """' AND time_tag <= '""" + end_time + """'""")

    cursor.execute(select_query)
    rows = cursor.fetchall()
    
    # reconstruct the attribute table
    response = []
    for row in rows:
        response.append({
            'time_tag': row[0],
            'active': row[1],
            'source': row[2],
            'range': row[3],
            'scale': row[4],
            'sensitivity': row[5],
            'manual_mode': row[6],
            'sample_size': row[7],
            'bt': row[8],
            'bx_gse': row[9],
            'by_gse': row[10],
            'bz_gse': row[11],
            'theta_gse': row[12],
            'phi_gse': row[13],
            'bx_gsm': row[14],
            'by_gsm': row[15],
            'bz_gsm': row[16],
            'theta_gsm': row[17],
            'phi_gsm': row[18],
            'max_telemetry_flag': row[19],
            'max_data_flag': row[20],
            'overall_quality': row[21]
        })

    # Commit changes and close cursor
    conn.commit()
    conn.close()

    return response

'''
Creates/initializes the database.
'''
def initDatabase():
    with open(filepath, 'r') as file:
        data = json.load(file)
        # Connect to SQLite database and create cursor
        createTable(data)

    return

'''
Fills out the relation of our new database using the data from filepath.
'''
def createTable(data):
    conn = sqlite3.connect('rtsw_mag_1m.db')
    cursor = conn.cursor()
    
    # Create table
    create_table_query = """
    CREATE TABLE IF NOT EXISTS my_table (
        time_tag TEXT,
        active BOOL,
        source TEXT,
        range FLOAT,
        scale FLOAT,
        sensitivity FLOAT,
        manual_mode BOOL,
        sample_size INTEGER,
        bt FLOAT,
        bx_gse FLOAT,
        by_gse FLOAT,
        bz_gse FLOAT,
        theta_gse FLOAT, 
        phi_gse FLOAT,
        bx_gsm FLOAT,
        by_gsm FLOAT,
        bz_gsm FLOAT,
        theta_gsm FLOAT,
        phi_gsm FLOAT,
        max_telemetry_flag INTEGER,
        max_data_flag INTEGER,
        overall_quality INTEGER
    )
    """

    cursor.execute(create_table_query)

    insert_query = """
    INSERT INTO my_table (
        time_tag,
        active,
        source,
        range,
        scale,
        sensitivity,
        manual_mode,
        sample_size,
        bt,
        bx_gse,
        by_gse,
        bz_gse,
        theta_gse, 
        phi_gse,
        bx_gsm,
        by_gsm,
        bz_gsm,
        theta_gsm,
        phi_gsm,
        max_telemetry_flag,
        max_data_flag,
        overall_quality)
    VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    # Insert data into table
    for item in data:
        cursor.execute(insert_query, (item['time_tag'], item['active'], item['source'], item['range'], 
                       item['scale'], item['sensitivity'], item['manual_mode'], item['sample_size'], 
                       item['bt'], item['bx_gse'], item['by_gse'], item['bz_gse'], item['theta_gse'], 
                       item['phi_gse'], item['bx_gsm'], item['by_gsm'], item['bz_gsm'], item['theta_gsm'],
                       item['phi_gsm'], item['max_telemetry_flag'], item['max_data_flag'], item['overall_quality']))

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print("SQLite table created and data inserted successfully.")

    return

if __name__ == '__main__':

    initDatabase()

    app.run(debug=True)  # Run the Flask application in debug mode
