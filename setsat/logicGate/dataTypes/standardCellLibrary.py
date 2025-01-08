from enum import Enum, auto


class CellTechnology_e(Enum):
    '''Cell technology enumeration'''
    BICMOS_IHP_130_NANOMETERS  = 0

    CMOS_NANGATE_15_NANOMETERS = auto()
    CMOS_NANGATE_45_NANOMETERS = auto()

    #FINFET = auto()

class StandardCellLibrary_t():
    ''' Standard Cell Library supported '''
    
    def __init__(self, cellTechnology_e: CellTechnology_e) -> None:
    
        match cellTechnology_e:
            case CellTechnology_e.BICMOS_IHP_130_NANOMETERS:
                self.activeDiffusionLayerList   = [1]
                self.connectorLayerList         = [6]
                self.connectorExtendedLayerList = []
                self.connectorMetalLayerList    = []
                self.metalLayerList             = [8]
                self.polyLayerList              = [5]
            case CellTechnology_e.CMOS_NANGATE_15_NANOMETERS:
                self.activeDiffusionLayerList   = [1]
                self.connectorLayerList         = [14]
                self.connectorExtendedLayerList = [12]
                self.connectorMetalLayerList    = [17]
                self.metalLayerList             = [15, 16, 18, 23]
                self.polyLayerList              = [7, 8, 13]
            case CellTechnology_e.CMOS_NANGATE_45_NANOMETERS:
                self.activeDiffusionLayerList   = [1]
                self.connectorLayerList         = [10]
                self.connectorExtendedLayerList = []
                self.connectorMetalLayerList    = []
                self.metalLayerList             = [11]
                self.polyLayerList              = [9]
            case _:
                raise ValueError('Invalid "CellTechnology_e" value')


######################################
### @Author: Mateus Estrêla Pietro ###
######################################