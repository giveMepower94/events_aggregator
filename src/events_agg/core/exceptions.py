class DomainError(Exception):
    pass


class EventNotFoundError(DomainError):
    pass


class TicketNotFoundError(DomainError):
    pass


class EventNotPublishedError(DomainError):
    pass


class RegistrationDeadlinePassedError(DomainError):
    pass


class EventAlreadyStartedError(DomainError):
    pass


class SeatDoesNotExistError(DomainError):
    pass


class SeatNotAvailableError(DomainError):
    pass


class IdempotencyConflictError(DomainError):
    pass


class IdempotencyInProgressError(DomainError):
    pass


class IdempotencyStateError(DomainError):
    pass


class CancellationNotAllowedError(DomainError):
    pass


class ProviderBadRequestError(DomainError):
    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class ProviderError(DomainError):
    pass
