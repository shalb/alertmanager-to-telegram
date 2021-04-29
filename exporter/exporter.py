#!/usr/bin/env python3

import http.server
import traceback
import sys
import time
import json
import urllib.request
import os
import logging


def get_config():
    '''Get configuration from ENV variables'''
    conf['url'] = 'https://api.telegram.org/'
   #conf['api_key'] = ''
    conf['log_level'] = 'INFO'
    conf['test_alerts_open'] = ''
    conf['test_alerts_close'] = ''
    env_text_options = ['url', 'api_key', 'log_level', 'test_alerts_open', 'test_alerts_close']
    for opt in env_text_options:
        opt_val = os.environ.get(opt.upper())
        if opt_val:
            conf[opt] = opt_val
    conf['alert_to_telegram_timeout'] = 10
    conf['main_loop_sleep_interval'] = 10
    conf['listen_port'] = 9647
   #conf['chat_id'] = 0
    env_int_options = ['alert_to_telegram_timeout', 'main_loop_sleep_interval', 'listen_port', 'chat_id']
    for opt in env_int_options:
        opt_val = os.environ.get(opt.upper())
        if opt_val:
            conf[opt] = int(opt_val)

def configure_logging():
    '''Configure logging module'''
    log = logging.getLogger(__name__)
    log.setLevel(conf['log_level'])
    FORMAT = '%(asctime)s %(levelname)s %(message)s'
    logging.basicConfig(format=FORMAT)
    return log

class CustomHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    '''Create http server class'''
    def do_POST(self):
        '''Define reaction to http POST'''
        content_length = int(self.headers['Content-Length'])
        post_data_json = self.rfile.read(content_length)
        post_data = json.loads(post_data_json.decode('utf-8'))
        alert_to_telegram(post_data)
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()

def create_allert_message(post_data):
    '''Convert web hook from alertmanager to alert message'''
    message = list()
    log.debug('POST data: "{}"'.format(post_data))
    for alert in post_data['alerts']:
        message.append('Status: {}'.format(alert['status']))
        message.append('Alertname: {}'.format(alert['labels']['alertname']))
        message.append('Instance: {}'.format(alert['labels']['instance']))
        message.append('Job: {}'.format(alert['labels']['job']))
        message.append('Annotations:')
        for key in alert['annotations']:
            message.append('    {}: {}'.format(key, alert['annotations'][key]))
        message.append('Labels:')
        for key in alert['labels']:
            if key in ['alertname', 'instance', 'job']:
                continue
            message.append('    {}: {}'.format(key, alert['labels'][key]))
        message.append('Generator URL: {}'.format(alert['generatorURL']))
    message.append('External URL: {}'.format(post_data['externalURL']))
    message = '\n'.join(message)
    log.debug('Message to push: "{}"'.format(message))
    return message

def alert_to_telegram(post_data):
    '''Send alert message to telegram'''
    data_to_send = dict()
    data_to_send['chat_id'] = conf['chat_id']
    data_to_send['text'] = create_allert_message(post_data)
    req = urllib.request.Request('{}{}/sendMessage'.format(conf['url'], conf['api_key']))
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    response = urllib.request.urlopen(req, json.dumps(data_to_send).encode('utf-8'), conf['alert_to_telegram_timeout'])
    log.debug('HTTP code: {}, response: "{}"'.format(response.getcode(), response.read()))

def run(server_class=http.server.HTTPServer, handler_class=CustomHTTPRequestHandler):
    '''Run whole code'''
    server_address = ('', conf['listen_port'])
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ != 'main':
    conf = dict()
    get_config()
    log = configure_logging()
    log.debug('Config: "{}"'.format(conf))
    while True:
        try:
            run()
        except KeyboardInterrupt:
            break
        except:
            trace = traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            print(trace)
        time.sleep(conf['main_loop_sleep_interval'])
