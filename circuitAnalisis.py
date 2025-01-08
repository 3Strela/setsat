# python circuitAnalisis.py < targetCells\Nangate_45nm.txt

from setsat.circuit.circuitSusceptibilityMethod import CircuitSusceptibilityMethod_e
from setsat.logicGate.dataTypes.standardCellLibrary import StandardCellLibrary_t, CellTechnology_e
from setsat.singleEventTransientParser import SingleEventTransientParser

import time
import datetime

cellTechnology = CellTechnology_e.CMOS_NANGATE_45_NANOMETERS

cellLibrary  = StandardCellLibrary_t(cellTechnology)
setParser    = SingleEventTransientParser(cellLibrary)

targetCellList = []
while True:
    try:
        cell = input()
        targetCellList.append(cell)
    except EOFError:
        break

gdsFilePath = 'cellLib/NangateOpenCellLibrary.gds'
setParser.AddCellLayoutToAnalisis(gdsFilePath, targetCellList)

verilogFilePath = 'circuitVerilog/c17_minimal.v'
# verilogFilePath = 'circuitVerilog/c432_minimal.v'
setParser.AddCircuitVerilog(verilogFilePath)


particleFlux = 3.6e-09
susceptibilityMethod = CircuitSusceptibilityMethod_e.SENSITIVE_GATES_BY_INPUT_VECTOR
setParser.ComputeCircuitSusceptibility(particleFlux, susceptibilityMethod)