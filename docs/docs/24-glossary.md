# 24. Glossary

This glossary collects the key terms and concepts used throughout the Apache Pinot playbook. Definitions are written to be self-contained, so you can look up any term without needing to re-read the chapter in which it first appears. Terms are listed in alphabetical order. Where a term maps directly to a Pinot configuration key or API surface, the canonical spelling is used.

## Analytics serving layer

A system optimized to answer analytical questions for applications, dashboards or users at low latency. Unlike a general-purpose OLAP warehouse, an analytics serving layer is designed to sustain high query throughput with predictable tail latencies, making it suitable for user facing and machine-facing workloads.

**Primary chapter:** Chapter 1 (Apache Pinot at a Glance)

## AsyncAPI

A specification for describing event-driven APIs, analogous to what OpenAPI does for request-response APIs. In a Pinot-centric data platform, AsyncAPI contracts can formally describe the schema and semantics of streams that feed realtime tables.

**Primary chapter:** Chapter 13 (APIs, Clients and Contracts)

## Batch ingestion

The process of loading data into Pinot from bounded data sets such as files in HDFS, S3, GCS or ADLS. Batch ingestion produces completed, immutable segments that are uploaded to the deep store and then assigned to servers for serving.

**Primary chapter:** Chapter 7 (Batch Ingestion)

## Bloom filter

A probabilistic data structure attached to a column that can quickly determine whether a value is definitely absent from a segment. Bloom filters trade a small amount of memory for significant query-time savings on equality predicates by enabling fast segment level pruning.

**Primary chapter:** Chapter 6 (The Indexing Cookbook)

## Broker

The Pinot component that accepts queries from clients, fans them out to the appropriate servers and merges partial results into a final response. Brokers maintain awareness of table-to-server mappings through Helix and apply query routing rules, replica group preferences and query quota enforcement before dispatching work.

**Primary chapter:** Chapter 2 (Architecture and Components)

## Cluster

The top-level unit of a Pinot deployment, consisting of controllers, brokers, servers and optionally minions, all coordinated through a shared ZooKeeper quorum. A single cluster can host many tables across multiple tenants and all metadata for the cluster is stored under a single ZooKeeper namespace.

**Primary chapter:** Chapter 2 (Architecture and Components), Chapter 3 (Storage Model: Segments, Tenants and Clusters)

## Column store

The physical storage layout Pinot uses within each segment, where values for each column are stored contiguously rather than row by row. Column-oriented storage enables efficient compression, vectorized reads and the ability to scan only the columns a query actually references.

**Primary chapter:** Chapter 3 (Storage Model: Segments, Tenants and Clusters)

## Comparison column

The column used to determine which record is newer when Pinot applies upsert logic. By default, Pinot uses the segment sequence number and record offset, but you can configure an explicit comparison column (often a timestamp or version counter) to give deterministic ordering regardless of ingestion order.

**Primary chapter:** Chapter 9 (Upsert, Dedup and CDC Patterns)

## Complex type

A schema field whose raw value is a structured object such as a JSON document, a map or a nested array. Pinot can flatten or unnest complex types during ingestion through transform functions or you can index them directly using the JSON index for runtime path-based queries.

**Primary chapter:** Chapter 4 (Schema Design and Data Modeling)

## Consuming lag

The difference, measured in time or offset, between the latest event published to a stream partition and the latest event ingested by a Pinot realtime server. Consuming lag is a primary health signal for realtime tables and directly impacts data freshness.

**Primary chapter:** Chapter 8 (Stream Ingestion), Chapter 18 (Observability, Operations and Minions)

## Controller

The Pinot component responsible for cluster administration, metadata management and orchestration of data movement. Controllers host the Helix controller logic, expose REST APIs for table and schema management and coordinate segment assignment, rebalance operations and minion task scheduling.

**Primary chapter:** Chapter 2 (Architecture and Components)

## Control plane

The part of the system responsible for metadata, administration and coordination. In Pinot, the control plane is primarily embodied by the controller and ZooKeeper, which together manage table configurations, schema definitions, segment assignments and cluster topology.

**Primary chapter:** Chapter 2 (Architecture and Components)

## Data contract

A formal, machine-readable agreement that defines the structure, semantics and quality expectations of a data interface. In the context of Pinot, data contracts can describe stream schemas (via AsyncAPI), query APIs (via OpenAPI) and configuration shapes (via JSON Schema), enabling automated validation and cross-team collaboration.

**Primary chapter:** Chapter 13 (APIs, Clients and Contracts)

## DateTime field

A schema field type that represents a time column with an explicitly declared format and granularity. DateTime fields are used for time based partitioning, retention enforcement and time-range pruning during query execution.

