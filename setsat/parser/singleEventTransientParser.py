from gdstk import Cell, read_gds

from setsat.__initialSettings.extractPolygons.extractInterestLayers import ExtractInterestLayerPolygons
from setsat.__initialSettings.extractPolygons.extractNodePolygons   import ExtractNodePolygons
from setsat.__initialSettings.logicGateGraph.logicGateGraph         import LogicGateGraph

from setsat.__susceptibilitySimulation.susceptibilitySimulation import GenerateTruthTable, SusceptibilitySimulation

from setsat.dataTypes.componentID_e        import ComponentID_e
from setsat.dataTypes.susceptibilityMethod import SusceptibilityMethod_e
from setsat.dataTypes.standardCellLibrary  import StandardCellLibrary_t

import setsat.__susceptibilitySimulation.susceptibilityMethodFunctions as susceptibilityFunctions

import numpy as np

class SingleEventTransientParser:
    ''' Class responsible for handling the entire flow regarding SETs '''

    def __init__(self, cellLibrary: StandardCellLibrary_t) -> None:
        self.__cellList: list[Cell] = []
        self.__cellLibrary = cellLibrary
        self.__unit        = None

    ##############################################
    ### +++++++++++ PUBLIC METHODS +++++++++++ ###
    ##############################################

    def AddGDSToAnalisis(self, gdsFilePath: str, targetCellList: list[str] = None) -> None:
        gdsFile     = read_gds(gdsFilePath)
        self.__unit = gdsFile.unit

        targetCellSet = set(targetCellList)
        for cell in gdsFile.cells:
            if targetCellList is None:
                self.__cellList.append(cell)
            elif cell.name in targetCellSet:
                self.__cellList.append(cell)

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
    
    def ComputeLogicGatesSusceptibility(self, particleFlux: float, 
                                        susceptibilityMethod: SusceptibilityMethod_e) -> None:
        match susceptibilityMethod:
            case SusceptibilityMethod_e.SENSITIVE_NODES_BY_INPUT_VECTOR:
                methodFunction = susceptibilityFunctions.SensitiveNodesByInputVector
            case SusceptibilityMethod_e.SUSCEPTIBILITY_BY_INPUT_VECTOR:
                methodFunction = susceptibilityFunctions.SusceptibilityByInputVector
            case SusceptibilityMethod_e.PROBABILISTIC_TRANSFER_MATRIX:
                methodFunction = susceptibilityFunctions.ProbabilisticTransferMatrix
            case _:
                raise NotImplementedError
        
        with open(str(methodFunction.__name__) + '.tsv', 'w') as tsvFile:
            pass

        for cell in self.__cellList:
            logicGateGraph    = self.__BuildLogicGateGraph(cell)
            logicGatePolygons = logicGateGraph.logicGatePolygons
            logicGateBehavior = SusceptibilitySimulation(logicGateGraph)

            methodFunction(cell.name, logicGatePolygons, logicGateBehavior, particleFlux, self.__unit)

    def ShowTruthTable(self) -> None:
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

    def ResetGDSToAnalisis(self) -> None:
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