# Wind speed sensor program
# Sends data to local MySQL DB
# MVB

from gpiozero import Button
import math
import time
import statistics
import mariadb

mariadb_connection = mariadb.connect(user='pi', password='zonnebril', database='weather')
cursor = mariadb_connection.cursor()
store_speeds = []   # create list to store wind speed values every log interval
wind_count = 0      # global count for amount of rotation of wind speed sensor
wind_interval = 5   # amount of rotations is summed over this time interval in s to calculate wind speed
interval = 600      # interval over which the wind speed is averaged and from which 1 wind gust value is calculated

def spin():
    # increases wind_count with 1 per half rotation of wind speed sensor
    global wind_count
    wind_count = wind_count + 1
    #print("rotations:" + str(wind_count))

def calculate_speed(time_sec):
    # calculate the wind speed in km/h
    global wind_count
    rotations = wind_count / 2.0
    speed = rotations * 2.4 / time_sec # Data sheet of anemometer specifies 1 rotation per sec = 2.4 km/h

    return speed;

def reset_wind():
    # reset wind_count to 0
    global wind_count
    wind_count = 0

wind_speed_sensor = Button(5) # make class Button
wind_speed_sensor.when_pressed = spin # when inut 5 activated run spin()

while True:
    start_time = time.time()
    while time.time() <= start_time + wind_interval: # loop over logging interval
        wind_start_time = time.time()
        while time.time() <= wind_start_time + wind_interval:
            reset_wind()
            time.sleep(wind_interval)
            wind_speed_kmh = round(calculate_speed(wind_interval),2)
            wind_speed_ms = round(wind_speed_kmh/3.6,2) # convert from km/h to m/s
            store_speeds.append(wind_speed_ms)
            print(str(wind_speed_kmh) + " km/h or " + str(wind_speed_ms) + " m/s"

    wind_gust = max(store_speeds)
    wind_speed = statistics.mean(store_speeds)
    store_speeds = []
    sql = "insert into wind(wind_speed, wind_gust_speed, wind_direction) values ('%g', '%g', '%g') %(wind_speed, wind_gust, 0)
    cursor.execute(sql)
    print("wind gust: " + str(wind_gust) + " m/s and average windspeed: " + str(wind_speed) + " ms")
                  
        