**Primary chapter:** Chapter 4 (Schema Design and Data Modeling)

## Dedup (deduplication)

A table-level mode that silently drops incoming records whose primary key already exists in the table, ensuring each key appears at most once. Unlike upsert, dedup does not compare or replace values. It simply discards duplicates, which makes it lighter weight but suitable only when first-write-wins semantics are acceptable.

**Primary chapter:** Chapter 9 (Upsert, Dedup and CDC Patterns)

## Deep store

A durable, shared storage system (such as S3, GCS, HDFS or ADLS) where Pinot persists completed segments for long-term retention. Servers download segments from the deep store when they are assigned new segment responsibilities and the deep store acts as the source of truth for segment recovery.

**Primary chapter:** Chapter 3 (Storage Model: Segments, Tenants and Clusters)

## Delete marker

A special record in an upsert-enabled table that signals the logical deletion of a primary key. When Pinot encounters a record flagged as a delete marker, it removes the key from query visibility without physically purging the underlying data until a subsequent compaction or purge task runs.

**Primary chapter:** Chapter 9 (Upsert, Dedup and CDC Patterns)

## Dimension (schema field type)

A schema field type used for columns that contain descriptive, categorical or identifying attributes. Dimension fields are typically the columns you filter, group by or join on and they are prime candidates for inverted, sorted or text indexes.

**Primary chapter:** Chapter 4 (Schema Design and Data Modeling)

## Dimension table

A lookup table that stores descriptive or enrichment data, typically much smaller than the fact tables it accompanies. In Pinot, dimension tables are replicated in full to every server, enabling fast broadcast joins without network shuffles during query execution.

**Primary chapter:** Chapter 4 (Schema Design and Data Modeling), Chapter 7 (Batch Ingestion)

## External view

A ZooKeeper-maintained view that reflects the actual, confirmed state of resource assignments across cluster participants. The external view lags behind the ideal state because it is updated only after a participant acknowledges that it has completed a state transition.

**Primary chapter:** Chapter 2 (Architecture and Components)

## Fact table

An append-only table of events or measurements, where each row represents a discrete occurrence such as a click, transaction or sensor reading. Fact tables are the most common table type in Pinot and are optimized for high-volume ingestion with time based partitioning and retention.

**Primary chapter:** Chapter 3 (Storage Model: Segments, Tenants and Clusters), Chapter 4 (Schema Design and Data Modeling)

## Flush threshold

A configuration that controls when a consuming segment on a realtime server is "sealed" and converted into an immutable, query-optimized segment. The threshold can be defined by row count, elapsed time or segment size and tuning it directly affects segment granularity, memory usage and ingestion latency.

**Primary chapter:** Chapter 8 (Stream Ingestion)

## Forward index

The base columnar data structure that stores the actual values (or dictionary-encoded IDs) for every row in a column. Every column in a segment has a forward index by default and it is the structure that other index types (inverted, range, sorted) augment to accelerate specific access patterns.

**Primary chapter:** Chapter 6 (The Indexing Cookbook)

## Freshness

How recent the data visible to queries is relative to the source of truth or event publication time. Freshness is determined by the end-to-end pipeline latency, including stream lag, consuming lag and segment commit time and it is often governed by a freshness SLO.

**Primary chapter:** Chapter 18 (Observability, Operations and Minions)

## Freshness SLO

A service-level objective that defines the maximum acceptable delay between an event occurring in the source system and that event becoming queryable in Pinot. Freshness SLOs are typically measured in seconds for realtime tables and are monitored using consuming lag and segment age metrics.

**Primary chapter:** Chapter 18 (Observability, Operations and Minions)

## FST index

An index based on finite-state transducers that supports efficient regular expression and prefix lookups on dictionary-encoded string columns. FST indexes are particularly effective for autocomplete and wildcard search use cases where a full text index would be overkill.

**Primary chapter:** Chapter 6 (The Indexing Cookbook)

## Geospatial index

An index type that enables spatial queries such as point-in-polygon tests, distance calculations and bounding-box filters on columns containing geographic coordinates or geometry objects. Geospatial indexes use H3 or other spatial representations internally to accelerate these operations.

**Primary chapter:** Chapter 6 (The Indexing Cookbook)

## Helix

The Apache Helix framework that Pinot uses for cluster management, resource assignment and state machine transitions. Helix manages the mapping of segments to servers, drives rebalance operations and maintains the ideal state and external view in ZooKeeper.

**Primary chapter:** Chapter 2 (Architecture and Components)

## Hybrid table

