# 23. Solution Key

## How to Use This Solution Key

This chapter provides design-quality answers to every exercise in Chapter 22. These are not the only valid answers. In many cases, there are multiple defensible approaches and the best answer depends on the specifics of your domain, your query workload and your operational constraints. What these answers aim to provide is a baseline that would hold up in a design review, a technical interview or a team planning session.

Each answer includes reasoning, not just a conclusion. The reasoning matters more than the specific answer because it demonstrates the kind of thinking that leads to sound Pinot design decisions in practice. Where relevant, answers reference the chapter that covers the underlying concept in depth, so you can revisit the full treatment if any point feels unfamiliar.

If you find yourself disagreeing with an answer, that is a good sign. It means you are thinking critically about the design space. Write down your alternative and the reasoning behind it. The best way to use this solution key is as a starting point for discussion, not as a final authority.


## Section A: Comprehension

### 1. Why does the repo maintain both `trip_events` and `trip_state`?

Because historical analytics and current-state queries are fundamentally different workloads and trying to serve both from a single table forces unacceptable compromises in one direction or the other.

The `trip_events` table is an append-only REALTIME table that captures every event as an immutable fact. When a trip is requested, started, completed or cancelled, each transition produces a new row. This table is optimized for time-range aggregations such as "how many trips were completed in the last hour?" or "what is the average fare by city over the past 7 days?" The append-only model means every historical event is preserved, making it ideal for trend analysis, funnel metrics and audit trails.

The `trip_state` table is a REALTIME upsert table that maintains exactly one row per `trip_id`, always reflecting the most recent state. When a consumer asks "what is the current status of trip X?" or "how many trips are currently in progress?", this table provides the answer without requiring the query to scan all historical events and compute the latest state at query time.

If you tried to serve both workloads from a single append-only table, current-state queries would need to deduplicate and find the latest row per entity at query time, which is expensive and scales poorly. If you tried to serve both from a single upsert table, you would lose the historical event trail because each update overwrites the previous row. Maintaining two tables, backed by two Kafka topics, gives each workload a storage model optimized for its access pattern. See Chapter 4 for the full discussion of schema design trade-offs and Chapter 9 for the mechanics of upsert tables.

### 2. What does the broker do that the server does not?

The broker is the query coordinator that sits between the client and the servers. It performs four critical functions that servers never handle.

First, the broker parses and validates the incoming SQL query against the table schema. If a query references a column that does not exist or uses unsupported syntax, the broker rejects it before any server is contacted.

Second, the broker prunes segments. Using segment metadata (time ranges, partition information and column min/max values stored in ZooKeeper), the broker determines which segments could possibly contain matching rows and excludes the rest. This pruning step is one of the most impactful performance optimizations in Pinot because it can eliminate the majority of segments from consideration before any data is scanned.

Third, the broker routes the query to the appropriate servers. It consults the routing table to determine which servers hold the relevant segments and fans the query plan out to those servers in parallel. This is the "scatter" phase of Pinot's scatter gather execution model.

Fourth, the broker merges partial results returned by each server into a single coherent response. Each server returns its local aggregation or partial result set and the broker performs the final reduction: merging aggregations, applying global ORDER BY and LIMIT, enforcing HAVING clauses and assembling the final BrokerResponse JSON that the client receives.

Servers, by contrast, are responsible for hosting segments on disk, executing the query plan against their local segments and returning partial results. They never see the full picture of which other servers are involved or what the final merged result looks like. See Chapter 2 for the full architecture and the scatter gather execution model.

### 3. Why is a segment more important than a single row for Pinot operations?

In Pinot, the segment is the atomic unit of nearly every operational action and individual rows have no independent operational identity.

Storage is organized by segment. Each segment is a self-contained columnar file with its own dictionaries, forward indexes, inverted indexes and metadata. You cannot address, move or reload a single row in isolation.

Indexing happens at the segment level. When you add or change an index, Pinot rebuilds the index for each affected segment independently. You do not index individual rows.

Routing and pruning operate on segments. The broker decides which segments to include in a query based on segment level metadata (time range, partition, column statistics). There is no row-level routing.

Replication, assignment and rebalancing are all segment-granular operations. When a server joins or leaves the cluster, Helix reassigns entire segments, not individual rows.

Retention policies delete entire segments when they fall outside the configured retention window. There is no row-level TTL.

Backfills and replacements work by pushing new segments that replace old ones at the segment level, using lineage tracking to ensure atomicity.

This is why segment sizing, segment count and segment lifecycle management are among the most important operational concerns in Pinot. A table with millions of tiny segments will have degraded metadata overhead and query fan-out, while a table with a handful of enormous segments will have poor parallelism and long reload times. See Chapter 3 for the complete treatment of segments, their lifecycle and sizing guidelines.

