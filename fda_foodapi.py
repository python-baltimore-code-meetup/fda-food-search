import requests
import json
import csv
import os
from datetime import date
import config

from globals import HEADERS
from globals import NUTRIENT_IDS as nu


def userSetup():
    name = input("What is your name: ")
    response = int(input("Is this your first time using the program input 1 for yes or 2 for no: "))
    if response is 1:
        return
    elif response is 2:
        filename = '{}_data.csv'.format(name)
        
    return filename

def foodSearch():
    searchTerm = input("Enter the food you want to search for: ").split()
    maxResults = input("What are the maximum number of results you would like: ")

    if len(searchTerm) > 1:
        searchTerm = '+'.join(searchTerm)
        searchURL = 'https://api.nal.usda.gov/ndb/search/?format=json&q={0}&sort=n&max={1}&offset=0&api_key={2}'.format(searchTerm, maxResults, config.api_key)
        
    else:
         searchURL = 'https://api.nal.usda.gov/ndb/search/?format=json&q={0}&sort=n&max={1}&offset=0&api_key={2}'.format(searchTerm[0], maxResults, config.api_key)
    
    return searchURL

def searchResults(url):
    response = requests.get(url)
    data = json.loads(response.text)
    data = data['list']['item']
    return data

def displaySearch(data):
    for index, item in enumerate(data):
        print('{0}) {1}'.format(index+1,item['name']))

def getNutrition(data):
    selection = int(input('Enter the food you would like the nutrition content for: '))
    index = selection - 1
    item_id = data[index]['ndbno']
    nutr_url = ('https://api.nal.usda.gov/ndb/nutrients/?format=json&api_key={0}&nutrients='
                '{1}&nutrients={2}&nutrients={3}&nutrients={4}&nutrients={5}&nutrients={6}&ndbno={7}'.format(config.api_key, nu['kcal'], 
                nu['fat'], nu['protein'], nu['carbs'], nu['fiber'], nu['sugars'], item_id))
    response = requests.get(nutr_url)
    nutr_data = json.loads(response.text)
    return nutr_data
    
def parseNutrition(nutr_data):
    '''user_date = input("Enter the date for this entry in mm-dd-yyyy format or enter today: ")
    #This breaks hopelessly if the user enters bad data, no idea why
    try:
        if user_date == 'today':
            user_date = date.today().strftime('%m-%d-%Y')
        else:
            month, day, year = map(int, user_date.split('-'))
            user_date = date(year, month, day).strftime('%m-%d-%Y')
    except ValueError:
        print('Enter a valid format')
        parseNutrition(nutr_data)'''
    user_date = date.today().strftime('%m-%d-%Y')
    nutrparse = nutr_data
    food_name = nutrparse['report']['foods'][0]['name']
    serving_size = nutrparse['report']['foods'][0]['measure']
    nutrient_list = nutrparse['report']['foods'][0]['nutrients']
    #Need a way to make this more memory efficient parsing, maybe a regex?
    for i in nutrient_list:
        if i['nutrient_id'] == '208':
            calories = i['value']
        elif i['nutrient_id'] == '291':
            fiber = i['value']
        elif i['nutrient_id'] == '203':
            protein = i['value']
        elif i['nutrient_id'] == '269':
            sugars = i['value']
        elif i['nutrient_id'] == '204':
            fat = i['value']
        elif i['nutrient_id'] == '205':
            carbs = i['value']
    keys = HEADERS
    values = [user_date,food_name,serving_size,calories,fiber,protein,sugars,fat,carbs]
    nutr_dict = dict(zip(keys,values))
    return nutr_dict

def recordResults(file_name, results):
    file_exist = os.path.isfile(file_name)
    with open(file_name, 'a+', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=HEADERS)
        if not file_exist:
            writer.writeheader()
        writer.writerow(results)


def test(item):
    search_url = 'https://api.nal.usda.gov/ndb/search/?format=json&q={0}&sort=n&max={1}&offset=0&api_key={2}'.format('Mcdonald', '60', config.api_key)
    user_file = 'Patrick_data.csv'
    nutr_url = ('https://api.nal.usda.gov/ndb/nutrients/?format=json&api_key={0}&nutrients='
                '{1}&nutrients={2}&nutrients={3}&nutrients={4}&nutrients={5}&nutrients={6}&ndbno={7}'.format(config.api_key, nu['kcal'], 
                nu['fat'], nu['protein'], nu['carbs'], nu['fiber'], nu['sugars'], item))
    response = requests.get(nutr_url)
    nutr_data = json.loads(response.text)
    results = parseNutrition(nutr_data)
    return nutr_data

def main_test():
    filename = 'test_data.csv'
    with open('testdata.txt','r') as testdata:
        item_list = testdata.read()
        item_list = item_list.split('\n')
    for item in item_list:
        nutr_data = test(item)
        results = parseNutrition(nutr_data)
        recordResults(filename, results)

    


main_test()
