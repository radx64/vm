
# R - register name after instruction
# I - constant value (immv)
opcodeToMnemonic = {
    0x00 : ("MOV",  "R", "R"),
    0x01 : ("SET",  "R", "I"),
    0x02 : ("LOAD", "R", "R"),
    0x03 : ("STOR", "R", "R"),
    0x10 : ("ADD",  "R", "R"),
    0x11 : ("SUB",  "R", "R"),
    0x12 : ("MUL",  "R", "R"),
    0x13 : ("DIV",  "R", "R"),
    0x14 : ("MOD",  "R", "R"),
    0x15 : ("OR",   "R", "R"),
    0x16 : ("AND",  "R", "R"),
    0x17 : ("XOR",  "R", "R"),
    0x18 : ("NOT",  "R"),
    0x19 : ("SHL",  "R"),
    0x1A : ("SHR",  "R"),
    0x20 : ("CMP",  "R", "R"),
    0x21 : ("JZ",   "I"),
    0x22 : ("JNZ",  "I"),
    0x23 : ("JC",   "I"),
    0x24 : ("JNC",  "I"),
    0x25 : ("JBE",  "I"),
    0x26 : ("JA",   "I"),
    0x30 : ("PUSH", "R"), 
    0x31 : ("POP",  "R"),
    0x40 : ("JMP",  "I"), 
    0x41 : ("JMPR", "R"),
    0x42 : ("CALL", "I"), 
    0x43 : ("CALR", "R"),
    0x44 : ("RET",  ), 
    0x50 : ("IN",   "I", "R"),
    0x51 : ("OUT",  "I", "R"),
    0xFF : ("HALT", )
}

generalRegisterIdToName = {
    0x00 : "R0",
    0x01 : "R1",
    0x02 : "R2",
    0x03 : "R3",
    0x04 : "R4",
    0x05 : "R5",
    0x06 : "R6",
    0x07 : "R7",
    0x10 : "I0",
    0xFD : "FR",
    0xFE : "SP",
    0xFF : "PC"
}

class Decompiler:
    def __init__(self):
        self.binary = ""

    def load(self, binaryStream):
        self.binary = binaryStream
        self.source = ""

    def run(self):
        index = 0;
        while index < len(self.binary):
            currentByte = self.binary[index]
            index = self._decode(index)

    def getDecompiled(self):
        return(self.source[0:-1])

    def _appendToEndOfASource(self, code):
        self.source += code

    def _appendNewLineToSource(self):
        self.source +="\n"

    def _decodeConstant(self, index):
        constantValue = "0x{0:02X}".format(self.binary[index])
        self._appendToEndOfASource(constantValue)

    def _decodeRegister(self, index):
        try :
            byte = self.binary[index]
            self._appendToEndOfASource(generalRegisterIdToName[byte])
        except KeyError :
            error = "Couldn't decode register 0x{0:02X} at byte 0x{1:02X}".format(byte, index)
            raise Exception("Decompilation failed! " + error)

    def _decodeOperands(self, opcode, index):
        try:
            operandsCount = len(opcodeToMnemonic[opcode])
            for operIndex, operand in enumerate(opcodeToMnemonic[opcode]):
                if operIndex == 0:   #skipping operand 0 as its mnemonic name
                    if operandsCount > 1:
                        self._appendToEndOfASource(operand + " ")
                    else:
                        self._appendToEndOfASource(operand)  
                    continue
                if operand == "R":
                    self._decodeRegister(index+operIndex)
                elif operand == "I":
                    self._decodeConstant(index+operIndex)
                else:
                    raise Exception("Error! Unknown operand type in mnemonic Look Up Table") # pragma: no cover
                if (operIndex < operandsCount-1):
                    self._appendToEndOfASource(", ")
            self._appendNewLineToSource()
            return operandsCount
        except KeyError:
            error = "Couldn't decode instruction 0x{0:02X} at byte 0x{1:02X}".format(opcode, index)
            raise Exception("Decompilation failed! " + error)

    def _decode(self,index):
        opcode = self.binary[index]
        newIndex = index + self._decodeOperands(opcode, index)
        return newIndex;

import sys
import array
def help():  # pragma: no cover
    helpText = ("Usage: decompiler.py source.bin output.asm\n"
                "\t source.bin - program filename \n"
                "\t output.asm - decompiled source code\n")
    print(helpText)

def readSource():  # pragma: no cover
    try:
        source = open(sys.argv[1], 'rb')
        return array.array('B', source.read()).tostring()
    except FileNotFoundError as e:
        raise Exception ("Source file " + sys.argv[1] + " not found")

def writeOutput(sourceCode):  # pragma: no cover
    try:
        output = open(sys.argv[2], 'w')
        output.write(sourceCode)
    except FileNotFoundError as e:
        raise Exception ("Couldn't create " + sys.argv[1] + " file") 

def main():  # pragma: no cover
    if len(sys.argv) != 3:
        help()
        return
    decompiler = Decompiler()
    decompiler.load(readSource())
    decompiler.run()
    writeOutput(decompiler.getDecompiled())

if __name__ == '__main__':  # pragma: no cover
    try:
        main()
    except Exception as e:
        print(e)