from bs4 import BeautifulSoup

with open("words_list.html", "r", encoding="utf-8") as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'lxml')

all_a_tags = soup.find_all('a')
result = []

for a_tag in all_a_tags:
    word = a_tag['href'].split('/')[-1]

    if len(word) == 5:
        result.append("'" + word.upper() + "'")

with open('result.txt', 'w') as txt_file:
   result_str = ', '.join(result)
   txt_file.write(result_str)

