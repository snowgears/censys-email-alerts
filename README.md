# Censys New Host Risks Email Alerts
Script to showcase email alerts for newly discovered host risks in the [Censys ASM platform](https://censys.io/).

**Steps for getting started:**
- Install the libraries in requirements.txt
   - ```pip install --upgrade -r requirements.txt```
- Set your Censys ASM API key
   - ```censys asm config```
   - (find your ASM API key here: https://app.censys.io/integrations)
- Set the variables in the **alert_host_risks.py** file
   - **MAIL_RECIPIENTS** - add any email addresses you want to recieve alerts
   - **MAIL_SUBJECT** - the subject line of the alert email
   - **MAIL_BODY** - the body of the alert email
   - **CHECK_INTERVAL** - how often to check for new host risks *(in minutes)*



Now just run the script:
``` 
python alert_host_risks.py
```
