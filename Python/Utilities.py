import math
import datetime

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

def CelciusToFahrenheit(celcius):
	fahrenheit = (celcius * (9/5)) + 32
	return fahrenheit