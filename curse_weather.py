import sys, requests
import curses
import basic_weather


def main(stdscr, _lines):
    """ Main loop, called by wrapper(main) imported from curses.
        _lines are a list of lines. Displays those lines, up to the
        maximum that will fit on the screen (slicing like so: lines[0:maxy]),
        and truncating those lines horizontally (slicing: line[0:maxx])
        """

    curses.curs_set(False)
    max_x, max_y = stdscr.getmaxyx()

    x_margin = 0
    y_margin = 0

    loop_flag = True
    while loop_flag is True:
        for y_index in range(0, len(_lines)):
            stdscr.addnstr(y_index + y_margin, x_margin, _lines[y_index],
                           max_x - (2 * x_margin))

        stdscr.refresh()
        nerd = stdscr.getch()
        loop_flag = False

if __name__ == '__main__':
    results = basic_weather.get_weather()
    lines = basic_weather.textify(results)
    curses.wrapper(main, lines)
