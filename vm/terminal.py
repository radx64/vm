
class Port:
	def __init__(self, readHandle, writeHandle):
		self.readHandle = readHandle
		self.writeHandle = writeHandle

	def read(self):
		if hasattr(self.readHandle, '__call__'):
			return self.readHandle()
		else:
			raise Exception("Not a callable")
		return 0

	def write(self, value):
		if hasattr(self.writeHandle , '__call__'):
			self.writeHandle(value)
		else:
			raise Exception("Not a callable")

class Terminal:
	def __init__(self):
		self.readbuffer = ''
		self.writebuffer = ''

		self.controlPort = Port(self._controlPortRead, self._controlPortWrite)
		self.dataInPort  = Port(self._dataInPortRead, None)
		self.dataOutPort = Port(None, self._dataOutPortWrite)

	def _controlPortRead(self):
		return None

	def _controlPortWrite(self, value):
		pass

	def _dataInPortRead(self):
		return input("CPU asked for data:")

	def _dataOutPortWrite(self, value):
		print (str(value))

if __name__ == '__main__':
	terminal = Terminal()
	terminal.dataOutPort.write("A")
	terminal.dataOutPort.write("B")
	terminal.dataOutPort.write("C")
	print("Got from terminal " + terminal.dataInPort.read())

