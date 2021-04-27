import requests
import json

ORAN_BASE_URL = 'http://143.107.145.46:1026/'
ORAN_ENTITIES_URL = ORAN_BASE_URL + 'v2/entities'

ORAN_CONTROL_CHANNEL_UPT_ATTR = ORAN_ENTITIES_URL + '/control__channel_1/attrs?options=forcedUpdate'

def create_control_channel():
    payload_create = {
        'id': 'control__channel_1',
        'type': 'control_channel',
        'CPU_CORES': {
            'type': 'int',
            'value': 0
        },
        'POST_CALLS': {
            'type': 'int',
            'value': 0
        },
        'DELAY': {
            'type': 'int',
            'value': 0
        },
        'PACKET_DATA_SIZE': {
            'type': 'int',
            'value': 0
        }
    }

    response = requests.request("POST",
                                ORAN_ENTITIES_URL,
                                headers={'Content-Type': 'application/json'},
                                data=json.dumps(payload_create))

    if response.status_code == 201:
        print('Successfully Created Control Channel')
    else:
        print('Error Creating Control Channel: {}'.format(response.text))

def update_control_channel(cores, post_calls, delay, data_size):
    payload_create = {
        'CPU_CORES': {
            'type': 'int',
            'value': cores
        },
        'POST_CALLS': {
            'type': 'int',
            'value': post_calls
        },
        'DELAY': {
            'type': 'int',
            'value': delay
        },
        'PACKET_DATA_SIZE': {
            'type': 'int',
            'value': data_size
        }
    }

    response = requests.request("POST",
                                ORAN_CONTROL_CHANNEL_UPT_ATTR,
                                headers={'Content-Type': 'application/json'},
                                data=json.dumps(payload_create))

    print(response.status_code)

    if response.status_code == 204:
        print('Successfully Created Control Channel')
    else:
        print('Error Creating Control Channel: {}'.format(response.text))

def get_control_channel():

    response = requests.request("GET",
                                ORAN_CONTROL_CHANNEL_UPT_ATTR,
                                headers={'Accept': 'application/json'},
                                data={})

    if response.status_code == 200:
        return json.loads(response.text)
    else:
        print('Error Getting Control Channel: {}'.format(response.text))
        return None

if __name__ == '__main__':
    while True:
        print("")
        print("Helix Multi-layered Mockup - IoT TX Departure\n")
        print("1 - Create Control Channel")
        print("2 - Update Control Channel")
        print("3 - Get Control Channel")
        print("0 - Exit")
        number = input("Choose an option: ")
        op = int(number)

        if op == 1:
            create_control_channel()
        elif op == 2:
            cores = int(input("Number of Cores [0-3]: "))
            post_calls = int(input("Number of Post Calls [0-3]: "))
            delay = int(input("Delay option [0-3]: "))
            data_size = int(input("Data size [0-3]: "))
            update_control_channel(cores, post_calls, delay, data_size)
        elif op == 3:
            op_mode_desc = get_control_channel()
            print(json.dumps(op_mode_desc, indent=4))
        else:
            break