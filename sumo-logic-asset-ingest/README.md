# runZero asset export to Sumo Logic

This folder provides two options for exporting your runZero assets to Sumo Logic.

1. `http-endpoint.py` will post your assets to an HTTP endpoint
2. `http-endpoint-aws-lambda.py` can be used in an AWS Lambda function - Lambdas have some oddities that you need to work around which is why the second script made sense
3. `script-action.py` will run as a script source on the Sumo Logic Collector - this has not been tested but should work :)
