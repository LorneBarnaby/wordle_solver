from time import sleep
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

def get_correct(guess:str,tiles) -> dict:
    correct = {'place':[],'letter':[],'wrong':[]}
    
    
    for place, letter in enumerate(list(guess)):
        if tiles[place].get_attribute('evaluation') == 'correct':
            correct['place'].append((letter,place))
        elif tiles[place].get_attribute('evaluation') == 'present':
            correct['letter'].append((letter,place))
        elif tiles[place].get_attribute('evaluation') == 'absent':
            correct['wrong'].append(letter)


    for l,p in correct['place']:
        if l in correct['wrong']:
            correct['wrong'].remove(l)
    for l,p in correct['letter']:
        if l in correct['wrong']:
            correct['wrong'].remove(l)


    return correct

def emojify(guess,tiles):
    emoji_string = ''
    
    for place,letter in enumerate(list(guess)):
        if tiles[place].get_attribute('evaluation') == 'correct':
            emoji_string += '🟩'
        elif tiles[place].get_attribute('evaluation') == 'present':
            emoji_string += '🟨'
        elif tiles[place].get_attribute('evaluation') == 'absent':
            emoji_string += '⬜️'
    return emoji_string


def word_filter(filters,guessed,word):
    
    for c_letter,c_place,wrong in filters:
        letter = all(l[0] in word for l in c_letter)
        place = all(word[place] == l for l,place in c_place)
        right_letter_wrong_place = all(word[place] != l for l,place in c_letter)
        not_guessed = word not in guessed
        no_wrong_letters = all(w not in word for w in wrong)
        
        if not (letter and place and right_letter_wrong_place and not_guessed and no_wrong_letters):
            return False
    return True



driver = webdriver.Firefox()
driver.get("https://www.powerlanguage.co.uk/wordle/")
body = driver.find_element(By.TAG_NAME,'body')
body.click()


with open('../sowpods.txt','r') as file:
    lines = [l.strip().upper() for l in file.readlines()]
len_5 = list(filter(lambda line: len(line)==5 , lines))

current = random.choice(len_5)
guessed = []
filters = []
emojis = []

for i in range(6):
    guessed.append(current)

    body.send_keys(current)
    body.send_keys(Keys.ENTER)
    sleep(3)
    for _ in range(5) :body.send_keys(Keys.BACKSPACE)
    tiles = driver.execute_script(f"return document.getElementsByTagName('game-app')[0].shadowRoot.getElementById('board').getElementsByTagName('game-row')[{i}].$tiles")

    correct_place, correct_letter, wrong = get_correct(current,tiles).values()
    emojis.append(emojify(current,tiles))
    filters.append((correct_letter,correct_place,wrong.copy()))
    print(f'guess {i+1}: {current}')

    try:
        filtered = list(filter(
            lambda word: word_filter(filters,guessed,word),
            len_5
        ))

        current = random.choice(filtered)

    except Exception as e:
        print(e)
        break
print('\n'.join(emojis))
sleep(2)
driver.close()
