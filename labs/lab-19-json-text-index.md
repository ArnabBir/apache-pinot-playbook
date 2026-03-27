# Lab 19: JSON Index and Full-Text Search

## Overview

Two of Apache Pinot's most powerful index types exist specifically for columns that store unstructured or semi-structured data. The JSON index accelerates predicate evaluation and path extraction on JSON columns, converting what would otherwise be a row-by-row deserialization pass into a fast inverted index lookup. The Text index and FST index serve the complementary case: free-form string columns where queries involve phrase matching, boolean operators, wildcards, and regular expressions rather than exact equality.

Without either index type, operating on these columns forces the query engine to decode every row's raw bytes to evaluate a predicate. At millions of rows this produces query latencies that are incompatible with interactive dashboards. With the correct index in place, the same queries resolve in milliseconds because the rows to be returned are identified before the raw column values are read.

This lab builds practical fluency with both index types against the `trip_events` table. You will measure the before-and-after query performance for JSON predicate filtering, implement phrase and wildcard text search against a driver notes column, and configure the FST index for optimized regular expression matching against a merchant name column.

> [!NOTE]
> Labs 1 through 3 must be complete and data must be present in `trip_events` and `merchants_dim` before this lab.

---

## Learning Objectives

| Objective | Success Criterion |
|-----------|-------------------|
| Understand how the JSON index eliminates row-level deserialization | You can explain the flat inverted index structure and how `json_match` uses it |
| Query JSON fields using `jsonExtractScalar` | Extraction queries return typed values without errors |
| Measure the speedup from JSON index vs forced scan | You have recorded `numDocsScanned` and `timeUsedMs` for both paths in the measurement table |
| Use `json_match` for fast JSON predicate evaluation | Compound JSON predicates return correct results |
| Add a TEXT index column and query it with `text_match` | Phrase, boolean, wildcard, and NOT queries return expected rows |
| Configure and verify the FST index for `regexp_like` | FST-accelerated regexp queries show reduced `numDocsScanned` in the measurement table |
| Distinguish the three advanced index types | Given a query type, you can identify the correct index and explain why |

---

## The `attributes` Column

The `trip_events` table carries an `attributes` column of type JSON. This column stores event-level metadata that varies by event type and does not fit neatly into a flat schema. A representative value for a completed trip looks like the following.

```json
{
  "payment": {
    "method": "card",
    "gateway": "stripe",
    "last4": "4242"
  },
  "route": {
    "origin": "BKC",
    "destination": "Airport",
    "distance_km": 28.5
  },
  "promo": {
    "code": "RIDE20",
    "discount_pct": 20
  },
  "device": {
    "os": "iOS",
    "app_version": "5.2.1"
  }
}
```

The nesting depth reaches two levels in most fields. The `payment.gateway`, `route.distance_km`, and `device.os` paths are among the most queried because they appear in operational dashboards and fraud detection pipelines.

---

## JSON Index Architecture

The following diagram contrasts how Pinot handles a JSON column predicate with and without a JSON index in place.

```mermaid
flowchart TB
    subgraph noidx["WITHOUT JSON INDEX — jsonExtractScalar at scan time"]
        direction TB
        ni1["Query: WHERE jsonExtractScalar(attributes, '$.payment.gateway', 'STRING') = 'stripe'"]
        ni2["Broker routes to all relevant servers"]
        ni3["Server iterates every row in the segment\nnumDocsScanned = all rows"]
        ni4["Each row: deserialize raw JSON bytes\nparse '$.payment.gateway'\ncompare to 'stripe'"]
        ni5["Rows matching the predicate passed to aggregation\ntimeUsedMs grows linearly with segment size"]
        ni1 --> ni2 --> ni3 --> ni4 --> ni5
    end

    subgraph withidx["WITH JSON INDEX — flat inverted index lookup"]
        direction TB
        wi1["JSON index built at segment creation time\nFlattened path-value pairs:\n  '$.payment.gateway' = 'stripe'  → {row 0, row 4, row 7}\n  '$.payment.gateway' = 'razorpay' → {row 1, row 2}\n  '$.payment.method'  = 'card'    → {row 0, row 1, row 4, row 7}\n  ..."]
        wi2["Query: WHERE json_match(attributes, '\"$.payment.gateway\" = ''stripe''')\nIndex lookup: key '$.payment.gateway=stripe'\nReturns posting list {row 0, row 4, row 7} instantly"]
        wi3["Only matching rows are deserialized\nnumDocsScanned = matching rows only\ntimeUsedMs = O(1) lookup + result fetch"]
        wi1 --> wi2 --> wi3
    end

    subgraph build["JSON Index Build Process"]
        direction LR
        b1["Ingest row\nRaw JSON string stored in forward index"]
        b2["At segment seal:\nParse every JSON value in every row\nFor each path-value pair:\n  encode as 'path=value' string\n  add row ID to posting list"]
        b3["Flat inverted index written to segment\nSame structure as column inverted index\nbut keyed on path=value strings"]
        b1 --> b2 --> b3
    end
```

