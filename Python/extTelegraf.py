import subprocess
# import os
import json
# import datetime
import re
import Utilities
import copy

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

		self.generic_metrics = [ "system", "nvidia_smi", "temp", "mem", "netstat", "disk"]
		self.complex_metrics = {
			"cpu":self.buildCPUMetrics,
			"net":self.buildNetworkMetrics
		}

		# when the telegraf process is started, Popen returns the process object
		# and assigns it to Telegraf_proc

		self.Telegraf_proc = None
		self.numUpdates = 0

	# starting and stopping the telegraf agent
	def StartTelegraf(self):
			# path to the telegraf executable and config files
		telegraf_exe = "C:\\Program Files\\InfluxData\\telegraf\\telegraf.exe"
		telegraf_conf = "C:\\Program Files\\InfluxData\\telegraf\\telegraf.conf"
		
			# command to run using Popen to run telegraf
		command = [telegraf_exe, "--config", telegraf_conf]
			# return object assigned to Telegraf_proc
		self.Telegraf_proc = subprocess.Popen(command)

		# for development purposes only
		try:
			op("../DevUtils").Telegraf_proc = copy.copy(self.Telegraf_proc)
		except:
			pass
		print("telegraf process has started")

	def StopTelegraf(self):
			# gets the process object stored in Telegraf_proc and calls terminate method
			# resets the Telegraf_proc variable
		try:
			self.Telegraf_proc.terminate()
			self.Telegraf_poc = None
			print("telegraf process has been terminated")
		except AttributeError:
			op("../DevUtils").StopTelegraf()
			print("telegraf process terminated from DevUtils")

		self.numUpdates = 0

	def InitAPI(self):
			# deletes the API tree
			# finds all children of the parent metric directories and destroys them
		for name, dir in self.metric_directories.items():
			try:
				children = dir.findChildren(type=COMP, name="*", path="*", depth=1)
				# print(children)
				for child in children:
					child.destroy()
			except:
				pass
		
		self.thisComp.store("API", False)
	
	#### BUILDING API TREE ####

	def buildMetric_Generic(self, name, metric_dict):
		ty = 0				# deals with arranging the metric COMPs
		self.name = name				# name of the metric
		self.metric_dict = metric_dict	# dictionary containing all metric endpoints

			# create a base COMP in the metric parent called "metrics"
		self.metrics_base = op("api/" + self.name).create("baseCOMP", "metrics")

			# for each field in the dict, create another COMP inside the "metrics" baseCOMP
			# and name it the key of that field
			# then create a textDAT inside that COMP and call it "data"
			# jsonify the current dictionary entry and dump it in the textDAT

		for key, val in self.metric_dict["fields"].items():

			self.metric_comp = self.metrics_base.create("baseCOMP", key)
			self.metric_dat = self.metric_comp.create("textDAT", "data")

			data = json.dumps({key:val})
			self.metric_dat.text = data

			self.metric_comp.nodeY = ty
			ty -= 150
			
			# add channel to api chop
			# new_channel = f'/{self.name}/metrics/{key}/data'
			# num_endpoints = str(op("time_base/inst").numChans)
			# op("time_base/inst").par['name' + num_endpoints] = new_channel
		
		# print(f'{self.name} metric has been built')

		## CPU and Network metrics are snowflakes and need special methods	
	def buildCPUMetrics(self, cpus):
		cpuTx = 0
		# cpus_array = []
		try:
			for key, val in cpus.items():
				metricTy = 0
				cpu_base = op("api/cpu").create("baseCOMP", key.replace("-", "_"))
				metrics_base = cpu_base.create("baseCOMP", "metrics")

				cpu_base.nodeX = cpuTx
				cpuTx += 200

				for _key, _val in cpus[key]["fields"].items():

					# if "guest" in _key:
					# 	pass
					# else:
					metric_comp = metrics_base.create("baseCOMP", _key)
					metric_dat = metric_comp.create("textDAT", "data")

					data = json.dumps({_key:_val})
					metric_dat.text = data

					metric_comp.nodeY = metricTy
					metricTy -= 150
		except:
			print("apparently there's a key error?")

	def buildNetworkMetrics(self, net):
		interfaceTx = 0
		for key, val in net.items():
			metricTy = 0
			# key = re.sub("[() /-]+", "_", key)
			interface_base = op("api/net").create("baseCOMP", re.sub("[()/\- ]+", "_", key))
			metrics_base = interface_base.create("baseCOMP", "metrics")

			interface_base.nodeX = interfaceTx
			interfaceTx += 200

			for _key, _val in net[key]["fields"].items():
				metric_comp = metrics_base.create("baseCOMP", _key)
				metric_dat = metric_comp.create("textDAT", "data")
				data = json.dumps({_key:_val})
				metric_dat.text = data

				metric_comp.nodeY = metricTy
				metricTy -= 150

	def BuildAPI(self):
		for metric in self.generic_metrics:
			try:
				metric_dict = self.PrettyMetrics[metric]
				self.buildMetric_Generic(metric, metric_dict)
			except Exception as e:
				print(e)

		for key, val in self.complex_metrics.items():
			metric_dict = self.PrettyMetrics[key]
			val(metric_dict)
		
		self.thisComp.store("API", True)

		# op("time_series/inst").lock = True

	#### HANDLING NEW BATCH OF METRICS ####
	def PrettifyMetrics(self, metrics_array):
		pretty_metrics = {}

		tagged_metrics = [
			("net", "interface"),
			("cpu", "cpu")
		]

		for m in self.generic_metrics:
			pretty_metrics[m] = self.CollapseMetrics(metrics_array, m)

		for tm in tagged_metrics:
			pretty_metrics[tm[0]] = self.CollapseTaggedMetrics(metrics_array, tm[0], tm[1] )

		return pretty_metrics
	
	def CollapseMetrics(self, metrics_array, metric_name):
		# this can probably be called CollapseAndPrettyMetrics
		# if there is only one instance of the a name in the metrics
		# I don't think there will be an error

		# metrics_array is the whole array
		# metric_name is the name of a metric that is spread across multiple objects
		
			# create a template pretty metric dictionary
		collapsed_metric = {
			"fields":{},
			"tags":{},
			"timestamp":-1
		}
			# collect timestamps from the multiple metric objects to be collapsed
		timestamps = []
			# cycle through the whole array of metrics
			# if name of the metric is equal to our target metric
			# cycle through its fields and tags adding them 
			#	to the collapsed pretty metric
			# also append the timestamp
			#	we'll then take the max and use that as the one timestamp
		for metric in metrics_array:
			if metric["name"] == metric_name:
				for field, value in metric["fields"].items():
					collapsed_metric["fields"][field] = value
				
				for tag, value in metric["tags"].items():
					collapsed_metric["tags"][tag] = value
				
				timestamps.append(metric["timestamp"])
		
		try:
			max_timestamp = max(timestamps)
		except:
			max_timestamp = -1
		collapsed_metric["timestamp"] = max_timestamp
		collapsed_metric["timestamp_formatted"] = Utilities.FormatTimestamp(max_timestamp)

		return collapsed_metric
	

	def CollapseTaggedMetrics(self, metrics_array, metric_name, tag_key):
		temp_array = []

		for metric in metrics_array:
			if metric["name"] == metric_name:
				temp_array.append(metric)
		
		metrics_array = temp_array

		collapsed_metric = {

		}

		for metric in metrics_array:
			key = metric["tags"][tag_key]
			if key in collapsed_metric:
				pass
			else:

				collapsed_metric.update({key:{"fields":{},"tags":{}}})
			for field, value in metric["fields"].items():
				collapsed_metric[key]["fields"][field] = value
			
			for tag, value in metric["tags"].items():
				collapsed_metric[key]["tags"][tag] = value


		return collapsed_metric
	#### POSTING METRICS TO THE API ####

	def PostMetrics(self):
		for m in self.generic_metrics:
			self.PostMetrics_Generic(m, self.PrettyMetrics[m])

		self.PostCPUMetrics(self.PrettyMetrics["cpu"])
		self.PostNetworkMetrics(self.PrettyMetrics["net"])

		for m in self.generic_metrics:
			# update the last_update DAT with POSIX and date/time formatted timestamps
			op(f'api/{m}/last_update')["POSIX", 1] = self.PrettyMetrics[m]["timestamp"]
			op(f'api/{m}/last_update')["formatted", 1] = self.PrettyMetrics[m]["timestamp_formatted"]

		return 1

	def PostMetrics_Generic(self, name, metrics):
		self.name = name
		self.metrics = metrics
		for field, value in self.metrics["fields"].items():
			op(f'api/{self.name}/metrics/{field}/data').text = json.dumps({field:value})
	
	def PostCPUMetrics(self, cpu_metrics):
	# print(cpu_metrics)
		for cpu, metrics in cpu_metrics.items():
			cpu = cpu.replace("-", "_")
			for field, value in metrics["fields"].items():
				# print(field)
				if "guest" in field:
					pass
				else:
					# print(field)
					# print(f'api/cpu/{cpu}/metrics/{field}/data')
					op(f'api/cpu/{cpu}/metrics/{field}/data').text = json.dumps({field:value})

	def PostNetworkMetrics(self, net_metrics):
		
		for iface, metrics in net_metrics.items():
			# iface = iface.replace("-", "_")
			iface = re.sub("[()/\- ]+", "_", iface)
			for field, value in metrics["fields"].items():
				op(f'api/net/{iface}/metrics/{field}/data').text = json.dumps({field:value})
	
	
	def HandleMetrics(self, new_metrics):
		self.TelegrafMetrics = new_metrics
		self.numUpdates += 1

		return self.numUpdates