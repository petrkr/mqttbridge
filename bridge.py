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


def on_src_connect(client, userdata, flags, rc):
    """Callback when source client connects - subscribe to topics here to ensure resubscription on reconnect."""
    if rc == 0:
        logger.info("Source MQTT connected successfully")
        # Subscribe to topics on every connect/reconnect
        for mapping in userdata['mappings']:
            src_topic = mapping['src_topic']
            if "+" in src_topic:
                logger.warning(f"Plus wildcards not supported yet, skipping {src_topic}")
                continue
            logger.debug(f"Subscribing to topic {src_topic}")
            client.subscribe(src_topic)
    else:
        logger.error(f"Source MQTT connection failed with code {rc}")


def on_src_disconnect(client, userdata, rc):
    """Callback when source client disconnects."""
    if rc == 0:
        logger.info("Source MQTT disconnected cleanly")
    else:
        logger.warning(f"Source MQTT disconnected unexpectedly (code {rc}), will attempt reconnect...")


def on_dst_connect(client, userdata, flags, rc):
    """Callback when destination client connects."""
    if rc == 0:
        logger.info("Destination MQTT connected successfully")
    else:
        logger.error(f"Destination MQTT connection failed with code {rc}")


def on_dst_disconnect(client, userdata, rc):
    """Callback when destination client disconnects."""
    if rc == 0:
        logger.info("Destination MQTT disconnected cleanly")
    else:
        logger.warning(f"Destination MQTT disconnected unexpectedly (code {rc}), will attempt reconnect...")


def on_mqtt_log(client, userdata, level, buf):
    """Log MQTT library messages for debugging."""
    if level == mqtt.MQTT_LOG_ERR:
        logger.error(f"MQTT: {buf}")
    elif level == mqtt.MQTT_LOG_WARNING:
        logger.warning(f"MQTT: {buf}")
    elif level == mqtt.MQTT_LOG_DEBUG:
        logger.debug(f"MQTT: {buf}")


def on_src_message(client, userdata, message):
    topic = message.topic
    try:
        payload = message.payload.decode('utf-8')
    except UnicodeDecodeError:
        logger.warning(f"Failed to decode payload as UTF-8 for topic {topic}, using raw bytes")
        payload = message.payload

    new_topic = map_topic(topic, userdata['mappings'])

    if new_topic:
        client_dst = userdata['client_dst']
        result = client_dst.publish(new_topic, payload)
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            logger.error(f"Failed to publish to {new_topic}: {mqtt.error_string(result.rc)}")


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

    # Set up source client callbacks
    client_src.on_connect = on_src_connect
    client_src.on_disconnect = on_src_disconnect
    client_src.on_message = on_src_message
    client_src.on_log = on_mqtt_log

    # Set up destination client callbacks
    client_dst.on_connect = on_dst_connect
    client_dst.on_disconnect = on_dst_disconnect
    client_dst.on_log = on_mqtt_log

    # Note: Subscriptions are now done in on_src_connect callback
    # This ensures they are renewed on every reconnect

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
