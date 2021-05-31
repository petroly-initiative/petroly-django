from typing import Dict
from bs4 import BeautifulSoup
import requests, json, re, csv, sys



url = sys.argv[1]
file_name = sys.argv[2]

cms = requests.get(url)
soup = BeautifulSoup(cms.content, "html.parser")

names = soup.find_all("h3", class_="gdlr-core-personnel-list-title")
imgs = soup.find_all("div", class_="gdlr-core-personnel-list-image gdlr-core-media-image gdlr-core-grayscale-effect")

# example
# print(names[0+1].a.text, imgs[0].a.img['src'])

names = names[1:]
with open(file_name + '.csv', 'w') as f:
    writer = csv.DictWriter(f, ('name', 'url'))
    for name, img in zip(names, imgs):
        img = str(img.a.img['src']).replace(' ', '%20')
        writer.writerow({'name':name.a.text, 'url':img})