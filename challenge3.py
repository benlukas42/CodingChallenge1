from flask import Flask, request, jsonify, render_template
import json
import sqlite3

filepath = './rtsw_mag_1m.json'

app = Flask(__name__)
time_period = ("2024-04-24T22:35:00", "2024-04-24T23:35:00")

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

    # Ensure window is only 1 hour max
    if not start['day'] == end['day']:
        if (start['hour'] == 23) and (end['hour'] == 0):
            if (start['minute'] - end['minute'] >= 0):
                # OK
                pass
            else:
                return {'Error message': 'Invalid entry: window of time cannot be >1 hour'}
        else:
            return {'Error message': 'Invalid entry: window of time cannot be >1 hour'}
    if end['hour'] - start['hour'] > 1:
        return {'Error message': 'Invalid entry: window of time cannot be >1 hour'}
    if end['hour'] - start['hour'] == 1:
        if end['minute'] - start['minute'] > 0:
           return {'Error message': 'Invalid entry: window of time cannot be >1 hour'} 
    
    response = queryDatabase(start_time, end_time)

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
