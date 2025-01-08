from gdstk import Polygon

from shapely.geometry import LineString, Polygon as gPolygon

from setsat.logicGate.dataTypes.logicGateNode_t     import LogicGateNode_t
from setsat.logicGate.dataTypes.logicGatePolygons_t import LogicGatePolygons_t
from setsat.logicGate.dataTypes.polygonLabel_t      import PolygonLabel_t

################################################
### +++++++++++ PUBLIC FUNCTIONS +++++++++++ ###
################################################

def ExtractNodePolygons(logicGatePolygons: LogicGatePolygons_t) -> list[LogicGateNode_t]:
    nodeID = 0
    nodePolygonList: list[LogicGateNode_t] = []

    for activeDiffusionPolygon in logicGatePolygons.activeDiffusionPolygonList:
        intercessionPoints = __GetSortedIntercessionPoints(activeDiffusionPolygon.points, logicGatePolygons.polyPolygonLabelList)
        nodePointsList     = __GetNodePointsList(activeDiffusionPolygon.points, intercessionPoints)

        for index, nodePoints in enumerate(nodePointsList):
            sensitiveNode = LogicGateNode_t()
            sensitiveNode.polygon = Polygon(__FormatPoints(nodePoints), 1)
            if index == 0:
                sensitiveNode.neighborList.append('node_'+str(nodeID+1).zfill(3))
            elif index == len(nodePointsList) - 1:
                sensitiveNode.neighborList.append('node_'+str(nodeID-1).zfill(3))
            else:
                sensitiveNode.neighborList.append('node_'+str(nodeID-1).zfill(3))
                sensitiveNode.neighborList.append('node_'+str(nodeID+1).zfill(3))

            sensitiveNode.nodeID = 'node_'+str(nodeID).zfill(3); nodeID += 1
            nodePolygonList.append(sensitiveNode)
    
    __ConnectNeighbors(nodePolygonList, logicGatePolygons)
    
    return nodePolygonList

#################################################
### +++++++++++ PRIVATE FUNCTIONS +++++++++++ ###
#################################################

def __ConnectNeighbors(nodePolygonList: list[LogicGateNode_t], 
                       logicGatePolygons: LogicGatePolygons_t)-> None:
    if len(logicGatePolygons.connectorExtendedPolygonList) == 0:
        return

    for i in range(len(nodePolygonList)):
        for j in range(i+1, len(nodePolygonList)):
            node1 = gPolygon(nodePolygonList[i].polygon.points)
            node2 = gPolygon(nodePolygonList[j].polygon.points)

            for connectorNodePolygon in logicGatePolygons.connectorExtendedPolygonList:
                connectorNodeGPolygon = gPolygon(connectorNodePolygon.points)

                if node1.intersects(connectorNodeGPolygon) and node2.intersects(connectorNodeGPolygon):
                    nodePolygonList[i].neighborList.append(nodePolygonList[j].nodeID)
                    nodePolygonList[j].neighborList.append(nodePolygonList[i].nodeID)
                    break


def __FormatPoints(pointList: list[tuple[float, float]]) -> list[tuple[float, float]]:
    pointList = [(x, y) for x, y in pointList]

    formatedPointList = [pointList.pop()]
    while len(pointList) > 0:
        for index in range(len(pointList)):
            pointA = pointList[index]
            pointB = formatedPointList[-1]
            if (pointA[0] == pointB[0] and pointA[1] != pointB[1]) \
                or (pointA[0] != pointB[0] and pointA[1] == pointB[1]):
                break
        
        if index == len(pointList):
            return None
        
        formatedPointList.append(pointList.pop(index))
        
    return formatedPointList

def __GetNodePointsList(activeZonePolygonPoints: list[tuple[float, float]], sortedIntercessionPoints: list) -> list[list[tuple, tuple]]:
    currentIndex = 0
    nodesPointList:list[list[tuple, tuple]] = []
    while currentIndex < len(sortedIntercessionPoints):
        limitA = sortedIntercessionPoints[currentIndex]
        limitB = sortedIntercessionPoints[currentIndex+1]
        nodesPointList.append([limitA, limitB])
        
        if currentIndex == 0:
            for point in activeZonePolygonPoints:
                if point[0] <= limitA[0]:
                    nodesPointList[-1].append(point)
        elif currentIndex == len(sortedIntercessionPoints) - 2:
            for point in activeZonePolygonPoints:
                if point[0] >= limitA[0]:
                    nodesPointList[-1].append(point)
        else:
            currentIndex += 2
            limitX = sortedIntercessionPoints[currentIndex]
            limitY = sortedIntercessionPoints[currentIndex+1]
            nodesPointList[-1].append(limitX)
            nodesPointList[-1].append(limitY)

            for point in activeZonePolygonPoints:
                if point[0] >= limitA[0] and point[0] <= limitX[0]:
                    nodesPointList[-1].append(point)
        currentIndex += 2

    return nodesPointList

def __GetSortedIntercessionPoints(activeZonePolygonPoints: list[tuple[float, float]], poliPolygonLabelList: list[PolygonLabel_t]) -> list:
    intercessionPointList = []
    for i in range(len(activeZonePolygonPoints)):
        pointA = activeZonePolygonPoints[i]
        pointB = activeZonePolygonPoints[i-1]
        line1 = LineString([pointA, pointB])

        for poliPolygon in poliPolygonLabelList:
            poliPolygonPoints = poliPolygon.polygon.points
            for j in range(len(poliPolygonPoints)):
                pointX = poliPolygonPoints[j]
                pointY = poliPolygonPoints[j-1]
                line2 = LineString([pointX, pointY])

                if line1.intersects(line2):
                    intercession = line1.intersection(line2)
                    intercessionCoordinates = (intercession.x, intercession.y)
                    intercessionPointList.append(intercessionCoordinates)
                    
    return sorted(intercessionPointList)

######################################
### @Author: Mateus Estrêla Pietro ###
######################################