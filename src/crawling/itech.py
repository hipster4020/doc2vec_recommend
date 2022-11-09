import logging
import time
from logging import handlers

import helper
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import config
from db import alchemy

# log setting
carLogFormatter = logging.Formatter("%(asctime)s,%(message)s")

carLogHandler = handlers.TimedRotatingFileHandler(
    filename="log/itech_scrap.log",
    when="midnight",
    interval=1,
    encoding="utf-8",
)
carLogHandler.setFormatter(carLogFormatter)
carLogHandler.suffix = "%Y%m%d"

scarp_logger = logging.getLogger()
scarp_logger.setLevel(logging.INFO)
scarp_logger.addHandler(carLogHandler)


def scrap():
    try:
        logging.info("I-TECH Scrap Start")
        url = "https://itech.keit.re.kr/index.do#02010100"
        list_con = []

        with helper.Helper(
            url,
            headless=False,
            timeout=1,
        ) as itech_helper:
            # 페이징 처리
            for p in range(3, 6):
                # 년도 처리 2022:option[2], 2021:option[3], 2020:option[4], 2019:option[5], 2018:option[6]
                # 년도를 반복 처리하면 작동이 안돼서 수동처리
                year = "/html/body/div[3]/div[2]/div/div[2]/form/div[3]/ul/li[1]/select/option[6]"

                itech_helper.click_by_xpath(year)
                itech_helper.driver.find_element(
                    By.XPATH,
                    "/html/body/div[3]/div[2]/div/div[2]/form/div[3]/ul/li[2]/button",
                ).send_keys(Keys.ENTER)

                # 페이징 처리
                time.sleep(1)
                itech_helper.driver.find_element(
                    By.XPATH,
                    "/html/body/div[3]/div[2]/div/div[2]/form/div[4]/ul/li["
                    + str(p)
                    + "]/a",
                ).send_keys(Keys.ENTER)

                # test용
                for i in range(1, 16):
                    # 년도 처리
                    itech_helper.click_by_xpath(year)
                    itech_helper.driver.find_element(
                        By.XPATH,
                        "/html/body/div[3]/div[2]/div/div[2]/form/div[3]/ul/li[2]/button",
                    ).send_keys(Keys.ENTER)

                    # 페이징 처리
                    time.sleep(1)
                    itech_helper.driver.find_element(
                        By.XPATH,
                        "/html/body/div[3]/div[2]/div/div[2]/form/div[4]/ul/li["
                        + str(p)
                        + "]/a",
                    ).send_keys(Keys.ENTER)

                    # 번호
                    num = itech_helper.get_text_by_xpath(
                        "/html/body/div[3]/div[2]/div/div[2]/form/table/tbody/tr["
                        + str(i)
                        + "]/td[1]"
                    )
                    # 정보 없으면 break
                    if not num:
                        break

                    # 공고명
                    ann_name = itech_helper.get_text_by_xpath(
                        "/html/body/div[3]/div[2]/div/div[2]/form/table/tbody/tr["
                        + str(i)
                        + "]/td[2]/a"
                    )
                    # 공고일
                    ann_date = itech_helper.get_text_by_xpath(
                        "/html/body/div[3]/div[2]/div/div[2]/form/table/tbody/tr["
                        + str(i)
                        + "]/td[3]"
                    )
                    # 접수유형
                    type1 = itech_helper.driver.find_elements(
                        By.CSS_SELECTOR,
                        "#list > tr:nth-child("
                        + str(i)
                        + ") > td:nth-child(4) > span.ic_label.plantype1",
                    )
                    type2 = itech_helper.driver.find_elements(
                        By.CSS_SELECTOR,
                        "#list > tr:nth-child("
                        + str(i)
                        + ") > td:nth-child(4) > span.ic_label.plantype2",
                    )
                    type3 = itech_helper.driver.find_elements(
                        By.CSS_SELECTOR,
                        "#list > tr:nth-child("
                        + str(i)
                        + ") > td:nth-child(4) > span.ic_label.plantype3",
                    )
                    receipt_type = []
                    if type1:
                        receipt_type.append("개념")
                    elif type2:
                        receipt_type.append("사업")
                    elif type3:
                        receipt_type.append("차단계")
                    receipt_type = ", ".join(receipt_type)
                    # 상태
                    receipt_status = itech_helper.get_text_by_xpath(
                        "/html/body/div[3]/div[2]/div/div[2]/form/table/tbody/tr["
                        + str(i)
                        + "]/td[5]/span"
                    )

                    # 사업목적

                    # itech_helper.click_by_xpath(
                    #     "/html/body/div[3]/div[2]/div/div[2]/form/table/tbody/tr["
                    #     + str(i)
                    #     + "]/td[2]/a"
                    # )
                    itech_helper.driver.find_element(
                        By.XPATH,
                        "/html/body/div[3]/div[2]/div/div[2]/form/table/tbody/tr["
                        + str(i)
                        + "]/td[2]/a",
                    ).send_keys(Keys.ENTER)
                    purpose = itech_helper.get_text_by_xpath(
                        "/html/body/div[3]/div[2]/div/div[2]/div[2]/table/tbody/tr[2]/td/div/ul[1]/li"
                    )
                    if not purpose:
                        purpose = itech_helper.get_text_by_xpath(
                            "/html/body/div[3]/div[2]/div/div[2]/div[2]/table/tbody/tr[2]/td/div/ul[1]/li[1]/ul/li"
                        )

                    # insert data into list
                    print(f"num : {num}")
                    print(f"ann_name : {ann_name}")
                    print(f"ann_date : {ann_date}")
                    print(f"receipt_type : {receipt_type}")
                    print(f"receipt_status : {receipt_status}")
                    print(f"purpose : {purpose}")

                    list_con.append(
                        {
                            "num": num,
                            "ann_name": ann_name,
                            "ann_date": ann_date,
                            "receipt_type": receipt_type,
                            "receipt_status": receipt_status,
                            "purpose": purpose,
                        }
                    )

                    # 이전 페이지 이동
                    itech_helper.back()

                    # 년도 처리
                    itech_helper.click_by_xpath(year)
                    itech_helper.driver.find_element(
                        By.XPATH,
                        "/html/body/div[3]/div[2]/div/div[2]/form/div[3]/ul/li[2]/button",
                    ).send_keys(Keys.ENTER)

                    # 페이징 처리
                    time.sleep(1)
                    itech_helper.driver.find_element(
                        By.XPATH,
                        "/html/body/div[3]/div[2]/div/div[2]/form/div[4]/ul/li["
                        + str(p)
                        + "]/a",
                    ).send_keys(Keys.ENTER)

            # dataframe 생성
            df = pd.DataFrame(
                list_con,
            )
            print(f"scrap df : {df.head()}")
            df.dropna(inplace=True)
            df.drop_duplicates(inplace=True)
            list_con.clear()

            logging.info("outstanding end")
            itech_helper.driver.close()
            itech_helper.driver.quit()

            return df

    except Exception as e:
        logging.info(e)
        itech_helper.driver.close()
        itech_helper.driver.quit()


if __name__ == "__main__":
    df = scrap()
    print(f"df : {df.head()}")

    alchemy.DataSource(
        config.db_info,
        "kistep",
    ).df_to_sql(df, "itech")

    del df
    print("Process Done!")