### 4. Why are message keys critical for the `trip-state` topic?

Message keys are critical because Pinot's upsert correctness depends on all records for the same entity being consumed by the same server instance. The mechanism that enforces this is Kafka's key-based partitioning.

When a producer writes a message to the `trip-state` topic with `trip_id` as the message key, Kafka hashes that key and assigns the message to a deterministic partition. All subsequent updates for the same `trip_id` land on the same partition. Because Pinot's LowLevel consumer assigns each partition to a specific server, all updates for a given trip are consumed by the same server, which maintains the in-memory primary key lookup map for that partition.

If messages were produced without keys (or with random keys), updates for the same `trip_id` could land on different partitions and therefore be consumed by different servers. Each server would have an incomplete view of that entity's history. The upsert lookup map on server A might point to version 3 of a trip while server B holds version 5. Queries would return duplicates or stale data and the upsert guarantee would be silently broken.

This is not a theoretical risk. It is one of the most common production failures in upsert deployments and it is entirely preventable by ensuring that producers always set the message key to the primary key column value. See Chapter 9 for the full discussion of partition alignment and upsert correctness and Chapter 8 for the partition-to-server assignment model.

### 5. What is the relationship between the JSON Schema contract and the Pinot schema?

The JSON Schema and the Pinot schema serve different purposes at different boundaries in the data pipeline and conflating them leads to governance gaps.

The JSON Schema (stored in the `contracts/` directory) is a data contract that validates the structure and types of event payloads at the producer boundary. It defines what fields a producer must include, what data types those fields must have, which fields are required versus optional and what value constraints apply (such as minimum values or enum ranges). It is enforced at publish time, before the data enters Kafka and its purpose is to prevent malformed events from contaminating the stream.

The Pinot schema (stored in the `schemas/` directory) is a configuration document that tells Pinot how to store, index and serve the fields it receives. It categorizes each field as a dimension, metric or dateTime column. It specifies data types in Pinot's own type system (which does not map one-to-one with JSON types). It defines the primary key columns for upsert tables. It controls null handling behavior. Its purpose is to optimize query performance and storage efficiency within Pinot.

The two schemas should align on field names and broad type compatibility, but they are not identical and should not be managed as a single artifact. A JSON Schema might define a field as a string with a regex pattern constraint, while the Pinot schema stores that same field as a STRING dimension with an inverted index. A JSON Schema might include metadata fields (like a schema version identifier) that Pinot does not need to store. Conversely, the Pinot schema might include derived helper columns (like a bucketed timestamp or a normalized country code) that do not exist in the source event at all.

Maintaining both schemas and validating their compatibility as part of your CI pipeline is the contract-driven approach that Chapter 21 demonstrates in the capstone. See Chapter 4 for Pinot schema design and Chapter 13 for the API and contract patterns.


## Section B: Modeling

### 6. Add three helper columns you would introduce for your own domain and justify each.

Helper columns are precomputed fields added to the Pinot schema that move work from query time to ingestion time. The goal is to eliminate repetitive runtime computation on hot query paths. Three strong examples for a rides platform are as follows.

A `trip_hour` column of type INT that stores `toEpochHours(event_time)` is the first example. Dashboard queries that group by hour are among the most common aggregation patterns and computing this bucketing at ingestion time means the GROUP BY operates on a compact integer rather than calling a transform function on every row during every query execution.

A `country_code` column of type STRING that normalizes the raw city or region field into a standardized ISO country code is the second example. Many operational and business queries filter or group by country and performing the normalization at ingestion time (via an ingestion transform or upstream enrichment) avoids repeated string manipulation at query time and makes inverted index lookups far more efficient due to lower cardinality.

A `fare_bucket` column of type STRING that classifies each trip's fare into a categorical range such as "under_10", "10_to_25", "25_to_50" or "over_50" is the third example. This supports common business intelligence queries that want to analyze trip distribution by fare tier without running CASE expressions on every query. The column has very low cardinality, making it an excellent candidate for a dictionary-encoded dimension with an inverted index.

The key principle is that helper columns should target recurring query patterns that affect the hot path. If a bucketing or normalization appears in five or more dashboard queries, it almost certainly belongs in the schema. See Chapter 4 for the full helper column design pattern.

### 7. Pick one field you would denormalize and one you would leave in a dimension table.

Denormalize `merchant_name` into the `trip_events` fact table. Merchant name appears in nearly every operational dashboard, typically as a display label alongside aggregated metrics like trip count or revenue. If merchant name lives only in the `merchants_dim` dimension table, every dashboard query must perform a lookup join (or an MSE join) to resolve it. Embedding the name directly in the fact table eliminates this join for the most common query pattern.

