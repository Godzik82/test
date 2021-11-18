# -*- coding: cp1251 -*-
import asyncio
import warnings
from bs4 import BeautifulSoup
import requests
import json


async def get_page_data(q):
    author_name = q.find("small", class_="author").text.strip()
    quote = q.find("span", class_="text").text.strip()
    quote = quote[1:len(quote)-2]
    tags = []
    taqs_quotes = q.find("div", class_="tags").find_all("a", class_="tag")
    for j in range(len(taqs_quotes)):
        tags.append(taqs_quotes[j].text)
    if author_name not in quotes_dict.keys():
        author_link = "https://quotes.toscrape.com" + q.find_all("span")[1].find("a").get("href")
        author_info = BeautifulSoup(requests.get (url=author_link, headers= headers, verify= False).text, "lxml")
        date_born = author_info.find("div", class_="author-details").find_all("p")[0].find("span", class_="author-born-date").text.strip()
        place_born = author_info.find("div", class_="author-details").find_all("p")[0].find("span", class_="author-born-location").text[3:].strip()
        discription = author_info.find("div", class_="author-description").text.strip()
        quotes_dict[author_name] = {
            "Date born": date_born,
            "Place born": place_born,
            "Biografy": discription,
            "Quotes": [{"quote": quote, "tags": tags}]
        }
    else:
        quotes_dict[author_name]["Quotes"].append({"quote": quote, "tags": tags})


async def main():
    global quotes_dict, dict_list, headers
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    dict_list, tasks = [], []
    quotes_dict = {}
    page_num = 1
    next = ""

    while next != "No quotes":
        url = f"https://quotes.toscrape.com/page/{page_num}"
        page_req = requests.get(url=url, headers=headers, verify=False).text
        page_soup = BeautifulSoup(page_req, "lxml")
        quotes = page_soup.find_all("div", class_="col-md-8")[1].find_all("div", class_="quote")
        for quote in quotes:
            task = asyncio.create_task(get_page_data(quote))
            tasks.append(task)
        await asyncio.gather(*tasks)
        try:
            next = page_soup.find("li", class_="next").text.strip()
            page_num += 1
        except AttributeError:
            next = "No quotes"

    with open("test.json", "w", encoding="utf-8") as file:
        json.dump(quotes_dict, file, indent=4, ensure_ascii=False)

    print(f"Обработано страниц - {page_num}. Количество авторов - {len(quotes_dict)}.")

if __name__ == "__main__":
    asyncio.run(main())
