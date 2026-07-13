class UserAlreadyExistsError(Exception):
    """Base exception for duplicate users."""


class UserNameAlreadyExistsError(UserAlreadyExistsError):
    pass


class UserEmailAlreadyExistsError(UserAlreadyExistsError):
    pass


class UserNotFoundError(Exception):
    pass


class UserForbiddenError(Exception):
    pass


class UserAuthorizationError(Exception):
    pass


class UserInvalidData(Exception):
    def __init__(self, field: str, reason: str):
        self.field = field
        self.reason = reason
        super().__init__(f"{field}: {reason}")
