import sys, requests
import curses
import time
import basic_weather


class CurseDisplay():
    """
    An object to be called by curse.wrapper, displays lists of lines.

    This object is the superclass of an object which will fetch, format and
    packages lists of lines. CurseDisplay will then loop through and display
    them. Requests for a new display list will be on a timer; requests for
    updates to the subclass objects, and the logic of which possible package
    will be displayed next, will be done by the next lower subclass.
    """

    def __init__(self, stdscr, timer=30, random_flag=False):
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
        # The following will be initialized here, and toggles in other modules
        self.loop_flag = True
        # These get initialized here and used in other modules
        self.maxy, self.maxx = self.stdscr.getmaxyx()
        self.xmargin = min(10, int(self.maxx / 8))
        self.ymargin = min(10, int(self.maxy / 8))

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
        # curses.init_pair(13
        # curses.init_pair(14
        # curses.init_pair(15
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
        return _res

    def parse_key(self, key):
        """ also exists to get overloaded
        """
        if key in "Qq":
            self.loop_flag = False

    def main_draw(self):
        """
        Where the magic happens
        """
        self.stdscr.clear()
        curses.curs_set(0)
        self.prev_draw_time = time.time() - self.timer  # prime the draw func!

        while self.loop_flag:
            # This loop is currently BUSTED and needs fixing
            if time.time() > self.prev_draw_time + self.timer:
                self.display_list = self.request_next()
                if len(self.display_list) > (self.maxy -
                                             2 * self.ymargin):
                    self.display_list[:self.maxy - (2 * self.ymargin)]
                c_index = 0
                for index in range(len(self.display_list)):
                    self.stdscr.addnstr(
                        self.ymargin + index,
                        self.xmargin,
                        self.display_list[index],
                        self.maxx - (2 * self.xmargin),
                        curses.color_pair(c_index))
                    c_index += 1
                self.prev_draw_time = time.time()
                self.stdscr.refresh()
                key = self.stdscr.getkey()
                self.parse_key(key)


def main(stdscr):
    """ Main loop, called by wrapper(main) imported from curses.
        """
    this_window = CurseDisplay(stdscr)
    this_window.main_draw()


if __name__ == '__main__':
    curses.wrapper(main)
