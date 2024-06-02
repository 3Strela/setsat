from setsat.__initialSettings.logicGateGraph.logicGateGraph import LogicGateGraph

from setsat.dataTypes.logicGateBehavior_t import LogicGateBehavior_t
from setsat.dataTypes.logicGateNode_t     import LogicGateNode_t
from setsat.dataTypes.polygonLabel_t      import PolygonLabel_t

import heapq

###############################################
### +++++++++++ PUBLIC FUNCTION +++++++++++ ###
###############################################

def SimulateLogicGateBehaviorWithInput(binaryInput: str, logicGateBehavior: LogicGateBehavior_t,               \
                    logicGateGraph: LogicGateGraph, labelToPolygon: dict[str, PolygonLabel_t|LogicGateNode_t], \
                    possibleSensitiveNode: LogicGateNode_t|None = None) -> dict[str, int]:
    logicGatePolygons    = logicGateGraph.logicGatePolygons
    polyPolygonLabelList = logicGatePolygons.polyPolygonLabelList

    inputPinList  = logicGateBehavior.inputPinList
    outputPinList = logicGateBehavior.outputPinList

    polyVoltage = __InstantiatePolyVoltage(binaryInput, inputPinList, polyPolygonLabelList)
    preResult   = __InstantiatePreResult(outputPinList, polyVoltage)

    pqNMOS, pqPMOS, \
    visitedPolygonNMOS, visitedPolygonPMOS = __InstantiatePriorityQueue(labelToPolygon, possibleSensitiveNode)

    heapq.heapify(pqNMOS); heapq.heapify(pqPMOS)

    pullPlane = 'NMOS'; isEndLess = 0
    if possibleSensitiveNode != None and possibleSensitiveNode.typeSource == 'VDD':
        pullPlane = 'PMOS'

    waitListNMOS: list[tuple[str, str]] = []
    waitListPMOS: list[tuple[str, str]] = []

    while len(pqNMOS) > 0 or len(pqPMOS) > 0 or \
          len(waitListNMOS) > 0 or len(waitListPMOS) > 0:
        
        adjacentList, neededVoltage, \
        priorityQueue, waitList,     \
        visitedPolygon = __GetDataFromPullPlane(logicGateGraph, pullPlane, pqNMOS, pqPMOS, 
                                                visitedPolygonNMOS, visitedPolygonPMOS, 
                                                waitListNMOS, waitListPMOS)
        
        if len(waitList) == 0 and len(priorityQueue) == 0:
            pullPlane = 'NMOS' if pullPlane == 'PMOS' else 'PMOS'
            continue
        elif len(priorityQueue) > 0:
            polygon = heapq.heappop(priorityQueue)
        elif len(waitList) > 0 and len(priorityQueue) == 0:
            doTakeOff = __TryTakeOffWaitList(adjacentList, neededVoltage, polyVoltage,
                                                    labelToPolygon, preResult, priorityQueue, 
                                                    visitedPolygon, waitList)
            if doTakeOff:
                isEndLess = 0
                continue

            isEndLess += 1
            if isEndLess == 2:
                break

            pullPlane = 'NMOS' if pullPlane == 'PMOS' else 'PMOS'
            continue
        
        isEndLess = 0
        
        polygonLabel = __GetPolygonLabel(polygon)
        if polygonLabel in preResult:
            preResult[polygonLabel][pullPlane] = True
            continue

        __AddConductiveNeighbors(adjacentList, neededVoltage, polyVoltage, labelToPolygon,
                                        polygonLabel, priorityQueue, visitedPolygon, waitList)

    correctResult = __ConvertPreResultToResult(preResult)
    return correctResult


#################################################
### +++++++++++ PRIVATE FUNCTIONS +++++++++++ ###
#################################################

def __AddConductiveNeighbors(adjacentList: dict[str, dict[str, str]], neededVoltage: int,
                             polyVoltage: dict[str, int|None],
                             labelToPolygon: dict[str, PolygonLabel_t|LogicGateNode_t],
                             polygonLabel: str, priorityQueue: list[PolygonLabel_t|LogicGateNode_t],
                             visitedPolygon: set[str], waitList: list[tuple[str, str]]) -> None:
    
    for neighbor, poly in adjacentList[polygonLabel].items():
            if neighbor in visitedPolygon:
                continue

            if poly == '' or poly == None:
                heapq.heappush(priorityQueue, labelToPolygon[neighbor])
                visitedPolygon.add(neighbor)
            elif polyVoltage[poly] == None and (polygonLabel, neighbor) not in waitList:
                waitList.append((polygonLabel, neighbor))
            elif neededVoltage == polyVoltage[poly]:
                heapq.heappush(priorityQueue, labelToPolygon[neighbor])
                visitedPolygon.add(neighbor)

def __ConvertPreResultToResult(preResult: dict[str, dict[str, bool]]) -> dict[str, int]:
    correctResult = {}
    for polygonLabel, resultCMOS in preResult.items():
        if polygonLabel[0:3] != 'net' and polygonLabel[0:3] != 'met':
            if (resultCMOS['NMOS'] != None and resultCMOS['PMOS'] != None) \
                or (resultCMOS['NMOS'] is None and resultCMOS['PMOS'] is None):
                correctResult[polygonLabel] = -1
            elif resultCMOS['NMOS']:
                correctResult[polygonLabel] = 0
            elif resultCMOS['PMOS']:
                correctResult[polygonLabel] = 1

    return correctResult

