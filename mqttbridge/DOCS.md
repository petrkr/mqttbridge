# Home Assistant Add-on: MQTT Bridge

## About

MQTT Bridge is a tool for creating a bridge between two MQTT brokers with topic mapping capabilities. It allows you to subscribe to topics on one MQTT broker and republish messages to another broker with customizable topic transformations.

This is particularly useful when:
- You have multiple MQTT brokers and want to share specific data between them
- You don't want to share all topics (unlike mosquitto bridge functionality)
- You don't have access to mosquitto configuration files on one or both brokers
- You need to transform topic names when moving data between brokers

## Configuration

### Source Broker (broker_src)

Configuration for the MQTT broker you want to subscribe to (where messages originate).

**host** (required):
- Hostname or IP address of the source MQTT broker
- Example: `mqtt.example.com` or `192.168.1.100`

**port** (required):
- MQTT broker port number
- Default: `8883` (MQTT over TLS) or `1883` (plain MQTT)

**client_id** (optional):
- Client ID for the MQTT connection
- Leave empty for auto-generated ID
- Example: `mqttbridge_src`

**username** (optional):
- Username for MQTT authentication
- Leave empty if authentication is not required

**password** (optional):
- Password for MQTT authentication
- Leave empty if authentication is not required

**tls** (optional):
- Enable TLS/SSL encryption for the connection
- Default: `true` (recommended for security)
- Set to `false` for unencrypted connections

### Destination Broker (broker_dst)

Configuration for the MQTT broker where you want to publish messages.

**host** (required):
- Hostname or IP address of the destination MQTT broker
- Use `core-mosquitto` to connect to Home Assistant's Mosquitto addon
- Example: `localhost`, `core-mosquitto`, or `192.168.1.200`

**port** (required):
- MQTT broker port number
- Default: `1883` for local/internal connections

**client_id** (optional):
- Client ID for the MQTT connection
- Leave empty for auto-generated ID
- Example: `mqttbridge_dst`

**username** (optional):
- Username for MQTT authentication
- Leave empty if authentication is not required

**password** (optional):
- Password for MQTT authentication
- Leave empty if authentication is not required

**tls** (optional):
- Enable TLS/SSL encryption for the connection
- Default: `false` for local connections
- Set to `true` if connecting to remote broker with TLS

### Topic Mappings

Define which topics to subscribe to and how to transform them when publishing.

Each mapping consists of:

**src_topic** (required):
- Topic pattern to subscribe to on the source broker
- Supports MQTT wildcard `#` (multi-level wildcard)
- Example: `sensors/temperature/#` subscribes to all sub-topics

**dst_topic** (required):
- Topic prefix for publishing on the destination broker
- The remaining path from src_topic will be appended
- Example: `homeassistant/sensors/temp/`

#### Mapping Examples

**Example 1: Simple topic renaming**
```yaml
mappings:
  - src_topic: "oldtopic/sensors/#"
    dst_topic: "newtopic/sensors/"
```
- `oldtopic/sensors/living_room` → `newtopic/sensors/living_room`
- `oldtopic/sensors/bedroom/temp` → `newtopic/sensors/bedroom/temp`

**Example 2: Multiple mappings**
```yaml
mappings:
  - src_topic: "remote/temperature/#"
    dst_topic: "homeassistant/climate/temp/"
  - src_topic: "remote/humidity/#"
    dst_topic: "homeassistant/climate/humidity/"
```

**Example 3: Single topic (no wildcard)**
```yaml
mappings:
  - src_topic: "source/specific/topic"
    dst_topic: "destination/topic"
```

### Log Level

Control the verbosity of logging output.

**Options:**
- `DEBUG`: Detailed debugging information (most verbose)
- `INFO`: General informational messages (recommended)
- `WARNING`: Warning messages only
- `ERROR`: Error messages only (least verbose)

## Example Configuration

### Basic Setup
```yaml
log_level: INFO
broker_src:
  host: "mqtt.remote-site.com"
  port: 8883
  client_id: "mqttbridge_src"
  username: "remote_user"
  password: "remote_password"
  tls: true
broker_dst:
  host: "core-mosquitto"
  port: 1883
  client_id: "mqttbridge_dst"
  username: ""
  password: ""
  tls: false
mappings:
  - src_topic: "remote/sensors/#"
    dst_topic: "homeassistant/sensors/"
```

### Advanced Setup with Multiple Mappings
```yaml
log_level: DEBUG
broker_src:
  host: "192.168.1.100"
  port: 1883
  client_id: ""
  username: "mqtt_user"
  password: "mqtt_pass"
  tls: false
broker_dst:
  host: "core-mosquitto"
  port: 1883
  client_id: ""
  username: "homeassistant"
  password: "ha_password"
  tls: false
mappings:
  - src_topic: "zigbee2mqtt/#"
    dst_topic: "z2m/"
  - src_topic: "tasmota/sensors/#"
    dst_topic: "homeassistant/tasmota/"
  - src_topic: "esphome/#"
    dst_topic: "ha/esp/"
```

## Usage Notes

### Wildcard Support
- Currently supports `#` (multi-level wildcard)
- The `+` (single-level wildcard) is not yet supported

### Connection Handling
- The bridge automatically reconnects to both brokers if connections are lost
- Subscriptions are automatically renewed on reconnection

### Topic Transformation
- The bridge removes the `src_topic` prefix (excluding wildcard) from incoming messages
- It then prepends the `dst_topic` prefix
- The wildcard `#` is automatically handled in the transformation

### Performance
- Messages are forwarded in real-time as they arrive
- Binary payloads are supported (not just UTF-8 text)

## Troubleshooting

### Bridge not receiving messages
1. Check that `broker_src` credentials and host are correct
2. Verify the source broker is reachable from Home Assistant
3. Check that `src_topic` pattern matches your actual topics
4. Enable `DEBUG` log level to see subscription details

### Messages not appearing on destination
1. Check that `broker_dst` credentials and host are correct
2. Verify you have publish permissions on the destination broker
3. Use MQTT Explorer or similar tool to monitor the destination broker
4. Check logs for publish errors

### Connection failures
1. Verify network connectivity between Home Assistant and brokers
2. Check firewall rules allow connections on MQTT ports
3. For TLS connections, ensure certificates are valid
4. Confirm username/password if authentication is enabled

### Topic not transforming correctly
1. Ensure `dst_topic` ends with `/` if you want to preserve the path structure
2. Check the logs to see how topics are being transformed
3. Test with a simple single-topic mapping first

## Support

For issues, feature requests, or contributions, please visit:
https://github.com/petrkr/mqttbridge/issues
