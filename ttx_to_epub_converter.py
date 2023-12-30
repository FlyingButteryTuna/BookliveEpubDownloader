from bs4 import BeautifulSoup


with open('index1.html', 'r', encoding='utf-8') as file:
    html = file.read()

soup = BeautifulSoup(html, 'html.parser')

with open('shinsekai.html', 'w', encoding='utf-8') as file:
    file.write(soup.prettify())
