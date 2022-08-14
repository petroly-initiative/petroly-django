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


with open('data/telegram_links.txt') as file:
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

        title = soup.find('div', class_='tgme_page_title').span.contents[0]
        img_url =  soup.find('img', class_='tgme_page_photo_image')
        description = soup.find('div', class_='tgme_page_description')

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
                category=Community.CategoryEnum.EDU,
                platform=Community.PlatformEnum.TELEGRAM,
                description=description.contents[0] if description else "",
            )



if __name__ == '__main__':
    import django
    django.setup()
    from cloudinary.uploader import upload_image

    from communities.models import Community

    find_and_populate()
