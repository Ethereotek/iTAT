import subprocess
import os
import json
import datetime
import re

class Telegraf:
    
	def __init__(self, thisComp):
		print("Initiating Telegraf extension")
		self.thisComp = thisComp

		self.TelegrafMetrics = {} 	# metrics as they arrive from telegraf
		self.PrettyMetrics = {}		# metrics prettified by metric handler

		self.metric_directories = {
			"nvidia":op("api/nvidia_smi"),
			"system":op("api/system"),
			"mem":op("api/mem"),
			"netstat":op("api/netstat"),
			"cpu":op("api/cpu"),
			"temp":op("api/temp"),
			"disk":op("api/disk"),
			"net":op("api/net")

		}

		self.Telegraf_proc = None

	# starting and stopping the telegraf agent
	def StartTelegraf(self):
		telegraf_exe = "C:\\Program Files\\InfluxData\\telegraf\\telegraf.exe"
		telegraf_conf = "C:\\Program Files\\InfluxData\\telegraf\\telegraf.conf"
		
		command = [telegraf_exe, "--config", telegraf_conf]
		self.Telegraf_proc = subprocess.Popen(command)
		print("telegraf process has started")

	def StopTelegraf(self):
		self.Telegraf_proc.terminate()
		self.Telegraf_poc = None
		print("telegraf process has been terminated")


	# def BuildAPI(self):
	# 	pass

	def InitAPI(self):
		for name, dir in self.metric_directories.items():
			try:
				children = dir.findChildren(type=COMP, name="*", path="*", depth=1)
				print(children)
				for child in children:
					child.destroy()
			except:
				pass
		
		self.thisComp.store("API", False)
	

	#### POSTING METRICS TO THE API ####

	def PostMetrics_Generic(self, name, metrics):
		self.name = name
		self.metrics = metrics
		for field, value in self.metrics:
			op(f'api/{self.name}/metrics/{field}/data').text = json.dumps({field:value})
	
	def PostCPUMetrics(self, cpu_metrics):
	# print(cpu_metrics)
		for cpu, metrics in cpu_metrics.items():
			cpu = cpu.replace("-", "_")
			for field, value in metrics["fields"].items():
				op(f'api/cpu/{cpu}/metrics/{field}/data').text = json.dumps({field:value})

	def PostNetworkMetrics(self, net_metrics):
		
		for iface, metrics in net_metrics.items():
			# iface = iface.replace("-", "_")
			iface = re.sub("[()/\- ]+", "_", iface)
			for field, value in metrics["fields"].items():
				op(f'api/net/{iface}/metrics/{field}/data').text = json.dumps({field:value})
	
	
	def HandleMetrics(self, new_metrics):
		self.TelegrafMetrics = new_metrics