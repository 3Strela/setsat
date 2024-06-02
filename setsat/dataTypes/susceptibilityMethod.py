from enum import Enum, auto

class SusceptibilityMethod_e(Enum):
    ''' Susceptibility Methods supported '''
    SENSITIVE_NODES_BY_INPUT_VECTOR = 0
    SUSCEPTIBILITY_BY_INPUT_VECTOR  = auto()
    PROBABILISTIC_TRANSFER_MATRIX   = auto() # Layout-method from doi=10.1109/ITC44778.2020.9325252
    #other = auto()


######################################
### @Author: Mateus Estrêla Pietro ###
######################################