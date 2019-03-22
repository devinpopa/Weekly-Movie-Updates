import requests
import html5lib
from bs4 import BeautifulSoup
from twilio.rest import Client
import os

def convert_percentage(pct):
  temp = pct[:-1]
  numeric = int(temp)
  return numeric

def scrape_rt():
  highest_rated = []
  
  req = requests.get('https://www.rottentomatoes.com')
  req.encoding = 'utf-8'
  soup = BeautifulSoup(req.content, "html.parser")

  new_movies = soup.find('table', id="Opening", class_="movie_list")
  for row in new_movies.findAll('tr'):
    l_col = row.find('td', class_='left_col')
    m_col = row.find('td', class_='middle_col')
    r_col = row.find('td', class_='right_col right')
    rating = l_col.find('span', class_='tMeterScore')
    
    if rating is not None:
      rating_text = rating.get_text()
      rating_numeric = convert_percentage(rating_text)
      title = m_col.find('a').get_text()
      release_date = r_col.find('a').get_text().strip()
      if rating_numeric >= 80:
        highest_rated.append((title, release_date, rating_numeric))
    else:
      continue

  return highest_rated

def send_update():
	# Bash environment variables used to hide information.
  ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
  AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
  client = Client(ACCOUNT_SID, AUTH_TOKEN)
  
  msg = ""
  found = scrape_rt()
  for t,d,r in found:
    msg += "{}({}) has an average critical rating of {}/100!\n".format(t, d, r)
  
  sent = client.messages.create(
    to=os.environ["MY_PHONE_NUM"],
    from_=os.environ["TWILIO_SENDER_NUM"],
    body=msg
  )

send_update()
  