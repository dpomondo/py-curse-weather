import sys
import time
import requests


class WeatherGetter():
    """
    A general class for getting weather data from the internet using
    site-specific APIs.
    """
    def __init__(self, name, url, api='', params={}, req_keys={}):
        # Debugging line
        if self.verbose:
            print("Initializing WeatherGetter instance...")
        self.name = name
        self.url = url
        self.api = api
        self.params = params
        if len(req_keys) > 0:
            self.req_keys = req_keys
        else:
            self.req_keys = {'features': '',
                             'settings': '',
                             'query': '',
                             'format': ''
                             }
        # self.basic_terms is a dictionary containing WHAT can get pulled from
        # the .json data, with a route to that data. self.derived_terms is
        # a dictionary of terms which can be massaged from the raw .json
        self.basic_terms = {}
        self.derived_terms = {}
        self.old_response = {}
        self.current_response = {}
        # self.last_query is in the format returned by time.time() -- that is,
        # seconds since the epoch. self.time_out is expressed in seconds
        self.last_query = 0
        self.time_out = False
        # here be the debugging flag!
        self.error = True
        self.bad_attempts = 0
        self.bad_attemps_total = 0
        self.good_attempts = 0

    def make_url(self):
        if not self.url.startswith('http://'):
            res = "{}{}".format("http://", self.url)
        else:
            res = self.url
        if self.req_keys.get('query', None):
            if self.req_keys.get('settings', None):
                res = "{}/api/{}/{}/{}/q/{}.{}".format(
                    res,
                    self.api,
                    self.req_keys['features'],
                    self.req_keys['settings'],
                    self.req_keys['query'],
                    self.req_keys['format']
                )
            else:
                res = "{}/api/{}/{}/q/{}.{}".format(
                    res,
                    self.api,
                    self.req_keys['features'],
                    self.req_keys['query'],
                    self.req_keys['format']
                )
        return res

    def get_response(self):
        """ Fill the self.current_response object with the .json returned
        from the website
        """
        if self.verbose:
            print("Getting response from the server...")
        if self.time_out:
            if self.response_age() < self.time_out:
                if self.error:
                    print("re-query too soon.")
                return
        r = requests.get(self.make_url(), params=self.params)
        self.old_response = self.current_response
        self.last_query = int(time.time())
        self.good_attempts += 1
        if sys.version_info[1] < 4:
            self.current_response = r.json
        else:
            self.current_response = r.json()

    def bad_connection(self):
        """ Called when the connection fails
        """
        res, color = [], []
        res.append("Exception raised: {}".format(self._except))
        color.append("{}{}".format('0' *
                                   (len(res[0]) - len(str(self._except))),
                                   '3' * len(str(self._except))))
        res.append("")
        color.append("")
        txt1, txt2 = "Current response is ", "seconds old"
        tmp = self.response_age()
        res.append("{}{:<5}{}".format(txt1, tmp, txt2))
        color.append("{}{}{}".format(
            '0' * len(txt1), '6' * 5, '0' * len(txt2)))
        res.append("{} attempts made".format(self.bad_attempts))
        color.append("{}{}".format('4' * len(str(self.bad_attempts)),
                     '0' * (len(res[-1]) - len(str(self.bad_attempts)))))
        return res, color

    def response_age(self):
        """ Called to see whenthe last call returned data
        """
        return int(time.time()) - self.last_query

    def set_time_out(self, time_in_seconds):
        """ Set the time between allowable calls to the server.
        """
        self.time_out = time_in_seconds

    def set_new_term(self, term, route):
        """ Generic function for adding new pullable items

        'term' is just a dictionary key
        'route' is a list of further keys used to parse a .json object
        """
        self.basic_terms[term] = route

    def parse_term(self, term):
        """ Helper function for pulling stuff from the response, as long
        as a route has been initialized
        This should NOT be called, it is a helper for return_term
        """
        if term not in self.basic_terms.keys():
            return
        route = self.basic_terms[term]
        if not isinstance(route, list):
            route = list(route)
        res = self.current_response[route[0]]
        route = route[1:]
        while route:
            res = res[route[0]]
            route = route[1:]
        return res

    def convert(self, *args):
        """ worker function for chaining functions

        Steps through the list, applying each subsequent function to the
        result of the previous operation. Feeding a single item returns
        the item.
        """
        initial = args[0]
        rest = args[1:]
        for func in rest:
            initial = func(initial)
        return initial

    def set_derived_term(self, term, *args):
        """ adds to the self.derived_terms a term and its related functions.

        A call of the form:

            set_derived_term('xxxx', 'zzzz', func_a, func_b, func_c)

        will be added as:

            'xxxx': ['zzzz', func_a, func_b, func_c])

        and can be called as return_term('xxxx'):

            func_c(func_b(func_a('zzzz')))

        """
        self.derived_terms[term] = list(args)

    def return_term(self, term):
        """ Returns the current value of term, as scrubbed and cleaned by
        the sequence of functions found in self.derived_terms[term].

        """
        if self.verbose:
            print("Trying to return the value of {}".format(term))
        if term in self.derived_terms.keys():
            return self.convert(*self.derived_terms[term])
        elif term in self.basic_terms.keys():
            return self.parse_term(term)
        else:
            if term in self.current_response.keys():
                if isinstance(self.current_response[term], str):
                    return self.current_response[term]
                else:
                    # THis should be a 'raise key error' but I ain't smart
                    # enough to do that yet
                    if term not in self.current_response.keys():
                        raise KeyError("{} not in response keys".format(term))
                    else:
                        raise KeyError(
                            "{} not part of a key:value pair".format(term))

    def kelvin_to_celsius(self, temp):
        return temp - 273.15

    def celsius_to_fahr(self, temp):
        return round((32.0 + ((temp * 9.0) / 5.0)), 2)
