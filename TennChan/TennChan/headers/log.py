class important:

	def __init__(self, msg, length = 15, bokstav="="):
		self.length = length
		self.txt = msg
		self.let = bokstav
		print(bokstav*length, self.txt, bokstav*length)
	def end(self):
		print(self.let*((self.length*2)+2+len(self.txt)),"\n")
	def __del__(self): 
		self.end()