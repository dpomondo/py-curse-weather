# file: wunderground.py
import classWeather
import curse_weather
import curses


class Wunderground(classWeather.WeatherGetter,
                   curse_weather.Texterizer):
    """ Here be the one what gets us done
    """
    def __init__(self, name, url, stdscr, api='', params={}, req_keys={},
                 timer=30, random_flag=False, verbose=False):
        """ Creates a dictionary for storing text stuff, then calls
        CurseDisplay __init__
        """
        print("Initializing WUnderground instance...")
        self.display_fuctions = []
        classWeather.WeatherGetter.__init__(self,
                                            name, url, api, params, req_keys)
        curse_weather.Texterizer.__init__(self,
                                          stdscr, timer, random_flag, verbose)

    def DISPLAY_temp(self):
        """ Here be the first time we actually do some stuff from the internet!
        """
        res, color = [], []
        text = "Current temperature:"
        res.append("{} {:>5}".format(
            text, self.parse_term('temp_in_fahr')))
        color.append("{}{}".format('1' * len(text), 'a' * 5))
        return res, color

    def request_next(self):
        """ Exists to get overloaded... again!
        """
        if len(self.display_fuctions) == 0:
            self.display_fuctions.append(self.DISPLAY_temp)
        words, color_mask = self.display_fuctions[0]()
        return words, color_mask


def make_instance(stdscr):
    url = 'api.wunderground.com'
    api = '32a3b46b738a7f0a'
    features = 'conditions/hourly'
    query = '80521'
    format_ = 'json'

    wunder = Wunderground('wunderground', url, stdscr, api=api,
                          req_keys={'features': features,
                                    'query': query,
                                    'format': format_}
                          )
    # here we make the thing!
    wunder.set_new_term('temp_in_fahr', ['current_observation', 'temp_f'])
    wunder.main_draw()


if __name__ == '__main__':
    curses.wrapper(make_instance)