A logical table that combines a realtime table and an offline table under the same table name and schema. Brokers transparently query both the realtime and offline portions and merge results, enabling architectures where recent data is served from the stream and older data from batch-built segments.

**Primary chapter:** Chapter 8 (Stream Ingestion)

## Ideal state

A ZooKeeper-stored document that declares the desired assignment of every segment to its target servers and the intended state (ONLINE, CONSUMING, etc.) of each assignment. Helix continuously works to converge the external view toward the ideal state by issuing transitions to participants.

**Primary chapter:** Chapter 2 (Architecture and Components)

## Instance assignment

The process by which Pinot determines which specific server instances will host a given table's segments. Instance assignment can be controlled through tag-based assignment, replica group configuration or custom instance-assignment strategies defined in the table configuration.

**Primary chapter:** Chapter 16 (Routing, Partitioning and Rebalancing)

## Inverted index

An index that maps each distinct value (or dictionary ID) in a column to the set of document IDs (rows) that contain that value. Inverted indexes dramatically accelerate equality and IN filters and are one of the most commonly enabled index types in Pinot.

**Primary chapter:** Chapter 6 (The Indexing Cookbook)

## JSON index

An index designed for columns that store JSON documents, enabling efficient evaluation of path-based predicates such as `JSON_EXTRACT_SCALAR` filters without scanning the full document. JSON indexes build an internal trie over JSON key paths and inverted indexes over leaf values.

**Primary chapter:** Chapter 6 (The Indexing Cookbook)

## JSON Schema

A vocabulary for annotating and validating the structure of JSON documents. In a Pinot platform context, JSON Schema can be used to validate table configurations, ingestion job specifications and API request payloads before they are applied to the cluster.

**Primary chapter:** Chapter 13 (APIs, Clients and Contracts)

## Metric (schema field type)

A schema field type used for numeric columns on which aggregation functions (SUM, AVG, MIN, MAX, etc.) are applied. Pinot can apply special optimizations to metric fields, including automatic aggregation in star-tree indexes and raw-value forward indexes tuned for numeric scan performance.

**Primary chapter:** Chapter 4 (Schema Design and Data Modeling)

## Minion

A Pinot component used for running asynchronous, distributed background tasks such as segment merge, purge, compaction and data conversion. Minions are coordinated by the controller's task scheduler and execute work on behalf of the cluster without affecting the serving path.

**Primary chapter:** Chapter 18 (Observability, Operations and Minions)

## MSE (multi stage engine)

The multi stage query engine (also called the v2 engine) that supports richer distributed SQL, including joins, window functions, set operations and correlated subqueries. The MSE decomposes a query into a DAG of pipeline stages and can shuffle intermediate data between servers, unlike the v1 engine's single stage scatter gather model.

**Primary chapter:** Chapter 11 (Multi-Stage Engine (v2 / MSE))

## Offline table

A Pinot table type that serves pre-built, immutable segments produced by batch ingestion jobs. Offline tables are ideal for data that does not require sub-minute freshness and can be periodically refreshed through scheduled ingestion pipelines.

**Primary chapter:** Chapter 7 (Batch Ingestion)

## OpenAPI

A specification for describing RESTful APIs with machine-readable definitions of endpoints, parameters and response schemas. Pinot's controller exposes an OpenAPI-documented REST API that can be used for table management, schema operations, segment administration and cluster health checks.

**Primary chapter:** Chapter 13 (APIs, Clients and Contracts)

## Partial upsert

An upsert mode in which only a subset of columns in the incoming record overwrites the existing record's values, while other columns retain their previously stored values. Partial upsert is useful for CDC patterns where different source systems or events update different attributes of the same entity.

**Primary chapter:** Chapter 9 (Upsert, Dedup and CDC Patterns)

## Peer download

A segment download mechanism in which a server fetches a segment directly from another server that already hosts it, rather than downloading from the deep store. Peer download reduces load on the deep store during rebalance operations and can significantly speed up segment transfers within a cluster.

**Primary chapter:** Chapter 16 (Routing, Partitioning and Rebalancing)

## Primary key

A field or set of fields that uniquely identifies a logical entity for state reconciliation in upsert and dedup tables. Pinot maintains an in-memory mapping from primary key to the segment and document ID of the latest record, which is consulted at query time to filter out stale versions.

**Primary chapter:** Chapter 9 (Upsert, Dedup and CDC Patterns)

## Query latency SLO

A service-level objective that defines the acceptable response time for queries, typically expressed as a percentile target (for example, p99 under 200 ms). Query latency SLOs drive decisions about indexing strategy, segment sizing, replica count and hardware provisioning.

**Primary chapter:** Chapter 18 (Observability, Operations and Minions)

## Query plane

