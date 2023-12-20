#!/bin/bash

# Get the directory of the current script
current_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Define the cron jobs
cron_job1="1 0 1 * * $current_dir/process_invoice.sh"
cron_job2="5 0 * * * $current_dir/handle_unpaid_invoice.sh"

# Define the identifiers
identifier1="process_invoice"
identifier2="handle_unpaid_invoice"

# Check if the cron jobs already exist
if ! crontab -l | grep -q "$identifier1"; then
    # Add the cron job if it doesn't exist
    (crontab -l; echo "$cron_job1") | crontab -
fi

if ! crontab -l | grep -q "$identifier2"; then
    # Add the cron job if it doesn't exist
    (crontab -l; echo "$cron_job2") | crontab -
fi