The JSON index trades segment build time and additional storage for dramatically reduced query scan cost. Every distinct path-value combination found in any row becomes an entry in a flat inverted index. A `json_match` predicate is translated into one or more lookups against this flat index, returning the row ID set before any raw JSON deserialization occurs.

---

## Step 1: Verify the JSON Index Configuration

The `attributes` column must have a JSON index declared in the `fieldConfigList` section of the table configuration. Retrieve the current table configuration and inspect the relevant section.

```bash
curl -s "http://localhost:9000/tables/trip_events_REALTIME/tableConfigs" \
  | python3 -m json.tool > /tmp/trip_events_table.json
```

Locate the `fieldConfigList` array and confirm that the entry for `attributes` matches the following.

```json
{
  "name": "attributes",
  "encodingType": "RAW",
  "indexTypes": ["JSON"]
}
```

If the `indexTypes` array does not include `"JSON"`, add it and resubmit the table configuration. After any change to `fieldConfigList`, existing segments must be reloaded to rebuild the index.

```bash
curl -s -X PUT \
  "http://localhost:9000/tables/trip_events_REALTIME" \
  -H "Content-Type: application/json" \
  -d @/tmp/trip_events_table.json \
  | python3 -m json.tool
```

Expected output:

```json
{
  "status": "Table config updated for trip_events_REALTIME"
}
```

Reload segments to apply the index.

```bash
curl -s -X POST \
  "http://localhost:9000/segments/trip_events_REALTIME/reload" \
  | python3 -m json.tool
```

Expected output:

```json
{
  "status": "Request to reload all segments of table trip_events_REALTIME submitted"
}
```

---

## Step 2: Query JSON Fields Using `jsonExtractScalar`

`jsonExtractScalar` is a scalar function that evaluates at query time. It extracts a value at a JSON path from a column, returning it as the specified type. It works on any JSON column regardless of whether a JSON index is present — but when used in a WHERE predicate without a JSON index, it triggers a full column scan.

### Extract Payment and Route Fields

```sql
SELECT
  trip_id,
  jsonExtractScalar(attributes, '$.payment.method',    'STRING') AS payment_method,
  jsonExtractScalar(attributes, '$.payment.gateway',   'STRING') AS gateway,
  jsonExtractScalar(attributes, '$.route.distance_km', 'DOUBLE') AS distance
FROM trip_events
LIMIT 10
```

Expected result (sample rows):

| trip_id     | payment_method | gateway  | distance |
|-------------|----------------|----------|:--------:|
| trip_000001 | card           | stripe   | 28.5     |
| trip_000002 | upi            | razorpay | 12.3     |
| trip_000003 | card           | stripe   | 31.0     |

### Aggregate by Extracted JSON Field

`jsonExtractScalar` can appear in GROUP BY and SELECT aggregate expressions. This pattern is more expensive than grouping on a native column because the extraction runs at scan time for every row, but it is correct and useful for ad hoc analysis.