The serving components that execute user facing queries, consisting primarily of brokers and servers. The query plane is designed to be stateless from a coordination perspective (all state is derived from Helix and ZooKeeper), which allows brokers and servers to be scaled independently.

**Primary chapter:** Chapter 2 (Architecture and Components)

## Query quota

A rate-limiting mechanism that caps the number of queries a table or tenant can execute per unit of time. Query quotas protect shared clusters from noisy-neighbor effects and ensure that critical workloads receive predictable resource allocation.

**Primary chapter:** Chapter 16 (Routing, Partitioning and Rebalancing)

## Query routing

The process by which a broker selects which server instances and which specific replicas to query for a given request. Routing strategies include balanced routing, replica-group routing and partition-aware routing, each offering different trade-offs between load distribution and cache efficiency.

**Primary chapter:** Chapter 16 (Routing, Partitioning and Rebalancing)

## Range index

An index that accelerates range predicates (greater than, less than, between) on numeric or time columns by organizing values into ordered structures. Range indexes complement sorted indexes when the column is not the sort key and are particularly useful for time-range filters on non-time columns.

**Primary chapter:** Chapter 6 (The Indexing Cookbook)

## Realtime table

A Pinot table type that ingests data directly from a streaming source such as Apache Kafka or Apache Pulsar. Realtime tables maintain consuming segments that are actively receiving new records and periodically seal them into immutable completed segments for optimized serving.

**Primary chapter:** Chapter 8 (Stream Ingestion)

## Rebalance

An operation that redistributes segment assignments across servers to reflect changes in cluster topology, replica count or tenant configuration. Rebalance can be triggered manually or automatically and proceeds by updating the ideal state, after which Helix drives servers to download or drop segments to converge.

**Primary chapter:** Chapter 16 (Routing, Partitioning and Rebalancing)

## Reload

An operation that instructs servers to re-process their locally hosted segments, typically to apply new index configurations, update star-tree indexes or refresh derived columns. Unlike rebalance, reload does not move segments between servers. It rebuilds segment metadata and indexes in place.

**Primary chapter:** Chapter 18 (Observability, Operations and Minions)

## Replica group

A placement and routing strategy in which each group of servers collectively holds a full copy of every segment for a table. Replica groups improve query isolation and cache efficiency because a query can be routed entirely to one group, avoiding cross-group data fetching.

**Primary chapter:** Chapter 16 (Routing, Partitioning and Rebalancing)

## Replace segment

An API operation that atomically swaps one or more existing segments with new replacement segments, ensuring that queries never see a partial update. Replace segment is commonly used in batch refresh workflows where an offline table's data is periodically rebuilt and swapped in without downtime.

**Primary chapter:** Chapter 7 (Batch Ingestion)

## Schema evolution

The process of modifying a table's schema over time by adding new columns, changing column types or altering index configurations. Pinot supports additive schema evolution (adding columns with default values) without requiring a full data reload, though some changes require segment regeneration.

**Primary chapter:** Chapter 4 (Schema Design and Data Modeling)

## Scatter-gather

The query execution pattern used by Pinot's v1 engine in which the broker scatters a query to all relevant servers in parallel and then gathers and merges the partial results. Scatter-gather is highly efficient for single-table aggregation queries but does not natively support joins or inter-server data shuffles.

**Primary chapter:** Chapter 10 (Querying Pinot: v1 SQL and Practical Patterns)

## Segment

Pinot's fundamental unit of physical storage, data distribution and query execution. Each segment is a self-contained, immutable columnar file that holds a horizontal partition of a table's data, complete with its own forward indexes, inverted indexes, dictionaries and metadata.

**Primary chapter:** Chapter 3 (Storage Model: Segments, Tenants and Clusters)

## Segment completion protocol

The protocol that governs how a consuming segment on a realtime server transitions from the CONSUMING state to the ONLINE (completed) state. The protocol ensures that exactly one copy of the completed segment is committed to the deep store and that all replicas converge to serving identical data.

**Primary chapter:** Chapter 8 (Stream Ingestion)

## Segment count

The total number of segments in a table, which directly affects query fan-out, metadata overhead and memory consumption. Monitoring segment count is essential for operational health because excessive segment proliferation can degrade query performance and increase ZooKeeper load.

**Primary chapter:** Chapter 18 (Observability, Operations and Minions)

## Segment pruning

An optimization in which the broker or server eliminates segments from consideration before scanning any data, based on segment level metadata such as partition information, time ranges or bloom filter checks. Effective segment pruning can reduce query latency by orders of magnitude on large tables.

**Primary chapter:** Chapter 6 (The Indexing Cookbook)

## Server