def __GetDataFromPullPlane(logicGateGraph: LogicGateGraph, pullPlane: str,
                           pqNMOS: list[PolygonLabel_t|LogicGateNode_t],
                           pqPMOS: list[PolygonLabel_t|LogicGateNode_t],
                           visitedPolygonNMOS: set[str], visitedPolygonPMOS: set[str],
                           waitListNMOS: list[tuple[str, str]],
                           waitListPMOS: list[tuple[str, str]])                        \
                           -> tuple[ dict[str, dict[str, str]], int,
                              list[PolygonLabel_t|LogicGateNode_t],
                              list[tuple[str, str]], set[str]]:
    match pullPlane:
        case 'NMOS':
            adjacentList   = logicGateGraph.adjacentDictNMOS
            neededVoltage  = 1 # NMOS conduz quando tem entrada lógica 1 causando baixa tensão
            priorityQueue  = pqNMOS
            waitList       = waitListNMOS
            visitedPolygon = visitedPolygonNMOS
        case 'PMOS':
            adjacentList = logicGateGraph.adjacentDictPMOS
            neededVoltage = 0 # PMOS conduz quando tem entrada lógica 0 causando alta tensão
            priorityQueue = pqPMOS
            waitList      = waitListPMOS
            visitedPolygon = visitedPolygonPMOS
    
    return adjacentList, neededVoltage, priorityQueue, waitList, visitedPolygon

def __GetPolygonLabel(polygon: PolygonLabel_t|LogicGateNode_t) -> str|None:
    if type(polygon) == PolygonLabel_t:
        return polygon.label
    elif type(polygon) == LogicGateNode_t:
        return polygon.nodeID

def __InstantiatePolyVoltage(binaryInput: str, inputPinList: list[str],
                             polyPolygonLabelList: list[PolygonLabel_t]) -> dict[str, int|None]:
    polyVoltage = {}
    for i, inputLabel in enumerate(inputPinList):
        polyVoltage[inputLabel] = int(binaryInput[i])

    for polyPolygonLabel in polyPolygonLabelList:
        polyLabel = polyPolygonLabel.label

        if polyLabel is None:
            continue

        if polyLabel in polyVoltage:
            continue

        polyVoltage[polyLabel] = None
        
    return polyVoltage

def __InstantiatePreResult(outputPinList: list[str],
                           polyVoltage: dict[str, int|None]) -> dict[str, dict[str, bool|None]]:
    preResult = {}
    for outputLabel in outputPinList:
        preResult[outputLabel] = {
            'PMOS': None,
            'NMOS': None
        }

    for poly, voltage in polyVoltage.items():
        if voltage == None:
            preResult[poly] = {
            'PMOS': None,
            'NMOS': None
        }
            
    return preResult

def __InstantiatePriorityQueue(labelToPolygon: dict[str, PolygonLabel_t|LogicGateNode_t],
                                possibleSensitiveNode: LogicGateNode_t|None = None)       \
                                -> tuple[list[PolygonLabel_t|LogicGateNode_t],
                                        list[PolygonLabel_t|LogicGateNode_t],
                                        set[str], set[str]]:
    pqNMOS = [labelToPolygon['VSS']]
    pqPMOS = [labelToPolygon['VDD']]
    visitedPolygonNMOS = set(); visitedPolygonNMOS.add('VSS')
    visitedPolygonPMOS = set(); visitedPolygonPMOS.add('VDD')

    if possibleSensitiveNode != None:
        nodeID = possibleSensitiveNode.nodeID
        match possibleSensitiveNode.typeSource:
            case 'VSS':
                pqNMOS.append(labelToPolygon[nodeID])
                visitedPolygonNMOS.add(nodeID)
            case 'VDD':
                pqPMOS.append(labelToPolygon[nodeID])
                visitedPolygonPMOS.add(nodeID)
    

    return pqNMOS, pqPMOS, visitedPolygonNMOS, visitedPolygonPMOS

def __TryTakeOffWaitList(adjacentList: dict[str, dict[str, str]], neededVoltage: int,
                         polyVoltage: dict[str, int|None],
                         labelToPolygon: dict[str, PolygonLabel_t|LogicGateNode_t],
                         preResult: dict[str, dict[str, bool]],
                         priorityQueue: list[PolygonLabel_t|LogicGateNode_t], 
                         visitedPolygon: set[str], waitList: list[tuple[str, str]]) -> bool:
    __TryUpdatePolys(preResult, polyVoltage)
    
    removeFromWaitList = []
    for i in range(len(waitList)):
        node1, node2 = waitList[i]
        poly = adjacentList[node1][node2]
        if polyVoltage[poly] == None:        
            continue
        
        if polyVoltage[poly] == neededVoltage:
            heapq.heappush(priorityQueue, labelToPolygon[node2])
            visitedPolygon.add(node2)
        
        removeFromWaitList.append(i)
    
    if len(removeFromWaitList) > 0:
        for i in range(len(removeFromWaitList)-1, -1, -1):
            indexToRemove = removeFromWaitList[i]
            waitList.pop(indexToRemove)
        
        return True
    
    return False

def __TryUpdatePolys(preResult: dict[str, dict[str, bool|None]],
                     polyVoltage: dict[str, int|None]) -> None:
    update = []
    for poly, voltage in polyVoltage.items():
        if voltage != None:
            continue

        resultNMOS = preResult[poly]['NMOS']
        resultPMOS = preResult[poly]['PMOS']
        
        newVoltage = None
        if resultNMOS != None:
            newVoltage = 1 if not resultNMOS else 0
        if resultPMOS != None:
            newVoltage = 1 if resultPMOS else 0
        
        if newVoltage != None:
            update.append((poly, newVoltage))

    if len(update) == 0:
        return
    
    for poly, newVoltage in update:
        polyVoltage[poly] = newVoltage
        del preResult[poly]


######################################
### @Author: Mateus Estrêla Pietro ###
######################################