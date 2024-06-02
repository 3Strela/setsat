from gdstk import Cell, Polygon

from shapely.geometry import Polygon as gPolygon
from shapely.ops      import unary_union

from setsat.dataTypes.componentID_e       import ComponentID_e
from setsat.dataTypes.logicGatePolygons_t import LogicGatePolygons_t
from setsat.dataTypes.polygonLabel_t      import PolygonLabel_t
from setsat.dataTypes.standardCellLibrary import StandardCellLibrary_t

import matplotlib.pyplot as plt

################################################
### +++++++++++ PUBLIC FUNCTIONS +++++++++++ ###
################################################

def ExtractInterestLayerPolygons(cell: Cell, cellLibrary: StandardCellLibrary_t) -> LogicGatePolygons_t:
    activeDiffusionPolygonList   = __ExtractAndMergeComponentPolygonList(cell, cellLibrary, ComponentID_e.ACTIVE_DIFFUSION)
    connectorExtendedPolygonList = __ExtractComponentPolygonList(cell, cellLibrary, ComponentID_e.CONNECTOR_EXTENDED)

    connectorPolygonList      = __ExtractComponentPolygonList(cell, cellLibrary, ComponentID_e.CONNECTOR)
    connectorMetalPolygonList = __ExtractComponentPolygonList(cell, cellLibrary, ComponentID_e.CONNECTOR_METAL)
    metalPolygonList          = __ExtractAndMergeComponentPolygonList(cell, cellLibrary, ComponentID_e.METAL)
    polyPolygonListMerged     = __ExtractAndMergeComponentPolygonList(cell, cellLibrary, ComponentID_e.POLY)

    metalPolygonListMerged = __MergeMetalAndConnectorMetal(metalPolygonList, connectorMetalPolygonList)

    metalPolygonLabelList     = __LabelMetalPolygonList(cell, metalPolygonListMerged, polyPolygonListMerged)
    connectorPolygonLabelList = __LabelConnectorPolygonList(connectorPolygonList, metalPolygonLabelList)
    polyPolygonLabelList      = __LabelPolyPolygonList(polyPolygonListMerged, connectorPolygonLabelList, 
                                                       connectorExtendedPolygonList)

    # fig, ax = plt.subplots()
    # for polygonLabel in metalPolygonLabelList:
    #     x = [p[0] for p in polygonLabel.polygon.points]
    #     y = [p[1] for p in polygonLabel.polygon.points]
    #     ax.plot(x, y)
    # plt.show()

    logicGatePolygons = LogicGatePolygons_t()
    logicGatePolygons.AddComponent(activeDiffusionPolygonList  , ComponentID_e.ACTIVE_DIFFUSION)
    logicGatePolygons.AddComponent(connectorPolygonLabelList   , ComponentID_e.CONNECTOR)
    logicGatePolygons.AddComponent(connectorExtendedPolygonList, ComponentID_e.CONNECTOR_EXTENDED)
    logicGatePolygons.AddComponent(metalPolygonLabelList       , ComponentID_e.METAL)
    logicGatePolygons.AddComponent(polyPolygonLabelList        , ComponentID_e.POLY)

    return logicGatePolygons

#################################################
### +++++++++++ PRIVATE FUNCTIONS +++++++++++ ###
#################################################

def __ExtractComponentPolygonList(cell: Cell, cellLibrary: StandardCellLibrary_t,
                                  componentID: ComponentID_e) -> list[Polygon]:
    componentLayer = None
    match componentID:
        case ComponentID_e.ACTIVE_DIFFUSION:
            componentLayer = cellLibrary.activeDiffusionLayerList
        case ComponentID_e.CONNECTOR:
            componentLayer = cellLibrary.connectorLayerList
        case ComponentID_e.CONNECTOR_EXTENDED:
            componentLayer = cellLibrary.connectorExtendedLayerList
        case ComponentID_e.CONNECTOR_METAL:
            componentLayer = cellLibrary.connectorMetalLayerList
        case ComponentID_e.METAL:
            componentLayer = cellLibrary.metalLayerList
        case ComponentID_e.POLY:
            componentLayer = cellLibrary.polyLayerList
    
    componentPolygonList = []
    for polygon in cell.get_polygons():
        if polygon.layer in componentLayer:
            componentPolygonList.append(polygon)
    
    return componentPolygonList

