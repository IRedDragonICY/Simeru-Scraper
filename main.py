from selenium import webdriver
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor
import os
import json

class Scraper:
    def __init__(self):
        self.driver = self.set_up_driver()

    def set_up_driver(self):
        options = webdriver.EdgeOptions()
        options.add_argument('--headless')
        options.add_argument('--log-level=3') 
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        prefs = {"profile.managed_default_content_settings.images": 2,
                 "profile.managed_default_content_settings.stylesheet": 2}
        options.add_experimental_option("prefs", prefs)

        options.add_experimental_option('excludeSwitches', ['enable-automation'])

        return webdriver.Edge(options=options)

    def login(self):
        self.driver.get('https://simeru.uad.ac.id/?mod=auth&sub=auth&do=process')
        self.driver.find_element(By.NAME, 'user').send_keys('mahasiswa')
        self.driver.find_element(By.NAME, 'pass').send_keys('mahasiswa')
        self.driver.find_element(By.NAME, 'submit').click()  

    def get_options(self, name):
        select = self.driver.find_element(By.NAME, name)
        options = select.find_elements(By.TAG_NAME, 'option')
        return options

    def print_and_get_input(self, options, prompt):
        print(prompt)
        for i in range(1, len(options)):
            print(f"{i}. {options[i].text}")
        return input("Enter the number of your choice: ")

    def process_row(self, row):
        columns = ['Hari', 'Kode', 'Mata Kuliah', 'Kelas', 'Sks', 'Jam', 'Semester', 'Dosen', 'Ruang']
        row_values = row.find_elements(By.XPATH, './td')
        return {col: row_values[i].text for i, col in enumerate(columns)}


    def save_data(self, data):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        print("Saving data to data.json")
        with open(os.path.join(current_dir, 'data.json'), 'w') as f:
            json.dump(data, f, indent=4)

    def scrape(self):
        self.login()

        self.driver.get('https://simeru.uad.ac.id/?mod=laporan_baru&sub=jadwal_prodi&do=daftar')

        options = self.get_options('fakultas')
        choice = self.print_and_get_input(options, "Fakultas:")
        options[int(choice)].click()

        options = self.get_options('prodi')
        choice = self.print_and_get_input(options, "Bidang Studi:")
        options[int(choice)].click()

        self.driver.find_element(By.NAME, 'submit').click()

        rows = self.driver.find_elements(By.XPATH, '//tr[@class="odd" or @class="even"]')

        with ThreadPoolExecutor(max_workers=40) as executor:
            data = list(executor.map(self.process_row, rows))

        for item in data:
            print(item)

        self.save_data(data)

if __name__ == "__main__":
    scraper = Scraper()
    scraper.scrape()
