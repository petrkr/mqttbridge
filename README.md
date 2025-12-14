# MQTT Bridge

Bridge between two MQTT brokers with topic mapping. Subscribe to topics on one broker and republish them to another with custom topic transformations.

**Use cases:**
- Share specific data between multiple MQTT brokers without sharing everything
- Alternative to mosquitto bridge when you don't have access to broker configuration
- Transform topic names when moving data between brokers
- Perfect for Home Assistant when integrating external MQTT brokers

## Installation

### Home Assistant Add-on (Recommended)

[![Add Repository](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https://github.com/petrkr/mqttbridge)

**Manual installation:**

1. In Home Assistant, go to **Settings** → **Add-ons** → **Add-on Store**
2. Click the **⋮** menu (three dots) in the top-right corner
3. Select **Repositories**
4. Add this repository URL: `https://github.com/petrkr/mqttbridge`
5. Click **Save**
6. Find "MQTT Bridge" in the add-on store and click **Install**
7. Configure the add-on through the UI
8. Start the add-on

**Configuration:**

Configure the add-on through the Home Assistant UI with:
- Source broker details (host, port, credentials, TLS)
- Destination broker details (use `core-mosquitto` for HA's MQTT broker)
- Topic mappings (define which topics to bridge and how to transform them)

See the [Documentation](https://github.com/petrkr/mqttbridge/blob/master/mqttbridge/DOCS.md) for detailed configuration options.

### Standalone Container

For use outside of Home Assistant as a standalone container:

**Build:**
```bash
podman build -t mqttbridge:latest .
# or
docker build -t mqttbridge:latest .
```

**Run:**
```bash
podman run -v /path/to/config:/app/config mqttbridge:latest
# or
docker run -v /path/to/config:/app/config mqttbridge:latest
```

**Configuration:**

Create a `config.yaml` file in your config directory. See [config.example.yaml](config/config.example.yaml) for reference:

```yaml
log_level: INFO

broker_src:
  host: "source-broker.example.com"
  port: 8883
  client_id: "mqttbridge_src"
  username: "user"
  password: "pass"
  tls: true

broker_dst:
  host: "destination-broker.example.com"
  port: 1883
  client_id: "mqttbridge_dst"
  username: ""
  password: ""
  tls: false

mappings:
  - src_topic: "source/topic/#"
    dst_topic: "destination/topic/"
  - src_topic: "another/source/#"
    dst_topic: "another/dest/"
```

## Features

- ✅ Bridge between any two MQTT brokers
- ✅ Topic mapping with wildcard support (`#`)
- ✅ TLS/SSL support for secure connections
- ✅ Authentication support (username/password)
- ✅ Automatic reconnection handling
- ✅ Configurable log levels
- ✅ Dual-mode: Home Assistant add-on or standalone container
- ✅ Binary and text message support

## Topic Mapping Examples

**Example 1:** Simple renaming
```yaml
- src_topic: "zigbee2mqtt/#"
  dst_topic: "z2m/"
```
- `zigbee2mqtt/sensors/living_room` → `z2m/sensors/living_room`

**Example 2:** Multiple mappings
```yaml
- src_topic: "remote/temperature/#"
  dst_topic: "homeassistant/climate/temp/"
- src_topic: "remote/humidity/#"
  dst_topic: "homeassistant/climate/humidity/"
```

## Support

For issues, feature requests, or contributions:
- GitHub Issues: https://github.com/petrkr/mqttbridge/issues

## License

MIT - see [LICENSE](LICENSE) file for details
