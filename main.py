from setsat.dataTypes.standardCellLibrary     import StandardCellLibrary_t, CellTechnology_e
from setsat.dataTypes.susceptibilityMethod    import SusceptibilityMethod_e
from setsat.parser.singleEventTransientParser import SingleEventTransientParser

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
        cellName = input()
        targetCellList.append(cellName)
    except EOFError:
        break

setParser.AddGDSToAnalisis(gdsFilePath, targetCellList)

# setParser.ComputeLogicGatesArea()
# setParser.ShowTruthTable()

particleFlux = 3.6e-09
susceptibilityMethod_e = SusceptibilityMethod_e.SUSCEPTIBILITY_BY_INPUT_VECTOR
setParser.ComputeLogicGatesSusceptibility(particleFlux, susceptibilityMethod_e)