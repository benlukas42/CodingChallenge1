from flask import Flask, jsonify
import json
import sqlite3

filepath = './rtsw_mag_1m.json'

app = Flask(__name__)
time_period = ("2024-04-24T22:35:00", "2024-04-24T23:35:00")

@app.route('/', methods=['GET'])
def hello_world():
    return "<p>Hello, World!</p>"

# @app.route('/getresource', methods=['GET'])
# def get_resource():
#     data = {'id': 1, 'name': 'Example Resource'}
#     return jsonify(data)  # Return the data as JSON response

def queryDatabase():
    # Connect to the database
    conn = sqlite3.connect('rtsw_mag_1m.db')
    cursor = conn.cursor()

    select_query = ("""
    SELECT time_tag
    FROM my_table
    WHERE time_tag >= '""" + time_period[0] +
    """' AND time_tag <= '""" + time_period[1] + """'""")

    # print(select_query)

    cursor.execute(select_query)
    rows = cursor.fetchall()

    # print("--> Results of query: ")
    # for row in rows:
    #     print(row)
    #     print()

    # Commit changes and close cursor
    conn.commit()
    conn.close()

    return


def openDatabase():
    with open(filepath, 'r') as file:
        data = json.load(file)
        # Connect to SQLite database and create cursor
        createTable(data)

    return

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

    openDatabase()

    queryDatabase()

    app.run(debug=True)  # Run the Flask application in debug mode
