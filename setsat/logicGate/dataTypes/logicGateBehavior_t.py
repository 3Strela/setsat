from setsat.logicGate.dataTypes.logicGatePolygons_t import LogicGatePolygons_t

class LogicGateBehavior_t:
    def __init__(self, logicGatePolygons: LogicGatePolygons_t) -> None:
        self.truthTable: dict[str, dict[str, int]] = {}

        self.inputPinList  = self.__LogicGateInputPinList(logicGatePolygons)
        self.outputPinList = self.__LogicGateOutputPinList(logicGatePolygons)

        self.numberOfBits        = len(self.inputPinList)
        self.totalNumberOfInputs = 2**self.numberOfBits

        self.sensitiveNodes = self.__InstantiateSensitiveNodes()

    ##############################################
    ### ----------- PRIVATE METHODS ---------- ###
    ##############################################

    def __LogicGateInputPinList(self, logicGatePolygons: LogicGatePolygons_t) -> list[str]:
        polyPolygonLabelList = logicGatePolygons.polyPolygonLabelList
        
        inputPinSet = set()
        for poliPolygonLabel in polyPolygonLabelList:
            if poliPolygonLabel.label != None and       \
               poliPolygonLabel.label[0:3] != 'net' and \
               poliPolygonLabel.label[0:3] != 'met':
                inputPinSet.add(poliPolygonLabel.label)
        
        inputPinList = list(inputPinSet)
        inputPinList.sort()
        return inputPinList

    def __LogicGateOutputPinList(self, logicGatePolygons: LogicGatePolygons_t) -> list[str]:
        metalPolygonLabelList = logicGatePolygons.metalPolygonLabelList

        outputPinSet = set()
        for metalPolygonLabel in metalPolygonLabelList:
            label = metalPolygonLabel.label
            if label[0:3] != 'met' and label[0:3] != 'net' and label != 'VDD' \
                and label != 'VSS' and label not in self.inputPinList:
                outputPinSet.add(label)

        outputPinList = list(outputPinSet)
        outputPinList.sort()
        return outputPinList

    def __InstantiateSensitiveNodes(self) -> dict[str, dict[str, list[str]]]:
        sensitiveNodes = {}
        for i in range(self.totalNumberOfInputs):
            binaryInput = bin(i).split('b')[1].zfill(self.numberOfBits)

            sensitiveNodes[binaryInput] = {}
            for outputPin in self.outputPinList:
                sensitiveNodes[binaryInput][outputPin] = []
        
        return sensitiveNodes

######################################
### @Author: Mateus Estrêla Pietro ###
######################################