import sys

from solution.core import read_events

if __name__ == "__main__":
    if sys.argv[1] == "-i":
        with open(sys.argv[2], "r") as input_file:
            events = input_file.read()
    else:
        events = sys.argv[1]

    print(read_events(events))
