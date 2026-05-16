"""Insurance Analytics - Life, P&C, catastrophe modeling, actuarial analysis"""

from .life_actuary import LifeActuary
from .property_casualty import PropertyCasualty
from .catastrophe_model import CatastropheModel

__all__ = [
    "LifeActuary",
    "PropertyCasualty",
    "CatastropheModel"
]
