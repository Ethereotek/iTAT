class DevUtils:
    
	def __init__(self, telegraf_agent):
		print("DevUtils created")
		self.telegraf_agent = telegraf_agent

		self.Telegraf_proc = None
	

	def TestFunc(self):
		print("Test Func")

	def Build(self):
		try:
			self.StopTelegraf()
		except AttributeError:
			pass

		self.telegraf_agent.par.Initapi.pulse()
		self.telegraf_agent.par.Lockapi = True
		self.telegraf_agent.op("Telegraf").par.file = ""
		self.telegraf_agent.op("Utilities").par.file = ""

		self.telegraf_agent.save("Build/iTAT.tox")
	
	def Dev(self):
		self.telegraf_agent.op("Telegraf").par.file = "Python/extTelegraf.py"
		self.telegraf_agent.op("Utilities").par.file = "Python/Utilities.py"

	def StopTelegraf(self):
			# gets the process object stored in Telegraf_proc and calls terminate method
			# resets the Telegraf_proc variable
		self.Telegraf_proc.terminate()
		self.Telegraf_poc = None
		print("telegraf process has been terminated")