Leave `merchant_contract_tier` in the `merchants_dim` dimension table. Contract tier is a business attribute that changes infrequently and is only relevant for a narrow set of analytical queries (such as "compare revenue by contract tier"). It does not appear on operational dashboards and is not a filter or group-by column on hot query paths. Denormalizing it into the fact table would increase storage cost for every event row while providing minimal query performance benefit. When a query does need contract tier, it can use a dimension lookup join or the MSE join path, which is acceptable for the lower query volume and less stringent latency requirements of that workload.

The decision framework is straightforward. If a field from a related entity appears in hot-path filters, GROUP BY clauses or display columns across multiple high-frequency queries, denormalize it. If a field is rarely queried or only needed for ad-hoc analysis, keep it in a dimension table and pay the join cost only when needed. See Chapter 4 for denormalization trade-offs and Chapter 7 for dimension table ingestion.

### 8. Explain when you would use a latest-state table rather than only an append-only fact table.

Use a latest-state (upsert) table whenever consumers regularly ask "what is true right now?" about individual entities and the cost of computing that answer from an append-only table would be prohibitive.

Consider a trip monitoring dashboard that shows all currently active trips with their latest status, driver assignment and estimated arrival time. In an append-only table, answering this question requires scanning all events, grouping by `trip_id` and selecting the row with the maximum timestamp for each group. For a table with hundreds of millions of events and millions of unique trips, this query is expensive and unpredictable in latency.

A latest-state upsert table maintains exactly one row per primary key, always reflecting the most recent update. The monitoring dashboard query becomes a simple scan with a WHERE clause on status, returning results in single digit milliseconds regardless of how many historical updates have occurred.

The trade-off is that upsert tables consume more memory (for the primary key lookup map), require strict partition alignment between the Kafka topic and Pinot servers and lose the historical event trail. This is why the capstone maintains both `trip_events` and `trip_state` rather than trying to serve all workloads from one table. If your workload is exclusively historical analytics with no current-state queries, an append-only table is simpler and more resource-efficient. See Chapter 9 for the full mechanics and memory implications of upsert.

### 9. Identify a potential null-handling risk in your own event model.

A common null-handling risk arises when an event field like `driver_id` is legitimately null during certain lifecycle stages but is used as a filter or GROUP BY column in queries. When a trip is first requested but not yet assigned to a driver, `driver_id` is null. If the Pinot schema does not enable column-based null handling (`enableColumnBasedNullHandling: true`), Pinot silently replaces the null with the default value for the column type, which is an empty string for STRING columns or zero for numeric columns.

This creates a subtle data quality problem. Queries that count trips per driver would include a phantom driver with ID "" (empty string) or 0, aggregating all unassigned trips under a fake driver entity. Queries that filter on `driver_id IS NOT NULL` would not work correctly because the null has been replaced with a default value that looks like a real value.

The mitigation is twofold. Enable column-based null handling in the schema so that nulls are tracked via null bitmaps and remain distinguishable from default values. Then ensure that query authors are aware of null semantics and use appropriate predicates. This is particularly important for upsert tables where early lifecycle events may have sparse field populations that are filled in by later updates. See Chapter 4 for the full null handling discussion.

### 10. Choose a field that deserves a range index and explain why.

The `fare_amount` field deserves a range index. Fare amount is a continuous numeric metric that is frequently queried with range predicates such as `WHERE fare_amount > 50` or `WHERE fare_amount BETWEEN 10 AND 25`. Without a range index, Pinot must scan every value in the column and evaluate the predicate row by row. With a range index, Pinot can use a tree-based structure to quickly identify the document IDs that fall within the requested range, skipping the majority of values.

A range index is more appropriate than an inverted index for this column because fare values have high cardinality (potentially thousands of unique values). An inverted index would create one bitmap per unique value, which is wasteful when the query pattern involves ranges rather than exact equality matches. The range index is specifically designed for this access pattern.

Fields that are good candidates for range indexes share two characteristics: they have numeric or timestamp types with high cardinality and they are queried with inequality or BETWEEN predicates rather than exact equality. Fields like `event_time`, `distance_km` and `duration_minutes` all fit this profile. See Chapter 6 for the full range index discussion, including the trade-offs around storage overhead and the relationship between range indexes and sorted indexes.


## Section C: Query Design

### 11. Rewrite a business KPI into a Pinot-friendly group-by query.

Consider the business KPI "average trip fare by city for the last 24 hours." A Pinot-friendly query for this would be:

```sql
SELECT city,
       AVG(fare_amount) AS avg_fare,
       COUNT(*) AS trip_count
FROM trip_events
WHERE event_time > ago('P1D')
  AND trip_status = 'COMPLETED'
GROUP BY city
ORDER BY avg_fare DESC
LIMIT 50
```

