""" Basic program to get weather data from OpenWeatherMap.org and display
    the temp (converted to F) by printing it
    """

import requests
import time
import sys

owm_dict = {'id': 5577147,
            'APPID': '821372fd828a41557654cd601c66fc35'
            }

owm_url = 'api.openweathermap.org/data/2.5/weather'

prev_time = time.time()


def get_weather(_url=owm_url, p=owm_dict):
    r = requests.get('http://' + _url, params=p)
    if sys.version_info[1] < 4:
        return r.json
    else:
        return r.json()


def get_temp(weather_dict):
    return weather_dict['main']['temp']


def K_to_C(temp):
    return temp - 273.15


def C_to_F(temp):
    return round((32.0 + ((temp * 9.0) / 5.0)), 2)


def print_results(temp, time):
    print("Current temp (in F): {}".format(temp))
    print("Time: {}\n".format(time))


def textify(weather_dict):
    lines = []
    lines.append("Temperature is {} Kelvin".format(
        weather_dict['main']['temp']))
    lines.append("Conditions: {}".format(
        weather_dict['weather'][0]['description']))
    return lines


def loop():
    res = get_weather()
    curr_temp = C_to_F(K_to_C(get_temp(res)))
    curr_time = time.ctime(res['dt'])
    print_results(curr_temp, curr_time)


if __name__ == '__main__':
    loop()
    while True:
        now = time.time()
        if now - 600 > prev_time:
            loop()
        prev_time = now
