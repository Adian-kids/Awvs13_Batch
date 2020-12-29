import json
import time
import requests
requests.packages.urllib3.disable_warnings()  #用于忽略SSL不安全信息


class AwvsApi(object):
    """
    Main Class
    """
    @staticmethod
    def Usage():
        usage = """
        +--------------------------------------------------------------+
        +                                                              +
        +            Awvs Tool for Low configuration VPS               +
        +                                                              +
        +                       By:AdianGg                             +
        +                                                              +
        +                    admin@e-wolf.top                          +
        +                                                              +
        +--------------------------------------------------------------+
        Press your filename to start it!
        Example: target.txt
        format:http://www.example.com
        """
        print(usage)

    def __init__(self):
        self.info_color = "\033[32m[info]\033[0m"
        self.error_color = "\033[31m[Error]\033[0m"
        self.file_name = "target.txt"  # 文件名
        self.api_host = "https://127.0.0.1:13443/"  # API地址
        self.api_key = "1986ad8c0a5b3df767028d5f3c06e936c7x34f541c03e44baab3b565fa49756b7"  #API key
        self.scan_mode = "11111111-1111-1111-1111-111111111112"  # 扫描模式
        self.scan_speed = "sequential"  # 扫描速度
        self.max_task = 5  # 最大同步任务
        self.target_list_len = 0 #任务总数
        self.target_list = []
        self.target_dict = {}
        self.headers = {
            'X-Auth': self.api_key,
            'content-type': 'application/json'
        }
        connect_status = self.checkConnect()
        if connect_status:
            print(self.info_color + "Awvs Api Connect Success")
            self.start()
        else:
            print(self.error_color + "Awvs Api Connect Error!")

    def start(self):
        """
        start do it !
        """
        print(self.info_color + "Read the target file .....")
        self.readTargetFile()
        self.target_list_len = len(self.target_list)
        print(self.info_color + "All  \033[34m" + str(self.target_list_len) +
              "\033[0m  Targets")
        print(self.info_color + "Scan Speed:" + self.scan_speed)
        self.addTarget()

    def addTarget(self):
        for i in self.target_list:
            data = {
                'address': i,
                'description': 'awvs-auto',
                'criticality': '10'
            }
            api = self.api_host + "/api/v1/targets"
            add_result = requests.post(url=api,
                                       data=json.dumps(data),
                                       headers=self.headers,
                                       verify=False)
            target_id = add_result.json().get("target_id")
            self.setSpeed(target_id)
            self.target_dict[i] = target_id
        self.scanTarget()

    def scanTarget(self):
        target_num = 0
        api = self.api_host + "/api/v1/me/stats"
        while True:
            stats_result = requests.get(url=api,
                                        headers=self.headers,
                                        verify=False)
            scan_num = stats_result.json().get("scans_running_count")
            if scan_num < self.max_task:
                if target_num == self.target_list_len:
                    print(self.info_color + "Done!")
                    break
                scan_target = self.target_list[target_num]
                scan_id = self.target_dict[scan_target]
                self.addScan(scan_target, scan_id)
                target_num += 1
            time.sleep(10)  # 检测延时

    def addScan(self, target, id):
        """
        add scan for run
        """
        api = self.api_host + "/api/v1/scans"
        data = {
            "target_id": id,
            "profile_id": self.scan_mode,
            "schedule": {
                "disable": False,
                "start_date": None,
                "time_sensitive": False
            }
        }
        add_result = requests.post(url=api,
                                   data=json.dumps(data),
                                   headers=self.headers,
                                   allow_redirects=False,
                                   verify=False)
        if add_result.status_code == 201:
            print(self.info_color + target + " ---add Success")
        else:
            print(self.error_color + target + "---add Failed")

    def setSpeed(self, target_id):
        """
        Set Scan Speed
        """
        api = self.api_host + "/api/v1/targets/" + target_id + "/configuration"
        data = {"scan_speed": self.scan_speed}
        speed_result = requests.patch(url=api, data=data, headers=self.headers, verify=False)

    def readTargetFile(self):
        """
        Get all the target to list
        """
        try:
            target_file = open(self.file_name, 'r')
            targets = target_file.readlines()
            for i in targets:
                self.target_list.append(i.strip("\n"))
            print(self.info_color + "Target read success")
        except Exception as e:
            print(self.error_color + "Target File Error,Please Check")

    def checkConnect(self):
        """
        Check if the Awvs Connect Success
        return bool
        """
        api = self.api_host + "/api/v1/info"
        try:
            check_result = requests.get(url=api,
                                        headers=self.headers,
                                        verify=False)
        except Exception as e:
            return False
        else:
            return True


if __name__ == "__main__":
    try:
        AwvsApi.Usage()
        scan = AwvsApi()
    except Exception as e:
        print(AwvsApi.error_color + "Done!")
    