from setsat.logicGate.dataTypes.componentID_e       import ComponentID_e
from setsat.logicGate.dataTypes.logicGateNode_t     import LogicGateNode_t
from setsat.logicGate.dataTypes.logicGatePolygons_t import LogicGatePolygons_t
from setsat.logicGate.dataTypes.polygonLabel_t      import PolygonLabel_t

import setsat.logicGate.__initialSettings.logicGateGraph.__logicGateGraphUtil as lggUtil

import heapq
import numpy as np

class LogicGateGraph:

    def __init__(self, cellPolygons: LogicGatePolygons_t) -> None:
        self.logicGatePolygons = cellPolygons

        self.adjacentDictPMOS: dict[str, dict[str, str]] = None
        self.adjacentDictNMOS: dict[str, dict[str, str]] = None

        self.__BuildGraph()
        
    ##############################################
    ### ----------- PRIVATE METHODS ---------- ###
    ##############################################

    def __BuildGraph(self):
        powerPolygonLabel  = None
        groundPolygonLabel = None
        for metalPolygonLabel in self.logicGatePolygons.metalPolygonLabelList:
            match metalPolygonLabel.label:
                case 'VDD':
                    powerPolygonLabel = metalPolygonLabel
                case 'VSS':
                    groundPolygonLabel = metalPolygonLabel
        
        centroidAxisY = lggUtil.CalculeCentroidAxisY(self.logicGatePolygons.activeDiffusionPolygonList)

        self.adjacentDictPMOS = self.__BuildParcialGraph(centroidAxisY, powerPolygonLabel)
        self.adjacentDictNMOS = self.__BuildParcialGraph(centroidAxisY, groundPolygonLabel)

    def __AddElementIntoPQ(self, father: str, son: PolygonLabel_t|LogicGateNode_t, connectionValue: str, \
                           adjacentDict: dict[str, dict[str, str]], priorityQueue: list) -> None:
        sonLabel = None
        if type(son) == PolygonLabel_t:
            sonLabel = son.label
        elif type(son) == LogicGateNode_t:
            sonLabel = son.nodeID

        adjacentDict[father][sonLabel] = connectionValue
        heapq.heappush(priorityQueue, son)

    def __BuildParcialGraph(self, centroidAxisY: float, sourcePolygonLabel: PolygonLabel_t) -> None:
        adjacentDict: dict[str, dict[str, str]] = {}
        
        activeDiffusionPolygonList   = self.logicGatePolygons.activeDiffusionPolygonList
        connectorExtendedPolygonList = self.logicGatePolygons.connectorExtendedPolygonList
        polyPolygonLabelList         = self.logicGatePolygons.polyPolygonLabelList

        metalPolygonLabelList     = self.logicGatePolygons.metalPolygonLabelList
        connectorPolygonLabelList = self.logicGatePolygons.connectorPolygonLabelList
        for polygonLabel in (metalPolygonLabelList + connectorPolygonLabelList):
            adjacentDict[polygonLabel.label] = {}

        logicGateNodePolygonList = self.logicGatePolygons.logicGateNodePolygonList
        for logicGateNode in logicGateNodePolygonList:
            adjacentDict[logicGateNode.nodeID] = {}

        visitedPolygons = set()
        priorityQueue = [sourcePolygonLabel]
        heapq.heapify(priorityQueue)
        
        while len(priorityQueue) > 0:
            polygon = heapq.heappop(priorityQueue)
            if polygon in visitedPolygons:
                continue
    
            visitedPolygons.add(polygon)
            
            if type(polygon) == PolygonLabel_t:
                match polygon.componentID:
                    case ComponentID_e.METAL:
                        metal = polygon
                        
                        connectorsInMetal = lggUtil.ConnectorsInMetal(metal, connectorPolygonLabelList)
                        
                        for connector in connectorsInMetal:
                            
                            connectorYaxis = np.min(connector.polygon.points, axis=0)[1]
                            if not lggUtil.CheckMetalLimitYaxis(centroidAxisY, connectorYaxis, sourcePolygonLabel.label):
                                continue
                            
                            connectionValue = ''
                            self.__AddElementIntoPQ(metal.label, connector, connectionValue, adjacentDict, priorityQueue)

                    case ComponentID_e.CONNECTOR:
                        connector = polygon
                        
                        connectionValue = ''

                        node = lggUtil.NodeFromConnector(connector, logicGateNodePolygonList, connectorExtendedPolygonList)
                        if node is not None :
                            self.__AddElementIntoPQ(connector.label, node, connectionValue, adjacentDict, priorityQueue)
                        
                        metal = lggUtil.MetalFromConnector(connector, metalPolygonLabelList)
                        self.__AddElementIntoPQ(connector.label, metal, connectionValue, adjacentDict, priorityQueue)

            elif type(polygon) == LogicGateNode_t:
                logicGateNode = polygon
                logicGateNode.typeSource = sourcePolygonLabel.label

                connectorsInSensitiveNode = lggUtil.ConnectorsInSensitiveNode(logicGateNode, connectorPolygonLabelList)
                
                for connector in connectorsInSensitiveNode:
                    connectionValue = ''
                    self.__AddElementIntoPQ(logicGateNode.nodeID, connector, connectionValue, adjacentDict, priorityQueue)
                
                for neighbor in logicGateNode.neighborList:
                    neighborID   = int(neighbor.split('_')[1])
                    neighborNode = logicGateNodePolygonList[neighborID]
                    
                    connectionValue = lggUtil.PoliLabelBetweenNodes(logicGateNode, neighborNode, 
                                                                    activeDiffusionPolygonList, polyPolygonLabelList)
                    
                    self.__AddElementIntoPQ(logicGateNode.nodeID, neighborNode, connectionValue, adjacentDict, priorityQueue)
                    
        return adjacentDict

######################################
### @Author: Mateus Estrêla Pietro ###
######################################