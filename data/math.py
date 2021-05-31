from typing import Dict
from bs4 import BeautifulSoup
import requests, json, re, csv, sys


url = sys.argv[1]
file_name = sys.argv[2]

cms = requests.get(url)
soup = BeautifulSoup(cms.content, "html.parser")

names = soup.find_all("tr")
imgs = soup.find_all("img")

# first one
print(names[1].find_all("td")[1].b.text, 'https://mathfiles.kfupm.edu.sa/data/files/mathonly/'+imgs[0]['src'])

with open(file_name + '.csv', 'w') as f:
    writer = csv.DictWriter(f, ('name', 'url'))
    for i in range(62):
        img = 'https://mathfiles.kfupm.edu.sa/data/files/mathonly/'+imgs[i]['src']
        name = names[2*i+1].find_all("td")[1].b.text
        writer.writerow({'name':name, 'url':img})