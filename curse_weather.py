# file: curse_weather.py
import curses
import time
import random


class CurseDisplay():
    """
    A gutless superclass, displays lists of lines.

    This object is the superclass of an object which will fetch, format and
    packages lists of lines. CurseDisplay will then loop through and display
    them. Requests for a new display list will be on a timer; requests for
    updates to the subclass objects, and the logic of which possible package
    will be displayed next, will be done by the next lower subclass.
    """

    def __init__(self, stdscr, timer=30, random_flag=False, verbose=False):
        """
        timer: how often a request for a new display set is made.
        random_flag: passed to the coordinating object, sets whether the
        next item will be random in a sequence.
        """
        self.stdscr = stdscr
        self.timer = timer
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
        # THe debugging flag:
        self.verbose = verbose

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

    def request_next(self):
        """
        This gets overloaded by the coordinating object, one subclass down.
        """
        _res = []
        _res.append("This is a test of the curse display function.")
        _res.append("This screen is {} by {},".format(
            self.maxx, self.maxy))
        _res.append("The maximum viewing area is {} by {}.".format(
            self.maxx - (2 * self.xmargin),
            self.maxy - (2 * self.ymargin)))
        _res.append("It is now {}.".format(time.asctime()))
        _res.append("Does the window have colors? {}".format(
            str(curses.has_colors())))
        _res.append("Can the window change colors? {}".format(
            str(curses.can_change_color())))
        _res.append("The window has {} colors and {} color pairs".format(
            str(curses.COLORS), str(curses.COLOR_PAIRS)))
        return _res, []

    def parse_key(self, key):
        """ also exists to get overloaded
        """
        if key in "Qq":
            self.loop_flag = False

    def main_draw(self):
        """ Where the magic happens
        """
        self.stdscr.clear()
        curses.curs_set(0)
        self.stdscr.nodelay(1)  # loop properly, getkey is non-blocking
        self.prev_draw_time = time.time() - self.timer  # prime the draw func!

        while self.loop_flag:
            # Loop was busted because (a) .getch was blocking (i.e. waiting
            # for input) and (b) .getch was INSIDE the time test so it was
            # only responding every 30 seconds
            if time.time() > self.prev_draw_time + self.timer:
                self.display_list, self.color_mask = self.request_next()
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

                self.prev_draw_time = time.time()
                self.stdscr.refresh()
            # keep input out of the loop!
            key = self.stdscr.getch()
            if key is not -1:
                self.parse_key(chr(key))


class Texterizer(CurseDisplay):
    """ Layer for returning fetched, formatted and packaged text.

    Returns lists of text strings, merged with data stored in an object
    that gets information from the internet. Primarily exists to overload
    key functions in CurseDisplay, acts as a glue layer to allow differnt
    behaviors without changing to info object or the display object.
    """
    def __init__(self, stdscr, timer=30, random_flag=False, verbose=False):
        """ Creates a dictionary for storing text stuff, then calls
        CurseDisplay __init__
        """
        self.display_fuctions = []
        CurseDisplay.__init__(self, stdscr, timer, random_flag, verbose)

    def DISPLAY_basic(self):
        res = []
        res.append("This is a line of text.")
        res.append("self.__dir__() has {} entries".format(len(
            self.__dir__())))
        res.append("")
        res.append("The current time is {}".format(
            time.asctime()))
        return res

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

    def request_next(self):
        """ Exists to get overloaded... again!
        """
        # Killed the following 'cos it seems like they cannot work;
        # it's possible to gather up the NAMES of functions from __dir__()
        # but not a list of CALLABLE functions, so the dream dies
        if len(self.display_fuctions) == 0:
            self.display_fuctions.append(self.DISPLAY_basic)
        words = self.display_fuctions[0]()
        if self.random_flag is False:
            return words, []
        else:
            return words, self.color_randomizer(words)


def main(stdscr):
    """ Main loop, called by wrapper(main) imported from curses.
        """
    this_window = Texterizer(stdscr, random_flag=False)
    this_window.main_draw()


if __name__ == '__main__':
    curses.wrapper(main)
