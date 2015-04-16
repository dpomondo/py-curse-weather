import classWeather

owm_dict = {'id': 5577147,
            'APPID': '821372fd828a41557654cd601c66fc35'
            }

owm_url = 'api.openweathermap.org/data/2.5/weather'

owm = classWeather.WeatherGetter('openWeatherMap', url=owm_url,
                                 params=owm_dict)


owm.set_time_out(600)
owm.set_new_term('temp', ['main', 'temp'])
owm.set_derived_term('temp_in_fahr', 'temp', owm.parse_term,
                     owm.kelvin_to_celsius, owm.celsius_to_fahr)
