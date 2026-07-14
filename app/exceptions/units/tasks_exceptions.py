class TaskNotFoundError(Exception):
    """Raised when a task does not exist or is inactive."""


class TaskAlreadyExistsError(Exception):
    """Raised when a task title already exists within the project."""


class TaskForbiddenError(Exception):
    """Raised when a user is not allowed to modify a task."""


class TaskInvalidDataError(Exception):
    """Raised when task data violates a business rule."""

    def __init__(self, field: str, reason: str):
        self.field = field
        self.reason = reason
        super().__init__(f"{field}: {reason}")
