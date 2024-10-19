# MQTT Bridge

Tool for make bridge between two MQTT servers and map topics

For example

MQTT Broker A subscribe mytopic/# and will send it to Broker B as yourtopic.

Usable for Home Assistant, when you have more MQTT brokers and you want share data, but do not want send all from source broker. So you can not use mosqutto bridge function.

Also you do not have all time access to mosqutitto configuration files

## Use in container

`podman build . -t mqttbridge:latest`

then you must map config directory to /app/config

`podman run -v /path/to/config:/app/config -it mqttbridge:latest`
