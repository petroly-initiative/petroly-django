from typing import Dict
from bs4 import BeautifulSoup
import requests, json, re, csv, sys



url = sys.argv[1]
file_name = sys.argv[2]

cms = requests.get(url)
soup = BeautifulSoup(cms.content, "html.parser")

names = soup.find_all("div", class_="shortDetails staffsTitle")
imgs = soup.find_all("img", class_="imgeBrd")



with open(file_name + '.csv', 'w') as f:
    writer = csv.DictWriter(f, ('name', 'url'))
    for name, img in zip(names, imgs):
        img = 'http://www.kfupm.edu.sa' + str(img['src']).replace(' ', '%20')
        writer.writerow({'name':name.p.text, 'url':img})