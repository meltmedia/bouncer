import sys
from .ext.config import Configuration, JsonLoader

sys.modules[__name__] = Configuration('bouncer', loader=JsonLoader())
