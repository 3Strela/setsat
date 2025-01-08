from setsat.circuit.circuitParser import CircuitParser

#########################################
### +++++++++++ CONSTANTS +++++++++++ ###
#########################################

NANOMETERS = 1e-9

###############################################
### +++++++++++ PUBLIC FUNCTION +++++++++++ ###
###############################################

def SensitiveGatesByInputVector(circuitParser: CircuitParser,
                                particleFlux: float, gdsUnit: float):
    with open('CircuitSensitiveGatesByInputVector.tsv', 'a') as tsvFile:
        circuitName      = circuitParser.circuitName
        inputVectorOrder = ' '.join(circuitParser.inputPinList)

        tsvFile.write(f'{circuitName}\nInputVector({inputVectorOrder})\n')
    
    outputPinList       = circuitParser.outputPinList
    numberOfBits        = len(circuitParser.inputPinList)
    totalNumberOfInputs = 2**numberOfBits
    
    with open('CircuitSensitiveGatesByInputVector.tsv', 'a') as tsvFile:
        for i in range(totalNumberOfInputs):
            binaryInputVector = bin(i).split('b')[1].zfill(numberOfBits)

            tsvFile.write(f'{binaryInputVector}\t')
            for j, circuitOutput in enumerate(outputPinList):
                sensitiveLogicGates = circuitParser.sensitiveLogicGates[binaryInputVector][circuitOutput]
                
                sensitiveLogicGatesStr = ''
                for k in range(len(sensitiveLogicGates)):
                    gateID, gateSensitiveArea = sensitiveLogicGates[k]
                    sensitiveLogicGatesStr += f'{gateID}.({gateSensitiveArea})|{circuitOutput}'

                    if k != len(sensitiveLogicGates) - 1:
                        sensitiveLogicGatesStr += '\t'
                        
                tsvFile.write(sensitiveLogicGatesStr)

                if j != len(outputPinList) - 1:
                    tsvFile.write('\t')
            
            tsvFile.write('\n')
        
        tsvFile.write('\n')

        for circuitLogicGate in circuitParser.topologicalSort:
            gateID        = circuitLogicGate.logicGateID
            cellName      = circuitLogicGate.cellName

            tsvFile.write(f'{gateID}\t{cellName}\n')

        tsvFile.write('\n')

######################################
### @Author: Mateus Estrêla Pietro ###
#####################################