"""
    To populate telegram links into out `community` service.
    How to use:
    run in the terminal:
        `python populate_communities.py {dev|prod}`
"""

import os
import sys

import requests as rq
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from cloudinary.uploader import upload_image
from django.contrib.auth import get_user_model
from django.conf import settings

from communities.models import Community

User = get_user_model()

def whatsapp_populate(urls):

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
                env = 'dev' if settings.DEBUG else 'prod'
                img = upload_image(
                    img_url['src'],
                    format="jpg",
                    overwrite=True,
                    invalidate=True,
                    transformation=[{"width": 100, "height": 100, "crop": "fill"}],
                    folder=f"communities/{env}/icons",
                )
            Community.objects.create(
                link=url,
                name=title,
                icon=img if img_url else None,
                category=Community.CategoryEnum.SECTION,
                platform=Community.PlatformEnum.WHATSAPP,
                owner=User.objects.get(username='admin')
            )
