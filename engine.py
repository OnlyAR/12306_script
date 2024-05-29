import time

from loguru import logger
from selenium import webdriver
from selenium.common import ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium_stealth import stealth


class Engine:
    def __init__(self):
        self.login_url = "https://kyfw.12306.cn/otn/resources/login.html"
        self.login_success_url = "https://kyfw.12306.cn/otn/view/index.html"
        self.test_url = "https://bot.sannysoft.com/"

        options = webdriver.ChromeOptions()

        self.driver = webdriver.Chrome(options=options)

        stealth(
            self.driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win64",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

    def login(self, seconds=300):
        self.driver.maximize_window()
        self.driver.get(self.login_url)
        logger.info(f"请在{seconds}秒内登录完成...")
        WebDriverWait(self.driver, seconds).until(ec.url_to_be(self.login_success_url))
        # self.driver.minimize_window()

    def test(self):
        self.driver.get(self.test_url)

    def query_train(self, from_city, to_city, date):

        def select_station(element, station):
            element.click()
            element.send_keys(station)
            station_elems = self.driver.find_element(by=By.ID, value='panel_cities')
            station_elems = station_elems.find_elements(by=By.TAG_NAME, value='div')
            for station_elem in station_elems:
                station_elem = station_elem.find_element(by=By.CLASS_NAME, value="ralign")
                if station_elem.text.strip() == station:
                    station_elem.click()
                    break

        url = "https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc"
        self.driver.get(url)

        from_input = self.driver.find_element(by=By.ID, value='fromStationText')
        to_input = self.driver.find_element(by=By.ID, value='toStationText')

        select_station(from_input, from_city)
        select_station(to_input, to_city)

        date_input = self.driver.find_element(by=By.ID, value='train_date')
        date_input.clear()
        date_input.send_keys(date)

        query_but = self.driver.find_element(by=By.ID, value='query_ticket')
        query_but.click()

        WebDriverWait(self.driver, 5).until(ec.presence_of_element_located((By.ID, 'trainum')))

    def order_ticket(self, train_id):
        query_table = self.driver.find_element(by=By.ID, value='queryLeftTable')
        rows = query_table.find_elements(by=By.TAG_NAME, value='tr')

        for idx in range(0, len(rows) - 1, 2):
            name = rows[idx + 1].get_attribute('datatran')
            if name.strip() == train_id:
                logger.info(f"找到车次: {train_id}")
                book_btn = rows[idx].find_element(by=By.CLASS_NAME, value='no-br')
                book_btn.click()
                return

        logger.error(f"未找到车次: {train_id}")

    def select_passengers(self, passengers_list):
        WebDriverWait(self.driver, 5).until(ec.presence_of_element_located((By.ID, 'normal_passenger_id')))
        passengers = self.driver.find_element(by=By.ID, value='normal_passenger_id')
        inputs = passengers.find_elements(by=By.TAG_NAME, value='input')
        labels = passengers.find_elements(by=By.TAG_NAME, value='label')
        for box, label in zip(inputs, labels):
            if label.text.strip() in passengers_list:
                box.click()

        submit_but = self.driver.find_element(by=By.ID, value='submitOrder_id')
        submit_but.click()

    def submit(self):
        WebDriverWait(self.driver, 5).until(ec.element_to_be_clickable((By.ID, 'qr_submit_id')))

        try:
            while True:
                submit_but = self.driver.find_element(by=By.ID, value='qr_submit_id')
                submit_but.click()
                logger.info("点击提交订单...")
                time.sleep(0.1)
        except ElementNotInteractableException:
            logger.info("提交订单成功！")

    def wait_for_success(self):
        success_message = "席位已锁定，请在提示时间内尽快完成支付，完成网上购票。"
        WebDriverWait(self.driver, 60).until(
            ec.text_to_be_present_in_element((By.CLASS_NAME, 'content'), success_message)
        )
        logger.info(success_message)

    def order_workflow(self, from_city, to_city, date, train_id, passengers):
        try:
            start = time.perf_counter()
            self.query_train(from_city, to_city, date)
            self.order_ticket(train_id)
            self.select_passengers(passengers)
            self.submit()
            end = time.perf_counter()
            logger.info("订单流程耗时: {:.2f}秒".format(end - start))
            self.wait_for_success()
        except Exception as e:
            logger.error(type(e))
            logger.error(e)
            logger.warning("系统错误，用户接管...")
            time.sleep(300)
