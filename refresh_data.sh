# This file should be called every 24 hours by cron. This deletes the previous scraped data and scrapes $
# To insert this into cron use the command: `crontab -e` and insert this line:
# `0 0 * * *  bash /home/agent25/agent-25/refresh_data.sh`
cd /usr/src/app
rm scraper/scraped.json
bash model/start.sh