def __ExtractAndMergeComponentPolygonList(cell: Cell, cellLibrary: StandardCellLibrary_t, \
                                          componentID: ComponentID_e) -> list[Polygon]:
    componentLayer = None
    match componentID:
        case ComponentID_e.ACTIVE_DIFFUSION:
            componentLayer = cellLibrary.activeDiffusionLayerList
        case ComponentID_e.CONNECTOR:
            componentLayer = cellLibrary.connectorLayerList
        case ComponentID_e.CONNECTOR_EXTENDED:
            componentLayer = cellLibrary.connectorExtendedLayerList
        case ComponentID_e.CONNECTOR_METAL:
            componentLayer = cellLibrary.connectorMetalLayerList
        case ComponentID_e.METAL:
            componentLayer = cellLibrary.metalLayerList
        case ComponentID_e.POLY:
            componentLayer = cellLibrary.polyLayerList
    
    if len(componentLayer) == 0:
        return []
    
    componentPolygonByLayer = {}
    componentPolygonList = []
    for polygon in cell.get_polygons():
        if polygon.layer in componentLayer:
            if polygon.layer not in componentPolygonByLayer:
                componentPolygonByLayer[polygon.layer] = []

            componentPolygonByLayer[polygon.layer].append(gPolygon(polygon.points))
            componentPolygonList.append(gPolygon(polygon.points))
    
    componentPolygonListMerged = []
    match componentID:
        case ComponentID_e.METAL:
            for layer in componentPolygonByLayer:
                if len(componentPolygonByLayer[layer]) == 1:
                    componentPolygonListMerged.append((componentPolygonByLayer[layer][0], layer))
                else:
                    for polygonMerged in list(unary_union(componentPolygonByLayer[layer]).geoms):
                        componentPolygonListMerged.append((polygonMerged, layer))
        case _:
            if len(componentPolygonList) == 1:
                componentPolygonListMerged = componentPolygonList
            else:
                componentPolygonListMerged = list(unary_union(componentPolygonList).geoms)

    # print(componentID.name)
    # fig, ax = plt.subplots()
    # for polygon in componentPolygonListMerged:
    #     x, y = polygon.exterior.xy
    #     ax.plot(x, y)
    # plt.show()

    componentPolygonList = []
    for componentPolygon in componentPolygonListMerged:
        if type(componentPolygon) == tuple:
            pointList = [point for point in list(componentPolygon[0].exterior.coords)]
            componentPolygonList.append(Polygon(pointList, componentPolygon[1]))
        else:
            pointList = [point for point in list(componentPolygon.exterior.coords)]
            componentPolygonList.append(Polygon(pointList))

    return componentPolygonList

def __LabelConnectorPolygon(connectorPolygon: Polygon, metalPolygonLabelList: list[PolygonLabel_t]) -> str | None:
    connectorGPolygon = gPolygon(connectorPolygon.points)

    for metalPolygon in metalPolygonLabelList:
        metalGPolygong = gPolygon(metalPolygon.polygon.points)
        if metalGPolygong.intersects(connectorGPolygon):
            return metalPolygon.label
        
def __LabelConnectorPolygonList(connectorPolygonList: list[Polygon],
                                metalPolygonLabelList: list[PolygonLabel_t]) -> list[PolygonLabel_t]:
    connectorPolygonLabelList = []; countConnectors = 0
    for connectorPolygon in connectorPolygonList:
        label = __LabelConnectorPolygon(connectorPolygon, metalPolygonLabelList)
        
        label += '_con_' + str(countConnectors).zfill(3)
        countConnectors += 1

        connectorPolygonLabelList.append(PolygonLabel_t(connectorPolygon, label, ComponentID_e.CONNECTOR))
    
    return connectorPolygonLabelList

def __LabelMetalPolygon(cell: Cell, metalPolygon: Polygon, polyPolygonList: list[Polygon]) -> str:
    for label in cell.get_labels():
        if label.layer == metalPolygon.layer and metalPolygon.contain_any(label.origin):
            return label.text
    
    for polyPolygon in polyPolygonList:
        if metalPolygon.contain_any(*polyPolygon.points):
            return 'net_'
        
    return 'met_'

def __LabelMetalPolygonList(cell: Cell, metalPolygonList: list[Polygon], 
                            polyPolygonList: list[Polygon]) -> list[PolygonLabel_t]:
    metalPolygonLabelList = []; countNet = 0; countMet = 0
    for metalPolygon in metalPolygonList:
        label = __LabelMetalPolygon(cell, metalPolygon, polyPolygonList)
        
        match label:
            case 'met_':
                label += str(countMet).zfill(3)
                countMet += 1
            case 'net_':
                label += str(countNet).zfill(3)
                countNet += 1

        metalPolygonLabelList.append(PolygonLabel_t(metalPolygon, label, ComponentID_e.METAL))
    
    return metalPolygonLabelList