This query is Pinot-friendly for several reasons. It includes a time boundary (`event_time > ago('P1D')`) that enables segment pruning, eliminating all segments whose time range falls entirely outside the last 24 hours. It uses a selective filter on `trip_status` that works well with an inverted index. The GROUP BY on `city` produces a bounded result set because the number of cities is finite and manageable. The aggregation functions (AVG, COUNT) are natively supported and can be partially computed on each server before the broker merges them.

The query avoids patterns that Pinot penalizes: there is no SELECT *, no unbounded scan, no complex subquery and no function applied to a column in the WHERE clause that would defeat index usage. See Chapter 10 for the full set of query writing guidelines and anti-patterns.

### 12. Give an example of a query that should use MSE.

A query that joins trip events with merchant dimension data to compute revenue by merchant contract tier should use the Multi-Stage Engine:

```sql
SET useMultistageEngine = true;
SELECT m.contract_tier,
       SUM(t.fare_amount) AS total_revenue,
       COUNT(*) AS trip_count
FROM trip_events t
JOIN merchants_dim m ON t.merchant_id = m.merchant_id
WHERE t.event_time > ago('P7D')
GROUP BY m.contract_tier
ORDER BY total_revenue DESC
```

This query requires MSE because it performs a distributed JOIN between two tables. The single stage (v1) engine does not support inter-table joins at all. MSE decomposes this query into multiple stages: one stage scans and filters `trip_events`, another scans `merchants_dim`, a shuffle stage co-locates rows by the join key (`merchant_id`) and a final stage performs the aggregation and ordering.

MSE is the right choice here because the join adds genuine analytical value that cannot be achieved through denormalization alone (contract tier is not denormalized into the fact table) and the query latency requirements for this type of business intelligence query are more relaxed than for operational dashboards. See Chapter 11 for the full MSE architecture and tuning guidance.

### 13. Give an example of a query that should probably not use MSE.

A simple aggregation query that operates on a single table should not use MSE:

```sql
SELECT city, COUNT(*) AS trip_count
FROM trip_events
WHERE event_time > ago('P1H')
GROUP BY city
ORDER BY trip_count DESC
LIMIT 20
```

This query involves no joins, no window functions, no subqueries and no set operations. It is a straightforward scatter gather aggregation that the v1 engine handles with maximum efficiency. Each server computes a local count per city and the broker merges the partial counts into a final result.

Running this query through MSE would add unnecessary overhead. MSE introduces query planning stages through Apache Calcite, intermediate result serialization and data shuffles between stages, all of which add latency for zero functional benefit when the query is a single-table aggregation. The v1 engine was purpose-built for this exact pattern and will consistently deliver lower latency for it. The rule of thumb is to use MSE only when the query requires a capability that the v1 engine lacks (joins, windows, subqueries). See Chapter 11 for the decision framework between v1 and MSE.

### 14. Write a query that would benefit from time pruning.

```sql
SELECT trip_status, COUNT(*) AS cnt
FROM trip_events
WHERE event_time BETWEEN '2024-01-15T00:00:00Z' AND '2024-01-15T23:59:59Z'
GROUP BY trip_status
```

This query benefits from time pruning because the WHERE clause constrains the time column to a single day. Every segment in Pinot carries metadata recording its minimum and maximum time values. Before the broker routes this query to servers, it examines each segment's time range and excludes any segment whose range does not overlap with January 15, 2024. In a table that retains 90 days of data, this single predicate eliminates roughly 98% of segments from the scan.

Time pruning is most effective when the time column is the table's dateTime column (which Pinot uses for segment level time metadata) and when the query's time filter is specific enough to exclude a meaningful proportion of segments. Queries that scan "all time" or use very broad time ranges receive no pruning benefit. See Chapter 10 for time pruning mechanics and Chapter 3 for how segment time ranges are recorded in metadata.

### 15. Write a query that would benefit from star-tree style pre-aggregation.

```sql
SELECT city, trip_status,
       SUM(fare_amount) AS total_fare,
       COUNT(*) AS trip_count
FROM trip_events
WHERE event_time > ago('P30D')
GROUP BY city, trip_status
```

This query aggregates fare amounts and trip counts by a fixed set of dimensions (city and trip status) over a rolling 30-day window. If this exact GROUP BY combination is served hundreds of times per minute across operational dashboards, each execution scans millions of rows and computes the same aggregation.

A StarTree index pre-computes these aggregations at segment build time for the configured dimension and metric combinations. With a StarTree that includes `city` and `trip_status` as dimensions and `fare_amount` and `*` (for COUNT) as metrics, Pinot can answer this query by reading pre-aggregated nodes from the tree structure instead of scanning raw rows. The speedup is often 10x to 100x for high cardinality tables.

StarTree is the right choice when the same dimension and metric combination appears in multiple hot-path queries and the acceptable trade-off is increased segment build time and storage. It is not appropriate for ad-hoc queries with unpredictable GROUP BY combinations. See Chapter 6 for the full StarTree configuration and Chapter 17 for measuring its performance impact.


