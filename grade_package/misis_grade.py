from loguru import logger
import datetime
import time
import os
import configparser

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException, InvalidSessionIdException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from tkinter import messagebox

# Получаем путь до текущей директории
current_directory = os.getcwd()
config = configparser.ConfigParser()
config.read('config.ini')

GRADE_REPORTS_DIR = os.path.join(current_directory, 'grade_reports')     # Путь для загрузки отчетов GradeReport
EXAM_RESULTS_DIR = os.path.join(current_directory, 'exam_results')       # Путь для загрузки отчетов ExamResult
DEFAULT_DOWNLOAD_DIR = os.path.join(current_directory, 'Downloads')       # Путь для загрузки еще чего-нибудь

USERNAME = config['npoo-settings']['USERNAME']
PASSWORD = config['npoo-settings']['PASSWORD']
UNI_SLUG = config['npoo-settings']['UNI_SLUG']

ERROR_LIST_COURSES = []

if not os.path.exists(GRADE_REPORTS_DIR):
    os.makedirs(GRADE_REPORTS_DIR)

def make_web_driver(type_driver: str = 'none'):
    """
    Функция создает и возвращает WebDriver для вызываемой задачи с указанным типом,
    чтобы не комментировать строки с настройками.

    :param type_driver: Тип WebDriver для установки директории скачивания
    :return: WebDriver
    """
    options = Options()

    # Установка директории для скачивания
    prefs = {
        "download.default_directory": DEFAULT_DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }

    if type_driver == 'grade_report':
        prefs["download.default_directory"] = GRADE_REPORTS_DIR
    elif type_driver == 'exam_results':
        prefs["download.default_directory"] = EXAM_RESULTS_DIR

    options.add_experimental_option("prefs", prefs)

    # Установка пути к ChromeDriver
    chromedriver_path = os.path.join(current_directory, 'chromedriver', 'chromedriver.exe')  # Путь к скаченному chromedriver
    driver_service = Service(executable_path=chromedriver_path)

    # Создание WebDriver
    driver = webdriver.Chrome(service=driver_service, options=options)

    driver.execute_cdp_cmd(
    "Network.setBlockedURLs",
    {"urls": ["https://connect.facebook.net/en_US/fbevents.js"]}
    )

    driver.execute_cdp_cmd("Network.enable", {})

    return driver


def login(web_driver):
    """
    Функция принимает в качестве параметра настроенный WebDriver и проводит авторизацию на портале openedu.ru

    :param web_driver:  WebDriver с которого ведется работа
    """
    # Авторизация на сайте openedu.ru https://openedu.ru/auth/login/npoedsso/
    link = 'https://openedu.ru/auth/login/npoedsso/'
    web_driver.get(link)
    web_driver.set_window_size(1920, 1015)
    WebDriverWait(web_driver, 30000).until(
        expected_conditions.presence_of_element_located((By.CLASS_NAME, 'auth-section')))
    web_driver.find_element(By.CLASS_NAME, 'auth-form').find_element(By.NAME, 'username').send_keys(USERNAME)
    web_driver.find_element(By.CLASS_NAME, 'auth-form').find_element(By.NAME, 'password').send_keys(PASSWORD)
    web_driver.find_element(By.CLASS_NAME, 'auth-form').find_element(By.TAG_NAME, 'button').click()
    time.sleep(0.5)


def grade_order(course_name: str, w_driver):
    """
    Функция переходит на страницу "Преподаватель", подраздел "Скачивание данных". Прокручивает страницу до
    таблицы с выгрузками и ожидает ее загрузки. Затем нажимает на клавишу "Создать оценочный лист", ожидает появления
    сообщения о том, что заказ принят или ошибку и переходит на главную страницу портала

    :param course_name: Шифр курса (прим. ARCHC+fall_2020)
    :param w_driver: WebDriver с которого ведется работа
    """
    # Сначала важно загрузить главную страницу курса, иначе в раздел преподавателя не попасть
    course_url1 = f'https://apps.openedu.ru/learning/course/course-v1:{UNI_SLUG}+{course_name}/home'
    course_url2 = f'https://courses.openedu.ru/courses/course-v1:{UNI_SLUG}+{course_name}/instructor#view-data_download'

    w_driver.get(course_url1)
    WebDriverWait(w_driver, 60).until(
        expected_conditions.presence_of_element_located((By.CLASS_NAME, 'row.course-outline-tab')))
    time.sleep(0.5)

    w_driver.get(course_url2)
    w_driver.execute_script("window.scrollTo(0,1200)")
    WebDriverWait(w_driver, 60).until(expected_conditions.presence_of_element_located(
        (By.CLASS_NAME, "file-download-link")))

    w_driver.find_element(By.CSS_SELECTOR, "input.async-report-btn:nth-child(1)").click()

    WebDriverWait(w_driver, 60).until(lambda x: expected_conditions.visibility_of_element_located(
        (By.CSS_SELECTOR, "#report-request-response")) or expected_conditions.visibility_of_element_located(
        (By.CSS_SELECTOR, "#report-request-response-error")))  # Проверка двух условий работает только через lambda
    time.sleep(0.5)

    response_text = w_driver.find_element(By.CSS_SELECTOR, '#report-request-response')
    response_text2 = w_driver.find_element(By.CSS_SELECTOR, '#report-request-response-error')

    if response_text.text == '':
        response = response_text2.text
        ERROR_LIST_COURSES.append(course_name)
    else:
        response = response_text.text

    logger.info('Заказан отчет по курсу: ' + course_name + '\nОтвет системы: ' + response + '\n')

    w_driver.get('https://openedu.ru/')


