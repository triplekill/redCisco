GlobalCommandRegistry = {}


class CommandRegistry:
    """Class to register classes on creation"""

    def __init__(self, cls):
        GlobalCommandRegistry[cls.__name__] = cls
