#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 12:25:17 2019

@author: htuovila
"""

from bs4 import BeautifulSoup
import pandas as pd
import selenium as se
from selenium import webdriver

options = se.webdriver.ChromeOptions()
options.add_argument('headless')

path="/Users/Heppa/Projects/drivers/chromedriver"
driver = webdriver.Chrome(options=options,executable_path=path)
#driver = se.webdriver.Chrome(chrome_options=options,executable_path=path)

link="https://vaalit.yle.fi/ev2019/fi/candidates"
driver.get(link)
html = driver.page_source.encode('utf-8')
page_num = 0

#selector="#all-content > div:nth-child(2) > div"
selector="#all-content > div:nth-child(2) > div > button"
# use selenium to click the button to load rest of the candidates
driver.find_element_by_css_selector(selector).click()
html = driver.page_source.encode('utf-8')
soup=BeautifulSoup(html,'html.parser')

rows_all=soup.find_all('tr')
len(rows_all)

def getFields(row):
    try:
        # in case we encounter tag for new members
        thing_to_ignore=str(row.find('a', class_="link__plane candidate_name").span)
        name_str=row.find('a', class_="link__plane candidate_name")
        name_str=str(name_str).replace(thing_to_ignore,"")
        name=BeautifulSoup(name_str,'html.parser').a.getText()
    except:
        # expected exception: no tag "New"
        name=row.a
    selected='Ei valita' # default value
    try:
        selected=row.find('div', class_="yui__CandidateImage_candidateImageLabel").getText()
    except:
        pass
    party=row.div.div.next_sibling.div.getText()
    votes=row.td.next_sibling.next_sibling.getText()
    comparison_num=row.find('span', class_="table_column__comparative_index_and_electorate").span.getText()
    region=row.find('a', class_="short_name").getText()
    dictionary={"Name": name, "Party": party, "Votes": votes, 
         "Comparative number": comparison_num, "Region": region,
         "Selected": selected}
    df_row=pd.DataFrame(dictionary,index=[0])
    return df_row

# in case we run line by line
try:
    del(df)
except:
    pass

for row in rows_all[1:]:
    try:
        df=df.append(getFields(row),ignore_index=True)
    except:
        df=getFields(row)
        

df.Votes=df.Votes.apply(int)
df["Comparative number"]=df["Comparative number"].apply(int)

# check if the number of accepted votes match
number_of_accepted_votes=3078492
print("Check sum matching: "+str(number_of_accepted_votes==df.Votes.sum()))

# save to csv
df.to_csv("finland_full_parliamentary_election_results_2019.csv")


