from gdstk import Polygon

from setsat.logicGate.dataTypes.componentID_e   import ComponentID_e
from setsat.logicGate.dataTypes.logicGateNode_t import LogicGateNode_t
from setsat.logicGate.dataTypes.polygonLabel_t  import PolygonLabel_t

class LogicGatePolygons_t:
    def __init__(self,) -> None:
        self.activeDiffusionPolygonList  : list[Polygon]         = None
        self.connectorPolygonLabelList   : list[PolygonLabel_t]  = None
        self.connectorExtendedPolygonList: list[Polygon]         = None
        self.metalPolygonLabelList       : list[PolygonLabel_t]  = None
        self.logicGateNodePolygonList    : list[LogicGateNode_t] = None
        self.polyPolygonLabelList        : list[PolygonLabel_t]  = None

    def AddComponent(self, componentList: list[Polygon|PolygonLabel_t|LogicGateNode_t], \
                     componentID: ComponentID_e) -> None:
        if len(componentList) == 0 and componentID != ComponentID_e.CONNECTOR_EXTENDED:
            raise ValueError(f'Cell with insufficient layer "{componentID.name}" values')
        
        match componentID:
            case ComponentID_e.ACTIVE_DIFFUSION:
                self.activeDiffusionPolygonList   = componentList
            case ComponentID_e.CONNECTOR:
                self.connectorPolygonLabelList    = componentList
            case ComponentID_e.CONNECTOR_EXTENDED:
                self.connectorExtendedPolygonList = componentList
            case ComponentID_e.METAL:
                self.metalPolygonLabelList        = componentList
            case ComponentID_e.NODE:
                self.logicGateNodePolygonList     = componentList
            case ComponentID_e.POLY:
                self.polyPolygonLabelList         = componentList

######################################
### @Author: Mateus Estrêla Pietro ###
######################################