"""
 To populate telegram links into out `community` service.
"""

import os
import sys

import requests as rq
from cloudinary.uploader import upload_image
from requests.exceptions import RequestException
from bs4 import BeautifulSoup

settings_type = sys.argv[1]
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "petroly.settings." + settings_type
)
# the above line is sufficient
# settings.configure()

print('DJANGO_SETTINGS_MODULE: ', os.environ.get("DJANGO_SETTINGS_MODULE"))



urls = [
    "https://t.me/ST_KFUPM",
    'https://t.me/physics_kfupm',
]

def find_and_populate():
    for url in urls:
        print(f'Working on {url}')

        try:
            res = rq.get(url)

        except RequestException as exc:
            print(f"error while requesting {url} : {exc}")
            continue

        soup = BeautifulSoup(res.content, 'html.parser')

        title = soup.find('div', class_='tgme_page_title').span.contents[0]
        img_url =  soup.find('img', class_='tgme_page_photo_image')['src']
        description = soup.find('div', class_='tgme_page_description')

        try:
            obj = Community.objects.get(link=url)
            print(obj, ' is already exist with the same link.')

        except Community.DoesNotExist:
            img = upload_image(
                img_url,
                format="jpg",
                overwrite=True,
                invalidate=True,
                transformation=[{"width": 200, "height": 200, "crop": "fill"}],
                folder=f"communities/{settings_type}/icons",
            )
            Community.objects.create(
                link=url,
                name=title,
                icon=img,
                category=Community.CategoryEnum.EDU,
                platform=Community.PlatformEnum.TELEGRAM,
                description=description.contents[0] if description else "",
            )



if __name__ == '__main__':
    import django
    django.setup()
    from communities.models import Community

    find_and_populate()
