from gdstk import Polygon

class LogicGateNode_t:
    def __init__(self) -> None:
        self.neighborList   : list[str] = []
        self.nodeID         : str       = None
        self.polygon        : Polygon   = None
        self.typeSource     : str       = None
    
    def __repr__(self) -> str:
        return f'{self.nodeID}|{self.typeSource}'
    
    def __lt__(self, other):
        return False

######################################
### @Author: Mateus Estrêla Pietro ###
######################################