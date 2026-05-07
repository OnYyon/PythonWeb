class UserDomainError(Exception):
    """Base error for user domain rules."""


class UserAlreadyExistsError(UserDomainError):
    def __init__(self, field: str) -> None:
        self.field = field
        super().__init__(f"User with this {field} already exists.")


class UserNotFoundError(UserDomainError):
    def __init__(self, user_id: object) -> None:
        self.user_id = user_id
        super().__init__(f"User with id={user_id} not found")

