# file: curse_weather.py
import curses
import time
import random


class CurseDisplay():
    """
    A gutless superclass, displays lists of lines using curses.

    This object is the superclass of an object which will fetch, format and
    packages lists of lines. CurseDisplay will then loop through and display
    them. Requests for a new display list will be on a timer; requests for
    updates to the subclass objects, and the logic of which possible package
    will be displayed next, will be done by the next lower subclass.
    """

    def __init__(self, timer=1, random_flag=False):
        """
        timer: how often a request for a new display set is made.
        random_flag: passed to the coordinating object, sets whether the
        next item will be random in a sequence.
        """
        # Debugging line
        if self.verbose:
            print("Initializing CurseDisplay instance...")
        # make the window
        self.stdscr = self.init_sceen()
        # TODO: split timer into draw_time and request_timer
        self.draw_timer = timer
        # self.request_timer = None
        self.prev_draw_time = 0    # will be initialized by the main_draw func
        self.random_flag = random_flag
        self.display_list = []  # filled in by the request_next func
        self.color_mask = []
        # The following will be initialized here, and toggles in other modules
        self.loop_flag = True
        # These get initialized here and used in other modules
        self.maxy, self.maxx = self.stdscr.getmaxyx()
        self.xmargin = min(10, int(self.maxx / 8))
        self.ymargin = min(10, int(self.maxy / 8))
        self.init_time = int(time.time())
        self.screen_draws = 0
        self._except = None

        # Here we make the pretty colors!
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_RED)
        curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_BLUE)
        curses.init_pair(11, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
        curses.init_pair(12, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(13, curses.COLOR_RED, curses.COLOR_YELLOW)
        curses.init_pair(14, curses.COLOR_CYAN, curses.COLOR_BLUE)
        curses.init_pair(15, curses.COLOR_YELLOW, curses.COLOR_MAGENTA)
        # curses.init_pair(16

    def init_sceen(self):
        """ Here we make the window
        """
        z = curses.initscr()
        curses.noecho()
        curses.cbreak()
        z.keypad(True)
        curses.start_color()
        return z

    def kill_screen(self):
        """ Here we kill the screen
        """
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()

    def request_next(self):
        """
        This gets overloaded by the coordinating object, one subclass down.
        """
        raise NotImplementedError

    def bad_connection(self):
        """ THis gets overloaded
        """
        raise NotImplementedError

    def parse_key(self, key):
        """ also exists to get overloaded
        """
        if key in "Qq":
            self.loop_flag = False

    def main_draw(self):
        """ Where the magic happens
        """
        curses.curs_set(0)
        self.stdscr.nodelay(1)  # loop properly, getkey is non-blocking
        # prime the draw func!
        self.prev_draw_time = int(time.time()) - self.draw_timer

        while self.loop_flag:
            # Loop was busted because (a) .getch was blocking (i.e. waiting
            # for input) and (b) .getch was INSIDE the time test so it was
            # only responding every 30 seconds
            if time.time() > self.prev_draw_time + self.draw_timer:
                try:
                    self.display_list, self.color_mask = self.request_next()
                    self.bad_attempts = 0
                except Exception as var:
                    self._except = var
                    self.bad_attempts += 1
                    self.bad_attemps_total += 1
                    self.display_list, self.color_mask = self.bad_connection()
                # clear, draw, refresh
                finally:
                    self.stdscr.clear()
                    self.draw_loop()
                    self.screen_draws += 1
                    self.stdscr.refresh()
            # keep input out of the loop!
            key = self.stdscr.getch()
            if key is not -1:
                self.parse_key(chr(key))

    def draw_loop(self):
        """ Where the drawing happens!
        """
        if not self.color_mask:
            for y_index in range(min(len(self.display_list),
                                     self.maxy - (2 * self.ymargin))):
                self.stdscr.addnstr(
                    self.ymargin + y_index,
                    self.xmargin,
                    self.display_list[y_index],
                    self.maxx - (2 * self.xmargin),
                    curses.color_pair(random.randint(0, 15))
                    )
        else:
            # Here we step through as many lines as will fit
            for y_index in range(min(len(self.display_list),
                                     self.maxy - (2 * self.ymargin))):
                # Here we make sure the mask and the text line
                # are the same length
                diff = len(self.color_mask[y_index]) - len(
                    self.display_list[y_index])
                if diff < 0:
                    self.color_mask[y_index] += ('0' * abs(diff))
                # Now we begin to print letter by letter!
                for x_index in range(
                    min(len(self.display_list[y_index]),
                        self.maxx - (2 * self.xmargin))):
                    # self.color_mask is sent as a list of text lines,
                    # where each letter is a hexadecimal number
                    # standing for a curses color pair
                    self.stdscr.addstr(
                        self.ymargin + y_index,
                        self.xmargin + x_index,
                        self.display_list[y_index][x_index],
                        curses.color_pair(int(
                            self.color_mask[y_index][x_index], 16))
                    )

        self.prev_draw_time = int(time.time())
        return

    def end_program(self):
        """ Quitting the program nicely gets a small tidbit of info
        """
        # after curses exits
        print("Program ran for {} seconds.".format(
            int(time.time()) - self.init_time))
        print("{} good and {} bad requests were made.".format(
            self.good_attempts, self.bad_attemps_total))
        print("The screen was drawn {} times.".format(self.screen_draws))


class Texterizer(CurseDisplay):
    """ Layer for returning fetched and formatted text to CurseDisplay.

    Returns lists of text strings, merged with data stored in object(s)
    that gets information from the internet. Acts as a glue layer to allow
    differnt behaviors by adding various specific Getter instances that
    do the actual interfacing with website APIs and packaging the results
    in lists of text strings with the appropriate color masks.
    """
    def __init__(self, timer=30, random_flag=False):
        """ Creates a dictionary for storing text stuff, then calls
        CurseDisplay __init__
        """
        self.display_fuctions = []
        CurseDisplay.__init__(self, timer, random_flag)

    def DISPLAY_basic(self):
        res = []
        res.append("This is a line of text.")
        res.append("This is a test of the curse display function.")
        res.append("This screen is {} by {},".format(
            self.maxx, self.maxy))
        res.append("The maximum viewing area is {} by {}.".format(
            self.maxx - (2 * self.xmargin),
            self.maxy - (2 * self.ymargin)))
        res.append("It is now {}.".format(time.asctime()))
        res.append("Does the window have colors? {}".format(
            str(curses.has_colors())))
        res.append("Can the window change colors? {}".format(
            str(curses.can_change_color())))
        res.append("The window has {} colors and {} color pairs".format(
            str(curses.COLORS), str(curses.COLOR_PAIRS)))
        res.append("self.__dir__() has {} entries".format(len(
            self.__dir__())))
        res.append("")
        return res, []

    def color_randomizer(self, lines):
        """ test function for crazy colors
        """
        res = []
        for lin in lines:
            sub_res = ''
            for char in lin:
                sub_res += random.choice('0123456789abcdef')
            res.append(sub_res)
        return res

    def add_getter(self, getter):
        """ Add a getter instance
        """
        raise NotImplementedError

    def request_next(self):
        """ Called to grab the next text for display.

        TODO:
        self.display_fuctions contains all the functions from all the Getters
        which output formated lines of text. The self.random_flag determines
        whether the functions are stepped through in order or whether they
        are chosen randomly.
        """
        # Killed the following 'cos it seems like they cannot work;
        # it's possible to gather up the NAMES of functions from __dir__()
        # but not a list of CALLABLE functions, so the dream dies
        if len(self.display_fuctions) == 0:
            self.display_fuctions.append(self.DISPLAY_basic)
        words, colors = self.display_fuctions[0]()
        if self.random_flag is False:
            return words, colors
        else:
            return words, self.color_randomizer(words)

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

    def connection_age(self):
        """ Called to see whenthe last call returned data

        Exists to get overloaded
        """
        raise NotImplementedError


def main(stdscr):
    """ Main loop, called by wrapper(main) imported from curses.
        """
    this_window = Texterizer(stdscr, random_flag=False)
    this_window.main_draw()


if __name__ == '__main__':
    curses.wrapper(main)
