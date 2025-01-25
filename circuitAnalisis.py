# python circuitAnalisis.py < targetCells.txt

from setsat.circuit.circuitSusceptibilityMethod import CircuitSusceptibilityMethod_e
from setsat.logicGate.dataTypes.standardCellLibrary import StandardCellLibrary_t, CellTechnology_e
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


verilogFilePath = 'circuitVerilog/c17.v'
setParser.AddCircuitVerilog(verilogFilePath)


setParser.ComputeCircuitArea()
setParser.ComputeCircuitDistinctGates()

susceptibilityMethod = CircuitSusceptibilityMethod_e.SENSITIVE_GATES_BY_INPUT_VECTOR
setParser.ComputeCircuitSusceptibility(susceptibilityMethod)