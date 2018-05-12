#!/usr/bin/python
#coding=utf-8

import os
import re
import csv

st ="""
^M 0 / 1 B                                                                                                     !   0.00%^M 1 / 1 Booooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo! 100.00%0s

Summary:
  Total:        0.0109 secs.
  Slowest:      0.0101 secs.
  Fastest:      0.0101 secs.
  Average:      0.0101 secs.
  Stddev:       0.0000 secs.
  Requests/sec: 91.3496

Response time histogram:
  0.0101 [1]    |∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎∎
  0.0101 [0]    |
  0.0101 [0]    |
  0.0101 [0]    |
  0.0101 [0]    |
  0.0101 [0]    |
  0.0101 [0]    |
  0.0101 [0]    |
  0.0101 [0]    |
  0.0101 [0]    |
  0.0101 [0]    |

Latency distribution:
Error distribution:
  [8]	rpc error: code = Unavailable desc = the server stops accepting new RPCs
  [1]	rpc error: code = Unavailable desc = transport is closing



"""
class EtcdStress(object):

    def __init__(self, cpu, memory):
        self.cpu = cpu
        self.memory = memory

    def read_test_case(self):
        """
        读取测试用例CSV格式文件
        :return: 
        """
        with open("./2018-5-10集群压力测试测试用例.csv",'r') as test_case_file:
            test_cases = csv.DictReader(test_case_file)
            return test_cases

    def save_test_result(self, clients, keys):
        cmd = """./benchmark --endpoints=http://8.16.0.33:20381 --target-leader --conns=1000 --clients=%d  put --key-size=8 --sequential-keys --total=%d --val-size=256 """%(clients, keys)
        response = str(os.popen(cmd).read())
        detail = re.compile("[a-zA-Z/]+:\s+([0-9\.]+)")
        time_out_re = re.compile(r"\[(\d+)\]\s+[a-z,A-Z]+: request timed out")
        matchs = detail.findall(response)
        result = "%s,%s,%s,%s"%(keys, self.cpu, self.memory, clients)
        for match in matchs[:-1]:
            result += ",%s"%(match)
        time_out = time_out_re.search(response)
        if time_out is not None:
            result += ",%s"%(time_out).group(1)
        else:
            result += ",%s" % ("0")
        with open("log", 'a') as log:
            log.write(result)
etcd = EtcdStress(1, "1Gi")
etcd.read_test_case()