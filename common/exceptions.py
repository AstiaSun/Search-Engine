class NotSupportedExtensionException(Exception):
    def __init__(self, extension):
        self.message = f'Extension {extension} is not supported'


class IncorrectQuery(ValueError):
    def __init__(self, query, position):
        self.message = f'Query "{query}" is incorrect in position {position}'
