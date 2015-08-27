"""
Objects we will be working with.
"""


__author__ = 'vance@hackthefed.org'


class Congress(object):
    """
    Congress is currently used only to pass data around may add it's own
    statistics to it later.

    This class has most of it's attributes assigned monkey patch style. As
    much as I hate that it's a fair bit of work to define each, so I'm
    adding them as the parsers are completed.
    """
    name = None
    legislation = None

    def __init__(self, congress):
        print("MAKE CONGRESS")
        print(congress)
        self.name = congress['congress']
