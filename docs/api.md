# API reference
Base URL: `/api/v1`

## Greens
### GET /greens
List green areas.
- 200 OK → `[Green]`

Example response snippet:
```json
[
  {
    "id": 1,
    "name": "Park",
    "polygon": { "type": "Polygon", "coordinates": [[[14.42, 50.08], [14.43, 50.08], [14.43, 50.07], [14.42, 50.07], [14.42, 50.08]]]},
    "frequency_days": 14,
    "last_mowed_at": "2024-09-01T00:00:00Z"
  }
]
```

## Lamps
### GET /lamps
List lamps.
- 200 OK → `[Lamp]`

```json
[{ "id": 1, "name": "Lamp A", "point": { "type": "Point", "coordinates": [14.42, 50.08] } }]
```

## Bins
### GET /bins
List bins with last known telemetry.
- 200 OK → `[Bin]`

### GET /bins/{id}
Retrieve single bin.
- 200 OK → `Bin`
- 404 Not Found

## Bin telemetry
### POST /bins/{bin_id}/telemetry
Create telemetry entry (protected by `X-API-TOKEN`).
- 201 Created → `Telemetry`
- 401 Unauthorized if token missing/invalid

Request body:
```json
{
  "fill_level": 60,
  "battery_level": 85,
  "temperature": 22.5,
  "at_time": "2024-09-01T12:30:00Z"
}
```

Example curl (valid token):
```bash
curl -X POST "https://localhost/api/v1/bins/1/telemetry" \
  -H "Content-Type: application/json" \
  -H "X-API-TOKEN: devtoken" \
  -d '{"fill_level":60,"battery_level":85,"temperature":22.5}' -k
```

Invalid token example:
```bash
curl -X POST "https://localhost/api/v1/bins/1/telemetry" \
  -H "Content-Type: application/json" \
  -H "X-API-TOKEN: wrong" \
  -d '{"fill_level":60}' -k
# → 401 Unauthorized
```

### GET /bins/{bin_id}/telemetry
List telemetry entries (most recent first).
- Query: `limit` (default 50)
- 200 OK → `[Telemetry]`

## Lamp issues
### POST /lamps/{lamp_id}/issues
Create issue report for a lamp.
- 201 Created → `LampIssue`

### GET /lamps/{lamp_id}/issues
List issues for a lamp.
- 200 OK → `[LampIssue]`

### PATCH /lamps/{lamp_id}/issues/{issue_id}
Admin update to change `status` or `resolution_note`.
- 200 OK
- 404 Not Found

## Bin issues
### POST /bins/{bin_id}/issues
Create issue report for a bin.
- 201 Created → `BinIssue`

### GET /bins/{bin_id}/issues
List issues for a bin.
- 200 OK

### PATCH /bins/{bin_id}/issues/{issue_id}
Admin update to change `status` or `resolution_note`.
- 200 OK
- 404 Not Found

## Response codes summary
- 200 OK: successful retrieval
- 201 Created: resource created
- 401 Unauthorized: missing/invalid API token for telemetry
- 404 Not Found: resource missing

