# runZero asset export to Sumo Logic

This folder provides two options for exporting your runZero assets to Sumo Logic.

1. `http-endpoint.py` will post your assets to an HTTP endpoint - you could put this in an AWS Lambda or run it locally
2. `script-action.py` will run as a script source on the Sumo Logic Collector - this has not been tested but should work :)
