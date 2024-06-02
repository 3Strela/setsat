from setsat.__initialSettings.logicGateGraph.logicGateGraph import LogicGateGraph

from setsat.__susceptibilitySimulation.__logicGateSimulation import SimulateLogicGateBehaviorWithInput

from setsat.dataTypes.logicGateBehavior_t import LogicGateBehavior_t
from setsat.dataTypes.logicGateNode_t     import LogicGateNode_t
from setsat.dataTypes.logicGatePolygons_t import LogicGatePolygons_t
from setsat.dataTypes.polygonLabel_t      import PolygonLabel_t

###############################################
### +++++++++++ PUBLIC FUNCTION +++++++++++ ###
###############################################

def GenerateTruthTable(logicGateGraph: LogicGateGraph) -> LogicGateBehavior_t:
    logicGatePolygons = logicGateGraph.logicGatePolygons
    logicGateBehavior = LogicGateBehavior_t(logicGatePolygons)

    labelToPolygon      = __InstantiateLabelToPolygon(logicGatePolygons)
    numberOfBits        = logicGateBehavior.numberOfBits
    totalNumberOfInputs = logicGateBehavior.totalNumberOfInputs

    for i in range(totalNumberOfInputs):
        binaryInput   = bin(i).split('b')[1].zfill(numberOfBits)
        correctResult = SimulateLogicGateBehaviorWithInput(binaryInput, logicGateBehavior, 
                                                           logicGateGraph, labelToPolygon)

        logicGateBehavior.truthTable[binaryInput] = correctResult
    
    return logicGateBehavior

def SusceptibilitySimulation(logicGateGraph: LogicGateGraph) -> LogicGateBehavior_t:
    logicGatePolygons = logicGateGraph.logicGatePolygons
    logicGateBehavior = LogicGateBehavior_t(logicGatePolygons)

    labelToPolygon      = __InstantiateLabelToPolygon(logicGatePolygons)
    numberOfBits        = logicGateBehavior.numberOfBits
    totalNumberOfInputs = logicGateBehavior.totalNumberOfInputs

    for i in range(totalNumberOfInputs):
        binaryInput   = bin(i).split('b')[1].zfill(numberOfBits)
        correctResult = SimulateLogicGateBehaviorWithInput(binaryInput, logicGateBehavior, 
                                                           logicGateGraph, labelToPolygon)

        logicGateBehavior.truthTable[binaryInput] = correctResult
        
        for nodePolygon in logicGatePolygons.logicGateNodePolygonList:
            resultWithSET = SimulateLogicGateBehaviorWithInput(binaryInput, logicGateBehavior,
                                                               logicGateGraph, labelToPolygon, 
                                                               nodePolygon)
            for outputPin in logicGateBehavior.outputPinList:
                if outputPin not in resultWithSET:
                    continue
                
                if correctResult[outputPin] == resultWithSET[outputPin]:
                    continue

                logicGateBehavior.sensitiveNodes[binaryInput][outputPin].append(nodePolygon.nodeID)

    return logicGateBehavior

#################################################
### +++++++++++ PRIVATE FUNCTIONS +++++++++++ ###
#################################################

def __InstantiateLabelToPolygon(logicGatePolygons: LogicGatePolygons_t) -> dict[str, PolygonLabel_t|LogicGateNode_t]:
    connectorPolygonLabelList = logicGatePolygons.connectorPolygonLabelList
    metalPolygonLabelList     = logicGatePolygons.metalPolygonLabelList
    logicGateNodePolygonList  = logicGatePolygons.logicGateNodePolygonList

    labelToPolygon = {}
    for polygonLabel in (connectorPolygonLabelList + metalPolygonLabelList):
        labelToPolygon[polygonLabel.label]   = polygonLabel
    for logicGateNode in logicGateNodePolygonList:
        labelToPolygon[logicGateNode.nodeID] = logicGateNode

    return labelToPolygon

######################################
### @Author: Mateus Estrêla Pietro ###
######################################