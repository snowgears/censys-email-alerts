# Censys New Host Risks Email Alerts
This script searches every 60 minutes *(by default)* for newly discovered host risks in the [Censys ASM platform](https://censys.io/). If any are found, emails will be sent to all configured recipients with a csv attachment of all newly found risks.

```
Checking for new host risks...
No new host risks.
Checking for new host risks...
No new host risks.
Checking for new host risks...
No new host risks.
Checking for new host risks...
11 new host risks found.
Email we will be sending from: exampleSender@gmail.com
Sent email alert to: exampleReceiver@example.com
```
![](https://i.imgur.com/r3Nr4Tz.png)

# Steps for getting started:
- Install the libraries in requirements.txt
   - ```pip install --upgrade -r requirements.txt```
- Set your Censys ASM API key
   - ```censys asm config```
   - (find your ASM API key here: https://app.censys.io/integrations)
- Set the variables in the **alert_host_risks.py** file
   - **MAIL_RECIPIENTS** - add any email addresses you want to recieve alerts
      - *the format here is a string seperated by semicolons and spaces:*
      - ```"example1@example.com; example2@example.com"```
   - **MAIL_SUBJECT** - the subject line of the alert email
   - **MAIL_BODY** - the body of the alert email
   - **CHECK_INTERVAL** - how often to check for new host risks *(in minutes)*
   - **RISK_SEVERITY_LOGLEVEL** - choose the minimum risk level you want to be alerted on. Options are 1, 2, 3, 4. (low, medium, high, critical)
- Make sure you are signed into Outlook locally with the account you will be sending the alerts from

## Now just run the script:
``` 
python alert_host_risks.py
```

The script is set to run every 60 minutes by default. When new host risks are discovered, an email will be sent to the configured **MAIL_RECIPIENTS** with an attached csv.
