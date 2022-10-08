import sys


def confirm(question):
    while True:
        response = input(question).lower().strip()

        if not response or response in ("n", "no"):
            return False

        if response in ("y", "yes"):
            return True

        print("Focus, kid! It is either (y)es or (n)o", file=sys.stderr)
