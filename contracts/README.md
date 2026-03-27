# Contracts

This repository treats Pinot as part of a larger platform, not as an isolated datastore. For that reason, the repo includes three contract layers:

1. **OpenAPI** for the demo analytics service in [`contracts/openapi/analytics-api.yaml`](contracts/openapi/analytics-api.yaml)
2. **AsyncAPI** for the Kafka topics in [`contracts/asyncapi/trip-events.asyncapi.yaml`](contracts/asyncapi/trip-events.asyncapi.yaml)
3. **JSON Schema** for the canonical `TripEvent` payload in [`contracts/jsonschema/trip-event.schema.json`](contracts/jsonschema/trip-event.schema.json)

Use these contracts in CI to prevent accidental drift between event producers, Pinot schemas, table configs and downstream consumers.