## Section D: Ingestion and CDC

### 16. Explain the failure mode if `trip-state` messages are not keyed by `trip_id`.

If messages on the `trip-state` topic lack a stable `trip_id` key, Kafka distributes them across partitions using round-robin or a random assignment strategy. This means successive updates for the same trip can land on different partitions.

Because Pinot assigns each partition to a specific server, updates for the same trip would be consumed by different servers. Each server maintains its own independent primary key lookup map. Server A might hold version 1 of trip T123, while server B holds version 3 and server C holds version 2. None of them knows about the others.

The observable failure is phantom duplicates in query results. A query for trip T123 returns three rows (one from each server) instead of one and none of them are necessarily the latest version. Aggregation queries that count active trips would overcount because the same trip appears multiple times. The upsert guarantee, which promises exactly one row per primary key, is silently violated.

This failure mode is particularly insidious because it does not produce errors or exceptions. The system appears to work normally. The only signal is incorrect query results, which may not be noticed until a stakeholder questions the numbers. Prevention requires ensuring that producers always set the Kafka message key to the primary key value (`trip_id`), which guarantees deterministic partition assignment. See Chapter 9 for the full partition alignment discussion and Chapter 8 for producer-side key requirements.

### 17. What evidence would you gather before changing realtime flush thresholds?

Changing flush thresholds affects segment size, segment count, query performance, ingestion freshness and recovery time. Making this change without evidence is dangerous because the effects are interconnected and not always intuitive.

Before changing thresholds, gather evidence on four dimensions. First, examine current segment sizes by querying the segment metadata API. Segments that are consistently under 100,000 rows suggest the threshold may be too aggressive, creating excessive small-segment churn. Segments that are consistently over 5 million rows suggest the threshold may be too loose, creating segments that are slow to build and reload.

