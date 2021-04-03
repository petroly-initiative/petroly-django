import csv
import os
from os import error, name, read
import kfupm.settings.dev
from django.conf import settings
import django
from cloudinary.uploader import upload
import cloudinary


# settings.configure()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kfupm.settings.prod')

print(os.environ.get('DJANGO_SETTINGS_MODULE'))
django.setup()


from evaluation.models import Instructor


def populate(name, dep, url):
    
    new_obj = Instructor.objects.get_or_create(name=name, department=dep)
    
    if url != 'https://i.pinimg.com/originals/0c/3b/3a/0c3b3adb1a7530892e55ef36d3be6cb8.png' and url != '':
        profile_pic = upload(
                            url,
                            folder='instructors/profile_pics',
                            public_id=name,
                            overwrite=True,
                            invalidate=True,
                            transformation=[
                                {'width': 200, 'height': 200, 'gravity': "face", 'crop': "thumb"}
                            ],
                            format='jpg'
                        )    
        new_obj[0].profile_pic = profile_pic['url']
    new_obj[0].save()


    print(new_obj)
with open('instructor.csv', 'r') as f:
    reader = csv.DictReader(f, delimiter=',')

    for row in reader:
        try:
            populate(row['name'], row['dep'], row['url'])
        except cloudinary.exceptions.Error as e:
            populate(row['name'], row['dep'], '')
            print(e)
        continue