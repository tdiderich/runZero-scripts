# Risk Assessment Reporting

This script will run through a series of runZero searches to perform a risk assessment on your environment. By default, this uses every query currently in the runZero default Query Library as of 12/14/2022. You can see these queries in the `queries.csv` file. 

You could also add your own searches based on your requirements. To do this, just add them to the CSV file. 

# Output

This results will output 3 CSVs: 

1. Executive Report - report showing the counts of assets for each search 
2. Action Report (Assets) - breakout of all the searches that matches for each asset 
3. Action Report (Risks) - breakout of all the assets that matches each search 