The Pinot component responsible for hosting segment data and executing the compute portion of queries. Servers load segments into memory-mapped storage, maintain local indexes and respond to query fragments dispatched by brokers. A server can act as a realtime server (consuming from streams), an offline server (serving batch segments) or both.

**Primary chapter:** Chapter 2 (Architecture and Components)

## Sorted index

An index that leverages the physical sort order of a column's values within a segment to enable binary-search-based lookups. A segment can have at most one sorted column and queries that filter on the sorted column benefit from extremely fast range and equality scans without additional index structures.

**Primary chapter:** Chapter 6 (The Indexing Cookbook)

## Star-tree index

A pre-aggregated, tree-based index structure that accelerates recurring aggregation query patterns by materializing partial aggregates at multiple levels of dimensional roll-up. Star-tree indexes trade additional storage space and build-time computation for dramatic query speedups on known aggregation workloads.

**Primary chapter:** Chapter 6 (The Indexing Cookbook)

## State table

A table intended to represent the latest known state of an entity rather than an append-only log of events. State tables are typically implemented using Pinot's upsert capability, where incoming records update the stored state for a given primary key.

**Primary chapter:** Chapter 9 (Upsert, Dedup and CDC Patterns)

## Stream consumer

The component within a Pinot realtime server that reads records from an external streaming platform (such as Kafka or Pulsar) and writes them into consuming segments. Each stream consumer is assigned one or more stream partitions and maintains its own consumption offset for exactly-once or at-least-once semantics.

**Primary chapter:** Chapter 8 (Stream Ingestion)

## Tag-based assignment

A mechanism for controlling which server instances are eligible to host a particular table's segments by matching server tags to table tenant configurations. Tag-based assignment enables multi-tenant isolation within a single cluster by logically partitioning servers into pools.

**Primary chapter:** Chapter 16 (Routing, Partitioning and Rebalancing)

## Tenant

A logical grouping of Pinot components (brokers and servers) identified by a tag, used to isolate workloads within a shared cluster. Tenants allow multiple teams or applications to share cluster infrastructure while maintaining resource boundaries and independent scaling.

**Primary chapter:** Chapter 3 (Storage Model: Segments, Tenants and Clusters)

## Text index

An index powered by Apache Lucene that enables full text search capabilities on string columns, supporting tokenized queries, phrase matching and boolean text predicates. Text indexes are appropriate for log search, product catalog search and other use cases where keyword-level matching is required.

**Primary chapter:** Chapter 6 (The Indexing Cookbook)

## Tier

A storage classification that allows segments to be placed on different classes of server hardware based on age, access frequency or other criteria. Tiered storage enables cost optimization by moving older or less frequently queried segments from high-performance servers to more economical storage tiers.

**Primary chapter:** Chapter 17 (Performance Engineering)

## Timestamp index

A specialized index on timestamp or dateTime columns that enables efficient time-range filtering at multiple granularities. Timestamp indexes can accelerate common patterns such as "last N hours" or "between date A and date B" without requiring the column to be the segment's sort key.

**Primary chapter:** Chapter 6 (The Indexing Cookbook)

## Upsert

A serving mode in which newer records replace or update older records sharing the same primary key, enabling Pinot to serve mutable, last-value semantics on top of its append-only storage engine. Upsert maintains an in-memory primary key map that resolves the latest version of each key at query time, which introduces memory overhead proportional to the number of unique keys.

**Primary chapter:** Chapter 9 (Upsert, Dedup and CDC Patterns)

## V1 engine

The original single stage query engine in Pinot that uses the scatter gather execution model. The v1 engine excels at single-table aggregation, filtering and group-by queries with very low latency, but it does not support joins, window functions or other operations that require inter-server data exchange.

**Primary chapter:** Chapter 10 (Querying Pinot: v1 SQL and Practical Patterns)

## Workload fit

The degree to which a system's strengths match the real requirements of the problem being solved. Evaluating workload fit involves comparing query patterns, latency requirements, freshness needs, data volumes and concurrency demands against the capabilities and trade-offs of the candidate system.

**Primary chapter:** Chapter 20 (Patterns, Anti-Patterns and Decision Framework)

## ZooKeeper

The Apache ZooKeeper ensemble that serves as Pinot's centralized coordination service for storing cluster metadata, segment assignments, table configurations and schema definitions. ZooKeeper is a critical dependency for Pinot's control plane and its availability directly affects the cluster's ability to perform administrative operations and state transitions.

**Primary chapter:** Chapter 2 (Architecture and Components)

*Previous chapter: [23. Solution Key](./23-solution-key.md)

*Next chapter: [99. References](./99-references.md)
