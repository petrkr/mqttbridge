#!/bin/sh
# ==============================================================================
# Home Assistant Add-on: MQTT Bridge
# Runs the MQTT Bridge application
# ==============================================================================

set -e

CONFIG_PATH="/app/config/config.yaml"

# Check if bashio is available (Home Assistant addon mode)
if command -v bashio >/dev/null 2>&1; then
    # ============================================================================
    # HOME ASSISTANT ADDON MODE
    # ============================================================================
    bashio::log.info "Running in Home Assistant addon mode"
    bashio::log.info "Generating configuration from addon options..."

    # Read configuration from addon options
    LOG_LEVEL=$(bashio::config 'log_level')

    BROKER_SRC_HOST=$(bashio::config 'broker_src.host')
    BROKER_SRC_PORT=$(bashio::config 'broker_src.port')
    BROKER_SRC_CLIENT_ID=$(bashio::config 'broker_src.client_id')
    BROKER_SRC_USERNAME=$(bashio::config 'broker_src.username')
    BROKER_SRC_PASSWORD=$(bashio::config 'broker_src.password')
    BROKER_SRC_TLS=$(bashio::config 'broker_src.tls')

    BROKER_DST_HOST=$(bashio::config 'broker_dst.host')
    BROKER_DST_PORT=$(bashio::config 'broker_dst.port')
    BROKER_DST_CLIENT_ID=$(bashio::config 'broker_dst.client_id')
    BROKER_DST_USERNAME=$(bashio::config 'broker_dst.username')
    BROKER_DST_PASSWORD=$(bashio::config 'broker_dst.password')
    BROKER_DST_TLS=$(bashio::config 'broker_dst.tls')

    # Generate config.yaml
    cat > "${CONFIG_PATH}" <<EOF
log_level: ${LOG_LEVEL}

broker_src:
  host: "${BROKER_SRC_HOST}"
  port: ${BROKER_SRC_PORT}
  client_id: "${BROKER_SRC_CLIENT_ID}"
  username: "${BROKER_SRC_USERNAME}"
  password: "${BROKER_SRC_PASSWORD}"
  tls: ${BROKER_SRC_TLS}

broker_dst:
  host: "${BROKER_DST_HOST}"
  port: ${BROKER_DST_PORT}
  client_id: "${BROKER_DST_CLIENT_ID}"
  username: "${BROKER_DST_USERNAME}"
  password: "${BROKER_DST_PASSWORD}"
  tls: ${BROKER_DST_TLS}

mappings:
EOF

    # Read mappings array and add to config
    MAPPINGS_COUNT=$(bashio::config 'mappings|length')

    i=0
    while [ "$i" -lt "$MAPPINGS_COUNT" ]; do
        SRC_TOPIC=$(bashio::config "mappings[${i}].src_topic")
        DST_TOPIC=$(bashio::config "mappings[${i}].dst_topic")

        cat >> "${CONFIG_PATH}" <<EOF
  - src_topic: "${SRC_TOPIC}"
    dst_topic: "${DST_TOPIC}"
EOF
        i=$((i + 1))
    done

    bashio::log.info "Configuration generated successfully"
    bashio::log.info "Starting MQTT Bridge..."
else
    # ============================================================================
    # STANDALONE MODE
    # ============================================================================
    echo "$(date '+%Y-%m-%d %H:%M:%S') - INFO - Running in standalone mode"

    if [ ! -f "${CONFIG_PATH}" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR - Configuration file not found at ${CONFIG_PATH}"
        echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR - Please mount your config directory to /app/config"
        exit 1
    fi

    echo "$(date '+%Y-%m-%d %H:%M:%S') - INFO - Using configuration from ${CONFIG_PATH}"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - INFO - Starting MQTT Bridge..."
fi

# Start the MQTT bridge
exec python /app/bridge.py
