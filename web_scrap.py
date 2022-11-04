import requests
from bs4 import BeautifulSoup


s = requests.session()

url1 = "https://registrar.kfupm.edu.sa/courses-classes/course-offering1/"
url2 = "https://registrar.kfupm.edu.sa/course-offerings"

res = s.get(url1)


with open("res1.html", "w") as file:
    file.write(res.content.decode("utf-8"))

bs = BeautifulSoup(res.content, "html.parser")
csrf = bs.find_all("input")[1]["value"]

res = s.post(
    url2,
    data={
        "csrfmiddlewaretoken": csrf,
        "term_code": "202220",
        "dept_code": "ICS",
        "page_choice": "CO",
    },
)


bs = BeautifulSoup(res.content, "html.parser")


with open("res2.txt", "w") as file:
    for el in bs.find_all("td"):
        file.write(el.text)
        print(el.text)
