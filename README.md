# Telegraf for Touch

## Updates
1. All documented HTTP endpoints now all return valid data
2. The command to start the telegraf process is now run directly by the subprocess module instead of through a .cmd file, meaning it should actually start on your computer. The process object is also stored in the Telegraf extension, and terminated with a call to that object, meaning termination is now much safer. It should be noted that during testing, stopping the telelgraf process sometimes resulted in a NoneType error, however, this was likely due to reinitializing the Telegraf extension. If this occurs, telegraf can be stopped from Task Manager.
3. The unzipped telegraf folder now uses the correct pathing, so the telegraf.exe can be found.
4. POSIX and date-formatted timestamps are now available for all parent metrics
5. The webserver now responds to the telegraf process. Previously, it returned nothing, meaning telegraf would concatenate each batch of metrics, and the TelegrafMetrics object would grow larger with each update.
6. The API build is delayed for the first couple of batches to account for inconsistent CPU batching. API building will be handled more elegantly in future updates.


## 1	Introduction
iTAT (Integrated Telegraf Agent for TouchDesigner) runs a Telegraf agent as a subprocess of TouchDesigner. Telegraf is an open source software from InfluxData that collects hardware metrics. Upon receiving the first batch of metrics, iTAT will automatically build out an HTTP API based on the host system. The API is accessible at `http://<host-IP>:10180/api/<metric url>`. The metrics are also accessible as a list of dictionaries (based on Telegraf’s JSON output), or a prettified version as a dictionary keyed by each metric name.

NOTE: This is an alpha release that has undergone minimal testing. There's a great deal of functionality that hasn't been implemented, and two extensions that need to be built out. The auto-generated HTTP API is also only half implemented, and documentation is sparse. There is no guarantee this will work properly, or even at all.

NOTE: This is for Windows only ¯\\_(ツ)_/¯


## 2	Installation
To install the telegraf agent, navigate to `/iTAT/telegraf/InfluxData` and unzip the telegraf.rar; choose 'Extract to telegraf/'. Then copy and paste the InfluxData folder into your Program Files directory. Copy the whole folder, not just the contents.

The iTAT folder can be stored anywhere on your machine, but all of the files must stay together and maintain the given directory structure.

You can also download and install from InfluxData's website; instructions found here: https://docs.influxdata.com/telegraf/v1.21/administration/windows_service/
Don't follow step 3. If you install as a service, the tox won't be able to find the correct telegraf process to kill when exiting. 

## 3	Starting Telegraf
NOTE: You must run TouchDesigner as an administrator.
NOTE: You must have an NVIDIA graphics card; an option to run with NVIDIA metrics will come in a future update.
To use the telegraf_agent .tox, it is preferable to drag and drop the file into the `External .tox` parameter of a baseCOMP instead of dragging the file directly into the TouchDesigner network.

The metric toggle parameters found on the component do not currently have any effect, but will be used in the future to allow the user to customize what metrics are gathered. It is not recommended to change the telegraf.conf file, as there are not yet any methods for handling variations in metrics.

## 4	Accessing metric data
There are two ways to access metrics. The first is through the provided Python extension:
### Python
`op(<telegraf agent base>).TelegrafMetrics` will return a deserialized version of the metrics that Telegraf posted to TouchDesigner; this is a list of dictionaries.

`op(<telegraf agent base>).PrettyMetrics` will return a dictionary with a key for each metric

### HTTP
The second is to use the auto-generated HTTP API. The endpoints are listed in the webpage documentation in `/iTAT/API_ref/iTAT API.html`

NOTE: The HTTP API should be built automatically when the webserver first receives metrics and should persist after saving and reopining the .toe file, as the base is not set to reload on start. However, the API can be manually built and initialized. Building the API is not really recommended, but Initializing it, which just destroys all the endpoints, may be useful if moving to a different machine or changing the configuration file.

NOTE: The metrics are also posted to a Prometheus client, which can be accessed at `http://<host-IP>:9273/metrics`, but this was employed for testing the agent, and nothing has really be done with it. If you're using a Prometheus server, it *should* work, but no promises.

