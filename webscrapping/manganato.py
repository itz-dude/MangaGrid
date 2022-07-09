from selenium import webdriver
from selenium.webdriver.common.by import By
import json

navegador = webdriver.Chrome()

navegador.get('https://manganato.com/index.php')

div = navegador.find_elements(By.CLASS_NAME, 'content-homepage-item')

dicionario = {}

for item in div:
    title = item.find_element(By.CLASS_NAME, 'item-title')
    image = item.find_element(By.CLASS_NAME, 'img-loading')
    author = item.find_element(By.CLASS_NAME, 'item-author')
    chapter = item.find_element(By.CLASS_NAME, 'item-chapter')

    dicionario[title.text] = {
        'author' : author.text,
        'image' : image.get_attribute('src'),
        'chapter' : chapter.text.split('\n')[0],
        'updated' : chapter.text.split('\n')[1]
    }

with open("dump.json", "w") as mangas:  
    mangas.write(json.dumps(dicionario, indent = 4))

navegador.quit()
