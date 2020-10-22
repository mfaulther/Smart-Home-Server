from __future__ import absolute_import, unicode_literals
from celery import task
import requests
import json
from django.core.mail import send_mail
import os

from .models import Setting
from ..settings import EMAIL_RECEPIENT, EMAIL_HOST, EMAIL_PORT, SMART_HOME_ACCESS_TOKEN, SMART_HOME_API_URL



url = SMART_HOME_API_URL
token = SMART_HOME_ACCESS_TOKEN


EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')


def write_data(data):
    j_data = {}

    for controller in data:
        key = controller.get('name')
        value = controller.get('value')
        j_data[key] = value

    with open('context.data', 'w') as f:
        f.write(json.dumps(j_data))

    return j_data


def form_post_json(data):

    return {'controllers': [{'name': key, 'value': value} for key, value in data.items()]}


def process_data(data):

    old_data = data.copy()

    if data.get('leak_detector'):
        data['hot_water'] = False
        data['cold_water'] = False
        send_mail('leak_detection', 'water have been closed', EMAIL_HOST_USER, [EMAIL_RECEPIENT])

    if not data.get('cold_water') and not data.get('smoke_detector'):
        data['boiler'] = False
        data['washing_machine'] = "off"
    else:
        hot_water_target_temperature = Setting.objects.get(controller_name='hot_water_target_temperature').value
        if data.get('boiler_temperature') < 0.9 * hot_water_target_temperature:
            data['boiler'] = True
        elif data.get('boiler_temperature') > 1.1 * hot_water_target_temperature:
            data['boiler'] = False

    if data.get('curtains') != 'slightly_open':

            if data.get('outdoor_light') < 50 and not data.get('bedroom_light'):
                data['curtains'] = 'open'
            elif data.get('outdoor_light') > 50 or data.get('bedroom_light'):
                data['curtains'] = 'close'


    if data.get('smoke_detector'):

        data['air_conditioner'] = False
        data['bedroom_light'] = False
        data['boiler'] = False
        data['washing_machine'] = "off"

    else:
        bedroom_target_temperature = Setting.objects.get(controller_name='bedroom_target_temperature').value
        if data.get('bedroom_temperature') > 1.1 * bedroom_target_temperature:
            data['air_conditioner'] = True
        elif data.get('bedroom_temperature') < 0.9 * bedroom_target_temperature:
            data['air_conditioner'] = False

    if data != old_data:
        json_to_send = form_post_json(data)
        response = requests.post(url, headers={'Authorization': 'Bearer {}'.format(token)}, json=json_to_send)





@task()
def smart_home_manager():
    headers = {'Authorization': 'Bearer {}'.format(token)}
    response = requests.get(url, headers=headers)
    data = response.json().get('data')
    json_data = write_data(data)
    process_data(json_data)





    
