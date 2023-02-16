# Task log handler

## Overview

This script is meant to take a runZero task log and turn the errors into a more usable CSV format.

1. Reads the task logs from the `TASK_LIST` list
2. Finds all logs with errors
3. Generates counts for all the different errors and writes to `{filename}_errors.csv`

## Configuration

1. Download your task log(s) from the runZero UI
2. Unzip the file(s)
3. Add your task log(s) to this directory
4. Update the `TASK_LIST` based on your filenames
