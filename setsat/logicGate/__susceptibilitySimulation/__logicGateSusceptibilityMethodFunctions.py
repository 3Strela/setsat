from setsat.logicGate.dataTypes.logicGateBehavior_t import LogicGateBehavior_t
from setsat.logicGate.dataTypes.logicGatePolygons_t import LogicGatePolygons_t

#########################################
### +++++++++++ CONSTANTS +++++++++++ ###
#########################################

NANOMETERS = 1e-9

###############################################
### +++++++++++ PUBLIC FUNCTION +++++++++++ ###
###############################################

def ProbabilisticTransferMatrix(cellName: str,
                                logicGatePolygons: LogicGatePolygons_t,
                                logicGateBehavior: LogicGateBehavior_t, 
                                particleFlux: float, gdsUnit: float) -> None:
    pass

def SensitiveNodesByInputVector(cellName: str,
                                logicGatePolygons: LogicGatePolygons_t,
                                logicGateBehavior: LogicGateBehavior_t, 
                                particleFlux: float, gdsUnit: float) -> None:
    
    with open('LogicGatesSensitiveNodesByInputVector.tsv', 'a') as tsvFile:
        inputVectorOrder = ''.join(logicGateBehavior.inputPinList)
        tsvFile.write(f'{cellName}\nInputVector({inputVectorOrder})\n')
    
    numberOfBits        = logicGateBehavior.numberOfBits
    totalNumberOfInputs = logicGateBehavior.totalNumberOfInputs

    sensitiveNodes = logicGateBehavior.sensitiveNodes
    with open('LogicGatesSensitiveNodesByInputVector.tsv', 'a') as tsvFile:        
        for i in range(totalNumberOfInputs):
            binaryInputVector = bin(i).split('b')[1].zfill(numberOfBits)

            tsvFile.write(f'{binaryInputVector}\t')
            for j, logicGateOutput in enumerate(sensitiveNodes[binaryInputVector]):
                sensitiveNodeList = sensitiveNodes[binaryInputVector][logicGateOutput]

                sensitiveNodesStr = f'|{logicGateOutput}\t'.join(sensitiveNodeList) + '|' + str(logicGateOutput)
                tsvFile.write(sensitiveNodesStr)

                if j != len(sensitiveNodes[binaryInputVector]) - 1:
                    tsvFile.write('\t')
            tsvFile.write('\n')
        
        tsvFile.write('\n')
        for nodePolygon in logicGatePolygons.logicGateNodePolygonList:
            nodeID        = nodePolygon.nodeID
            nodePullPlane = 'Pull-down' if nodePolygon.typeSource == 'VSS' else 'Pull-up'
            nodePoints    = '\t'.join(list(map(str, nodePolygon.polygon.points)))

            tsvFile.write(f'{nodeID}\t{nodePullPlane}\t{nodePoints}\n')

        tsvFile.write('\n')

def SusceptibilityByInputVector(cellName: str,
                                logicGatePolygons: LogicGatePolygons_t,
                                logicGateBehavior: LogicGateBehavior_t, 
                                particleFlux: float, gdsUnit: float) -> None:
    
    with open('LogicGatesSusceptibilityByInputVector.tsv', 'a') as tsvFile:
        inputVectorOrder = ''.join(logicGateBehavior.inputPinList)
        logicGateOutputs = '\t\t\t\t'.join(logicGateBehavior.outputPinList)

        headFile  = f'{cellName}\tInputVector({inputVectorOrder})\t{logicGateOutputs}\t\t\t\t'
        headFile += f'Total sensitive area\tNumber of sensitive nodes\tSusceptibility({particleFlux})\n'
        tsvFile.write(headFile)
        
        pullPlanes = ['NMOS sensitive area', 'NMOS sensitive nodes', 'PMOS sensitive area', 'PMOS sensitive area']
        pullPlanes = '\t'.join(pullPlanes* len(logicGateBehavior.outputPinList))
        tsvFile.write(f'\t\t{pullPlanes}\t\t\t\n')

    numberOfBits        = logicGateBehavior.numberOfBits
    totalNumberOfInputs = logicGateBehavior.totalNumberOfInputs

    sensitiveNodes = logicGateBehavior.sensitiveNodes
    with open('LogicGatesSusceptibilityByInputVector.tsv', 'a') as tsvFile:        
        for i in range(totalNumberOfInputs):
            binaryInputVector = bin(i).split('b')[1].zfill(numberOfBits)
            
            totalSensitiveArea  = 0
            totalSensitiveNodes = 0

            tsvFile.write(f'\t{binaryInputVector}\t')
            for logicGateOutput in sensitiveNodes[binaryInputVector]:
                sensitiveNodeList = sensitiveNodes[binaryInputVector][logicGateOutput]

                pullDown = {'sensitiveArea': 0, 'sensitiveNodes': 0}
                pullUp   = {'sensitiveArea': 0, 'sensitiveNodes': 0}
                for sensitiveNode in sensitiveNodeList:
                    nodeIndex = int(sensitiveNode.split('_')[1])
                    node = logicGatePolygons.logicGateNodePolygonList[nodeIndex]

                    match node.typeSource:
                        case 'VDD':
                            pullUp['sensitiveArea']  += __TransformAreaUnitToNanometers(node.polygon.area(), gdsUnit)
                            pullUp['sensitiveNodes'] += 1
                        case 'VSS':
                            pullDown['sensitiveArea']  += __TransformAreaUnitToNanometers(node.polygon.area(), gdsUnit)
                            pullDown['sensitiveNodes'] += 1
                
                totalSensitiveArea  += pullDown['sensitiveArea'] + pullUp['sensitiveArea']
                totalSensitiveNodes += pullDown['sensitiveNodes'] + pullUp['sensitiveNodes']

                pullDownSensitiveArea = str(pullDown['sensitiveArea']).replace('.', ',')
                pullUpSensitiveArea   = str(pullUp['sensitiveArea']).replace('.', ',')

                pullDownNodes = str(pullDown['sensitiveNodes'])
                pullUpNodes   = str(pullUp['sensitiveNodes'])

                tsvFile.write(f'{pullDownSensitiveArea}\t{pullDownNodes}\t{pullUpSensitiveArea}\t{pullUpNodes}\t')
            
            susceptibility     = str(round(totalSensitiveArea * particleFlux, 15)).replace('.', ',')
            totalSensitiveArea = str(totalSensitiveArea).replace('.', ',')
            tsvFile.write(f'{totalSensitiveArea}\t{totalSensitiveNodes}\t{susceptibility}\n')

        tsvFile.write('\n\n')

#################################################
### +++++++++++ PRIVATE FUNCTIONS +++++++++++ ###
#################################################

def __TransformAreaUnitToNanometers(area: float, gdsUnit: float) -> float:
    area = round(area, 15)

    auxUnit = gdsUnit
    constantToNano = 0

    if gdsUnit > NANOMETERS:
        while auxUnit > NANOMETERS:
            auxUnit /= 10
            constantToNano += 1

        return area * (10**constantToNano)**2

    while auxUnit < NANOMETERS:
        auxUnit *= 10
        constantToNano += 1

    return area / (10**constantToNano)**2

######################################
### @Author: Mateus Estrêla Pietro ###
######################################