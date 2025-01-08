# Montar grafo
# --> Nodo (porta logica) tem: (fio, pino) e nome da célula, 
#                              caso não houver pino, adota-se: os primeiros fios são entradas e dps saída, em ordem alfabética dos pinos da célula
# Ordem topológica


# Simular suceptibilidade
# Cell suceptibility para pegar as areas sensiveis

from gdstk import Cell

from setsat.logicGate.__initialSettings.extractPolygons.extractInterestLayers import ExtractInterestLayerPolygons
from setsat.logicGate.__initialSettings.extractPolygons.extractNodePolygons   import ExtractNodePolygons
from setsat.logicGate.__initialSettings.logicGateGraph.logicGateGraph         import LogicGateGraph

from setsat.logicGate.__susceptibilitySimulation.susceptibilitySimulation import SusceptibilitySimulation

from setsat.logicGate.dataTypes.componentID_e       import ComponentID_e
from setsat.logicGate.dataTypes.logicGateBehavior_t import LogicGateBehavior_t
from setsat.logicGate.dataTypes.standardCellLibrary import StandardCellLibrary_t

from setsat.circuit.__circuitLogicGateNode import CircuitLogicGateNode_t

#########################################
### +++++++++++ CONSTANTS +++++++++++ ###

INPUT_WIRES  = 'input'
OUTPUT_WIRES = 'output'

NANOMETERS = 1e-9

#########################################

