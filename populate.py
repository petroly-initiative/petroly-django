import csv
import os
from os import error, name, read
import kfupm.settings.dev
from django.conf import settings
import django
from cloudinary.uploader import upload_image
import cloudinary
import sys


settings_type = sys.argv[1]
departments = [] + sys.argv[2:]

# settings.configure()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kfupm.settings.'+settings_type)

print(os.environ.get('DJANGO_SETTINGS_MODULE'))
django.setup()


from evaluation.models import Instructor


def populate(name, dep, url):
    
    new_obj = Instructor.objects.get_or_create(name=name, department=dep)
    
    if url != 'https://i.pinimg.com/originals/0c/3b/3a/0c3b3adb1a7530892e55ef36d3be6cb8.png' and url != '' and url != None:
        profile_pic = upload_image(
                            url,
                            folder='instructors/profile_pics',
                            public_id=name,
                            overwrite=True,
                            invalidate=True,
                            transformation=[
                                {'width': 200, 'crop': "thumb"}
                            ],
                            format='jpg'
                        )    
        new_obj[0].profile_pic = profile_pic
    new_obj[0].save()


    print(new_obj)

deps = departments if departments else [
    # 'AE', 'ARC', 'ARE', 'CE', 'CEM', 'CHE', 
    # 'CHEM', 'COE', 
    # 'CRP', 'EE', 'GS', 'ICS', 'ISOM',
    # 'LS', 'MATH', 'ME', 'MGT', 'PE', 'PHYS', 'SE', 'IAS'
    'ELD'
]


for dep in deps:
    print('\n>>>>>>>>>>>>>>>>>>>>>>>> ' + dep)

    with open('data/'+dep+'.csv', 'r') as file:
        reader = csv.DictReader(file, delimiter=';')

        for row in reader:
            try:
                populate(row['name'], dep, row['url'])
            except cloudinary.exceptions.Error as e:
                populate(row['name'], dep, None)
                print(e)
            except Exception as e:
                print(e)
                exit(-1)
            continue