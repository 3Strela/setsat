from gdstk import Cell, read_gds

from setsat.circuit.circuitParser import CircuitParser

from setsat.logicGate.__initialSettings.extractPolygons.extractInterestLayers import ExtractInterestLayerPolygons
from setsat.logicGate.__initialSettings.extractPolygons.extractNodePolygons   import ExtractNodePolygons
from setsat.logicGate.__initialSettings.logicGateGraph.logicGateGraph         import LogicGateGraph

from setsat.logicGate.__susceptibilitySimulation.susceptibilitySimulation import GenerateTruthTable, SusceptibilitySimulation

from setsat.logicGate.dataTypes.componentID_e        import ComponentID_e
from setsat.logicGate.dataTypes.standardCellLibrary  import StandardCellLibrary_t

from setsat.logicGate.__susceptibilitySimulation.logicGateSusceptibilityMethod import LogicGateSusceptibilityMethod_e
import setsat.logicGate.__susceptibilitySimulation.__logicGateSusceptibilityMethodFunctions as logicGateSusceptibilityMethod

from setsat.circuit.circuitSusceptibilityMethod import CircuitSusceptibilityMethod_e
import setsat.circuit.__circuitSusceptibilityMethodFunctions as circuitSusceptibilityMethod

import numpy as np

class SingleEventTransientParser:
    ''' Class responsible for handling the entire flow regarding SETs '''

    def __init__(self, cellLibrary: StandardCellLibrary_t) -> None:
        self.__cellList: list[Cell] = []
        self.__cellLibrary   = cellLibrary
        self.__circuitParser = None
        self.__unit          = None

    ##############################################
    ### +++++++++++ PUBLIC METHODS +++++++++++ ###
    ##############################################

    def AddCellLayoutToAnalisis(self, gdsFilePath: str, targetCellList: list[str] = None) -> None:
        gdsFile     = read_gds(gdsFilePath)
        self.__unit = gdsFile.unit

        targetCellSet = set(targetCellList)
        for cell in gdsFile.cells:
            if targetCellList is None:
                self.__cellList.append(cell)
            elif cell.name in targetCellSet:
                self.__cellList.append(cell)

    def AddCircuitVerilog(self, verilogFilePath: str) -> None:
        self.__circuitParser = CircuitParser(verilogFilePath, self.__cellList, self.__cellLibrary, self.__unit)

    def ComputeCircuitSusceptibility(self, susceptibilityMethod: CircuitSusceptibilityMethod_e,
                                        particleFlux: float|None = None) -> None:
        match susceptibilityMethod:
            case CircuitSusceptibilityMethod_e.SENSITIVE_GATES_BY_INPUT_VECTOR:
                methodFunction = circuitSusceptibilityMethod.SensitiveGatesByInputVector
            case _:
                raise NotImplementedError
        
        with open('Circuit' + str(methodFunction.__name__) + '.tsv', 'w') as tsvFile:
            pass

        methodFunction(self.__circuitParser, particleFlux, self.__unit)
    
    def ComputeCircuitTruthTable(self) -> None:
        raise NotImplementedError

    def ComputeLogicGatesArea(self) -> None:
        with open('LogicGatesArea.tsv', 'w') as tsvFile:
            tsvFile.write(f"Cell's name\tArea(In {self.__unit} m^2)\n")

            for cell in self.__cellList:
                metalPolygonPoints = []
                for polygon in cell.polygons:
                    if polygon.layer in self.__cellLibrary.metalLayerList:
                        metalPolygonPoints.append(polygon.points)
                
                metalPolygonPoints = np.vstack(metalPolygonPoints)
                minPoint = np.min(metalPolygonPoints, axis=0)
                maxPoint = np.max(metalPolygonPoints, axis=0)

                height = maxPoint[1] - minPoint[1]
                width  = maxPoint[0] - minPoint[0]
                area   = str(round(height * width, 12)).replace('.', ',')
                
                tsvFile.write(f"{cell.name}\t{area}\n")
    
    def ComputeLogicGatesSusceptibility(self, logicGatesusceptibilityMethod: LogicGateSusceptibilityMethod_e,
                                        particleFlux: float|None = None) -> None:
        match logicGatesusceptibilityMethod:
            case LogicGateSusceptibilityMethod_e.SENSITIVE_NODES_BY_INPUT_VECTOR:
                methodFunction = logicGateSusceptibilityMethod.SensitiveNodesByInputVector
            case LogicGateSusceptibilityMethod_e.SUSCEPTIBILITY_BY_INPUT_VECTOR:
                methodFunction = logicGateSusceptibilityMethod.SusceptibilityByInputVector
            case LogicGateSusceptibilityMethod_e.PROBABILISTIC_TRANSFER_MATRIX:
                methodFunction = logicGateSusceptibilityMethod.ProbabilisticTransferMatrix
            case _:
                raise NotImplementedError
        
        with open('LogicGates' + str(methodFunction.__name__) + '.tsv', 'w') as tsvFile:
            pass

        for cell in self.__cellList:
            logicGateGraph    = self.__BuildLogicGateGraph(cell)
            logicGatePolygons = logicGateGraph.logicGatePolygons
            logicGateBehavior = SusceptibilitySimulation(logicGateGraph)

            methodFunction(cell.name, logicGatePolygons, logicGateBehavior, particleFlux, self.__unit)

    def ComputeLogicGatesTruthTable(self) -> None:
        with open('LogicGatesTruthTable.tsv', 'w') as tsvFile:
            for cell in self.__cellList:
                logicGateGraph    = self.__BuildLogicGateGraph(cell)
                logicGateBehavior = GenerateTruthTable(logicGateGraph)

                numberOfBits        = logicGateBehavior.numberOfBits
                totalNumberOfInputs = logicGateBehavior.totalNumberOfInputs

                tsvFile.write(f"{cell.name}:\n")
                
                logicGateOutputs = '\t'.join(logicGateBehavior.outputPinList)
                inputVectorOrder = ''.join(logicGateBehavior.inputPinList)
                
                tsvFile.write(f"InputVector({inputVectorOrder})\t{logicGateOutputs}\n")
                for i in range(totalNumberOfInputs):
                    binaryInput = bin(i).split('b')[1].zfill(numberOfBits)

                    results = []
                    for outputPin in logicGateBehavior.outputPinList:
                        outputResult = logicGateBehavior.truthTable[binaryInput][outputPin]
                        results.append(str(outputResult))

                    results = '\t'.join(results)
                    tsvFile.write(f"{binaryInput}\t{results}\n")
                    
                tsvFile.write('\n')

    def ResetCellLayoutToAnalisis(self) -> None:
        self.__cellList = []

    ##############################################
    ### ----------- PRIVATE METHODS ---------- ###
    ##############################################

    def __BuildLogicGateGraph(self, cell: Cell) -> LogicGateGraph:
        # Extracting & Labeling logic gate polygons
        logicGatePolygons = ExtractInterestLayerPolygons(cell, self.__cellLibrary)
        nodePolygons      = ExtractNodePolygons(logicGatePolygons)
        logicGatePolygons.AddComponent(nodePolygons, ComponentID_e.NODE)

        # Building logic gate graph
        logicGateGraph = LogicGateGraph(logicGatePolygons)
        return logicGateGraph

######################################
### @Author: Mateus Estrêla Pietro ###
######################################