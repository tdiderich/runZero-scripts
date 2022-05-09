# Stop active tasks

This script will stop all tasks that are currently active and/or queued to run. You could update the search param to only stop active tasks `status:active` or queued `status:queued` if preferred. 

# Sample outputs 
```
1 task running 

$ python3 stop-active-tasks/run.py
Stopped: 885ed75c-4cc8-4f58-9a8d-f541b2e8144e

No tasks running 
$ python3 stop-active-tasks/run.py
No tasks running.
```