```sql
SELECT
  jsonExtractScalar(attributes, '$.payment.method', 'STRING') AS method,
  COUNT(*)              AS trips,
  SUM(fare_amount)      AS gmv
FROM trip_events
GROUP BY method
ORDER BY trips DESC
```

Expected result: A row per distinct payment method value found in the `attributes` column, ordered by trip count descending.

---

## Step 3: Fast JSON Predicate Filtering with `json_match`

`json_match` evaluates predicates directly against the JSON index without deserializing raw JSON bytes. The syntax uses JSON path expressions enclosed in double quotes, with string values enclosed in single quotes within the predicate string.

### Forced Scan Baseline

The `SET skipIndexes` hint instructs Pinot to bypass the named index type for the named column, forcing the execution path that would apply without the index. Use this to establish a baseline for comparison.

```sql
SET skipIndexes='attributes=json';
SELECT COUNT(*)
FROM trip_events
WHERE jsonExtractScalar(attributes, '$.payment.gateway', 'STRING') = 'stripe'
```

Record the `numDocsScanned` and `timeUsedMs` values from the BrokerResponse for this query. At meaningful data volumes you will observe that `numDocsScanned` equals the total number of rows in the table, because every row must be read to evaluate the expression.

### JSON Index Accelerated

```sql
SELECT COUNT(*)
FROM trip_events
WHERE json_match(attributes, '"$.payment.gateway" = ''stripe''')
```

The predicate string `"$.payment.gateway" = 'stripe'` uses single-quoted values within the outer SQL string. The outer SQL string uses double-quoted SQL string delimiters. When writing this query in a client that uses single-quoted SQL strings, escape the inner single quotes by doubling them: `'"$.payment.gateway" = ''stripe'''`.

Record `numDocsScanned` and `timeUsedMs` for this query. You should observe that `numDocsScanned` matches the number of rows where the gateway is actually `stripe`, not the total table size.

### Compound JSON Predicate

`json_match` supports `AND` and `OR` within the predicate string, allowing multi-path filtering in a single index lookup.

```sql
SELECT trip_id, fare_amount
FROM trip_events
WHERE json_match(
  attributes,
  '"$.payment.method" = ''card'' AND "$.route.distance_km" > ''20'''
)
```

Expected result: Trips paid by card with a route distance greater than 20 kilometres. Note that numeric comparisons in `json_match` use string representation of the numeric value — Pinot performs the type coercion internally based on the JSON index's stored types.

### JSON Index Performance Measurement Table

Record your observed values from the two approaches above.

| Approach | Query | numDocsScanned | timeUsedMs |
|----------|-------|:--------------:|:----------:|
| Scan (skipIndexes hint) | `jsonExtractScalar` equality | | |
| JSON index | `json_match` equality | | |
| JSON index | `json_match` compound AND | | |

A well-functioning JSON index will show `numDocsScanned` for the `json_match` queries at or near the actual number of matching rows, rather than the total table size. The `timeUsedMs` reduction is typically one to two orders of magnitude for large datasets.

---

## Step 4: Extract Keys Using `jsonExtractKey`

`jsonExtractKey` returns the keys at a given JSON path level, useful for discovery queries against documents with variable structure.

```sql
SELECT
  trip_id,
  jsonExtractKey(attributes, '$') AS top_level_keys
FROM trip_events
LIMIT 5
```

Expected result: Each row shows the list of top-level keys present in its `attributes` document. For trips that carry all four top-level sections, the result is `["payment", "route", "promo", "device"]`.

This function is particularly useful during schema exploration — when onboarding a new JSON column, `jsonExtractKey` lets you discover what paths are present in the actual data before writing extraction queries.

---

## Full-Text Index

### The Text Index Model

A Text index (also called an inverted term index) tokenizes a string column's values into individual terms at segment build time. Each term maps to the set of row IDs whose column value contains that term. A subsequent `text_match` query is evaluated by looking up one or more terms in this posting structure, combining the resulting row ID sets according to the boolean logic of the query, and returning the intersection without touching the raw column values.