def order_exam_results(course_name: str, w_driver):
    """
    Функция переходит на страницу "Преподаватель", подраздел "Скачивание данных". Прокручивает страницу до
    таблицы с выгрузками и ожидает ее загрузки. Затем нажимает на клавишу
    "Создать отчёт о результатах наблюдаемого испытания", ожидает появления сообщения о том, что заказ принят
    или ошибку и переходит на главную страницу портала.

    :param course_name: Шифр курса (прим. ARCHC+fall_2020)
    :param w_driver: WebDriver с которого ведется работа
    """
    course_url1 = f'https://apps.openedu.ru/learning/course/course-v1:{UNI_SLUG}+{course_name}/home'
    w_driver.get(course_url1)
    WebDriverWait(w_driver, 60).until(
        expected_conditions.presence_of_element_located((By.CLASS_NAME, 'row.course-outline-tab')))
    time.sleep(0.5)

    course_url2 = f'https://courses.openedu.ru/courses/course-v1:{UNI_SLUG}+{course_name}/instructor#view-data_download'
    w_driver.get(course_url2)
    w_driver.execute_script("window.scrollTo(0,1200)")
    WebDriverWait(w_driver, 60).until(expected_conditions.presence_of_element_located(
        (By.CLASS_NAME, "file-download-link")))
    w_driver.execute_script("window.scrollTo(0,500)")
    try:
        w_driver.find_element(By.NAME, "proctored-exam-results-report").click()
        WebDriverWait(w_driver, 60).until(lambda x: expected_conditions.visibility_of_element_located(
            (By.CSS_SELECTOR, "#report-request-response")) or expected_conditions.visibility_of_element_located(
            (By.CSS_SELECTOR, "#report-request-response-error")))  # Проверка двух условий работает только через lambda

        time.sleep(0.5)
        response_text = w_driver.find_element(By.CSS_SELECTOR, '#report-request-response')
        response_text2 = w_driver.find_element(By.CSS_SELECTOR, '#report-request-response-error')

        if response_text.text == '':
            response = response_text2.text
            ERROR_LIST_COURSES.append(course_name)
        else:
            response = response_text.text

        logger.info('Заказан отчет наблюдаемых испытаний по курсу: '+course_name+'\nОтвет системы: ' + response + '\n')
    except NoSuchElementException:
        print("Нет наблюдаемых испытаний на курсе - " + course_name)
    w_driver.get('https://openedu.ru/')


def grade_download(course_name: str, w_driver):
    """
    Функция переходит на страницу "Преподаватель", подраздел "Скачивание данных". Прокручивает страницу до
    таблицы с выгрузками и ожидает ее загрузки. Затем находит все элементы с классом "file-download-link", и
    записывает их в список.

    Проходим циклом по списку отсекая расширенные отчеты с содержанием слова Problem и скачиваем первый сверху
    отчет Grade Report. Если дата не является сегодняшней, то файл скачает, но выведется предупреждение, что файл
    не является актуальным.

    Если отчета Grade Report нет в списке, то выводится предупреждение "Нет отчета Grade Report"

    :param course_name: Шифр курса (прим. ARCHC+fall_2020)
    :param w_driver: WebDriver с которого ведется работа
    """
    course_url1 = f'https://apps.openedu.ru/learning/course/course-v1:{UNI_SLUG}+{course_name}/home'
    course_url2 = f'https://courses.openedu.ru/courses/course-v1:{UNI_SLUG}+{course_name}/instructor#view-data_download'
    tday = str(datetime.date.today().strftime('%d.%m.%Y'))  # сегодняшняя дата для сравнения

    w_driver.get(course_url1)
    WebDriverWait(w_driver, 30).until(
        expected_conditions.presence_of_element_located((By.CLASS_NAME, 'row.course-outline-tab')))
    time.sleep(1)

    w_driver.get(course_url2)
    w_driver.execute_script("window.scrollTo(0,1200)")

    WebDriverWait(w_driver, 60).until(expected_conditions.presence_of_element_located(
        (By.CLASS_NAME, "file-download-link")))

    # Поиск строки, где есть grade report
    file_list = w_driver.find_elements(By.CLASS_NAME, 'file-download-link')
    flag = 1
    for i in file_list:
        if 'problem' in i.text:
            continue
        elif 'grade_report' in i.text:
            grade_date_list = i.text.split(sep='_')[-1].split(sep='-')[2::-1]  # получаем дату отчета из имени файла
            grade_date = '.'.join(grade_date_list)                             # дата скачиваемого Grade Report

            if tday != grade_date:
                logger.warning(f'Дата скачиваемого отчета Grade_Report для курса'
                               f' {course_name} не является актуальной')       # дата не актуальная

            w_driver.find_element(By.LINK_TEXT, i.text).click()
            flag -= 1
            logger.info(i.text)
            break
    if flag == 1:
        logger.warning('Нет отчета Grade Report для курса: ' + course_name)

    w_driver.get('https://openedu.ru/')


