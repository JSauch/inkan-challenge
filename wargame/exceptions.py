class WargameException(Exception):

    message = "An exception occured with the wargame"

    def __init__(self, message):
        super().__init__(message)


class UnitCannotAttackException(WargameException):

    message = "Unit cannot attack for unknown reasons."


class InvalidAttackTargetException(WargameException):

    message = "No valid target for the attack."