The FST index (Finite State Transducer index) is a companion structure built over the same column to accelerate regular expression matching. Where the Text index accelerates term-based queries, the FST index accelerates regexp patterns that can be evaluated against the sorted term dictionary without a full dictionary scan.

---

## Step 5: Add a `driver_notes` TEXT Column

Add a `driver_notes` column to the `trip_events` schema. This column stores free-form text notes entered by drivers at trip completion.

```json
{
  "name": "driver_notes",
  "dataType": "STRING",
  "singleValueField": true
}
```

Submit the schema update as in previous steps. Then configure the Text index for this column in the `fieldConfigList` of the table configuration.

```json
{
  "name": "driver_notes",
  "encodingType": "RAW",
  "indexTypes": ["TEXT"]
}
```

After updating both the schema and the table configuration, reload segments.

Ingest the following sample records to `/tmp/driver_notes_sample.jsonl`.

```
{"trip_id":"trip_000009","city":"mumbai","fare_amount":0.0,"event_time_ms":1706745680000,"event_type":"trip_cancelled","driver_notes":"passenger no show after 5 minutes"}
{"trip_id":"trip_000010","city":"delhi","fare_amount":195.0,"event_time_ms":1706745690000,"event_type":"trip_completed","driver_notes":"route blocked due to construction near airport"}
{"trip_id":"trip_000011","city":"bangalore","fare_amount":220.0,"event_time_ms":1706745700000,"event_type":"trip_completed","driver_notes":"passenger requested airport drop priority lane"}
{"trip_id":"trip_000012","city":"mumbai","fare_amount":0.0,"event_time_ms":1706745710000,"event_type":"trip_cancelled","driver_notes":"no show at pickup location waited 7 minutes"}
{"trip_id":"trip_000013","city":"delhi","fare_amount":310.0,"event_time_ms":1706745720000,"event_type":"trip_completed","driver_notes":"construction diversion added 15 minutes to route"}
```

```bash
docker exec -i kafka kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic trip-events \
  < /tmp/driver_notes_sample.jsonl
```

Expected output: Silent exit after streaming all five records.

---

## Step 6: Text Search Using `text_match`

All `text_match` queries follow the syntax `text_match(column_name, 'query_expression')`. The query expression language supports phrases (in double quotes), boolean operators (`AND`, `OR`, `NOT`), and wildcards (`*`).

### Phrase Search

A phrase query matches rows where the exact sequence of terms appears in the column value. Enclose the phrase in double quotes within the query expression string.

```sql
SELECT trip_id, driver_notes
FROM trip_events
WHERE text_match(driver_notes, '"no show"')
LIMIT 10
```

Expected result:

| trip_id     | driver_notes                              |
|-------------|-------------------------------------------|
| trip_000009 | passenger no show after 5 minutes         |
| trip_000012 | no show at pickup location waited 7 minutes |

Both rows contain the exact two-word sequence `no show`. A row containing `show no` would not match a phrase query for `"no show"`.

### Boolean AND Search

An `AND` query matches rows that contain both terms, regardless of their position or adjacency in the text.

```sql
SELECT trip_id, driver_notes
FROM trip_events
WHERE text_match(driver_notes, 'airport AND priority')
LIMIT 10
```

Expected result:

| trip_id     | driver_notes                                          |
|-------------|-------------------------------------------------------|
| trip_000011 | passenger requested airport drop priority lane        |

Only `trip_000011` contains both `airport` and `priority`. The rows referencing airport construction do not contain `priority`.

### Wildcard Search

A wildcard query matches any term that begins with the specified prefix. The wildcard character `*` must appear at the end of the prefix — leading wildcards are not supported by the default Lucene-compatible analyzer.

```sql
SELECT trip_id, driver_notes
FROM trip_events
WHERE text_match(driver_notes, 'construct*')
LIMIT 10
```

Expected result:

| trip_id     | driver_notes                                                  |
|-------------|---------------------------------------------------------------|
| trip_000010 | route blocked due to construction near airport                |
| trip_000013 | construction diversion added 15 minutes to route              |

Both `construction` values match the `construct*` prefix pattern.

