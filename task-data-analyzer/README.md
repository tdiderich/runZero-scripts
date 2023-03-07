# Task log handler

## Overview

This script is meant to take a set of runZero task data files and return high level info about each task

1. Reads the task data files
2. Parses the files and generates output CSVs that are easiler to read

## Configuration

1. Download your task data files(s) from the runZero UI
2. Unzip the file(s)
3. Update the `TASK_LIST = ['task1', 'task2', 'etc]` to the filenames for your tasks

## Output

1. One directory per task called `<taskname>-out` which contains a few CSVs with consolidated info on the task data like host information and error summary

- `errors.csv` is the raw error log with counts
- `errors_reduced.csv` is the summarized error log with counts and lists of hosts affected
- `results.csv` is the list of hosts and ports open
- `summary.csv` is the summary of the findings with information like host count, unique ports seen, etc

2. `results_summary.csv` is the high level info for each task in a single CSV
3. `results_summary_full.csv` is similar to `results_summary.csv`
