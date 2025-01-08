from gdstk import Polygon
from shapely import Polygon as gPolygon

from setsat.logicGate.dataTypes.polygonLabel_t  import PolygonLabel_t
from setsat.logicGate.dataTypes.logicGateNode_t import LogicGateNode_t

import numpy as np

def CalculeCentroidAxisY(activeDiffusionPolygonList: list[Polygon]) -> float:
    activeDiffusionPointList = []
    for polygon in activeDiffusionPolygonList:
        activeDiffusionPointList.append(polygon.points)
    
    activeDiffusionPointArray = np.vstack(activeDiffusionPointList)
    minPoint = np.min(activeDiffusionPointArray, axis=0)
    maxPoint = np.max(activeDiffusionPointArray, axis=0)

    centroidYaxis = (maxPoint[1] + minPoint[1]) / 2
    return centroidYaxis

def CheckMetalLimitYaxis(centroidHeight: float, polygonY: float, sourceLabel: str) -> float|None:
    match sourceLabel:
        case 'VSS':
            return polygonY < centroidHeight
        case 'VDD':
            return polygonY > centroidHeight

def LogicGateInputList(polyPolygonLabelList: list[PolygonLabel_t]) -> list[str]:
    logicGateInputLabel = set()
    
    for poliPolygonLabel in polyPolygonLabelList:
        if poliPolygonLabel.label != None and       \
           poliPolygonLabel.label[0:3] != 'net' and \
           poliPolygonLabel.label[0:3] != 'met':
           logicGateInputLabel.add(poliPolygonLabel.label)

    logicGateInputList = list(logicGateInputLabel)
    logicGateInputList.sort()
    return logicGateInputList

def ConnectorsInMetal(metalPolygonLabel: PolygonLabel_t, \
                      connectorPolygonLabelList: list[PolygonLabel_t]) -> list[PolygonLabel_t]:
    polygonLabelsInMetalList = []
    for polygonLabel in connectorPolygonLabelList:
        if metalPolygonLabel.polygon.contain_any(*polygonLabel.polygon.points):
            polygonLabelsInMetalList.append(polygonLabel)
    
    return polygonLabelsInMetalList

def ConnectorsInSensitiveNode(logicGateNode: LogicGateNode_t, \
                              connectorPolygonLabelList: list[PolygonLabel_t]) -> list[PolygonLabel_t]:
    connectorsInSensitiveNode = []
    for connectorPolygonLabel in connectorPolygonLabelList:
        if logicGateNode.polygon.contain_any(*connectorPolygonLabel.polygon.points):
            connectorsInSensitiveNode.append(connectorPolygonLabel)
    
    return connectorsInSensitiveNode

def MetalFromConnector(connectorPolygonLabel: PolygonLabel_t, \
                       metalPolygonLabelList: list[PolygonLabel_t]) -> PolygonLabel_t:
    for metalPolygonLabel in metalPolygonLabelList:
        if metalPolygonLabel.polygon.contain_any(*connectorPolygonLabel.polygon.points):
            return metalPolygonLabel  

def NodeFromConnector(connectorPolygonLabel: PolygonLabel_t,
                      logicGateNodePolygonList: list[LogicGateNode_t],
                      connectorExtendedLayerList: list[Polygon]) -> LogicGateNode_t | None:
    for logicGateNode in logicGateNodePolygonList:
        if logicGateNode.polygon.contain_any(*connectorPolygonLabel.polygon.points):
            return logicGateNode
    
    connectorGPolygon = gPolygon(connectorPolygonLabel.polygon.points)
    for connectorMetalPolygon in connectorExtendedLayerList:
        connectorMetalGPolygon = gPolygon(connectorMetalPolygon.points)
        for logicGateNode in logicGateNodePolygonList:
            if logicGateNode.polygon.contain_any(*connectorMetalPolygon.points) and \
               connectorMetalGPolygon.intersects(connectorGPolygon):
                return logicGateNode
        
def PoliLabelBetweenNodes(node1: LogicGateNode_t, node2: LogicGateNode_t,
                          activeDiffusionPolygonList: list[Polygon], 
                          polyPolygonLabelList: list[PolygonLabel_t]) -> str:

    minPoint1 = np.min(node1.polygon.points, axis=0)
    maxPoint1 = np.max(node1.polygon.points, axis=0)

    minPoint2 = np.min(node2.polygon.points, axis=0)
    maxPoint2 = np.max(node2.polygon.points, axis=0)
    
    centroidY1 = (minPoint1[1] + maxPoint1[1]) / 2
    centroidY2 = (minPoint2[1] + maxPoint2[1]) / 2
    centroidY  = (centroidY1 + centroidY2) / 2

    poliPoint = None
    if minPoint1[0] < minPoint2[0]:
        poliPoint = (maxPoint1[0] + (minPoint2[0] - maxPoint1[0]) / 2, centroidY)
    else:
        poliPoint = (maxPoint2[0] + (minPoint1[0] - maxPoint2[0]) / 2, centroidY)
    
    insideActiveDiffusion = False
    for activeDiffusionPolygon in activeDiffusionPolygonList:
        if activeDiffusionPolygon.contain_any(poliPoint):
            insideActiveDiffusion = True
            break
    
    if not insideActiveDiffusion:
        return ''

    for poliPolygonLabel in polyPolygonLabelList:
        if poliPolygonLabel.polygon.contain_any(poliPoint):
            return poliPolygonLabel.label

######################################
### @Author: Mateus Estrêla Pietro ###
######################################