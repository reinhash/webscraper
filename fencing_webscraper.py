import requests
import pandas as pd
from bs4 import BeautifulSoup
from time import *
import random
import os
import json
import hashlib


class Fechter:
    def __init__(self, url, photo_url, indexnummer):
        self.header = None
        self.indexnummer = indexnummer
        self.name = None
        self.ergebnisse = None
        self.ergebnisse_json = None
        self.age = None
        self.country_club = None
        self.soup = None
        self.soup_ergebnisse = None
        self.url = url
        self.photo_url = photo_url
        self.get_soup_build(self.url)
        self.get_name()
        self.get_age()
        self.get_ergebnisse()
        self.get_country_and_club()
        self.get_photo()


    def get_soup_build(self, url):
        try:
            proxies = {'http': 'socks5://127.0.0.1:9150', 'https': 'socks5://127.0.0.1:9150'}
            headers = {}
            headers['User-agent'] = "friendlyusername"
            page = requests.get(url, proxies=proxies, headers=headers)
            self.soup = BeautifulSoup(page.text, "html.parser")
        except(Exception):
        	print("Failed to build soup")

    def get_name(self):
        try:
	        soup_fechtername = self.soup.find("h1")
	        self.name = soup_fechtername.contents[0].rstrip()
        except(Exception):
	        print("failed to get name")

    def get_age(self):
        try:
	        soup_alter = self.soup.find("span", attrs={"class": "badge-secondary"})
	        self.age = int(soup_alter.contents[0].rstrip())
        except(Exception):
        	print("failed to get age")

    def get_ergebnisse(self):
        try:
	        self.soup_ergebnisse = self.soup.find("div", attrs={"role": "tabpanel", "class": "tab-pane", "id": "results"})
	        soup_ergebnisse_tabelle = self.soup_ergebnisse.find_all("tbody")
	        soup_ergebnisse_header = self.soup_ergebnisse.find_all("thead")

	        fechter_header = []
	        soup_header = soup_ergebnisse_header[0].find_all("th")
	        for i in soup_header:
	            fechter_header.append(i.contents[0])
	        lastitem = fechter_header[-1]
	        fechter_header.append(str(lastitem) + "_add_detail_1")
	        fechter_header.append(str(lastitem) + "_add_detail_2")
	        fechter_header.append(str(lastitem) + "_add_detail_3")

	        fechter_ergebnisse_tabelle_level2 = []
	        for i in soup_ergebnisse_tabelle:
	            soup_ergebnisse_tabelle_level1 = i.find_all("tr")
	            for tuniere, y in enumerate(soup_ergebnisse_tabelle_level1):
	                soup_ergebnisse_tabelle_level2 = y.find_all("td")
	                fechter_ergebnisse_tabelle_level3 = []
	                for datenzaehler, z in enumerate(soup_ergebnisse_tabelle_level2):
	                    try:
	                        if datenzaehler == 2:
	                            datum_1 = str(z.contents[0])
	                            datum_2 = datum_1.replace(" ", "")
	                            datum_1 = datum_2.replace("\n", "")
	                            fechter_ergebnisse_tabelle_level3.append(str(datum_1))
	                        else:
	                            fechter_ergebnisse_tabelle_level3.append(z.contents[0])
	                    except Exception:
	                        fechter_ergebnisse_tabelle_level3.append("")
	                fechter_ergebnisse_tabelle_level2.append(fechter_ergebnisse_tabelle_level3)
	        self.ergebnisse = fechter_ergebnisse_tabelle_level2
	
	        fechter_ergebnisse_json = {}
	        for j, i in enumerate(self.ergebnisse):
	            fechter_ergebnisse_json.update({"Tunier "+str(j):dict(zip(fechter_header, i))})
	        self.ergebnisse_json = fechter_ergebnisse_json
        except(Exception):
            print("failed to get ergebnisse")

    def get_country_and_club(self):
        try:
            soup_country = self.soup.find("div", attrs={"class": "page-header bios_header"})
            soup_country_countryandclub = soup_country.p.img.contents
            self.country_and_club = soup_country_countryandclub
        except(Exception):
            print("failed get_country_and_club")


    def get_photo(self):
        try:
            print("kommt beim foto an", self.photo_url)
            proxies = {'http': 'socks5://127.0.0.1:9150', 'https': 'socks5://127.0.0.1:9150'}
            headers = {}
            headers['User-agent'] = "friendlyusername"
            page = requests.get(self.photo_url, proxies=proxies, headers=headers, allow_redirects=True)
            print(page.content)
		    #making sure its not the default photo which we do not want to save
            if str(hashlib.md5(page.content).hexdigest()) == 'dd3016cb6933a00ccaa4647666a42ff1':
                print("Photo skipped")
                return
            else:
                print("trying to save now")
                open(str(os.getcwd()) + "/photos/" + str(self.indexnummer) + ".jpg", 'wb').write(page.content)
                print("photo saved")
        except(Exception):
                print("failed to get photo")



fechterindexnummer = 18907
while(True):
    url = "https://fencing.ophardt.online/de/biography/athlete/"+str(fechterindexnummer)+"/embed"
    photo_url = "https://cdn.ophardt.online/fencing//images/athlete/F" + str(fechterindexnummer) + ".jpg"
    try:
    	fechter = Fechter(url, photo_url, fechterindexnummer)
    	print("fechter created")
    	fechter.indexnummer = fechterindexnummer
    	json_dict = {}
    	json_dict.update({"name" : fechter.name, "id" : fechter.indexnummer, "age": fechter.age, 
    		"country_club": fechter.country_and_club, "results": fechter.ergebnisse_json})
    	if (fechter.name == None) or (fechter.name == ""):
    		pass
    		print("JSON not saved since no name is given")
    	else:
    		with open(str(os.getcwd())+"/raw data/" + fechter.name + ".json", "w") as jsonfile:
    			jsonfile.write(str(json_dict))
    			print("JSON successfully saved")


    except(Exception):
    	print("fail ", fechterindexnummer)

    fechterindexnummer += 1
    sleepy = random.randint(1,100)
    sleep(sleepy/20)