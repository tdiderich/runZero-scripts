# Task log handler

## Overview

This script is meant to take a set of runZero task data files and return high level info about each task

1. Reads the task data files
2. Parses the files and generates output CSVs that are easiler to read

## Configuration

1. Download your task data files(s) from the runZero UI
2. Unzip the file(s)
3. Update the `TASK_LIST = ['task3', 'task4', 'task1']` to the filenames for your tasks

## Output

1. One directory per task called `<taskname>-out` which contains a few CSVs with consolidated info on the task data like host information and error summary
2. `results_summary.csv` is the high level info for each task in a single CSV
3. `results_summary_full.csv` is similar to `results_summary.csv`
