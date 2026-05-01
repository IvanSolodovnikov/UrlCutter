

class ShortenerBaseError(Exception):
    pass


class NoLongUrlFoundError(ShortenerBaseError):
    pass


class SlugAlreadyExistsError(ShortenerBaseError):
    pass

class SlugDoesntExistError(ShortenerBaseError):
    pass

class DatabaseError(ShortenerBaseError):
    pass

class SlugNotAvailableError(ShortenerBaseError):
    pass