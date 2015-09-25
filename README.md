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

Example:
{code}
{code}

## Contact
Matteo Cerutti - matteo.cerutti@hotmail.co.uk
