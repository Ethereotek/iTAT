agent = op("telegraf_agent")

op("telegraf_agent/Telegraf").par.file = "Python/extTelegraf.py"
op("telegraf_agent/Utilities").par.file = "Python/Utilities.py"
op("telegraf_agent/MetricsHandler").par.file = "Python/MetricsHandler.py"