### Boolean NOT Search

A `NOT` operator excludes rows that contain the specified term from the result set.

```sql
SELECT trip_id, driver_notes
FROM trip_events
WHERE text_match(driver_notes, 'airport NOT construction')
LIMIT 10
```

Expected result:

| trip_id     | driver_notes                                          |
|-------------|-------------------------------------------------------|
| trip_000011 | passenger requested airport drop priority lane        |

`trip_000010` contains both `airport` and `construction` and is therefore excluded. Only `trip_000011` contains `airport` without `construction`.

---

## Step 7: FST Index for `regexp_like` Optimization

The FST (Finite State Transducer) index is built over the sorted term dictionary of a string column. It encodes the dictionary as a compact automaton that allows regular expression patterns to be evaluated against terms without iterating every term in the dictionary. This accelerates prefix patterns (`Cafe.*`), suffix patterns (`.*Cafe`), and anchored patterns significantly.

### Configure the FST Index on `merchant_name`

In the `fieldConfigList` of the `merchants_dim` table configuration, add `FST` to the `indexTypes` array for the `merchant_name` column.

```json
{
  "name": "merchant_name",
  "encodingType": "DICTIONARY",
  "indexTypes": ["FST"]
}
```

Submit the updated configuration.

```bash
curl -s -X PUT \
  "http://localhost:9000/tables/merchants_dim_OFFLINE" \
  -H "Content-Type: application/json" \
  -d @/tmp/merchants_dim_table.json \
  | python3 -m json.tool
```

Expected output:

```json
{
  "status": "Table config updated for merchants_dim_OFFLINE"
}
```

Reload segments.

```bash
curl -s -X POST \
  "http://localhost:9000/segments/merchants_dim_OFFLINE/reload" \
  | python3 -m json.tool
```

### Forced Scan Baseline

Bypass the FST index to measure the unaccelerated baseline.

```sql
SET skipIndexes='merchant_name=fst';
SELECT COUNT(*)
FROM merchants_dim
WHERE regexp_like(merchant_name, '.*Cafe.*')
```

Record `numDocsScanned` and `timeUsedMs`. With no FST index, every value in the `merchant_name` column dictionary must be evaluated against the regexp pattern.

### FST-Accelerated Query

Remove the `skipIndexes` hint to allow the FST index to be used.

```sql
SELECT COUNT(*)
FROM merchants_dim
WHERE regexp_like(merchant_name, '.*Cafe.*')
```

Record `numDocsScanned` and `timeUsedMs`. The FST index evaluates the pattern against the automaton-encoded dictionary, identifying matching terms before accessing the inverted index posting lists. Only rows whose `merchant_name` belongs to a matching term are scanned.

### FST Index Performance Measurement Table

| Approach | Pattern | numDocsScanned | timeUsedMs |
|----------|---------|:--------------:|:----------:|
| Full scan (skipIndexes hint) | `.*Cafe.*` | | |
| FST-accelerated | `.*Cafe.*` | | |
| Full scan (skipIndexes hint) | `.*Bakery.*` | | |
| FST-accelerated | `.*Bakery.*` | | |

### FST Index Scope of Acceleration

The FST index accelerates regexp patterns that can be evaluated against the term dictionary. Not all patterns benefit equally.

| Pattern Type | Example | FST Effective | Reason |
|--------------|---------|:-------------:|--------|
| Prefix anchor | `Cafe.*` | Yes | FST traversal terminates early for non-matching prefixes |
| Suffix pattern | `.*Cafe` | Partial | Requires reverse traversal; effective if reverse FST is built |
| Contains pattern | `.*Cafe.*` | Partial | Cannot short-circuit at any position; dictionary still filtered |
| Full regex with alternation | `(Cafe|Bakery).*` | Yes | Each branch evaluated against FST; union of matching terms |
| Complex character classes | `[A-Z][a-z]{3,8}` | No | Requires full dictionary scan; FST cannot represent arbitrary character ranges |

