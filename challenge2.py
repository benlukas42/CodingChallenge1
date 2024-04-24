import pandas as pd
import matplotlib.pyplot as plt
import json

filepath = "./differential-protons-1-day.json"

'''
Helper function for plotData.
'''
def getP1andMovingAvg(dataframe):

    # Create a new column movingAvg in the pandas Dataframe
    windowSize = 4 # We're doing a 20-minute moving average, measurements are each 5 minutes
    dataframe['movingAvg'] = dataframe['flux'].rolling(window=windowSize).mean()

    # Create a new dataframe that only includes P1 channel rows
    p1_predicate = dataframe['channel'] == 'P1'
    raw = dataframe[p1_predicate]

    return raw


'''
Plots the raw data of the P1 channel against the 20-minute moving average
    for a given pandas dataframe.
X-axis of the resulting plot is the time_tag column, y-axis is the flux column.
'''
def plotData(dataframe):

    # Get P1 raw dataframe, and set movingAvg column of the original dataframe
    p1_raw = getP1andMovingAvg(dataframe)

    # Plot the P1 raw data and the movingAvg data on the same plot
    plt.plot(p1_raw['time_tag'], p1_raw['flux'], label='P1')
    plt.plot(dataframe['time_tag'], dataframe['movingAvg'], label='movingAvg')

    # Style the plot
    plt.xlabel('time_tag')
    plt.ylabel('flux')
    plt.title('P1 Flux vs. 20-Min Moving Avg')
    plt.legend()

    # Show the plot
    plt.show()

    return


def main():
    with open(filepath, "r") as file:
        data = json.load(file)
        frame = pd.DataFrame(data)
        plotData(frame)
    pass

if __name__ == '__main__':
    main()

