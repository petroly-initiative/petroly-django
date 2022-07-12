"""
This module is to define the fetching, filtering, and processing the data
from the KFUPM API
"""
import json
from requests import get

API = "https://registrar.kfupm.edu.sa/api/course-offering"

def fetch_data(term: int, department: str) -> dict:
    """This method performs a GET request to the KFUPM API
    for the specific args.

    Args:
        term (int): e.g., 202210
        department (str): e.g., 'ICS'

    Returns:
        dict: the response JSON after converting into dict object,
    """
    res = get(API, params={'term_code': term, 'department_code': department})

    assert res.ok
    data = json.loads(res.content)

    return data
