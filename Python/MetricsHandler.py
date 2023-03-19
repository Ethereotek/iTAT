import datetime
import json
import math
import re

def FormatUptime(uptime):
	# takes POSIX formatted uptime and formats to days, hours, minutes, seconds
	secondsPerDay = 60*60*24
	secondsPerHour = 60*60
	days = math.floor(uptime/secondsPerDay)
	uptime -= (days*secondsPerDay)
	hours = math.floor(uptime/secondsPerHour)
	uptime -= (hours*secondsPerHour)
	minutes = math.floor(uptime/60)
	uptime -= minutes
	seconds = uptime
	uptime = f'{days}d {hours}h {minutes}m {seconds}s'

	return uptime

def FormatTimestamp(timestamp):
	# takes posix timestamp and formats them into a datetime
	try:
		timestamp = datetime.datetime.fromtimestamp(timestamp)
		formatted_timestamp = timestamp.strftime('%m/%d/%Y %H:%M:%S')
	except:
		formatted_timestamp = "error"
		
	return formatted_timestamp


def CollapseTaggedMetrics(metrics_array, metric_name, tag_key):
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
	

def CollapseMetrics(metrics_array, metric_name):
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
	collapsed_metric["timestamp_formatted"] = FormatTimestamp(max_timestamp)

	return collapsed_metric

	
def ConvertTimestamp(timestamp):
	# date = datetime.datetime.fromtimestamp(timestamp)
	date = datetime.datetime.fromtimestamp(timestamp).strftime("%m-%d-%Y, %H:%M:%S:%p")
	return date

def celciusToFahrenheit(celcius):
	fahrenheit = (celcius * (9/5)) + 32
	return fahrenheit


def ParseTemperature(metric):
	temp = metric["fields"]["temp"]
	tempF = celciusToFahrenheit(temp)
	parsedMetric = {
		"temperature-celcius": temp,
		"temperature-fahrenheit": tempF
	}

	return parsedMetric


def ParseNVIDIAMetrics(nvidia_metrics):
	name = nvidia_metrics["tags"]["name"]
	index = nvidia_metrics["tags"]["index"]

	fields = nvidia_metrics["fields"]

	driver = fields["driver_version"]
	fan_speed = fields["fan_speed"]
	total_memory = str(fields["memory_total"] / 1000) + " GB"
	used_memory = str(fields["memory_used"] / 1000) + " GB"
	power_draw = str(fields["power_draw"]) + " W"

	tempC = fields["temperature_gpu"]
	tempF = celciusToFahrenheit(tempC)
	temperature = {
		"celcius": str(tempC) + " C",
		"fahrenheit": str(tempF) + " F"
	}

	parsedMetric = {
		"name":name,
		"index":index,
		"driver":driver,
		"fan_speed":fan_speed,
		"total_memory":total_memory,
		"used_memory":used_memory,
		"power_draw":power_draw,
		"temperature":temperature
	}

	return parsedMetric

def ParseSystemMetrics(sys_metrics):
	fields = sys_metrics["fields"]

	uptime = FormatUptime(fields["uptime"])
	load5 = fields["load5"]
	last_updated = ConvertTimestamp(sys_metrics["timestamp"])

	parsed_metric = {
		"last_updated":last_updated,
		"load5":load5,
		"uptime":uptime
	}

	return parsed_metric

def ParseMemoryMetrics(mem_metrics):
	fields = mem_metrics["fields"]

	available = fields["available"]/1000000000
	available_p = fields["available_percent"]
	used = fields["used"]/1000000000
	used_p = fields["used_percent"]

	last_update = ConvertTimestamp(mem_metrics["timestamp"])

	parsed_metrics = {
		"last_updated":last_update,
		"available":available,
		"available_p":available_p,
		"used":used,
		"used_p":used_p
	}

	return parsed_metrics


def PostMetrics_Generic(name, generic_metrics):
	for field, value in generic_metrics:
		op(f'api/{name}/metrics/{field}/data').text = json.dumps({field:value})

def ParseCPUMetrics(cpu_metrics):
	return 0

def PostSystemMetrics(system_metrics):
	for field, value in system_metrics["fields"].items():
		op(f'api/system/metrics/{field}/data').text = json.dumps({field:value})

def PostMemoryMetrics(memory_metrics):
	for field, value in memory_metrics["fields"].items():
		op(f'api/mem/metrics/{field}/data').text = json.dumps({field:value})

def PostNVIDIAMetrics(nvidia_metrics):
	for field, value in nvidia_metrics["fields"].items():
		op(f'api/nvidia_smi/metrics/{field}/data').text = json.dumps({field:value})
	
def PostTempMetrics(temp_metrics):
	for field, value in temp_metrics["fields"].items():
		op(f'api/temp/metrics/{field}/data').text = json.dumps({field:value})

def PostNetstatMetrics(netstat_metrics):
	for field, value in netstat_metrics["fields"].items():
		op(f'api/netstat/metrics/{field}/data').text = json.dumps({field:value})

def PostCPUMetrics(cpu_metrics):
	for cpu, metrics in cpu_metrics.items():
		cpu = cpu.replace("-", "_")
		for field, value in metrics["fields"].items():
			op(f'api/cpu/{cpu}/metrics/{field}/data').text = json.dumps({field:value})

def PostNetworkMetrics(net_metrics):
	for iface, metrics in net_metrics.items():
		# iface = iface.replace("-", "_")
		iface = re.sub("[()/\- ]+", "_", iface)
		for field, value in metrics["fields"].items():
			op(f'api/net/{iface}/metrics/{field}/data').text = json.dumps({field:value})

def PostDiskMetrics(disk_metrics):
	for field, value in disk_metrics["fields"].items():
		op(f'api/disk/metrics/{field}/data').text = json.dumps({field:value})

def PrettifyMetrics(metrics_array):
	pretty_metrics = {}
	metrics = [
		"system",
		"mem",
		"nvidia_smi",
		"temp",
		"netstat",
		"disk"
	]

	tagged_metrics = [
		("net", "interface"),
		("cpu", "cpu")
	]

	for m in metrics:
		pretty_metrics[m] = CollapseMetrics(metrics_array, m)

	for tm in tagged_metrics:
		pretty_metrics[tm[0]] = CollapseTaggedMetrics(metrics_array, tm[0], tm[1] )

	return pretty_metrics

def PostMetrics(pretty_metrics):
	
	metrics = [
		"system",
		"mem",
		"nvidia_smi",
		"temp",
		"netstat",
		"disk"
	]

	PostSystemMetrics(pretty_metrics["system"])
	PostNVIDIAMetrics(pretty_metrics["nvidia_smi"])
	PostCPUMetrics(pretty_metrics["cpu"])
	PostNetstatMetrics(pretty_metrics["netstat"])
	PostDiskMetrics(pretty_metrics["disk"])
	PostNetworkMetrics(pretty_metrics["net"])

	for m in metrics:
		# update the last_update DAT with POSIX and date/time formatted timestamps
		op(f'api/{m}/last_update')["POSIX", 1] = pretty_metrics[m]["timestamp"]
		op(f'api/{m}/last_update')["formatted", 1] = pretty_metrics[m]["timestamp_formatted"]