op("telegraf_agent").par.Stop.pulse()

op("telegraf_agent").par.Initapi.pulse()

op("telegrag_agent/Telegraf").par.file = ""
op("telegrag_agent/Utilities").par.file = ""
# op("telegrag_agent/MetricsHandler").par.file = ""

op("telegraf_agent").save("../Build/NamedElements.tox")