## Selenium attendance script
1. Install chromedriver from https://chromedriver.storage.googleapis.com/index.html?path=114.0.5735.90/ for m1-arm-64
2. Create .env with your wmata account username , password and which card history you want to pull ( by default 0 )
```
username= ...
password= ...
card_index= 0
```
*Change the card_index only if you have multiple cards*

The usage_data.json contains the parsed data from wmata and is cached for subsequent runs of the script. 
You can also change the start_date, end_date in the script as per your need.