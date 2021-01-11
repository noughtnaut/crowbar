import enum


class Socket(enum.Enum):
    """ This defines, in an abstract fashion, where on a Component a Wire is attached.
        Calling `Component.socketPoint(s: Socket)` will return the concrete point, in scene coordinates.
    """
    NONE = 0
    TOP = 1
    RIGHT = 2
    BOTTOM = 3
    LEFT = 4

    # TODO The above represents socket "facing"; for RAS we will need several sockets on the same face,
    # TODO and also socket name, type, order (incl. grouping/spacers), etc.

    def oppositeOf(self, s) -> bool:
        """ Return TRUE if the two sockets are facing in opposite directions (up/down or left/right).
            Does not take into account whether they are facing one-another (they might be facing away).
        """
        if abs(s.value - self.value) == 2:
            return True
        return False


class Mode(enum.Enum):
    """ This defines the usage and appearance of a Wire:
        - NORMAL: This is the default exit path after completing the Component operation.
        - TRUE: Applicable to Conditions, yields the exit path if the condition was TRUE.
        - FALSE: Applicable to Conditions, yields the exit path if the condition was FALSE.
        - ERROR: In case the Component operation caused an error, *only* paths of this mode will be followed.
        Note:
        - If not specified, NORMAL is assumed.
    """
    NORMAL = 0
    TRUE = 1
    FALSE = 2
    ERROR = 4
