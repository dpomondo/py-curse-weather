import sys
import time
import requests


class WeatherGetter():
    """ 
    A class for getting weather data from the internet using
    site-specific APIs.
    """
    def __init__(self, name, url, params):
        self.name = name
        self.url = url
        self.params = params
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
        self.verbose = False
        self.error = True

    def get_response(self):
        """ Fill the self.current_response object with the .json returned
        from the website
        """
        if self.time_out:
            if time.time() - self.last_query < self.time_out:
                if self.error:
                    print("re-query too soon.")
                return
        r = requests.get('http://' + self.url, params=self.params)
        self.old_response = self.current_response
        self.last_query = time.time()
        if sys.version_info[1] < 4:
            self.current_response = r.json
        else:
            self.current_response = r.json()

    def set_time_out(self, time_in_seconds):
        """ Set the time between allowable calls to the server.
        """
        self.time_out = time_in_seconds

    def set_new_term(self, term, route):
        """ Generic function for adding new pullable items
        """
        self.basic_terms[term] = route

    def parse_term(self, term):
        """ Generic function for pulling stuff from the response, as long
        as a route has been initialized
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

    def set_derived_term(self, term, *funcs):
        """ adds to the self.derived_terms a term and its related functions.

        A call of the form:

            set_derived_term('xxxx', 'zzzz', func_a, func_b, func_c)

        will be added as:

            'xxxx': ['zzzz', func_a, func_b, func_c])

        and can be called as return_term('xxxx'):

            func_c(func_b(func_a('zzzz')))

        """
        self.derived_terms[term] = list(funcs)

    def return_term(self, term):
        """ Returns the current value of term, as scrubbed and cleaned by
        the sequence of functions found in self.derived_terms[term].


        """
        if self.verbose:
            print("Trying to return the value of {}".format(term))
            nerds = self.derived_terms[term]
            print("passing {} to convert function".format(nerds))
        if term in self.derived_terms.keys():
            return self.convert(*self.derived_terms[term])
        else:
            return self.parse_term(term)

    def kelvin_to_celsius(self, temp):
        return temp - 273.15

    def celsius_to_fahr(self, temp):
        return round((32.0 + ((temp * 9.0) / 5.0)), 2)
