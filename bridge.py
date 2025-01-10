import paho.mqtt.client as mqtt
import yaml
import ssl
import logging
import threading

version = "0.0.1"

logger = logging.getLogger("bridge")

stop_event = threading.Event()

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
        logger.debug(f"Setting up user/pass for {host}")
        client.username_pw_set(username, password)

    if tls_enabled:
        logger.debug(f"Activating TLS for {host}")
        client.tls_set_context(ssl.create_default_context())
    
    logger.info(f"Connecting to {host}:{port} with clientId: {client_id}")
    client.connect(host, port)

    return client


def main(cfg_file="config/config.yaml"):

    logger.info(f"Starting MQTT Bridge v{version}")
    logger.info(f"Loading config file {cfg_file}")
    config = load_config(cfg_file)

    client_src = connect_mqtt(config['broker_src'])
    client_dst = connect_mqtt(config['broker_dst'])

    # Add dest broker object, so later on source can use it on_message callback
    client_src.user_data_set({'client_dst': client_dst, 'mappings': config['mappings']})

    client_src.on_message = on_src_message

    logger.info("Subscribe source mqtt topics")
    for src_topic in [mapping["src_topic"] for mapping in config['mappings']]:
        if "+" in src_topic:
            logger.warn(f"Plus wildcards not supported yet, skipping {src_topic}")
            continue

        logger.debug(f"Adding topic {src_topic}")
        client_src.subscribe(src_topic)


    logger.info("Starting source client loop")
    client_src.loop_start()

    logger.info("Starting destination client loop")
    client_dst.loop_start()

    try:
        stop_event.wait()
    except KeyboardInterrupt:
        logger.info("Exiting...")

        logger.info("Stopping source client loop")
        client_src.loop_stop()

        logger.info("Stopping destination client loop")
        client_dst.loop_stop()

        stop_event.set()


if __name__ == "__main__":
    logging.basicConfig(format="{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M:%S %z", level=logging.DEBUG)
    main()
