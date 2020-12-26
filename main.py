import requests
import datetime
import math
import os
from send_sms import send_sms

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
UP_ARROW = "\U000025B2"
DOWN_ARROW = "\U000025BC"
NO_MOVE_ARROW = ""
PCT_DIFF_INDICATOR = 0.02 # Indicator for when to monitor stock movement
TODAY = datetime.datetime.today() # Today's date
DAY_0 = TODAY - datetime.timedelta(days=2)  # Identify previous day
strDAY_0 = DAY_0.strftime("%Y-%m-%d")   # Convert to YY-MM-DD format
DAY_Neg1 = DAY_0 - datetime.timedelta(days=1)   # Identify day before day_0
strDAY_Neg1 = DAY_Neg1.strftime("%Y-%m-%d")    # Convert to YY-MM-DD format



## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").

stock_data_API_Key = os.environ["ALPHAVANTAGE_API_AUTH_TOKEN"]
stock_data_endpoint = "https://www.alphavantage.co/query"


stock_data_parameters = {
    "function": "TIME_SERIES_DAILY_ADJUSTED",
    "symbol": STOCK,
    "apikey": stock_data_API_Key
}

response = requests.get(url=stock_data_endpoint, params=stock_data_parameters)
response.raise_for_status()

stock_data = response.json()

stock_data_Day_0 = stock_data["Time Series (Daily)"][strDAY_0]
stock_data_Day_Neg1 = stock_data["Time Series (Daily)"][strDAY_Neg1]

# Get Closing price on Day 0 and Day Neg1
stock_closing_price_Day_0 = float(stock_data_Day_0["5. adjusted close"])
stock_closing_price_Day_Neg1 = float(stock_data_Day_Neg1["5. adjusted close"])
pct_movement = (stock_closing_price_Day_0 - stock_closing_price_Day_Neg1) / stock_closing_price_Day_Neg1
print(pct_movement)
str_pct_movement = "{:.0%}".format(abs(pct_movement))
if pct_movement > 0:
    # Positive increase
    str_pct_movement_arrow = UP_ARROW
elif pct_movement < 0:
    str_pct_movement_arrow = DOWN_ARROW
else:
    pct_movement = NO_MOVE_ARROW
if abs(pct_movement) >= PCT_DIFF_INDICATOR:
    print("Get News")


## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 

news_endpoint = "https://newsapi.org/v2/everything"
news_data_API_Key = os.environ["NEWS_API_AUTH_TOKEN"]
news_query_keyword = COMPANY_NAME

news_data_parameters = {
    "q": news_query_keyword,
    "apikey": news_data_API_Key
}

response = requests.get(url=news_endpoint, params=news_data_parameters)
response.raise_for_status()

news_data = response.json()["articles"]

print(news_data)

## STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number. 

#Optional: Format the SMS message like this:

# Article Count Variable
article_count = 0
news_source = ""
for ix in range(len(news_data)):
    if len(news_source) != 0:
        if news_data[ix]["source"]["name"] == news_source:
            # Skip iteration to get a news article from a different source
            continue
    article_count += 1
    news_source = news_data[ix]["source"]["name"]
    news_headline = news_data[ix]["title"]
    news_brief = news_data[ix]["description"]
    news_url = news_data[ix]["url"]
    if ix == 0:
        msg_text = f"{STOCK}: {str_pct_movement_arrow}{str_pct_movement}"
    msg_text += f"\n\nHeadline: {news_headline}\nBrief: {news_brief}\nURL: {news_url}"
    # After 3 articles have been added, exit loop
    if article_count == 3:
        break

send_sms(msg_text)

"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

