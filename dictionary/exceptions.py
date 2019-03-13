class NotSupportedExtensionException(Exception):
    def __init__(self, extension):
        self.message = f'Extension {extension} is not supported'
