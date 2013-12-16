import atexit
import sys


def ex(a):
	print a


atexit.register(ex, "hugs")

sys.exit(0)


