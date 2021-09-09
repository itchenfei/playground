import sys


class ExitCode3(Exception):

    @staticmethod
    def set_exit_code():
        return 3


class ExitCode4(Exception):

    @staticmethod
    def set_exit_code():
        return 4


class TESTException(ExitCode4):
    """pass"""


def handle_uncaught_exception(exc_type, exc_value, exc_trace):

    old_hook(exc_type, exc_value, exc_trace)

    if isinstance(exc_value, ExitCode3):
        sys.exit(exc_value.set_exit_code())
    if isinstance(exc_value, ExitCode4):
        sys.exit(exc_value.set_exit_code())


print(sys.excepthook)

sys.excepthook, old_hook = handle_uncaught_exception, sys.excepthook
print(old_hook)
print(sys.excepthook)


raise TESTException("test 1")
