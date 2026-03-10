class AppError(Exception):
    """Base class for all controllable errors in the application.
    It inherits from Exception, so it can be `raised` if necessary.
    """

    @property
    def message(self) -> str:
        """Returns a human-readable error message."""
        return "An unexpected error occurred in the application."
