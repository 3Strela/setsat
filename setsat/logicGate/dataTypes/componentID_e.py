from enum import Enum, auto

class ComponentID_e(Enum):
    ACTIVE_DIFFUSION   = 0
    CONNECTOR          = auto()
    CONNECTOR_EXTENDED = auto()
    CONNECTOR_METAL    = auto()
    METAL              = auto()
    NODE               = auto()
    POLY               = auto()

######################################
### @Author: Mateus Estrêla Pietro ###
######################################