Second, measure ingestion freshness. The consuming-to-online lag (visible through Pinot's consumption status metrics) tells you how long data sits in a consuming segment before it becomes queryable. If the current threshold creates a flush cadence of 30 minutes but the business needs 5-minute freshness, you need a more aggressive threshold.

Third, assess segment churn rate. A table that produces hundreds of new segments per hour creates metadata pressure in ZooKeeper and increases the broker's pruning workload. If the segment creation rate is unusually high, the flush threshold may be too small.

Fourth, understand recovery time. When a server restarts, it must rebuild consuming segments by replaying from the last committed offset. Larger flush thresholds mean longer replay times during recovery.

Only with this evidence can you make a principled trade-off between segment size (larger is better for query efficiency), freshness (more frequent flushes mean newer data is queryable sooner) and recovery speed (smaller segments mean faster crash recovery). See Chapter 8 for flush threshold configuration and Chapter 18 for the observability metrics that inform this decision.

### 18. How would you backfill a missing dimension table?

Backfilling a dimension table is a batch ingestion operation that requires planning, a clear rollback path and validation.

Start by preparing the data source. For a missing `merchants_dim` table, extract the dimension data from your source of truth (a relational database, a curated CSV export or a data lake table). Validate the data against the JSON Schema contract defined in `contracts/` to ensure all required fields are present and correctly typed.

Create a versioned ingestion JobSpec that specifies the input format, the input path, the table name, the push mode and any transforms. Versioning the JobSpec means storing it alongside your table configuration in source control so that the exact ingestion parameters are reproducible.

Execute the batch ingestion using the Pinot ingestion job (either the standalone launcher or the Minion-based task framework). For a new dimension table, use `APPEND` push mode for the initial load. For a replacement of an existing dimension table, use `REFRESH` or segment replacement with lineage tracking to atomically swap old segments for new ones.

After ingestion completes, validate the results by querying the table to confirm row counts, spot-checking key values and verifying that downstream lookup joins produce expected results. If validation fails, the rollback plan is to delete the newly pushed segments and, if you used segment replacement, allow the lineage to revert to the previous segments.

Document the backfill (date, source, row count, any data quality exceptions) so that future operators understand the provenance of the data. See Chapter 7 for the full batch ingestion framework and Chapter 21 for the capstone's approach to dimension table management.

### 19. What data contract change would force a schema and table review?

Any change to a contract field that serves as a primary key, a time column, a partition key or a comparison column in an upsert table requires both a schema review and a table config review because these fields have structural dependencies beyond their data type.

For example, changing the type of `trip_id` from STRING to INT in the event contract would require updating the Pinot schema's primaryKeyColumns type, potentially rebuilding the upsert primary key lookup map and reprocessing all existing segments. Changing the time column's granularity (from milliseconds to seconds, for instance) would affect segment time metadata, time boundary calculations and every query that references the time column.

Adding a new required field to the contract is lower risk but still demands a schema review to determine whether the field should be added as a dimension, metric or dateTime column, whether it needs an index and whether the default value for existing segments (which lack the field) is acceptable.

Removing a field from the contract is especially dangerous if any Pinot index, ingestion transform or downstream query depends on that field. The schema review must confirm that no active configuration references the removed field before the change is deployed.

The contract-driven approach in Chapter 21 treats these reviews as a CI gate: contract changes trigger automated validation against the Pinot schema and table config and breaking changes require explicit approval. See Chapter 4 for schema evolution and Chapter 13 for the contract validation pattern.

### 20. How would you model logical deletes?

Pinot does not support physical row deletion in REALTIME tables. Modeling logical deletes requires an explicit convention between producers and the table configuration.

The recommended approach is to add a `deleted` field (BOOLEAN or STRING) to both the event contract and the Pinot schema. When an entity is logically deleted, the producer emits an update with `deleted: true` (and the same primary key). In an upsert table, this update replaces the previous row and the `deleted` flag is now visible to queries.

All queries that should respect logical deletes must include `WHERE deleted = false` (or equivalent) as a standard predicate. This is a discipline requirement: any query that omits the predicate will include logically deleted rows in its results.

For tables with high delete volumes, consider configuring an ingestion filter that drops records marked as deleted before they are stored. This reduces storage overhead but sacrifices the ability to query deleted records for audit purposes.

An alternative approach uses Pinot's `deleteRecordColumn` feature in upsert table config, which allows you to designate a boolean column that, when true, causes the upsert engine to remove the key from the primary key lookup map. This makes the deletion invisible to queries without requiring every query to include a WHERE clause filter. However, it also means the deletion is not recoverable from the Pinot side, so you must retain the delete event in Kafka for replay scenarios.

Whichever approach you choose, the delete semantics must be documented in the data contract and understood by both producers and query consumers. See Chapter 9 for the `deleteRecordColumn` configuration and Chapter 4 for schema modeling patterns.


## Section E: Operations

### 21. Define a freshness SLO for `trip_state`.

A freshness SLO for `trip_state` should state a specific, measurable lag tolerance. For example: "99% of consumed records must be queryable within 30 seconds of arriving on the `trip-state` Kafka topic, measured over any rolling 5-minute window."

This definition has several important properties. It names a concrete number (30 seconds) rather than a vague commitment like "near real time." It specifies a percentile (99%) rather than an average, because average freshness can mask a long tail where some records take minutes to become visible. It defines the measurement window (rolling 5 minutes) so that brief transient spikes during segment flushes do not trigger false alerts.

The 30-second threshold is appropriate for a trip state table because operational consumers (dispatchers, customer support agents) need current data but can tolerate a half-minute delay. If the table served a fraud detection system that required sub second freshness, the SLO would be tighter.

To monitor this SLO, track the `realtimeConsumptionCatchUpTimeMs` metric and the difference between the Kafka topic's latest offset and the Pinot consumer's committed offset. Alert when the lag exceeds the SLO threshold for longer than the measurement window. See Chapter 18 for the observability metrics that support freshness monitoring.

### 22. Define a query latency SLO for one dashboard path.

For the city operations dashboard that displays real time trip counts and average fares by city, a reasonable SLO is: "The p95 broker response time for the city summary query must be under 200 milliseconds, measured over any rolling 10-minute window, under production concurrency."

The "under production concurrency" qualifier is essential. A query that returns in 50ms on an idle cluster may take 500ms when 200 concurrent dashboard users are all polling every 10 seconds. The SLO must reflect realistic load conditions, not best-case single-query benchmarks.

The 200ms threshold is appropriate for a dashboard query because users perceive dashboard refreshes under 300ms as instantaneous and the 200ms target provides a safety margin. API-serving queries that back a mobile application might require a tighter SLO (under 50ms at p99), while ad-hoc analyst queries might accept a looser target (under 2 seconds at p90).

Monitor this SLO using broker-side query latency metrics, broken down by table and query pattern. Pinot exposes per-table query latency histograms that can be scraped by Prometheus and visualized in Grafana. See Chapter 17 for the performance engineering methodology and Chapter 18 for dashboard and alerting setup.

### 23. What would you inspect first in a stale-data incident?

When data freshness degrades, start by checking the Kafka consumer lag for the table's realtime consumers. The consumer lag is the difference between the latest offset on the Kafka partition and the offset that Pinot has consumed up to. This single metric tells you whether the problem is on the ingestion side (Pinot is falling behind) or the source side (no new messages are being produced).

If consumer lag is growing, the issue is on the Pinot side. Check whether any consuming segments are stuck in the CONSUMING state by querying the segment status API. Look for servers that may be overloaded, experiencing garbage collection pressure or failing to flush consuming segments due to resource constraints. Check the controller logs for any segment commit failures.

If consumer lag is zero but the data still appears stale in queries, the issue may be that consuming segments have not yet been flushed and committed. Data in consuming segments is queryable, but if the consuming segment is healthy and the broker response still shows old data, verify that the broker's routing table includes the consuming segments and that the time boundary is not inadvertently excluding them.

If no new messages are appearing on the Kafka topic at all, the problem is upstream of Pinot. Check the producer service health and the Kafka cluster health. See Chapter 18 for the full stale-data troubleshooting runbook and Chapter 19 for common failure modes.

### 24. What would you inspect first after a rebalance?

After a rebalance, the first thing to inspect is whether all segments have transitioned to the ONLINE state on their newly assigned servers. Query the segment status API or the Pinot controller UI to verify that no segments are stuck in OFFLINE, ERROR or IN_TRANSITION states.

A rebalance moves segment assignments between servers and the receiving servers must download segments from deep store and load them into memory. If a server is low on disk space, has insufficient memory or is experiencing network issues reaching deep store, segments can fail to come online. These failures are silent from the query perspective: queries will still execute, but they will silently skip the missing segments, returning incomplete results.

After confirming that all segments are ONLINE, verify that the routing table on each broker reflects the new assignments. Brokers periodically refresh their routing tables from ZooKeeper, so there may be a brief window where the broker routes to the old server assignments. Check the broker logs for routing table refresh events.

Finally, run a representative set of queries and compare results against a pre-rebalance baseline. If row counts or aggregation values change significantly, investigate whether any segments were lost or duplicated during the transition. See Chapter 16 for rebalancing mechanics and Chapter 18 for post-rebalance validation procedures.

### 25. How would you prove an index change improved the hot path?

Proving an index change requires controlled before-and-after measurement under representative conditions. The word "prove" is important here because adding an index always has a cost (storage, build time, reload time) and you must demonstrate that the performance benefit justifies that cost.

Before making the index change, establish a baseline. Run the target hot-path queries at least 50 times under representative production concurrency (not on an idle cluster). Record the p50, p95 and p99 broker response times. Also record the `numEntriesScannedInFilter` and `numEntriesScannedPostFilter` values from the broker response metadata, which tell you how many rows Pinot actually examined to answer the query.

Apply the index change in the table config and trigger a segment reload. Wait for all segments to finish reloading (verify through the segment status API).

After the reload completes, repeat the same measurement protocol: same queries, same concurrency level, same number of iterations. Compare the p50, p95 and p99 latencies. Compare the scan counts. A successful index change should show a meaningful reduction in scanned entries (often by orders of magnitude) and a corresponding reduction in query latency.

Document the results with the specific numbers: "Adding an inverted index on `city` reduced p95 latency for the city summary query from 340ms to 45ms and reduced entries scanned in filter from 12 million to 85,000." This evidence is what holds up in a design review. See Chapter 17 for the complete before-and-after measurement methodology and Chapter 6 for index selection guidance.


## Section F: Architecture

### 26. Build a decision tree that says when Pinot is the right serving layer for your workload.

The decision tree follows three questions, each of which must be answered affirmatively for Pinot to be the right choice.

First, does the workload require data freshness measured in seconds or low single digit minutes? If the data can be hours or days old, a traditional data warehouse (BigQuery, Snowflake, Redshift) or a lakehouse (Databricks, Apache Iceberg on Trino) is simpler, often cheaper and provides richer SQL support. Pinot's architecture is optimized for stream ingestion and using it purely for batch workloads surrenders its primary advantage.

Second, are the queries analytical in nature, meaning aggregations, GROUP BY operations and filters over large datasets rather than single row transactional lookups? If the workload is primarily key value lookups or CRUD operations, a relational database (PostgreSQL, MySQL) or a key value store (DynamoDB, Redis) is the right tool. Pinot's columnar storage and segment level indexing are designed for analytical scans, not point lookups.

Third, must the results be served at low latency (sub second) and high concurrency (hundreds or thousands of simultaneous queries per second) to applications, dashboards or APIs? If the consumer is a data analyst running ad-hoc queries who can wait 10 to 30 seconds, a query engine like Trino, Spark SQL or Presto is more flexible and does not require the data modeling discipline that Pinot demands.

When all three conditions are true, Pinot is in its sweet spot. When one or more conditions are false, the workload is likely better served by a different tool or by a combination where Pinot handles the real time serving layer and another system handles the workload that falls outside its strengths. See Chapter 20 for the full decision framework.

### 27. Name two reasons to keep a warehouse or lakehouse alongside Pinot.

First, warehouses and lakehouses are the right home for long-horizon historical analysis and heavyweight joins. Pinot's retention policies typically keep 30 to 90 days of data. Analysts who need to analyze trends over multiple years, join dozens of tables or run complex window functions across massive datasets need a system designed for those query patterns. Warehouses provide practically unlimited retention, full SQL compliance and optimizers designed for long-running analytical queries.

Second, warehouses serve as the source of truth for backfills, reconciliation and data quality auditing. When a schema change or data quality issue requires reprocessing historical data, the warehouse provides the authoritative dataset from which corrected segments can be generated and pushed to Pinot. Without a warehouse, you are dependent on Kafka retention (which is finite) as your only source for historical replay and that is a fragile position for any production system.

A well designed architecture treats Pinot and the warehouse as complementary layers: Pinot for real time serving with sub second latency and the warehouse for deep analysis with minutes-to-hours latency. Data flows from source systems into both layers (via streams to Pinot and via batch pipelines to the warehouse) and the warehouse can also feed corrected or enriched data back into Pinot through batch ingestion. See Chapter 20 for the full architectural pairing discussion.

### 28. What cluster isolation boundary would you introduce first in a multi-team environment?

The first isolation boundary to introduce is tenant-based separation at the server and broker level. Pinot's tenant model allows you to assign servers and brokers to named tenants and then assign each table to a specific server tenant and broker tenant. This ensures that one team's tables are hosted on a dedicated set of servers that are not shared with another team's workload.

This matters because without tenant isolation, a single team's expensive query or runaway ingestion pipeline can consume all available server resources (CPU, memory, disk I/O), degrading query performance for every other team on the cluster. Tenant isolation creates a resource boundary: team A's servers can be saturated without affecting team B's servers.

Tenant isolation should be introduced before index-level or query-level optimizations because it addresses the most catastrophic failure mode in a shared cluster, which is noisy-neighbor interference. It is also a prerequisite for meaningful SLOs because you cannot guarantee latency for team B's queries if team A's workload can consume unbounded resources on the same servers.

Within each tenant, you can then apply finer-grained controls such as query quotas (limiting queries per second per table), resource limits (bounding the number of threads or memory per query) and workload isolation policies. But the tenant boundary is the foundation on which all other isolation mechanisms build. See Chapter 16 for tenant configuration and Chapter 14 for deployment topology patterns.

### 29. Which part of the capstone would you reuse unchanged in a production deployment?

The contract-driven approach, including the JSON Schema event contracts, the AsyncAPI stream contracts and the CI validation that checks compatibility between contracts and Pinot schemas, is the part most directly reusable in production. It requires no modification because its value is architectural, not implementation-specific.

The contracts define a governance boundary between producers and consumers that prevents the most common class of production incidents: a producer changes a field type, removes a required field or adds a field that conflicts with an existing schema and the change silently breaks downstream ingestion or query correctness. By validating contracts in CI before any code is deployed, you catch these breaking changes early, when they are cheap to fix, rather than in production, when they cause data quality incidents.

The specific schemas, table configs and query packs from the capstone are also useful as templates, but they require adaptation to your domain's entities, access patterns and scale requirements. The contract framework, by contrast, works for any domain because it encodes a process (validate before deploy) rather than a domain model. See Chapter 21 for the full capstone walkthrough and Chapter 13 for the contract and API patterns.

### 30. Which part would you replace first?

The synthetic data generator is the first thing you would replace. The capstone's generator produces simulated trip events with randomized fields, which is invaluable for demonstration and testing but has no place in a production deployment that consumes real business events from real source systems.

In production, the generator is replaced by the actual producer services (trip service, order service, merchant service) that emit events based on real user activity. These producers use the same JSON Schema contracts that the capstone defines, so the contract validation layer continues to work. But the data itself comes from production systems rather than random number generators.

The replacement is straightforward because the capstone's architecture intentionally decouples the producer layer from the Pinot serving layer through Kafka topics and data contracts. Swapping the synthetic generator for a real producer requires no changes to the Pinot schemas, table configs, ingestion pipelines or query layer. The only change is in the source of messages on the Kafka topics. This clean separation is a key design lesson of the capstone: build your Pinot layer so that it is agnostic to the producer implementation, caring only that messages conform to the agreed contract. See Chapter 21 for the full architecture.

## Stretch Exercise Note

### 31. Extend the repo.

This exercise is intentionally open-ended. A strong response would include a new dimension table (for example, `drivers_dim` with driver rating, vehicle type and home city), a new API endpoint that joins trip data with the new dimension, a simulation script that generates dimension updates on a schedule, a contract validation test that verifies the new dimension schema and a brief write-up explaining the denormalization trade-off.

The purpose is to verify that you can apply the full contract-driven workflow end to end: define the contract first, derive the schema and table config, build the ingestion path, expose the data through an API and validate with automated tests. See Chapter 21 for the pattern to follow.

*Previous chapter: [22. Exercises](./22-exercises.md)

*Next chapter: [24. Glossary](./24-glossary.md)