def exam_results_download(course_name: str, w_driver):
    """
    Функция переходит на страницу "Преподаватель", подраздел "Скачивание данных". Прокручивает страницу до
    таблицы с выгрузками и ожидает ее загрузки. Затем находит все элементы с классом "file-download-link", и
    записывает их в список.

    Проходим циклом по списку и скачиваем первый сверху отчет Exam Results. Если дата не является сегодняшней,
    то файл скачает, но выведется предупреждение, что файл не является актуальным.
    Если отчета Exam_Results нет в списке, то выводится предупреждение "Нет отчета Exam Results"

    :param course_name: Шифр курса (прим. ARCHC+fall_2020)
    :param w_driver: WebDriver с которого ведется работа
    """
    course_url1 = f'https://apps.openedu.ru/learning/course/course-v1:{UNI_SLUG}+{course_name}/home'
    w_driver.get(course_url1)
    WebDriverWait(w_driver, 60).until(
        expected_conditions.presence_of_element_located((By.CLASS_NAME, 'row.course-outline-tab')))
    time.sleep(0.5)

    course_url2 = f'https://courses.openedu.ru/courses/course-v1:{UNI_SLUG}+{course_name}/instructor#view-data_download'
    tday = str(datetime.date.today().strftime('%d.%m.%Y'))  # сегодняшняя дата для сравнения

    w_driver.get(course_url2)
    w_driver.execute_script("window.scrollTo(0,1200)")
    WebDriverWait(w_driver, 60).until(expected_conditions.presence_of_element_located(
        (By.CLASS_NAME, "file-download-link")))

    # Поиск строки, где есть exam results
    file_list = w_driver.find_elements(By.CLASS_NAME, 'file-download-link')
    flag = 1
    for i in file_list:
        if 'exam_results_report' in i.text:
            grade_date_list = i.text.split(sep='_')[-1].split(sep='-')[2::-1]  # получаем дату отчета из имени файла
            grade_date = '.'.join(grade_date_list)                             # дата скачиваемого Exam Results

            if tday != grade_date:
                logger.warning(f'Дата скачиваемого отчета Exam_Results для курса'
                               f' {course_name} не является актуальной')  # дата не актуальная

            w_driver.find_element(By.LINK_TEXT, i.text).click()
            flag -= 1
            logger.info(i.text)
            break
    if flag == 1:
        logger.warning('Нет отчета Exam Results для курса: ' + course_name)

    w_driver.get('https://openedu.ru/')


def make_grade_report_order(list_courses):
    """
    Функция создает WebDriver с настройками для заказа отчета Grade report, проходит по списку курсов и в каждом
    из них нажимает на клавишу "Создать отчет" с помощью функции grade_order. Затем
    завершает работу WebDriver.
    """
    driver = make_web_driver()
    login(driver)
    for course in list_courses:
        try:
            grade_order(course, driver)
        except (NoSuchWindowException, InvalidSessionIdException):
            raise Exception("Браузер закрыт вручную")
    driver.close()


def make_exam_results_order(list_courses):
    """
    Функция создает WebDriver с настройками для заказа отчета Grade report, проходит по списку курсов и в каждом
    из них нажимает на клавишу "Создать отчет наблюдаемых испытаний" с помощью функции order_exam_results. Затем
    завершает работу WebDriver.
    """
    driver = make_web_driver()
    login(driver)
    for course in list_courses:
        order_exam_results(course, driver)
    driver.close()


def download_grade_report(list_courses):
    """
    Функция создает WebDriver с настройками для скачивания отчета Grade report, проходит по списку курсов и в каждом
    из них пытается скачать Grade Report с помощью функции grade_download. Затем завершает работу WebDriver.
    """
    driver = make_web_driver('grade_report')
    login(driver)
    for course in list_courses:
        try:
            grade_download(course, driver)
        except (NoSuchWindowException, InvalidSessionIdException):
            raise Exception("Браузер закрыт вручную")
    driver.close()


def download_exam_results(list_courses):
    """
    Функция создает WebDriver с настройками для скачивания отчета Exam Results, проходит по списку курсов и в каждом
    из них пытается скачать отчет Exam Results с помощью функции exam_results_download.
    Затем завершает работу WebDriver.
    """
    driver = make_web_driver('exam_results')
    login(driver)
    for course in list_courses:
        exam_results_download(course, driver)
    driver.close()
