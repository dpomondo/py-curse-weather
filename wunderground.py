# file: wunderground.py
import classWeather
import curse_weather
import time


class Wunderground(classWeather.WeatherGetter):
    """ Here be the one what gets us done
    """
    def __init__(self, name, url, api='', params={},
                 req_keys={}, verbose=False):
        """ Creates a dictionary for storing text stuff, then calls
        CurseDisplay __init__
        """
        self.verbose = verbose
        if self.verbose:
            print("Initializing Wunderground instance...")
        self.display_fuctions = []
        classWeather.WeatherGetter.__init__(self, name, url,
                                            api, params, req_keys)

    def DISPLAY_temp(self):
        """ Here be the first time we actually do some stuff from the internet!
        """
        res, color = [], []
        text = "Current temperature:"
        res.append("{}{:>5}".format(
            text, self.return_term('temp_in_fahr')))
        color.append("{}{}".format('0' * len(text), '6' * 5))
        res.append("Wind: {}".format(self.return_term('wind_string')))
        color.append('0' * len(res[1]))
        res.append("Current time: {}".format(time.asctime()))
        color.append('0' * len(res[2]))
        res.append("")
        color.append("")
        res.append("{}".format(self.return_term('observation_time')))
        color.append('0' * len(res[-1]))
        txt1 = "Request time: "
        tmp = time.asctime(time.localtime(self.last_query))
        res.append("{}{}".format(txt1, tmp))
        color.append("{}{}".format('0' * len(txt1), '4' * len(tmp)))
        txt1, txt2 = "Connection is ", "seconds old"
        tmp = int(time.time()) - self.last_query
        res.append("{}{:<5}{}".format(txt1, tmp, txt2))
        color.append("{}{}{}".format(
            '0' * len(txt1), '6' * 5, '0' * len(txt2)))
        res.append("time out length: {}".format(self.time_out))
        color.append('2' * len(res[-1]))
        return res, color

    def request_next(self):
        """ Exists to get overloaded... again!
        """
        # is this really the best place to put this?
        self.get_response()
        if len(self.display_fuctions) == 0:
            self.display_fuctions.append(self.DISPLAY_temp)
        words, color_mask = self.display_fuctions[0]()
        return words, color_mask


class Wunderground_Curse(Wunderground, curse_weather.Texterizer):
    def __init__(self, name, url, api='', params={}, req_keys={},
                 verbose=False, timer=1, random_flag=False):
        Wunderground.__init__(self, name, url, api, params,
                              req_keys, verbose)
        curse_weather.Texterizer.__init__(self, timer, random_flag)


def make_instance():
    url = 'api.wunderground.com'
    api = '32a3b46b738a7f0a'
    features = 'conditions/hourly/astronomy'
    query = '80521'
    format_ = 'json'

    if __name__ == '__main__':
        wunder = Wunderground_Curse('wunderground', url, api=api, 
                                    req_keys={'features': features, 
                                              'query': query, 
                                              'format': format_},
                                    verbose=True)
    else:
        wunder = Wunderground('wunderground', url, api=api, 
                              req_keys={'features': features, 
                                        'query': query, 
                                        'format': format_}, 
                              verbose=True)
    # here we make the thing!
    wunder.set_time_out(300)
    wunder.set_new_term('temp_in_fahr', ['current_observation', 'temp_f'])
    wunder.set_new_term('wind_string', ['current_observation', 'wind_string'])
    wunder.set_new_term('observation_time',
                        ['current_observation', 'observation_time'])
    wunder.get_response()
    return wunder


if __name__ == '__main__':
    wunder = make_instance()
    try:
        wunder.init_sceen()
        wunder.main_draw()
    except Exception as E:
        raise E
    finally:
        wunder.kill_screen()
        wunder.end_program()
