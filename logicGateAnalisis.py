# python logicGateAnalisis.py < targetCells.txt

from setsat.logicGate.dataTypes.standardCellLibrary import StandardCellLibrary_t, CellTechnology_e

from setsat.logicGate.__susceptibilitySimulation.logicGateSusceptibilityMethod import LogicGateSusceptibilityMethod_e
from setsat.singleEventTransientParser import SingleEventTransientParser

# cellTechnology = CellTechnology_e.CMOS_NANGATE_15_NANOMETERS
# gdsFilePath    = 'cellLib/NanGate_15nm_OCL.gds'

cellTechnology = CellTechnology_e.CMOS_NANGATE_45_NANOMETERS
gdsFilePath    = 'cellLib/NangateOpenCellLibrary.gds'

# cellTechnology = CellTechnology_e.BICMOS_IHP_130_NANOMETERS
# gdsFilePath    = 'cellLib/sg13g2_stdcell.gds'

cellLibrary  = StandardCellLibrary_t(cellTechnology)
setParser    = SingleEventTransientParser(cellLibrary)

targetCellList = []
while True:
    try:
        cell = input()
        targetCellList.append(cell)
    except EOFError:
        break

setParser.AddCellLayoutToAnalisis(gdsFilePath, targetCellList)

setParser.ComputeLogicGatesArea()
setParser.ComputeLogicGatesTruthTable()


# particleFlux = 3.6e-09
# susceptibilityMethod = LogicGateSusceptibilityMethod_e.PROBABILISTIC_TRANSFER_MATRIX
# setParser.ComputeLogicGatesSusceptibility(susceptibilityMethod, particleFlux)

# susceptibilityMethod = LogicGateSusceptibilityMethod_e.SENSITIVE_NODES_BY_INPUT_VECTOR
# setParser.ComputeLogicGatesSusceptibility(susceptibilityMethod)

susceptibilityMethod = LogicGateSusceptibilityMethod_e.SUSCEPTIBILITY_BY_INPUT_VECTOR
setParser.ComputeLogicGatesSusceptibility(susceptibilityMethod)