class Telegraf:
    
	def __init__(self, thisComp):
		print("Initiating Telegraf extension")
		self.thisComp = thisComp
		self.telegraf_starter = op("start_telegraf")
		self.telegraf_pid_getter = op("find_telegraf_pid")
		self.pid = op("PID")
		self.telegraf_killer = op("kill_telegraf")

		self.TelegrafMetrics = {}
		self.PrettyMetrics = {}

	def StartTelegraf(self):
		self.telegraf_starter.run()
		print("telegraf process has started")

	def StopTelegraf(self):
		self.telegraf_pid_getter.run()
		if self.pid[0,0]:
			print("Telegraf PID = ", pid[0,0])
			self.telegraf_killer.run()
			self.pid.clear(keepSize = True)
			print("telegraf process has been stopped")
		else:
			print("the telegraf process is not running")