def __LabelPolyPolygon(polyPolygon: Polygon, connectorPolygonLabelList: list[PolygonLabel_t],
                       connectorExtendedPolygonList: list[Polygon]) -> str | None:
    polyGPolygon = gPolygon(polyPolygon.points)

    for connectorPolygon in connectorPolygonLabelList:
        connectorGPolygon = gPolygon(connectorPolygon.polygon.points)
        if polyGPolygon.intersects(connectorGPolygon):
            return connectorPolygon.label.split('_con_')[0]
    
    for connectorPolygon in connectorPolygonLabelList:
        connectorGPolygon = gPolygon(connectorPolygon.polygon.points)
        for connectorMetalPolygon in connectorExtendedPolygonList:
            connectorMetalGPolygon = gPolygon(connectorMetalPolygon.points)
            if connectorMetalGPolygon.intersects(connectorGPolygon) and \
               polyGPolygon.intersects(connectorMetalGPolygon):  
                return connectorPolygon.label.split('_con_')[0]
        
def __LabelPolyPolygonList(polyPolygonList: list[Polygon],
                           connectorPolygonLabelList: list[PolygonLabel_t],
                           connectorExtendedPolygonList: list[Polygon]) -> list[PolygonLabel_t]:
    polyPolygonLabelList = []
    for polyPolygon in polyPolygonList:
        label = __LabelPolyPolygon(polyPolygon, connectorPolygonLabelList, connectorExtendedPolygonList)
        polyPolygonLabelList.append(PolygonLabel_t(polyPolygon, label, ComponentID_e.POLY))
    
    return polyPolygonLabelList

def __MergeMetalAndConnectorMetal(metalPolygonList: list[Polygon], 
                                  connectorMetalPolygonList: list[Polygon]) -> list[tuple[Polygon, list[int]]]:
    metalPolygonListMerged =[]; gPolygonMerged = {}
    for connectorMetalPolygon in connectorMetalPolygonList:
        connectorMetalGPolygon = gPolygon(connectorMetalPolygon.points)
        for i in range(len(metalPolygonList)):
            for j in range(i+1, len(metalPolygonList)):
                metalPolygon1 = metalPolygonList[i]
                metalPolygon2 = metalPolygonList[j]

                metalGPolygon1 = gPolygon(metalPolygon1.points)
                metalGPolygon2 = gPolygon(metalPolygon2.points)

                if metalGPolygon1.contains(connectorMetalGPolygon) and \
                   metalGPolygon2.contains(connectorMetalGPolygon):
                    metalGPolygonMerged = unary_union([metalGPolygon1, metalGPolygon2])

                    if i not in gPolygonMerged and j not in gPolygonMerged:
                        gPolygonMerged[i] = {
                            'polygonMerged': metalGPolygonMerged,
                            'neighbors': [i, j]
                        }
                        gPolygonMerged[j] = {
                            'polygonMerged': metalGPolygonMerged,
                            'neighbors': [i, j]
                        }
                    else:
                        indexMerged = None; otherIndex = None
                        if i in gPolygonMerged:
                            indexMerged = i; otherIndex = j
                        else:
                            indexMerged = j; otherIndex = i
                        
                        if otherIndex not in gPolygonMerged:
                            gPolygonMerged[otherIndex] = {
                                'polygonMerged': None,
                                'neighbors': None
                            }
                        
                        polygonMerged = unary_union([gPolygonMerged[indexMerged]['polygonMerged'], metalGPolygonMerged])
                        gPolygonMerged[indexMerged]['polygonMerged'] = polygonMerged
                        gPolygonMerged[indexMerged]['neighbors'].append(otherIndex)

                        for neighbor in gPolygonMerged[indexMerged]['neighbors']:
                            if neighbor == i or neighbor == j:
                                continue

                            gPolygonMerged[neighbor]['polygonMerged'] = polygonMerged
                            gPolygonMerged[neighbor]['neighbors'] = gPolygonMerged[indexMerged]['neighbors']
                        
                        gPolygonMerged[otherIndex]['polygonMerged'] = polygonMerged
                        gPolygonMerged[otherIndex]['neighbors'] = gPolygonMerged[indexMerged]['neighbors']

    uniqueGroupOfPolygonMerged = set()
    for key in gPolygonMerged:
        neighbors = list(map(str, gPolygonMerged[key]['neighbors']))
        uniqueGroupOfPolygonMerged.add(' '.join(neighbors))
    
    for group in uniqueGroupOfPolygonMerged:
        firstIndex = int(group.split()[0])

        layerSet = set()
        for index in group.split():
            layerSet.add(metalPolygonList[int(index)].layer)

        pointList = [point for point in list(gPolygonMerged[firstIndex]['polygonMerged'].exterior.coords)]
        polygon   = Polygon(pointList, layer= max(layerSet))

        metalPolygonListMerged.append(polygon)
    
    for i, metalPolygon in enumerate(metalPolygonList):
        if i not in gPolygonMerged:
            metalPolygonListMerged.append(metalPolygon)

    return metalPolygonListMerged

######################################
### @Author: Mateus Estrêla Pietro ###
######################################