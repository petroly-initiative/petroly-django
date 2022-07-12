"""
This module is to define the fetching, filtering, and processing the data
from the KFUPM API
"""

from requests import get

API = "https://registrar.kfupm.edu.sa/api/course-offering?term_code=202210&department_code=PE"

def fetch_data(term: int, department: str) -> dict:
    """This method performs a GET request to the KFUPM API
    for the specific args.

    Args:
        term (int): e.g., 202210
        department (str): e.g., 'ICS'

    Returns:
        dict: the response JSON after converting into dict object,
    """
    res = get(API, params={'term': term, 'department': department})

    print(res.status_code)
    print(res.content)
