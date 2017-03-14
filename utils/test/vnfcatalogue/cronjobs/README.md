# CRONJOB Directory

## Helper to setup cronjob to fill the vnf table

There are two important parameters that need to be set in github.js
before running cronjob.


```
   access_token : generate an access token from github account for accessing
   the github apis. This is necessary as the non access token limit tends to 
   be 50 api calls per hour.
   delta : the threshold between the last update of the row of the vnf table
   and current time. It is measured in seconds.
```

Enter the details namely username and password in the **database.js**.
Then setup the cronjob by putting the following line in the crontab

In the crontab

```bash
    node github
```
