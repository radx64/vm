class Cpu:    
    WORD_SIZE = 1 << 8
    CARRY_FLAG = 1 << 1
    ZERO_FLAG = 1 << 0

    available_registers = {
    "R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7",
    "FR", "SP", "PC"
    }

    def _initRegisters(self):
        self.registers = {}
        for register in self.available_registers:
            self.registers[register] = 0;
        self.registers["SP"] = 0xFF   

    def _getOpcodeToHandlerMapping(self):
        return {
            0x00 : self.__MOV,
            0x01 : self.__SET,
            0x02 : self.__LOAD,
            0x03 : self.__STOR,
            0x10 : self.__ADD,
            0x11 : self.__SUB,
            0x12 : self.__MUL,
            0x13 : self.__DIV,
            0x14 : self.__MOD,
            0x15 : self.__OR,
            0x16 : self.__AND,
            0x17 : self.__XOR,
            0x18 : self.__NOT,
            0x19 : self.__SHL,
            0x1A : self.__SHR,
            0x20 : self.__CMP,
            0x21 : self.__JZ,
            0x22 : self.__JNZ,
            0x23 : self.__JC,
            0x24 : self.__JNC,
            0x25 : self.__JBE,
            0x26 : self.__JA,
            0x30 : self.__PUSH,
            0x31 : self.__POP,
            0x40 : self.__JMP,
            0x41 : self.__JMPR,
            0x42 : self.__CALL,
            0x43 : self.__CALR,
            0x44 : self.__RET,
            0x50 : self.__IN,
            0x51 : self.__OUT,
            0xFF : self.__HALT }

    @staticmethod
    def __registerIdToName(registerId):
        registerIdToName = {
        0x00 : "R0",
        0x01 : "R1",
        0x02 : "R2",
        0x03 : "R3",
        0x04 : "R4",
        0x05 : "R5",
        0x06 : "R6",
        0x07 : "R7",
        0xFD : "FR",
        0xFE : "SP",
        0xFF : "PC",
        }
        try:
            return registerIdToName[registerId]
        except KeyError:
            raise Exception("Unknown register " + str(registerId))
    
    def __init__(self, ram, terminal, debug=False):
        self.ram = ram
        self.rom = []
        self.running = False
        self.terminal = terminal
        self._initRegisters()
        self.opcodeToHandlerMapping = self._getOpcodeToHandlerMapping()
        self.io_devices = self.__initDevices()
        self.debug = debug

    def __initDevices(self):
        devices = {
        0x00 : self.terminal.controlPort,
        0x01 : self.terminal.dataInPort,
        0x02 : self.terminal.dataOutPort
        }
        return devices

    def __fetchNextByteFromRom(self):
        byte = self.rom[self.registers["PC"]]
        self.registers["PC"] += 1
        return byte

    def __debugPrint(self, string):
        if self.debug:
            print("PC:0x{0:02X} [DEBUG] {1}".format(self.registers["PC"], string))

    def __setRegisterValueById(self, id, value):
        self.__debugPrint("Setting register 0x{0:02X}, with 0x{1:02X}".format(id,value))
        self.registers[self.__registerIdToName(id)] = value

    def __getRegisterValueById(self, id):
        self.__debugPrint("Fetching register 0x{0:02X}".format(id))
        return self.registers[self.__registerIdToName(id)]

    def __validateAddress(self, address):
        if address >= len(self.ram) or address < 0:
            raise Exception ("Address 0x{0:02X} points outside memory "
                "address space (avail. 0x00-0x{1:02X})".format(address, len(self.ram)-1))    

    def __getMemoryValueAt(self, address):
        self.__validateAddress(address)
        return self.ram[address]

    def __setMemoryValueAt(self, address, value):
        self.__validateAddress(address)
        self.ram[address] = value

    def __setCarryFlag(self):
        self.registers["FR"] |= self.CARRY_FLAG

    def __clearCarryFlag(self):
        self.registers["FR"] &= (~self.CARRY_FLAG)

    def __setZeroFlag(self):
        self.registers["FR"] |= self.ZERO_FLAG

    def __clearZeroFlag(self):
        self.registers["FR"] &= (~self.ZERO_FLAG)

    def __isZeroFlagSet(self):
        return bool(self.registers["FR"] & self.ZERO_FLAG)

    def __isCarryFlagSet(self):
        return bool(self.registers["FR"] & self.CARRY_FLAG)

    def __readByteFromPort(self, address):
        try:
            port = self.io_devices[address]
            return port.read()
        except KeyError:
            raise Exception("Port with address 0x{0:02X} not found".format(address))

    def __writeByteToPort(self, address, value):
        try:
            port = self.io_devices[address]
            return port.write(value)
        except KeyError:
            raise Exception("Port with address 0x{0:02X} not found".format(address))


    def __MOV(self):
        destinationRegisterId = self.__fetchNextByteFromRom()
        sourceRegisterId = self.__fetchNextByteFromRom()
        value = self.__getRegisterValueById(sourceRegisterId)
        self.__setRegisterValueById(destinationRegisterId, value)

    def __SET(self):
        registerId = self.__fetchNextByteFromRom()
        constValue = self.__fetchNextByteFromRom()
        self.__setRegisterValueById(registerId, constValue)

    def __LOAD(self):
        destinationRegisterId = self.__fetchNextByteFromRom()
        sourceRegisterId = self.__fetchNextByteFromRom()
        memoryAddress = self.__getRegisterValueById(sourceRegisterId)
        memoryValue = self.__getMemoryValueAt(memoryAddress)
        self.__setRegisterValueById(destinationRegisterId, memoryValue)

    def __STOR(self):
        destinationRegisterId = self.__fetchNextByteFromRom()
        sourceRegisterId = self.__fetchNextByteFromRom()
        memoryAddress = self.__getRegisterValueById(destinationRegisterId)
        memoryValue = self.__getRegisterValueById(sourceRegisterId)
        self.__setMemoryValueAt(memoryAddress, memoryValue)

    def __ADD(self):
        self.__clearCarryFlag()
        destinationRegisterId = self.__fetchNextByteFromRom()
        sourceRegisterId = self.__fetchNextByteFromRom()
        A = self.__getRegisterValueById(sourceRegisterId)
        B = self.__getRegisterValueById(destinationRegisterId)
        if A + B >= self.WORD_SIZE:
            self.__setCarryFlag()
        result = (A + B) % self.WORD_SIZE
        self.__setRegisterValueById(destinationRegisterId, result)

    def __SUB(self):
        self.__clearCarryFlag()
        destinationRegisterId = self.__fetchNextByteFromRom()
        sourceRegisterId = self.__fetchNextByteFromRom()
        A = self.__getRegisterValueById(sourceRegisterId)
        B = self.__getRegisterValueById(destinationRegisterId)
        result = B - A
        if result < 0:
            self.__setCarryFlag()
            result = self.WORD_SIZE - B
        self.__setRegisterValueById(destinationRegisterId, result)

    def __MUL(self):
        self.__clearCarryFlag()
        destinationRegisterId = self.__fetchNextByteFromRom()
        sourceRegisterId = self.__fetchNextByteFromRom()
        A = self.__getRegisterValueById(sourceRegisterId)
        B = self.__getRegisterValueById(destinationRegisterId)
        if A * B >= self.WORD_SIZE:
            self.__setCarryFlag()
        result = (A * B) % self.WORD_SIZE
        self.__setRegisterValueById(destinationRegisterId, result)

    def __DIV(self):
        self.__clearCarryFlag()
        destinationRegisterId = self.__fetchNextByteFromRom()
        sourceRegisterId = self.__fetchNextByteFromRom()
        A = self.__getRegisterValueById(sourceRegisterId)
        B = self.__getRegisterValueById(destinationRegisterId)
        if A == 0:
            raise Exception("Division by 0 error")
        result = B // A
        self.__setRegisterValueById(destinationRegisterId, result)

    def __MOD(self):
        destinationRegisterId = self.__fetchNextByteFromRom()
        sourceRegisterId = self.__fetchNextByteFromRom()
        A = self.__getRegisterValueById(sourceRegisterId)
        B = self.__getRegisterValueById(destinationRegisterId)
        if A == 0:
            raise Exception("Division by 0 error")
        result = B % A
        self.__setRegisterValueById(destinationRegisterId, result)

    def __OR(self):
        destinationRegisterId = self.__fetchNextByteFromRom()
        sourceRegisterId = self.__fetchNextByteFromRom()
        A = self.__getRegisterValueById(sourceRegisterId)
        B = self.__getRegisterValueById(destinationRegisterId)
        result = (B | A)
        self.__setRegisterValueById(destinationRegisterId, result)

    def __AND(self):
        destinationRegisterId = self.__fetchNextByteFromRom()
        sourceRegisterId = self.__fetchNextByteFromRom()
        A = self.__getRegisterValueById(sourceRegisterId)
        B = self.__getRegisterValueById(destinationRegisterId)
        result = (B & A)
        self.__setRegisterValueById(destinationRegisterId, result)

    def __XOR(self):
        destinationRegisterId = self.__fetchNextByteFromRom()
        sourceRegisterId = self.__fetchNextByteFromRom()
        A = self.__getRegisterValueById(sourceRegisterId)
        B = self.__getRegisterValueById(destinationRegisterId)
        result = (B ^ A)
        self.__setRegisterValueById(destinationRegisterId, result)

    def __NOT(self):
        destinationRegisterId = self.__fetchNextByteFromRom()
        A = self.__getRegisterValueById(destinationRegisterId)
        result = (~ A) % self.WORD_SIZE
        self.__setRegisterValueById(destinationRegisterId, result)

    def __SHL(self):
        destinationRegisterId = self.__fetchNextByteFromRom()
        A = self.__getRegisterValueById(destinationRegisterId)
        result = (A << 1) 
        if result >= self.WORD_SIZE :
            result %= self.WORD_SIZE
            self.__setCarryFlag()
        self.__setRegisterValueById(destinationRegisterId, result)

    def __SHR(self):
        destinationRegisterId = self.__fetchNextByteFromRom()
        A = self.__getRegisterValueById(destinationRegisterId)
        result = (A >> 1) 
        self.__setRegisterValueById(destinationRegisterId, result)
        
    def __CMP(self):
        self.__clearCarryFlag()
        self.__clearZeroFlag()
        destinationRegisterId = self.__fetchNextByteFromRom()
        sourceRegisterId = self.__fetchNextByteFromRom()
        B = self.__getRegisterValueById(destinationRegisterId)
        A = self.__getRegisterValueById(sourceRegisterId)
        result = B - A
        if result < 0:
            self.__setCarryFlag()
            result = self.WORD_SIZE - B
        elif result == 0:
            self.__setZeroFlag()

    def __jumpOf(self, offset):
        self.__debugPrint("Jumping of 0x{0:02X}, to 0x{1:02X}".format(offset,
            (self.registers["PC"] + offset)% self.WORD_SIZE ))
        self.registers["PC"] = (self.registers["PC"] + offset) % self.WORD_SIZE 

    def __JZ(self):
        jumpOffset = self.__fetchNextByteFromRom()
        if self.__isZeroFlagSet():
            self.__jumpOf(jumpOffset) 

    def __JNZ(self):
        jumpOffset = self.__fetchNextByteFromRom()
        if not self.__isZeroFlagSet():
            self.__jumpOf(jumpOffset) 

    def __JC(self):
        jumpOffset = self.__fetchNextByteFromRom()
        if self.__isCarryFlagSet():
            self.__jumpOf(jumpOffset) 

    def __JNC(self):
        jumpOffset = self.__fetchNextByteFromRom()
        if not self.__isCarryFlagSet():
            self.__jumpOf(jumpOffset)

    def __JBE(self):
        jumpOffset = self.__fetchNextByteFromRom()
        if (self.__isCarryFlagSet() or self.__isZeroFlagSet()):
            self.__jumpOf(jumpOffset)

    def __JA(self):
        jumpOffset = self.__fetchNextByteFromRom()
        if (self.__isCarryFlagSet() and (not self.__isZeroFlagSet())):
            self.__jumpOf(jumpOffset)

    def __pushToStack(self, value):
        if(self.registers["SP"] == 0):
            raise Exception("Stack pointer is already at 0x00. Can't move it further back.")
        self.registers["SP"] -= 0x1
        self.ram[self.registers["SP"]] = value
        self.__debugPrint("Pushing to stack 0x{0:02X}, SP=0x{1:02X}".format(value,
            self.registers["SP"]))

    def __popFromStack(self):
        if(self.registers["SP"] == 0xFF):
            raise Exception("Stack pointer is already at 0xFF. Can't move it further.")
        A = self.ram[self.registers["SP"]]
        self.registers["SP"] += 0x1
        self.__debugPrint("Poping from stack 0x{0:02X}, SP=0x{1:02X}".format(A, self.registers["SP"]))
        return A        

    def __PUSH (self):
        sourceRegisterId = self.__fetchNextByteFromRom()
        A = self.__getRegisterValueById(sourceRegisterId)
        self.__pushToStack(A)

    def __POP(self):
        destinationRegisterId = self.__fetchNextByteFromRom()
        A = self.__popFromStack()
        self.__setRegisterValueById(destinationRegisterId, A)

    def __JMP(self):
        jumpOffset = self.__fetchNextByteFromRom()
        self.__jumpOf(jumpOffset)

    def __JMPR(self):
        sourceRegisterId = self.__fetchNextByteFromRom()
        jumpAddress = self.__getRegisterValueById(sourceRegisterId)
        self.registers["PC"] = jumpAddress

    def __CALL(self):
        functionPointerOffset = self.__fetchNextByteFromRom()
        self.__debugPrint("Calling function ahead: 0x{0:02X}".format(functionPointerOffset))
        self.__pushToStack(self.registers["PC"])
        self.__jumpOf(functionPointerOffset)

    def __CALR(self):
        sourceRegisterId = self.__fetchNextByteFromRom()
        functionPointer = self.__getRegisterValueById(sourceRegisterId)
        self.__pushToStack(self.registers["PC"])
        self.registers["PC"] = functionPointer

    def __RET(self):
        functionPointer = self.__popFromStack()
        self.__debugPrint("Returning from function to PC = : 0x{0:02X}".format(functionPointer))
        self.registers["PC"] = functionPointer

    def __IN(self):
        portAddress = self.__fetchNextByteFromRom()
        value = self.__readByteFromPort(portAddress)
        destinationRegisterId = self.__fetchNextByteFromRom()
        self.__setRegisterValueById(destinationRegisterId, value)

    def __OUT(self):
        portAddress = self.__fetchNextByteFromRom()
        sourceRegisterId = self.__fetchNextByteFromRom()
        value = self.__getRegisterValueById(sourceRegisterId)
        self.__writeByteToPort(portAddress, value)

    def __HALT(self):
        self.running = False

    def run(self, program):
        self.registers["PC"] = 0x00
        self.rom = program
        self.rom = self.rom + [0xFF]*(0xFF - len(self.rom))
        self.running = True
        while self.running: 
            instruction = self.__fetchNextByteFromRom()
            self.__debugPrint("Executing instruction: 0x{0:02X}".format(instruction))
            try:
                self.opcodeToHandlerMapping[instruction]() 
            except Exception as e:
                print (e)
                raise Exception(e)
