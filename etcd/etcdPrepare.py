#coding=utf-8
import configparser
import os
import re
import io
import argparse

# base_dir = os.path.dirname(os.path.abspath(__file__))
# parser = argparse.ArgumentParser(description='Generate *.cm.yaml')
# parser.add_argument('-f', default=os.path.join(base_dir, '../harbor.cfg'),
#                     dest='config_file', help='[Optional] path of harbor config file')

# args = parser.parse_args()
#
# # 读取配置文件
# config_str = ''
# if os.path.isfile(args.config_file):
#     with open("./etcd.cfg") as conf:
#         config_str = conf.read()
# else:
#     raise Exception('Error: No such file(' + args.config_file + ')')


# config_str = '[etcd]\n' + "cpu_num=adadada"
# print(config_str)
# fp = io.StringIO()
# fp.write(config_str)
# fp.seek(0, os.SEEK_SET)
# config = configparser.RawConfigParser()
# config.readfp(fp)

#
# def get_config(key):
#     """get value by key
#     """
#     if config.has_option('etcd', key):
#         return config.get('etcd', key)
#     print('Warning: Key(' + key + ') is not existing. Use empty string as default')
#     return ''
# print(get_config("CPU"))

variable = re.compile(r'{{.+?}}')
detail = re.compile(r'(([a-zA-Z_0-9-])+)')
def render_template(tmpl, config):
    """渲染模板
    从配置文件中替换 {{(name}} 
    examples:
    config:
    hostname='test\ntest'

    {{hostname}} -> 'test\ntest'
    {{4 hostname}} -> 'test\n    test'
    """
    matches = variable.findall(tmpl)
    for match in matches:
        segs = detail.search(match)
        value = config[segs.group(1)]
        tmpl = tmpl.replace(match, value)
    return tmpl


def generate_template(tmpl, dest, config):
    """generate file
    """
    with open(tmpl) as tmpl:
        with open(dest, 'w') as dest:
            dest.write(render_template(tmpl.read(), config))


file1 = "./templates/etcd.yaml"
file2 = "./etcd.yaml"
config = {}
config["cpu_num"] = "2"
config["mem_size"] = "1Gi"
print(config["cpu_num"])
generate_template(file1, file2, config)