#!/bin/bash

# Start cron
service cron start

# Execute the main script
/usr/bin/python3 /app/monitor_file.py
