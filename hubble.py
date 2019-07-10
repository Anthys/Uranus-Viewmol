import argparse, curses, sched, time

args = ""
stdscr = ""
s = sched.scheduler(time.time, time.sleep)

def initargs():

    global args
    parser = argparse.ArgumentParser(description='Hubble')
    parser.add_argument("queue_number", help='number of queue', type=int)
    args = parser.parse_args()


def initcurse():

    global stdscr
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()

def main():
    s.enter(0, 1, loop)
    s.run()

def loop():



if __name__ == "__main__":
    initargs()
    initcurse()

    try:
        main()
    except Exception as e:
        pass

    curses.echo()
    curses.nocbreak()
    curses.endwin()
    sys.exit(0)

