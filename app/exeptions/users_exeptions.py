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