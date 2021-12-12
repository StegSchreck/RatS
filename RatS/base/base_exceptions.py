class RatSException(Exception):
    pass


class LoginFailedException(RatSException):
    pass


class CaptchaPresentException(LoginFailedException):
    pass


class CSVDownloadFailedException(RatSException):
    pass


class NoValidCredentialsException(RatSException):
    pass


class SiteNotReachableException(RatSException):
    pass

class NoMoviesForInsertion(LoginFailedException):
    pass
