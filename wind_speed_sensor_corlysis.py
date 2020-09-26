# Wind speed sensor program
# Sends data to remote InfluxDB of Corlysis
# MVB

import requests
import argparse
from gpiozero import Button
import math
import statistics

# Constants
URL = 'https://corlysis.com:8086/write'
READING_DATA_PERIOD_MS = 5000.0
SENDING_PERIOD = 3 # Send a batch of data to Influx every SENDING_PERIOD times
MAX_LINES_HISTORY # Size of buffer if no connection to DB?

wind_count = 0      # global count for amount of rotations of wind speed sensor
wind_interval = 5   # amount of rotations is summed over this time interval ins to calculate wind speed
interval = 20       # interval over which the wind speed is averaged and from which 1 gust value is calculated

def spin():
    # increases wind_count with 1 per half rotation of wind speed sensor
    global wind_count
    wind_count = wind_count + 1

def calculate_speed(time_sec):
    # calculate the wind speed in km/h
    global wind_count
    rotations = wind_count / 2.0
    speed = rotations * 2.4 / time_sec # Data sheet of anemometer specifies 1 rotation per sec equals 2.4km/h

    return speed;

def reset_wind():
    # Reset reset_wind to 0
    global wind_count
    wind_count = 0

wind_speed_sensor = Button(5) # make Class Button
wind_speed_sensor.when_pressed = spin # when input 5 is activated run spin()

def main():
    corlysis_params = {"db": "weather", "u": "token", "p":"7b1b40d86663ea6242f515abe3adfb5e", "precision": "ms"}
    counter = 1
    problem_counter = 0

    #infinite loop
    while True:
        unix_time_ms = int(time.time()*1000)
        store_speeds = [] # create list to store wind speed values every log interval

        # read sensor data and convert it to line protocol
        start_time = time.time()
        while time.time() <= start_time + interval: # loop over logging interval
            wind_start_time = time.time()
            while time.time() <= wind_start_time + wind_interval:
                reset_wind()
                time.sleep(wind_interval)
                wind_speed_kmh = round(calculated_speed(wind_interval),2)
                wind_speed_ms round(wind_speed_kmh / 3.6, 2) # convert from km/h to m/s
                sotre_speeds.append(wind_speed_ms)
                print(str(wind_speed_kmh) + " km/h or " + str(wind_speed_ms) + " m/s")

        wind_gust = max(store_speeds)
        wind_speed = statistics.mean(store_speeds)
        print("average wind speed (m/s): " + str(wind_speed_ms))
        print("wind gust (m/s): " + str(wind_gust))
        store_speeds = []

        payload = "sensor_data_2,type=average value={}\n ".format(wind_speed)
        payload += "sensor_data_2,type=gust value={}\n".format(wind_gust)

        if counter % SENDING_PERIOD == 0:
            try:
                # try to send data to cloud
                r= request.post(URL, params=corlysis.params, data=payload)
                print(r)
                if r.status_cod != 204:
                    raise Exception("data not written")
                payload = ""
            except:
                problem_counter +1
                print("cannot write to InfluxDB")
                if problem_counter == MAX_LINES_HISTORY:
                    problem_counter = 0
                    payload = ""
        counter += 1

        # Wait for selected time
        time_diff_ms = int(time.time()*1000) - unix_time_ms
        print(time_diff_ms)
        if time_diff_ms < READING_DATA_PERIOD_MS:
            time.sleep((READING_DATA_PERIOD_MS - time_diff_ms) / 1000.0)

if __name__ == "__main__":
    main()
    
