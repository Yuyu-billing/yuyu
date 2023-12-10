#!/bin/bash

case $1 in
  current_time)
    date +"Current Time: %Y-%m-%d %H:%M:%S %Z"
    ;;
  
  end_of_month)
    current_month=$(date +%m)
    current_year=$(date +%Y)
    last_day=$(cal $current_month $current_year | awk 'NF {DAYS = $NF} END {print DAYS}')
    end_of_month=$(date -d "$current_year-$current_month-$last_day 23:59:00" +"%Y-%m-%d %H:%M:%S %Z")
    sudo systemctl stop systemd-timesyncd
    sudo date -s "$end_of_month"
    date +"Time set to end of the month: %Y-%m-%d %H:%M:%S %Z"
    echo "Restarting cron"
    sudo systemctl restart cron
    ;;

  end_of_day)
    days_offset=$2
    end_of_day=$(date -d "+$days_offset days 23:59:00" +"%Y-%m-%d %H:%M:%S %Z")
    sudo systemctl stop systemd-timesyncd
    sudo date -s "$end_of_day"
    date +"Time set to end of the day: %Y-%m-%d %H:%M:%S %Z"
    echo "Restarting cron"
    sudo systemctl restart cron
    ;;

  add_minutes)
    minutes_offset=$2
    end_of_day=$(date -d "+$minutes_offset minutes" +"%Y-%m-%d %H:%M:%S %Z")
    sudo systemctl stop systemd-timesyncd
    sudo date -s "$end_of_day"
    date +"Time set to: %Y-%m-%d %H:%M:%S %Z"
    echo "Restarting cron"
    sudo systemctl restart cron
    ;;

  reset_time)
    sudo systemctl stop systemd-timesyncd
    sudo systemctl start systemd-timesyncd
    date +"Time reset to NTP"
    echo "Restarting cron"
    sudo systemctl restart cron
    ;;

  *)
    echo "Usage: $0 {current_time|end_of_month|end_of_day <days_offset>|reset_time}"
    exit 1
    ;;
esac
