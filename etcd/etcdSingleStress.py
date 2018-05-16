#!/usr/bin/python
# coding=utf-8

import re
import csv
import time
import argparse

from etcdPrepare import generate_template as generate_template
import os

#创建命令行参数
parse = argparse.ArgumentParser()
parse.add_argument("-f", dest="test_case", default="/var/run/stress.csv", help="path of test case")
parse.add_argument("-e", dest="endpoint", default="http://apollo-etcd.stress-test:2379", help="path of endpoint")
parse.add_argument("-o", dest="result", default="/var/log/result", help="path of result")
parse.add_argument("-c", dest="conn_num", default="/1000", help = "connection num")
parse.add_argument("-s", dest="cluster", default=False, help = "single is Flase else True")
args = parse.parse_args()

class EtcdStress(object):

    def __init__(self, cpu, memory, endpoint, is_cluster):
        self.cpu = cpu
        self.memory = memory
        self.endpoint = endpoint
        self.cluster = is_cluster

    def read_test_case(self, file_name):
        """
        读取测试用例CSV格式文件
        :return: 
        """

        with open(file_name, 'r') as test_case_file:
            test_cases = list(csv.DictReader(test_case_file))
        return test_cases

    def update_etcd(self):
        """
        修改k8s Etcd的使用cpu和内存
        :return:
        """
        config = {}
        temp = "./templates/etcd.yaml"
        file2 = "./etcd.yaml"
        config["cpu_num"] = self.cpu
        config["mem_size"] = self.memory
        generate_template(temp, file2, config)
        os.popen("kubectl delete -f etcd.yaml")
        time.sleep(60)
        os.popen("kubectl create -f etcd.yaml")
        time.sleep(60)

    def save_test_result(self, clients, keys):
        """
        保存测试结果为csv
        :param clients: 并发连接数
        :param keys: 插入key的数目
        :return: None
        """
        cmd = r"""../../benchmark --endpoints=%s  --conns=%s --clients=%s  \
              put --key-size=8 --sequential-keys --total=%s --val-size=256 """ % (self.endpoint,args.conn_num, clients, keys)
        response = str(os.popen(cmd).read())
        detail = re.compile("[a-zA-Z/]+:\s+([0-9\.]+)")
        time_out_re = re.compile(r"\[(\d+)\]\s+[a-z,A-Z]+: request timed out")
        matchs = detail.findall(response)
        result = "%s,%s,%s,%s" % (keys, self.cpu, self.memory, clients)
        for match in matchs[:-1]:
            result += ",%s" % (match)
        time_out = time_out_re.search(response)
        if time_out is not None:
            result += ",%s\n"%(time_out).group(1)
        else:
            result += ",%s\n" % ("0")
        with open(args.result+"/log.csv", 'a') as log:
            log.write(result)

    def run_test(self, test_cases_file):
        """
        开始压力测试任务    
        :return:
        """

        for test_case in self.read_test_case(test_cases_file):
            if self.cluster is False:
                if test_case["cpu"] != self.cpu or test_case["memory"] != self.memory:
                    self.cpu = test_case["cpu"]
                    self.memory = test_case["memory"]
                    self.update_etcd()
            self.save_test_result(test_case["clients"], test_case["keys"])

etcd = EtcdStress(1, "1G", args.endpoint, args.cluster)
etcd.run_test(args.test_case)

