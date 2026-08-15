# Labs

Twenty-one hands on labs organized across five progressive phases. Each lab builds directly on the previous phase. Every lab contains a conceptual diagram that makes the mental model visible before any commands run, a challenge section that asks you to design or predict before the answer is revealed, a measurement tracking table so improvements are quantified rather than assumed and four reflection prompts that demand reasoning rather than recall.

See the [Suggested Learning Paths](#suggested-learning-paths) table to navigate by goal rather than sequence.


## Phase 1: Foundation

These four labs establish the cluster, data model and ingestion pipeline. Every subsequent lab assumes this phase is complete.

| Lab | Title | Core Objective | Key Technical Focus |
|:---:|-------|----------------|---------------------|
| 01 | [Local Cluster](lab-01-local-cluster.md) | Bootstrap the full Pinot topology and verify every component | Controller, Broker, Server, ZooKeeper, Kafka, health endpoints, incident triage matrix |
| 02 | [Schemas and Tables](lab-02-schemas-and-tables.md) | Define the data contract and create all three table types | Dimension, Metric, DateTime field classification; REALTIME and OFFLINE tables |
| 03 | [Stream Ingestion](lab-03-stream-ingestion.md) | Connect Kafka to Pinot and query consuming segments in real time | Kafka consumer, consuming segment lifecycle, BrokerResponse statistics |
| 04 | [Index Tuning](lab-04-index-tuning.md) | Apply indexes and measure their effect using `SET skipIndexes` A/B testing | Inverted, range, bloom filter, star-tree indexes; segment pruning; direct A/B comparison |


## Phase 2: Advanced Data Modeling

These labs extend the data model to handle mutable state, hybrid storage, schema changes and semi-structured data.

| Lab | Title | Core Objective | Key Technical Focus |
|:---:|-------|----------------|---------------------|
| 05 | [Upsert and CDC](lab-05-upsert-cdc.md) | Maintain latest-state records from a changelog stream | Primary keys, FULL upsert mode, comparison columns, strictReplicaGroup |
| 09 | [Hybrid Tables](lab-09-hybrid-tables.md) | Combine realtime and offline segments under one logical table | Time boundary, segment handoff, RealtimeToOfflineSegmentsTask |
| 10 | [Schema Evolution](lab-10-schema-evolution.md) | Add and modify columns without downtime | Safe vs breaking changes, segment reload, schema review checklist |
| 18 | [Multi-Value Column Analytics](lab-18-multi-value-columns.md) | Query array-valued fields with MV aggregate functions | `countMV`, `valueIn`, `arrayLength`, `percentileMV`, `distinctCountMV` |
| 19 | [JSON and Text Index Workshop](lab-19-json-text-index.md) | Query semi-structured columns with `json_match` and `text_match` | JSON index, `jsonExtractScalar`, `text_match` phrase/boolean/wildcard, FST index |


## Phase 3: Query Engineering

These labs build deep fluency in query construction, optimization, time-series patterns and distributed execution.

| Lab | Title | Core Objective | Key Technical Focus |
|:---:|-------|----------------|---------------------|
| 06 | [Multi-Stage Queries](lab-06-multi-stage-queries.md) | Execute distributed joins and window functions | MSE v2, hash join, RANK(), denormalization trade-off |
| 07 | [Time Series Analytics](lab-07-time-series.md) | Build and compare three time-bucketing approaches | Pre-computed columns, SQL FLOOR, native time-series engine |
| 12 | [SQL Optimization Workshop](lab-12-sql-optimization.md) | Diagnose and fix eight progressively complex query problems | EXPLAIN PLAN, BrokerResponse statistics, index selection, join order |
| 16 | [Star-Tree Index Design Workshop](lab-16-star-tree-workshop.md) | Design an optimal star-tree configuration from first principles | Dimension split order, function-column pairs, EXPLAIN PLAN validation |


## Phase 4: Operations and Reliability

These labs cover production operations: compaction, chaos, tenancy, SLO definition, monitoring integration, ingestion methods and storage tier management.

| Lab | Title | Core Objective | Key Technical Focus |
|:---:|-------|----------------|---------------------|
| 11 | [Minion Tasks and Compaction](lab-11-minion-tasks.md) | Compact fragmented segments and automate data lifecycle | MergeRollupTask, PurgeTask, before/after segment count measurement |
| 13 | [Chaos Engineering](lab-13-chaos-engineering.md) | Kill each component, measure blast radius, execute structured recovery | Server, Broker, Controller, ZooKeeper failure experiments with hypothesis tables |
| 15 | [Multi-Tenancy](lab-15-multi-tenancy.md) | Isolate workloads across teams on a shared cluster | Server and broker tenant tags, placement verification, isolation measurement |
| 20 | [Ingestion Methods and Transform Functions](lab-20-ingestion-methods.md) | Perform the same operation via API, CLI, UI and SQL; master transforms | `INSERT INTO FROM FILE`, `pinot-admin.sh`, Swagger; `jsonPathString`, Groovy, timestamp index |
| 21 | [Storage Tiers and Cold Data Management](lab-21-storage-tiers.md) | Configure hot and cold tiers with per-tier index overrides | `tierConfigs`, `tierOverwrites`, Minion-based segment relocation, cost analysis |
| 08 | [SLO and Incident Drill](lab-08-slo-incident.md) | Define SLOs and conduct structured incident investigations | SLI/SLO/SLA hierarchy, incident triage matrix, runbook production |
| 17 | [Grafana Integration](lab-17-grafana-integration.md) | Build a six-panel operational dashboard backed by Pinot SQL | StarTree plugin, `$__from`/`$__to` variables, freshness gauge, city filter variable |


## Phase 5: Domain Use Cases

These labs apply Pinot skills to new problem domains, demonstrating that the same architectural patterns generalize across industries.

| Lab | Title | Domain | Core Objective |
|:---:|-------|--------|----------------|
| 14 | [Fraud Detection Analytics](lab-14-fraud-detection.md) | Financial Services | Detect velocity, anomaly and concentration patterns in real time |


## Suggested Learning Paths

| Goal | Recommended Labs |
|------|-----------------|
| Fastest working demo | 01 → 02 → 03 |
| Pinot evaluation for a new project | 01 → 02 → 03 → 05 → 06 → 12, then read Chapter 20 (Patterns) |
| Production readiness review | 09 → 10 → 11 → 13 → 15 → 21 → 08 |
| Query performance engineering | 04 → 12 → 16 → 06 → 07 |
| Semi-structured and search workloads | 19 → 18 → 12 |
| Data ingestion mastery | 03 → 20 → 09 → 11 |
| Domain application: financial analytics | 01 → 02 → 03 → 05 → 14 |
| Deep mastery - full course | All 21 labs in phase order |


## What Makes These Labs Hands On

| Element | What It Forces |
|---------|---------------|
| `SET skipIndexes` A/B testing (Lab 04, 19) | Index value becomes a measured number, not a claimed benefit |
| Challenge sections (Labs 10, 14, 16) | Schema and index design must be committed to before the answer is revealed |
| Hypothesis tables (Lab 13) | Blast radius must be predicted before each chaos experiment runs |
| Measurement tracking tables (all labs) | Every optimization produces a before/after row in a table |
| Multiple interaction methods (Lab 20) | The same operation performed via API, CLI, UI and SQL |
| Reflection prompts (all labs, 4 per lab) | Each question requires reasoning about trade-offs, not just recall |
