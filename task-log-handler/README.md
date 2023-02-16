# Task log handler

## Overview

This script is meant to take a runZero task log and turn the errors into a more usable CSV format.

1. Reads the task log at `task.log` in the same directory
2. Finds all logs with errors
3. Generates counts for all the different errors and writes to `errors.csv`

## Configuration

1. Download your task log from the runZero UI
2. Unzip the file
3. Add your task log to this directory at `task.log`
