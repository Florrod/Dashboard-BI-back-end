from models import Order

class Wrapper():
    def __init__(integration):
        self.integration = integration,


    def wrap(json) -> Order:
        if self.integration.platform.id == 1:
            wrapper = WrapperJustEat(self.integration)
            return wrapper.wrap(json)
        elif self.integration.platform.id == 2:
            wrapper = WrapperGlovo(self.integration)
        else:
            raise PlatformNotSupported()
        return wrapper.wrap(json)