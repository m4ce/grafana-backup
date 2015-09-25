# Grafana backup tool
Simple tool to backup Grafana configuration in pure JSON format using the HTTP API.

The backup currently supports the following:

* Dashboards (including Home)
* Data sources
* Users
* Organizations
* Front-end settings
* Admin settings

See the usage section for more details.

## Usage
Any command line options can be overridden from a YAML formatted configuration file (see --config)

Currently, it's recommended using basic authentication (instead of API token) for API access as some endpoints (e.g. orgs, users etc.)
require grafana admin permissions (see https://github.com/grafana/grafana/issues/2821#issuecomment-143044297).

You can run the tool with --help to check out all the command line options available.

```
usage: grafana-backup.py [-h] [-H API_HOST] [-P API_PORT] [-k API_KEY]
                         [-u USERNAME] [-p PASSWORD] [-o OUTPUT_DIR]
                         [-c CONFIG_FILE]
                         [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]

Grafana Backup Tool

optional arguments:
  -h, --help            show this help message and exit
  -H API_HOST, --host API_HOST
                        API host (default: 127.0.0.1)
  -P API_PORT, --port API_PORT
                        API port (default: 3001)
  -k API_KEY, --key API_KEY
                        API key
  -u USERNAME, --user USERNAME
                        User for basic authentication
  -p PASSWORD, --password PASSWORD
                        Password for basic authentication
  -o OUTPUT_DIR, --output OUTPUT_DIR
                        Directory where backup will be stored (default: .)
  -c CONFIG_FILE, --config CONFIG_FILE
                        Optional configuration file to read options from
                        (default: ./grafana-backup.yaml)
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set the logging level (default: INFO)
```

I might write a script to do the restore part in the future, feel free to make a pull request for it.

For now, you would have to script it quickly as follows:

```
curl -X PUT -H 'Content-Type: application/json' -H 'Authorization: Bearer <api_key>' http://<grafana_host>:<grafana_port>/api/datasources -d@datasource.json
curl -X POST -H 'Content-Type: application/json' -H 'Authorization: Bearer <api_key>' http://<grafana_host>:<grafana_port>/api/dashboards/db -d@dashboard.json
```

## Contact
Matteo Cerutti - matteo.cerutti@hotmail.co.uk
