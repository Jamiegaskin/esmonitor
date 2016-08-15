import subprocess
import sys
import os
import time
import requests
import socket
import threading
import json

print("Starting up")
"""
ARGS: refresh_interval (seconds), metrics hostname, metrics send port,
        elastic username, elastic password, elastic url, nodes
"""
print(sys.argv)
REFRESH_INTERVAL = int(sys.argv[1]) #seconds
METRICS_URL = "http://{0}:6188/ws/v1/timeline/metrics".format(sys.argv[2])
METRIC_TEMPLATE = ('{{'
    '"metrics": ['
        '{{'
            '"timestamp": {0},'
            '"metricname": "{1}",'
            '"appid": "esmonitor",'
            '"hostname": "{5}",'
            '"starttime": {2},'
            '"metrics": {{'
                '"{3}": {4}'
                '}}'
            '}}'
        ']'
'}}')
HEADER = {'Content-Type': 'application/json'}
JMX_START = """{
  "beans": [ """
JMX_END = """  ]
}
"""
HOST, PORT = '', int(sys.argv[3])
USER, PASS = int(sys.argv[4]), int(sys.argv[5])
ELASTIC_URL = sys.argv[6]
NODES_SET = set(sys.argv[7:])

LABELS = ['index', 'shard', 'prirep', 'state', 'docs', 'store', 'ip', 'node']

hostname = open("/etc/hostname", "r").read().strip()
nodes = set()
shards = []

def update():
    global nodes, shards
    nodes_request = requests.get(ELASTIC_URL + "/_cluster/state/nodes", auth=(USER, PASS))
    nodes = set([node['name'] for node in nodes_request.json()['nodes'].values()])

    shards = []
    shards_request = requests.get(ELASTIC_URL + "/_cat/shards", auth=(USER, PASS))
    shards_texts = shards_request.text.split('\n')
    for shard in shards_texts:
        shards.append(dict(zip(LABELS, shard.split())))


def send_to_metrics_shards(percent_ok):
    #import pdb; pdb.set_trace()
    curr_time = int(time.time() * 1000) #convert to ms
    json_data = METRIC_TEMPLATE.format(curr_time,
        "shardsOK", curr_time, curr_time, percent_ok,
        hostname)
    post_response = requests.post(METRICS_URL, data = json_data,
        headers = HEADER)
    print("{1} - OK: {0}%, {2}".format(
        percent_ok, time.ctime(), post_response))
    if post_response.status_code != 200:
        status = "FAILURE"
        print("status not 200!")

def send_to_metrics_nodes():
    #import pdb; pdb.set_trace()
    curr_time = int(time.time() * 1000) #convert to ms
    num_nodes_out = len(NODES_SET - nodes)
    json_data = METRIC_TEMPLATE.format(curr_time,
        "num_nodes_missing", curr_time, curr_time, num_nodes_out,
        hostname)
    post_response = requests.post(METRICS_URL, data = json_data,
        headers = HEADER)
    print("{1} - Nodes out: {0}%, {2}".format(
        num_nodes_out, time.ctime(), post_response))
    if post_response.status_code != 200:
        status = "FAILURE"
        print("status not 200!")

def calc_and_send_metrics():
    global filesystems
    print("Starting metrics loop")
    while(True):
        try:
            #print("sending to metrics: ", filename, METRICS_URL)
            update()
            percent_ok = requests.get(ELASTIC_URL + "/_cluster/health", auth=(USER, PASS)).json()['active_shards_percent_as_number']
            send_to_metrics_shards(percent_ok)
            send_to_metrics_nodes()
        except:
            print(sys.exc_info())
        time.sleep(REFRESH_INTERVAL)

def get_jmx_metrics():
    #shards
    unassigned_other_shards = []
    unassigned_raw_shards = []
    for shard in shards:
        name = shard['index'] + shard['shard'] + shard['prirep']
        if shard['state'] == "UNASSIGNED":
            if shard['index'] == "raw":
                unassigned_raw_shards.append[name]
            else:
                unassigned_other_shards.append[name]
    if unassigned_raw_shards:
        shard_status = 2
    elif unassigned_other_shards:
        shard_status = 1
    else:
        shard_status = 0

    #nodes
    nodes_diff = NODES_SET - nodes
    if nodes_diff:
        node_status = 1
    else:
        node_status = 0
    return {'shard_status_code': shard_status, 'unassigned_other_shards': warning,
            'unassigned_raw_shards': critical, 'nodes_status_code', node_status,
            'nodes_not_found': nodes_diff}


def metrics_server():
    global filesystems
    print("Starting metrics server")
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind((HOST, PORT))
    listen_socket.listen(1)
    while True:
        client_connection, client_address = listen_socket.accept()
        request = client_connection.recv(1024)
        http_response = JMX_START + json.dumps(get_jmx_metrics(), sort_keys=True, indent=4) + JMX_END
        print (http_response)
        client_connection.sendall(http_response)
        client_connection.close()

pid = str(os.getpid())
pidfile = "/tmp/esmonitor.pid"
file(pidfile, 'w').write(pid)

calc_thread = threading.Thread(target = calc_and_send_metrics)
server_thread = threading.Thread(target = metrics_server)

calc_thread.start()
server_thread.start()
