from setsat.logicGate.dataTypes.logicGateBehavior_t import LogicGateBehavior_t
from setsat.logicGate.dataTypes.logicGatePolygons_t import LogicGatePolygons_t

class CircuitLogicGateNode_t:

    def __init__(self, cellName: str, logicGateBehavior: LogicGateBehavior_t,
                 logicGatePolygons: LogicGatePolygons_t, logicGateID: str,
                 pinList: list[str]) -> None:
        self.cellName           = cellName
        self.logicGateBehavior  = logicGateBehavior
        self.logicGatePolygons  = logicGatePolygons
        self.logicGateID        = logicGateID
        
        expectedNumberOfPins = len(logicGateBehavior.inputPinList) + len(logicGateBehavior.outputPinList)
        if expectedNumberOfPins != len(pinList):
            raise ValueError(f'{cellName} expected pins= {expectedNumberOfPins}, received= {len(pinList)}')

        self.inputWireList      = []
        self.outputWireList     = []
        self.wireToLogicGatePin = self.__ComputeWireToLogicGatePin(pinList, logicGateBehavior)
    
    def __repr__(self) -> str:
        return f'{self.logicGateID}|{self.cellName}|{self.wireToLogicGatePin}'

    ##############################################
    ### ----------- PRIVATE METHODS ---------- ###
    ##############################################

    def __ComputeWireToLogicGatePin(self, pinList: list[str],
                                    logicGateBehavior: LogicGateBehavior_t) -> dict[str, str]:
        wireToLogicGatePin = {}

        wireAndPin = pinList[0]
        if len(wireAndPin.split('(')) == 1: # wires not labeled 
            raise ValueError(f'Verilog without labeled wires')
        
        # wires labeled
        for wireAndPin in pinList:
            wire = wireAndPin.split('(')[1].replace(')', '')
            pin  = wireAndPin.split('(')[0].replace('.', '')

            if pin not in logicGateBehavior.inputPinList and pin not in logicGateBehavior.outputPinList:
                raise ValueError(f'{self.cellName} does not have {pin} pin')
            
            if pin in logicGateBehavior.inputPinList:
                self.inputWireList.append(wire)
            else:
                self.outputWireList.append(wire)

            wireToLogicGatePin[wire] = pin

        return wireToLogicGatePin

######################################
### @Author: Mateus Estrêla Pietro ###
######################################