For patterns that fall outside the FST's acceleration range, Pinot falls back transparently to a dictionary scan. No error is raised — the FST index provides a best-effort acceleration, not a correctness guarantee.

---

## Index Comparison Table

| Index Type | Column Type | Query Function | Primary Use Case | Key Limitation |
|------------|-------------|----------------|-----------------|----------------|
| JSON index | JSON string | `json_match(col, predicate)` | Fast predicate evaluation and filtering on JSON paths; eliminates row-level deserialization | Only accelerates `json_match`; `jsonExtractScalar` in WHERE still causes a scan without `json_match` |
| Text index | String | `text_match(col, expression)` | Phrase search, boolean term search, wildcard prefix search on free-form text | Terms indexed at segment build time; schema-on-write for the term dictionary; no numeric range support |
| FST index | String | `regexp_like(col, pattern)` | Regular expression matching against a string column's value dictionary | Effectiveness depends on pattern structure; leading wildcards and complex character classes reduce benefit |
| Inverted index | Any | Equality and IN predicates | Exact value matching, low-to-medium cardinality columns | Not effective for range predicates or LIKE patterns |
| Range index | Numeric, timestamp | Range predicates, ORDER BY, BETWEEN | Numeric and time range filtering; segment pruning via min/max metadata | Not effective for equality-only queries; higher storage than inverted index for low-cardinality columns |

---

## `SET skipIndexes` Reference Table

The `SET skipIndexes` hint accepts a comma-separated list of `column=indextype` pairs. Use it to measure baseline performance before an index is applied, or to investigate whether an index is producing correct results.

| Index Type Identifier | Index Being Bypassed | Example Hint |
|-----------------------|---------------------|--------------|
| `json` | JSON index on a JSON column | `SET skipIndexes='attributes=json'` |
| `fst` | FST index on a string column | `SET skipIndexes='merchant_name=fst'` |
| `text` | Text index on a string column | `SET skipIndexes='driver_notes=text'` |
| `inverted` | Inverted index on any column | `SET skipIndexes='city=inverted'` |
| `range` | Range index on a numeric or timestamp column | `SET skipIndexes='fare_amount=range'` |
| `bloom` | Bloom filter on a column | `SET skipIndexes='trip_id=bloom'` |

Multiple hints can be combined in a single statement. Separate them with a comma inside the string value: `SET skipIndexes='attributes=json,city=inverted'`. The hint applies only to the query in the current statement. It does not modify any index configuration and has no effect on subsequently executed queries.

---

## Reflection Prompts

1. A `json_match` query for `"$.route.distance_km" > '20'` returns correct results, but a colleague observes that the numeric comparison is expressed as a string. Explain how the JSON index stores numeric values and how Pinot performs the comparison internally. What would happen if the stored value had been ingested as the string `"28.5"` rather than the number `28.5`?

2. You run the same `text_match` query immediately after ingestion and notice that newly ingested rows are not appearing in the results. A row ingested 30 seconds ago with the note "airport no show" does not match `text_match(driver_notes, '"no show"')`. Explain the lifecycle of the Text index relative to segment sealing, and describe the ingestion state in which `text_match` cannot yet use the index for recently arrived rows.

3. The FST index measurement table shows that `numDocsScanned` for the FST-accelerated query equals the total number of matching rows, but the reduction in `timeUsedMs` compared to the full scan is smaller than expected. Propose two explanations for why the time reduction might be modest even when `numDocsScanned` shows clear improvement.

4. Your team needs to support the following query pattern against a `customer_feedback` JSON column: `WHERE json_match(customer_feedback, '"$.sentiment" = ''negative'' AND "$.category" = ''driver_behavior''')`. Six months after launch, you discover that the JSON index size for `customer_feedback` has grown to 40 GB per server, consuming more disk than the raw column data. Explain why this occurred in terms of the JSON index build process, and describe two strategies for reducing the index size without removing it entirely.

---

[Previous: Lab 18 — Multi-Value Column Analytics](lab-18-multi-value-columns.md) | [Next: Lab 1 — Local Cluster Setup](lab-01-local-cluster.md)
