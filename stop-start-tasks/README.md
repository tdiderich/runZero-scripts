# Start and Pause Tasks

This is a script that can be used to start or pause recurring tasks.

Sample output:

```shell
$ python3 run.py                                                                                                      [10:46:38]
Paused: 93f6bb9e-1950-4dae-954f-e6e3b44ed092
Paused: 4c436500-11a2-49ba-b626-46723ab05e10
Paused: 69a7a0b8-fdf4-4409-a97a-85c51098c8e6
Started: b93c3a05-4778-4f88-bbc1-45f3285f80d9
Started: 68f082ba-712e-4639-a67e-e418b996730f
```

You can update the searches for tasks to start or pause in the global variables:

```python
PAUSE_SEARCH = "status:active recur:t not source:passive"
START_SEARCH = "status:paused recur:t not source:passive"
```

If you ONLY want to start or pause tasks, you can just comment out the code as needed:

1. This block does the starts:

```python
tasks_to_pause = get_tasks(search=PAUSE_SEARCH)
if len(tasks_to_pause) > 0:
    for t in tasks_to_pause:
        id = t["id"]
        success = pause_task(id=id)
        if success:
            print(f"Paused: {id}")
        else:
            print(f"Failed to pause: {id}")
else:
    print("No tasks to pause")
```

2. This block does the pauses:

```python
tasks_to_pause = get_tasks(search=PAUSE_SEARCH)
if len(tasks_to_pause) > 0:
    for t in tasks_to_pause:
        id = t["id"]
        success = pause_task(id=id)
        if success:
            print(f"Paused: {id}")
        else:
            print(f"Failed to pause: {id}")
else:
    print("No tasks to pause")
```
