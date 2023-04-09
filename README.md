# Telegraf for Touch

## Updates
1. Changed API service port from 10180 to 10190; this gives telegraf its own port.
2. Moved all API management and metric parsing into Telegraf extension.


## 1	Introduction
iTAT (Integrated Telegraf Agent for TouchDesigner) runs a Telegraf agent as a subprocess of TouchDesigner. Telegraf is an open source software from InfluxData that collects hardware metrics. Upon receiving the first couple batches of metrics, iTAT will automatically build out an HTTP API based on the host system. The API is accessible at `http://<host-IP>:10190/api/<metric url>`. The metrics are also accessible as a list of dictionaries (based on Telegraf’s JSON output), or a prettified version as a dictionary keyed by each metric name.

iTAT has only been developed and tested on Windows and currently requires an NVIDIA graphics card to start.

## 2	Installation
To install the telegraf agent, navigate to `/iTAT/telegraf/InfluxData` and unzip the telegraf.rar; choose 'Extract to telegraf/'. Then copy and paste the InfluxData folder into your Program Files directory. Copy the whole folder, not just the contents.

The iTAT folder can be stored anywhere on your machine, but all of the files must stay together and maintain the given directory structure.

You can also download and install from InfluxData's website; instructions found here: https://docs.influxdata.com/telegraf/v1.21/administration/windows_service/
Don't follow step 3. If you install as a service, the tox won't be able to find the correct telegraf process to kill when exiting. 

## 3	Starting Telegraf
NOTE: You must run TouchDesigner as an administrator.
NOTE: You must have an NVIDIA graphics card; an option to run with NVIDIA metrics will come in a future update.

The tox can be found at `/iTAT/Build/iTAT.tox`. Simply drag and drop the telegraf_agent TOX into your network and click the `Start` button under the `Telegraf` tab

## 4	Accessing metric data
There are two ways to access metrics. The first is through the provided Python extension:
### Python
`op(<telegraf agent base>).TelegrafMetrics` will return a deserialized version of the metrics that Telegraf posted to TouchDesigner; this is a list of dictionaries.

`op(<telegraf agent base>).PrettyMetrics` will return a dictionary with a key for each metric

### HTTP
The second is to use the auto-generated HTTP API. The endpoints are listed in the webpage documentation in `/iTAT/API_ref/iTAT API.html`

NOTE: The HTTP API should be built automatically when the webserver first receives metrics and should persist after saving and reopining the .toe file, as the base is not set to reload on start. However, the API can be manually built and initialized. Building the API is not really recommended, but Initializing it, which just destroys all the endpoints, may be useful if moving to a different machine or changing the configuration file.

NOTE: The metrics are also posted to a Prometheus client, which can be accessed at `http://<host-IP>:9273/metrics`, but this was employed for testing the agent, and nothing has really be done with it. If you're using a Prometheus server, it *should* work, but no promises.

