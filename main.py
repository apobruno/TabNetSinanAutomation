import shutil
import time
import os
import glob
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class DataSUS():
    
    def __init__(self, state: str = 'pa'):
        self.state = state
        self.url = f"http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/hansw{self.state}.def"
        self.line_id = 'L'
        self.collumn_id = 'C'
        self.content_id = 'I'
        self.time_id = 'A'
        self.selection_class = 'opcoes'
        self.download_section_class = 'escondido'
        self.download_path = './'
        
        self.zero_lines_checkbox_xpath = '/html/body/div/div/center/div/form/div[4]/div[2]/div[1]/div[1]/input[2]'
        self.button_xpath = '/html/body/div/div/center/div/form/div[4]/div[2]/div[2]/input[1]'
        self.csv_xpath = '/html/body/div/div/div[3]/table/tbody/tr/td[1]/a'
        self.chrome_options = webdriver.ChromeOptions()
        self.prefs = {'download.default_directory': self.download_path}
        self.chrome_options.add_experimental_option('prefs', self.prefs)
        self.chrome_service = webdriver.ChromeService(executable_path='./chromedriver.exe')

    def get_table(self, collumn: str, line: str, metric: str | list, dates: list, show_zero_lines: bool, options: dict):
        
        driver = webdriver.Chrome(options=self.chrome_options, service=self.chrome_service)
        driver.get(self.url)
        
        collumn_items = driver.find_element(By.ID, self.collumn_id)
        line_items = driver.find_element(By.ID, self.line_id)
        metric_items = driver.find_element(By.ID, self.content_id)
        date_items = driver.find_element(By.ID, self.time_id)
        options_items = driver.find_element(By.CLASS_NAME, self.selection_class)
        options_keys = list(options.keys())
        zero_lines_checkbox = driver.find_element(By.XPATH, self.zero_lines_checkbox_xpath)

        button = driver.find_element(By.XPATH, self.button_xpath)


        time.sleep(2)
        for item in collumn_items.find_elements(By.TAG_NAME, 'option'):
            if item.text == collumn:
                    item.click()

        for item in line_items.find_elements(By.TAG_NAME, 'option'):
            if item.text == line:
                item.click()

        if metric != 'Frequência':
            for item in metric_items.find_elements(By.TAG_NAME, 'option'):
                if type(metric) == str:
                    if item.text == metric:
                        item.click()
                elif type(metric) == list:
                    for m in metric:
                        if item.text == m:
                            item.click()                
        
        time.sleep(2)
        date_items_list = date_items.find_elements(By.TAG_NAME, 'option')
        date_items_list[0].click()
        
        time.sleep(2)
        for item in date_items_list:
            for date in dates:
                if item.text == date:
                    item.click()

        time.sleep(2)
        sections = options_items.find_elements(By.CLASS_NAME, 'titulo_select')
        for section in sections:
            img = section.find_element(By.TAG_NAME, 'img')
            img.click()

        time.sleep(2)
        for key in options_keys:
            select = options_items.find_element(By.ID, key)        
            items = select.find_elements(By.TAG_NAME, 'option')

            for item in items:
                for option in options[key]:
                    if item.text == option:
                        item.click()    
        
        time.sleep(2)
        if show_zero_lines:
            zero_lines_checkbox.click()
        
        time.sleep(2)
        button.click()
        
        windows = driver.window_handles
        driver.switch_to.window(windows[-1])
        
        
        try:
            download_section = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, self.download_section_class))
            )
            
            link = download_section.find_element(By.XPATH, self.csv_xpath)
            
            time.sleep(2)
            link.click()

            time.sleep(2)
            
        finally:
            driver.quit()
            
    def rename_table(self, archive_name: str):
        downloads_folder = os.path.expanduser("~") + '/Downloads/'
        archives = glob.glob(os.path.join(downloads_folder, 'sinannet*'))

        try:
            archive = archives[0]
            filename = f'{archive_name}.csv'
            renamed = os.path.join(downloads_folder, filename)
            
            print(f'file renamed for "{filename}"')
            
            os.rename(archive, renamed)

            os.makedirs(r'./data/', exist_ok=True)

            shutil.move(renamed, r'./data/')
            
            print(f'file {archive_name} was moved to ./data/')
        
        except IndexError:
            print('No files with a name starting with "sinannet_cnv_hanswpa" found in the downloads folder.')
        
        except Exception as e:
            print(f'An error occurred while renaming the file: {str(e)}')
