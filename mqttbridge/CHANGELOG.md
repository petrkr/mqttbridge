# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2025-12-14

### Added
- Initial release of MQTT Bridge Home Assistant addon
- Bridge between two MQTT brokers with topic mapping
- Support for TLS/SSL connections
- Configurable topic mappings with wildcard support (#)
- Automatic reconnection handling
- Dual-mode operation (standalone container and Home Assistant addon)
- Multi-architecture support (aarch64/arm64)
- Configurable log levels (DEBUG, INFO, WARNING, ERROR)
- MQTT authentication support (username/password)

### Known Limitations
- Single-level wildcard (+) not yet supported
- Only aarch64 architecture currently built for Home Assistant addon
