# python logicGateAnalisis.py < targetCells\inTest.txt

from setsat.logicGate.dataTypes.standardCellLibrary import StandardCellLibrary_t, CellTechnology_e

from setsat.logicGate.__susceptibilitySimulation.logicGateSusceptibilityMethod import LogicGateSusceptibilityMethod_e
from setsat.singleEventTransientParser import SingleEventTransientParser

cellTechnology = CellTechnology_e.CMOS_NANGATE_45_NANOMETERS

cellLibrary  = StandardCellLibrary_t(cellTechnology)
setParser    = SingleEventTransientParser(cellLibrary)

# gdsFilePath    = 'cellLib/sg13g2_stdcell.gds'
# gdsFilePath    = 'cellLib/NanGate_15nm_OCL.gds'
gdsFilePath    = 'cellLib/NangateOpenCellLibrary.gds'

targetCellList = []
runtimeCell    = {}
while True:
    try:
        cell = input()
        targetCellList.append(cell)

        runtimeCell[cell] = 0
    except EOFError:
        break

setParser.AddCellLayoutToAnalisis(gdsFilePath, targetCellList)

# setParser.ComputeLogicGatesArea()
# setParser.ShowTruthTable()

particleFlux = 3.6e-09
susceptibilityMethod = LogicGateSusceptibilityMethod_e.SENSITIVE_NODES_BY_INPUT_VECTOR
setParser.ComputeLogicGatesSusceptibility(particleFlux, susceptibilityMethod)