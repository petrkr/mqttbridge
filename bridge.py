import paho.mqtt.client as mqtt
import yaml
import ssl


def load_config(config_file):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config


def map_topic(topic, mapping):
    for item in mapping:
        src_topic = item['src_topic'].replace('#', '')
        if not topic.startswith(src_topic):
            continue

        dst_topic = item['dst_topic'].replace('#', '')
        if dst_topic[-1] != "/" and item['src_topic'][-1] == '#':
            dst_topic += "/"

        new_topic = topic.replace(src_topic, dst_topic)
        return new_topic

    return None


def on_src_message(client, userdata, message):
    topic = message.topic
    payload = message.payload.decode('utf-8')

    new_topic = map_topic(topic, userdata['mappings'])

    if new_topic:
        userdata['client_dst'].publish(new_topic, payload)


def connect_mqtt(broker_config):
    host = broker_config.get('host', 'localhost')
    port = broker_config.get('port', '1883')
    client_id = broker_config.get('client_id', 'mqttbridge')
    username = broker_config.get('username', '')
    password = broker_config.get('password', '')
    tls_enabled = broker_config.get('tls', False)

    client = mqtt.Client(client_id)

    if username and password:
        client.username_pw_set(username, password)

    if tls_enabled:
        client.tls_set_context(ssl.create_default_context())
    
    client.connect(host, port)

    return client


def main():
    config = load_config('config.yaml')

    client_src = connect_mqtt(config['broker_src'])
    client_dst = connect_mqtt(config['broker_dst'])

    # Add dest broker object, so later on source can use it on_message callback
    client_src.user_data_set({'client_dst': client_dst, 'mappings': config['mappings']})

    client_src.on_message = on_src_message

    for src_topic in [mapping["src_topic"] for mapping in config['mappings']]:
        if "+" in src_topic:
            print(f"Plus wildcards not supported yet, skipping {src_topic}")
            continue

        client_src.subscribe(src_topic)


    client_src.loop_start()
    client_dst.loop_start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Exiting...")
        client_src.loop_stop()
        client_dst.loop_stop()

if __name__ == "__main__":
    main()