class CircuitParser:

    def __init__(self, verilogFilePath: str, cellList: list[Cell], cellLibrary: StandardCellLibrary_t, gdsUnit: float) -> None:
        self.circuitName   =  verilogFilePath.split('/')[-1].split('\\')[-1].replace('v', '')
        self.inputPinList  = self.__GetPinList(INPUT_WIRES, verilogFilePath)
        self.outputPinList = self.__GetPinList(OUTPUT_WIRES, verilogFilePath)

        circuitLogicGateNodeList = self.__GetCircuitLogicGateNodeList(cellList, cellLibrary, verilogFilePath)
        self.topologicalSort     = self.__TopoSort(circuitLogicGateNodeList)
        self.sensitiveLogicGates = self.__ComputeSensitiveLogicGateList(gdsUnit)

    ##############################################
    ### ----------- PRIVATE METHODS ---------- ###
    ##############################################

    def __CircuitBehaviorSimulation(self, wireLogicalLevel: dict[str, str], 
                                    possibleSensitiveGate: tuple[str, str]|None = None) -> tuple[str, str]:
        sensitiveInputGate = None

        for circuitLogicGate in self.topologicalSort:
            inputWireLogicalLevel = ''.join([wireLogicalLevel[wire] for wire in circuitLogicGate.inputWireList])
            
            gateTruthTable = circuitLogicGate.logicGateBehavior.truthTable[inputWireLogicalLevel]
            for outputWire in circuitLogicGate.outputWireList:
                for outputPin in gateTruthTable:
                    if circuitLogicGate.wireToLogicGatePin[outputWire] == outputPin:
                        outputWireLogicalLevel = str(gateTruthTable[outputPin])

                        if possibleSensitiveGate != None:
                            sensitiveGateID, sensitiveGateOutput = possibleSensitiveGate
                            if sensitiveGateID == circuitLogicGate.logicGateID and sensitiveGateOutput == outputPin:
                                outputWireLogicalLevel = str(1 if gateTruthTable[outputPin] == 0 else 0)
                                sensitiveInputGate     = inputWireLogicalLevel
                        
                        wireLogicalLevel[outputWire] = outputWireLogicalLevel
                        break
        
        outputPinLogicalLevel = ''.join([wireLogicalLevel[outputPin] for outputPin in self.outputPinList])
        return outputPinLogicalLevel, sensitiveInputGate

    def __ComputeLogicGateBehaviorDict(self, cellList: list[Cell], 
                                       cellLibrary: StandardCellLibrary_t) -> dict[str, LogicGateBehavior_t]:
        logicGateData = {}
        for cell in cellList:
            # Extracting & Labeling logic gate polygons
            logicGatePolygons = ExtractInterestLayerPolygons(cell, cellLibrary)
            nodePolygons      = ExtractNodePolygons(logicGatePolygons)
            logicGatePolygons.AddComponent(nodePolygons, ComponentID_e.NODE)

            # Building logic gate graph
            logicGateGraph = LogicGateGraph(logicGatePolygons)
            
            # Logic gate behavior
            logicGateBehavior = SusceptibilitySimulation(logicGateGraph)

            logicGateData[cell.name] = {'behavior': logicGateBehavior, 'polygons': logicGatePolygons}

        return logicGateData

    def __ComputeSensitiveLogicGateList(self, gdsUnit: float) -> dict[str, list[str]]:
        sensitiveLogicGates: dict[str, dict[str, list[tuple[str, int]]]] = {}

        numberOfBits = len(self.inputPinList)
        totalNumberOfInputs = 2**numberOfBits
        for i in range(totalNumberOfInputs):
            binaryInput = bin(i).split('b')[1].zfill(numberOfBits)
            
            sensitiveLogicGates[binaryInput] = {}
            for outputPin in self.outputPinList:
                sensitiveLogicGates[binaryInput][outputPin] = []

            wireLogicalLevel = {}
            for i, bit in enumerate(binaryInput):
                wireLogicalLevel[self.inputPinList[i]] = bit

            expectedResult, _ = self.__CircuitBehaviorSimulation(wireLogicalLevel)

            for circuitLogicGate in self.topologicalSort:
                for outputWire in circuitLogicGate.outputWireList:
                    outputGate = circuitLogicGate.wireToLogicGatePin[outputWire]
                    gateID     = circuitLogicGate.logicGateID

                    possibleSensitiveGateID = (gateID, outputGate)
                    resultWithSET, sensitiveInputGate = self.__CircuitBehaviorSimulation(wireLogicalLevel, possibleSensitiveGateID)

                    if resultWithSET == expectedResult:
                        continue

                    gateSensitiveNodeList = circuitLogicGate.logicGateBehavior.sensitiveNodes[sensitiveInputGate][outputGate]
                    gateSensitiveArea     = 0
                    for sensitiveNodeID in gateSensitiveNodeList:        
                        nodeIndex = int(sensitiveNodeID.split('_')[1])
                        node      = circuitLogicGate.logicGatePolygons.logicGateNodePolygonList[nodeIndex]
                        nodeArea  = self.__TransformAreaUnitToNanometers(node.polygon.area(), gdsUnit)

                        gateSensitiveArea += nodeArea

                    for i, outputBit in enumerate(expectedResult):
                        if outputBit != resultWithSET[i]:
                            circuitOutputPin = self.outputPinList[i]
                            
                            sensitiveLogicGates[binaryInput][circuitOutputPin].append((gateID, gateSensitiveArea))

        return sensitiveLogicGates

    def __GetCircuitLogicGateNodeList(self, cellList: list[Cell], cellLibrary: StandardCellLibrary_t,
                                      verilogFilePath: str) -> list[CircuitLogicGateNode_t]:
        with open(verilogFilePath, 'r') as vFile:
            vFileLines = vFile.readlines()
        
        logicGateData = self.__ComputeLogicGateBehaviorDict(cellList, cellLibrary)

        beginWireLine = False; endWireLine   = False
        isLogicGate = False
        circuitLogicGateNodeList = []
        for line in vFileLines:
            lineWithoutSpace = line.split()

            beginWireLine, endWireLine = self.__IsLineAfterWires(lineWithoutSpace, beginWireLine, endWireLine)
            if not endWireLine:
                continue
            
            if not isLogicGate:
                isLogicGate = True
                continue

            cellName     = lineWithoutSpace[0]
            logicGateID  = line.split('(', 1)[0].split()[1]
            pinList      = line.split('(', 1)[1].removesuffix(');\n').replace(' ', '').split(',')
            
            cellBehavior = logicGateData[cellName]['behavior']
            cellPolygons = logicGateData[cellName]['polygons']
            
            circuitLogicGateNode = CircuitLogicGateNode_t(cellName, cellBehavior, cellPolygons, logicGateID, pinList)
            circuitLogicGateNodeList.append(circuitLogicGateNode)
    
        return circuitLogicGateNodeList

    def __GetPinList(self, wireType: int, verilogFilePath: str) -> list[str] | None:
        wireList = []
        with open(verilogFilePath, 'r') as vFile:
            for line in vFile.readlines():
                lineWithoutSpace = line.split()
                
                if len(wireList) > 0:
                    if wireList[-1] == '':
                        wireList.pop()

                    if wireList[-1][-1] == ';':                    
                        wireList[-1] = wireList[-1].replace(';', '')
                        return wireList
                    
                    wireList += ''.join(lineWithoutSpace).split(',')
                    
                if len(lineWithoutSpace) > 0 and lineWithoutSpace[0] == wireType:
                    wireList = ''.join(lineWithoutSpace[1:]).split(',')
    
    def __IsLineAfterWires(self, lineWithoutSpace: list[str], beginWireLine: bool, 
                           endWireLine: bool) -> bool:
        if len(lineWithoutSpace) == 0:
            return beginWireLine, endWireLine

        if lineWithoutSpace[0] == 'wire':
            if lineWithoutSpace[-1][-1] == ';':
                return True, True
            return True, endWireLine
        
        if lineWithoutSpace[0] == 'endmodule':
            return False, False

        if not beginWireLine or beginWireLine and lineWithoutSpace[-1][-1] != ';':
            return beginWireLine, endWireLine

        return beginWireLine, True

    def __TopoSort(self, circuitLogicGateNodeList: list[CircuitLogicGateNode_t]) -> list[CircuitLogicGateNode_t]:     
        visitedWire = set()
        for inputPin in self.inputPinList:
            visitedWire.add(inputPin)

        removeIndex = []; topoOrder = []
        while len(circuitLogicGateNodeList) > 0:
            for i, circuitLogicGateNode in enumerate(circuitLogicGateNodeList):
                numberOfNeededWire = len(circuitLogicGateNode.inputWireList)
                for inputWire in circuitLogicGateNode.inputWireList:
                    if inputWire in visitedWire:
                        numberOfNeededWire -= 1
                        
                if numberOfNeededWire == 0:
                    topoOrder.append(circuitLogicGateNode); removeIndex.append(i)
                    for outputWire in circuitLogicGateNode.outputWireList:
                        visitedWire.add(outputWire)

            removeIndex.reverse()
            for i in removeIndex:
                circuitLogicGateNodeList.pop(i)
            removeIndex.clear()
        
        return topoOrder
    
    def __TransformAreaUnitToNanometers(self, area: float, gdsUnit: float) -> float:
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