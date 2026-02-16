class BusinessException(Exception):
    """
    Biznes xatolik uchun custom exception
    """

    def __init__(self, message):
        self.message = message
        super().__init__(message)
