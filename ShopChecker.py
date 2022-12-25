from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import json
import telepot
from pyvirtualdisplay import Display
display = Display(visible=0, size=(800, 800))  
display.start()


class Producto:
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre


options = webdriver.ChromeOptions()
options.add_experimental_option("useAutomationExtension", False)
options.add_experimental_option("excludeSwitches", ["enable-automation"])

options.add_experimental_option("detach", True)
options.add_argument('--headless')

def getToken(nombreFichero):
    with open(nombreFichero,'r') as f:
        return f.readline()
    
telegram_id = 1067171165
TOKEN = getToken('pwd.txt')


# ////div[@class = 'collection__image__bottom lazyloaded lazypreload'] - LAS CUATRO PRIMERAS
# //div[@class = 'collection__image__bottom lazypreload lazyloaded'] - TODAS LAS DEMÁS

# //div[@aria-label= 'Puma Black Hoodie'] - NOMBRE PRODUCTO
url = 'https://impalavintage.com/collections/all'
def impalaVintage(nameFichero):
    
    with webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install())) as driver:
        driver.get(url)
        time.sleep(5)
        bot = None
        # Poner que espere a que aparezca el elemento y luego lo clicke.
        driver.find_element(
            By.XPATH, "//button[@id = 'contact-modal-exit']").click()
        products = driver.find_elements(By.XPATH, "//a[contains(@href, '/collections/all/products/') and not(contains(@class,'lazy-image double__image'))]//p[contains(@class, 'accent strong name')]")
        productosGuardados = loadJson(nameFichero)
        contador = 0
        if len(products) == 0:
            return

        nuevosProductos = []
        for product in products:
            id = str(product.find_element(By.XPATH, '..').get_attribute('href'))
            nombre = product.text

            if id in productosGuardados:
                continue

            producto = Producto(id, nombre)
            nuevosProductos.append(producto)
        
        del products #Quitar de memoria la lista con los 200+ productos con sus características

        if bot == None:
            bot = telepot.Bot(TOKEN)
        
        for producto in nuevosProductos:
            avisarProductoNuevo(producto.id, producto.nombre, 'ImpalaVintage', driver, bot)
            addProduct(producto.nombre,producto.id, productosGuardados)
            contador += 1
        if contador > 0:
            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)
            bot.sendMessage(telegram_id,f'{contador} productos nuevos! Hora: {current_time}')
        saveJson(nameFichero, productosGuardados)
        print('Número de productos nuevos:', contador)
        
#lazy-image double__image
#//a[contains(@href, '/collections/all/products/') and not(contains(@class,'lazy-image double__image'))]//p[contains(@class, 'accent strong name')]
def avisarProductoNuevo(id, nombre, tienda, driver, bot):
    #newid = id.replace(url, '')
    openAnotherTab(driver, id)
    
    with open('Logo.png', 'wb') as file:
        foto = driver.find_elements(By.XPATH, "//img[@fetchpriority = 'high']")[0]
        file.write(foto.screenshot_as_png)
        #bot.sendPhoto(telegram_id, photo=file) 
        precio = driver.find_element(By.XPATH, "//span[@class = 'money']").text
        mensaje = f'Nombre: {nombre}\nPrecio: {precio}\nTienda: {tienda}\nLink de Compra: {id}'
        bot.sendPhoto(telegram_id, photo = open('Logo.png', 'rb'), caption = mensaje)
    #closeCurrentTab(driver)
    time.sleep(2)
        
    
#def sendTelegramMessage(message):


def addProduct(nombre, id, productosGuardados):
    productosGuardados[id] = nombre


def saveEverythingToTxt(nameFichero, driver):
    list = driver.find_elements(By.XPATH, "//div[@aria-label]")
    dictionary = {}
    for element in list:
        dictionary[element.id] = element.accessible_name
    
    saveJson(nameFichero,dictionary)



def loadJson(nombre):
    with open(nombre) as json_file:
        return json.load(json_file)


def saveJson(nombre, file):
    with open(nombre, 'w') as json_file:
        json.dump(file, json_file)
        print('Dumped!')

def openAnotherTab(driver, url):
    driver.execute_script("window.open('');")

    # Switch to the new window and open new URL
    driver.switch_to.window(driver.window_handles[1])
    driver.get(url)

def closeCurrentTab(driver):
    driver.close()


def main():
    while True:
        impalaVintage('impalaVintage.json')
        time.sleep(20)

if __name__ == "__main__":
    main()
