import requests
import os
from datetime import date
from twilio.rest import Client

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").

alphavantage_api_key = os.environ["ALPHAVANTAGE_API_KEY"]
news_api_key = os.environ["NEWS_API_KEY"]
twilio_account_sid = os.environ["TWILIO_ACCOUNT_SID"]
twilio_auth_token = os.environ["TWILIO_AUTH_TOKEN"]

stock_price_parameters = {
    "symbol": STOCK,
    "function": "TIME_SERIES_DAILY",
    "apikey": alphavantage_api_key,
}

stock_price_response = requests.get(url="https://www.alphavantage.co/query",params=stock_price_parameters)
stock_price_response.raise_for_status()
price_data = stock_price_response.json()["Time Series (Daily)"]
# transfer all closing_price into a list
data_list = [float(value['4. close']) for (key,value) in price_data.items()]
# print(data_list)
price_difference = data_list[0]-data_list[1]

up_down = None
if price_difference > 0:
    up_down = "🔺"
else:
    up_down = "🔻"


price_diff_in_percent = round((price_difference/data_list[1])*100, 2)
# print(price_diff_in_percent)

if abs(price_diff_in_percent) > 5:
    # print("Get News")
## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.
    news_api_parameters = {
        "q": COMPANY_NAME,
        "from": date.today(),
        "sortBy": "popularity",
        "apiKey": news_api_key,
    }

    news_api_response = requests.get(url="https://newsapi.org/v2/everything", params=news_api_parameters)
    news_api_response.raise_for_status()
    news_data = news_api_response.json()['articles']
    three_articles = news_data[:3]
    # print(three_articles)


## STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number. 

    formatted_messages = [f"{STOCK}: {up_down}{price_diff_in_percent}%\nHeadline: {article['title']}\nBrief: {article['description']}" for article in three_articles]
    print(formatted_messages)

    client = Client(twilio_account_sid, twilio_auth_token)
    for formatted_message in formatted_messages:
        message = client.messages.create(
            body=formatted_message,
            from_=os.environ["TWILIO_PHONE_NUMBER"],
            to=os.environ["PHONE_NUMBER"]
        )
        print(message.status)





#Optional: Format the SMS message like this: 
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

