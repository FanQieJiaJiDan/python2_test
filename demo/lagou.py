#!/usr/bin/python
# -*- coding: UTF-8 -*-

import logging
import requests
import json
import random
import time

from threadpool import ThreadPool

logger = logging.getLogger('mylogger')


class LaGouScrapy():

    def __init__(self):
        self.data = {}
        self.num = 0
        cookie = "LGUID=20170428150518-0978a796-2be1-11e7-b419-5254005c3644; user_trace_token=20170428150518-948c64146cba4ebb8cd2885e542e4ead; index_location_city=%E4%B8%8A%E6%B5%B7; JSESSIONID=ABAAABAAAFCAAEG693C0B0911D74612E9A536CF20CCAFAE; PRE_UTM=; PRE_HOST=www.baidu.com; PRE_SITE=https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DrrMtHq5X1zJ9DRUKnHkb-W3lsMEWJzs6J2saWwalhgi%26wd%3D%26eqid%3Dea9a0f0a0001477c0000000359f97422; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; TG-TRACK-CODE=index_search; _gid=GA1.2.1200658222.1509520423; _gat=1; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1508334275,1509348342,1509520423,1509520427; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1509520505; _ga=GA1.2.1098192760.1493363119; LGSID=20171101151346-337f1fae-bed4-11e7-afb8-525400f775ce; LGRID=20171101151504-621fa613-bed4-11e7-afb8-525400f775ce; SEARCH_ID=9be3dd5d3d4c49cb9f8eac877474d873"
        self.session = requests.session()
        self.timeout = 10
        self.session.headers["Host"] = "www.lagou.com"
        self.session.headers["Origin"] = "https://www.lagou.com"
        self.session.headers["X-Anit-Forge-Code"] = "0"
        self.session.headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
        self.session.headers["Accept"] = "application/json, text/javascript, */*; q=0.01"
        self.session.headers["X-Requested-With"] = "XMLHttpRequest"
        self.session.headers["X-Anit-Forge-Token"] = "None"
        self.session.headers["Referer"] = "https://www.lagou.com/jobs/list_python?labelWords=&fromSearch=true&suginput="
        self.session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36"
        self.session.headers["Accept-Encoding"] = "gzip, deflate, br"
        self.session.headers["Accept-Language"] = "zh-CN,zh;q=0.8"
        self.session.headers["Cookie"] = cookie

    def lagouScrapy(self):
        tp = ThreadPool(18)
        for i in range(200):
            tp.add_task(self.lagou, i)
            i += 1
        tp.destroy()

    def lagou(self,i):
            time.sleep(random.randint(3, 5))
            data = {
                "first": "true",
                "pn": "%s"%(i+1),
                "kd": "python",
            }
            if i != 0:
                data['first'] = 'false'
            url = "https://www.lagou.com/jobs/positionAjax.json?px=default&needAddtionalResult=false&isSchoolJob=0"
            response = self.session.post(url, data = data,timeout=self.timeout, verify=False)
            if not json.loads(response.content.decode('utf-8'))['success']:
                return
            html_pq = json.loads(response.content.decode('utf-8'))['content']['positionResult']['result']
            if not html_pq:
                return

            for info in html_pq:
                companyId = info['companyShortName']
                city = info['city']
                station = info['positionName']
                monthWage = info['salary']
                workYear = info['workYear']
                education = info['education']
                data = {"companyId":companyId,
                        "city": city,
                        "station": station,
                        "monthWage": monthWage,
                        "workYear": workYear,
                        "education": education
                        }
                self.num = self.num + 1
                print(data)

if __name__ == '__main__':
    r = LaGouScrapy()
    r.lagouScrapy()








