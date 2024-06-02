from gdstk import Polygon

from setsat.dataTypes.componentID_e   import ComponentID_e 
from setsat.dataTypes.logicGateNode_t import LogicGateNode_t

class PolygonLabel_t:
    def __init__(self, polygon: Polygon, label: str|None, componentID: ComponentID_e) -> None:
        self.componentID = componentID
        self.label       = label
        self.polygon     = polygon
    
    def __repr__(self) -> str:
        return f'{self.componentID.name}-{self.label}'

    def __lt__(self, other):
        if type(other) == LogicGateNode_t:
            return True
        
        prioritySelf  = self.__GetPriorityToPQ(self.componentID)
        priorityOther = self.__GetPriorityToPQ(other.componentID)
        
        return prioritySelf < priorityOther

    def __GetPriorityToPQ(self, componentID: ComponentID_e) -> int:
        match componentID:
            case ComponentID_e.POLY:
                return 0
            case ComponentID_e.METAL:
                return 1
            case ComponentID_e.CONNECTOR:
                return 2

######################################
### @Author: Mateus Estrêla Pietro ###
######################################