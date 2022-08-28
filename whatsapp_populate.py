"""
    To populate telegram links into out `community` service.
    How to use:
    run in the terminal:
        `python populate_communities.py {dev|prod}`
"""

import os
import sys
import csv

import requests as rq
from requests.exceptions import RequestException
from bs4 import BeautifulSoup

settings_type = sys.argv[1]
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "petroly.settings." + settings_type
)
# the above line is sufficient
# settings.configure()

print('DJANGO_SETTINGS_MODULE: ', os.environ.get("DJANGO_SETTINGS_MODULE"))


with open('data/groups.txt', encoding='utf-8') as file:
    urls = file.readlines()


def find_and_populate():
    for url in urls:
        url = url.removesuffix('\n')

        print(f'Working on {url}')

        try:
            res = rq.get(url)

        except RequestException as exc:
            print(f"error while requesting {url} : {exc}")
            continue

        soup = BeautifulSoup(res.content, 'html.parser')

        block = soup.find('div', id='main_block')
        title = block.find('h3', class_='_9vd5 _9scr').contents[0]
        img_url =  block.find('img', class_='_9vx6')

        try:
            obj = Community.objects.get(link=url)
            print('Community is already exist with the same link. ', obj)

        except Community.DoesNotExist:
            if img_url:
                img = upload_image(
                    img_url['src'],
                    format="jpg",
                    overwrite=True,
                    invalidate=True,
                    transformation=[{"width": 200, "height": 200, "crop": "fill"}],
                    folder=f"communities/{settings_type}/icons",
                )
            Community.objects.create(
                link=url,
                name=title,
                icon=img if img_url else None,
                category=Community.CategoryEnum.SECTION,
                platform=Community.PlatformEnum.WHATSAPP,
            )



if __name__ == '__main__':
    import django
    django.setup()
    from cloudinary.uploader import upload_image

    from communities.models import Community

    find_and_populate()
