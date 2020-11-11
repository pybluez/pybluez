

class Device:
	name: str
	address: str
	classcode: str

	def __init__(self, name:str, address:str):
		self.name = name
		self.address = address

	def __repr__(self):
		return f"<Blutooth Device '{self.name}' ({self.address})>"