"""
This module is to define the fetching, filtering, and processing the data
from the KFUPM API
"""


import json
from typing import List, Dict

import requests as rq
from faas_cache_dict import FaaSCacheDict

API = "https://registrar.kfupm.edu.sa/api/course-offering"

# create in-memory cache
cache = FaaSCacheDict(default_ttl=60, max_size_bytes='10M')

def fetch_data(term: int, department: str, check_cache=True) -> List[Dict]:
    """This method performs a GET request to the KFUPM API
    for the specific args.

    Args:
        term (int): e.g., 202210
        department (str): e.g., 'ICS'

    Returns:
        dict: the response JSON after converting into dict object,
    """

    if check_cache:
        try:
            return cache[(term, department)]
        except KeyError:
            # handle cache miss
            res = rq.get(API, params={'term_code': term, 'department_code': department})

            assert res.ok
            data = json.loads(res.content)['data']

            cache[(term, department)] = data # store data into cache

            return data

    return data
