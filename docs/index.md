---
hide:
  - navigation
  - toc
---

<section class="hero" markdown>

# Build real-time analytics that holds up in production.

Apache Pinot is built for sub-second analytics on data that is still arriving. This playbook turns that promise into a working system: the mental models, configurations, measurements, and failure modes that matter when the workload is real.

<div class="hero-actions" markdown>

[Start with the architecture](01-apache-pinot-at-a-glance.md){ .md-button .md-button--primary }
[Choose a learning path](overview.md){ .md-button }

</div>
</section>

<div class="signal-strip" markdown>

**25 chapters**

**21 hands-on labs**

**One production-shaped demo**

</div>

## The operating model

<div class="card-grid" markdown>

<article markdown>

### Learn the system

Start with the control plane, query plane, storage model, and the workload characteristics that make Pinot a fit.

[Read the foundations](02-architecture-and-components.md)

</article>

<article markdown>

### Make design choices

Model data deliberately, select indexes from query shape, and design ingestion for both freshness and recovery.

[Design and ingest](04-schema-design-and-data-modeling.md)

</article>

<article markdown>

### Prove it under load

Work through query planning, observability, tuning, and failure modes with runnable artifacts and measurable experiments.

[Operate and scale](17-performance-engineering.md)

</article>

</div>

## Pick a path

| If you need to... | Read this | Then do this |
| --- | --- | --- |
| Evaluate Pinot quickly | [At a Glance](01-apache-pinot-at-a-glance.md), [Architecture](02-architecture-and-components.md), [Patterns](20-patterns-antipatterns-and-decision-framework.md) | [Lab 01: Local Cluster](labs/lab-01-local-cluster.md) |
| Build a streaming application | [Schema Design](04-schema-design-and-data-modeling.md), [Stream Ingestion](08-stream-ingestion.md), [Upsert & CDC](09-upsert-dedup-cdc.md) | [Lab 03: Stream Ingestion](labs/lab-03-stream-ingestion.md) |
| Tune a production workload | [Indexing](06-indexing-cookbook.md), [Routing](16-routing-partitioning-rebalancing.md), [Performance](17-performance-engineering.md) | [Lab 04: Index Tuning](labs/lab-04-index-tuning.md) |
| Run the platform reliably | [Deployment](14-deployment-docker-kubernetes-cloud.md), [Observability](18-observability-operations-and-minions.md), [Troubleshooting](19-failure-modes-and-troubleshooting.md) | [Lab 13: Chaos Engineering](labs/lab-13-chaos-engineering.md) |

## Built to be used

The companion repository includes Docker Compose, Pinot schemas and table configurations, Kafka streams, SQL packs, API contracts, and simulations. The book explains the decisions. The code lets you verify them.

[Open the repository](https://github.com/ArnabBir/apache-pinot-playbook){ .md-button }

## Complete Playbook

Every chapter is designed to stand alone, but the sequence below builds a complete production mental model.

### Start Here

<div class="index-grid" markdown>

- [**00** Preface](00-preface.md)  
  How to use the playbook and choose a learning path.
- [**01** Pinot at a Glance](01-apache-pinot-at-a-glance.md)  
  Fit, use cases, design principles, and trade-offs.
- [**02** Architecture](02-architecture-and-components.md)  
  Control plane, query plane, and query lifecycle.
- [**03** Storage Model](03-storage-model-segments-tenants-clusters.md)  
  Segments, tenants, deep store, and cluster topology.

</div>

### Design & Ingest

<div class="index-grid" markdown>

- [**04** Schema Design](04-schema-design-and-data-modeling.md)  
  Data modeling, cardinality, nulls, and schema evolution.
- [**05** Table Configuration](05-table-config-deep-dive.md)  
  Table types, retention, routing, and ingestion settings.
- [**06** Indexing Cookbook](06-indexing-cookbook.md)  
  Inverted, range, bloom, star-tree, and geospatial indexes.
- [**07** Batch Ingestion](07-batch-ingestion.md)  
  Segment generation, push jobs, and offline workflows.
- [**08** Stream Ingestion](08-stream-ingestion.md)  
  Kafka consumption and consuming segment lifecycle.
- [**09** Upsert, Dedup & CDC](09-upsert-dedup-cdc.md)  
  Primary keys, changelogs, and latest-state patterns.

</div>

### Query & Integrate

<div class="index-grid" markdown>

- [**10** Pinot SQL](10-querying-v1-and-sql.md)  
  Single-stage SQL and practical query patterns.
- [**11** Multi-Stage Engine](11-multi-stage-engine-v2.md)  
  Distributed joins, windows, and query planning.
- [**12** Time Series Engine](12-time-series-engine.md)  
  Time-bucketed analytics and specialized queries.
- [**13** APIs & Contracts](13-apis-clients-and-contracts.md)  
  Clients, REST APIs, OpenAPI, and AsyncAPI.
- [**14** Deployment](14-deployment-docker-kubernetes-cloud.md)  
  Docker, Kubernetes, cloud, and topology decisions.
- [**15** Security & Governance](15-security-and-governance.md)  
  Authentication, authorization, TLS, and access control.

</div>

### Operate & Scale

<div class="index-grid" markdown>

- [**16** Routing & Rebalancing](16-routing-partitioning-rebalancing.md)  
  Partition routing, replicas, and segment movement.
- [**17** Performance Engineering](17-performance-engineering.md)  
  Profiling, index tuning, memory, and capacity planning.
- [**18** Observability & Minions](18-observability-operations-and-minions.md)  
  Metrics, alerting, and background data operations.
- [**19** Failure Modes](19-failure-modes-and-troubleshooting.md)  
  Diagnosis, runbooks, recovery, and troubleshooting.
- [**20** Patterns & Decisions](20-patterns-antipatterns-and-decision-framework.md)  
  Decision frameworks and anti-patterns.
- [**21** Rides Platform Capstone](21-capstone-building-a-rides-platform.md)  
  An end-to-end real-time analytics platform.

</div>

### Practice & Reference

<div class="index-grid" markdown>

- [**22** Exercises](22-exercises.md)  
  Scenario-based design and operations practice.
- [**23** Solution Key](23-solution-key.md)  
  Worked answers with reasoning and trade-offs.
- [**24** Glossary](24-glossary.md)  
  Canonical Pinot terminology.
- [**99** References](99-references.md)  
  Papers, talks, and primary documentation.

</div>

## Hands-On Labs

Labs turn the ideas into observable behavior. Complete each phase in sequence, or use the links below to focus on a specific skill.

### Phase 1: Foundation

<div class="index-grid lab-index" markdown>

- [**01** Local Cluster](labs/lab-01-local-cluster.md)
- [**02** Schemas & Tables](labs/lab-02-schemas-and-tables.md)
- [**03** Stream Ingestion](labs/lab-03-stream-ingestion.md)
- [**04** Index Tuning](labs/lab-04-index-tuning.md)

</div>

### Phase 2: Advanced Data Modeling

<div class="index-grid lab-index" markdown>

- [**05** Upsert & CDC](labs/lab-05-upsert-cdc.md)
- [**09** Hybrid Tables](labs/lab-09-hybrid-tables.md)
- [**10** Schema Evolution](labs/lab-10-schema-evolution.md)
- [**18** Multi-Value Columns](labs/lab-18-multi-value-columns.md)
- [**19** JSON & Text Index](labs/lab-19-json-text-index.md)

</div>

### Phase 3: Query Engineering

<div class="index-grid lab-index" markdown>

- [**06** Multi-Stage Queries](labs/lab-06-multi-stage-queries.md)
- [**07** Time Series Analytics](labs/lab-07-time-series.md)
- [**12** SQL Optimization](labs/lab-12-sql-optimization.md)
- [**16** Star-Tree Design](labs/lab-16-star-tree-workshop.md)

</div>

### Phase 4: Operations & Reliability

<div class="index-grid lab-index" markdown>

- [**08** SLO & Incident Drill](labs/lab-08-slo-incident.md)
- [**11** Minion Tasks](labs/lab-11-minion-tasks.md)
- [**13** Chaos Engineering](labs/lab-13-chaos-engineering.md)
- [**15** Multi-Tenancy](labs/lab-15-multi-tenancy.md)
- [**17** Grafana Integration](labs/lab-17-grafana-integration.md)
- [**20** Ingestion Methods](labs/lab-20-ingestion-methods.md)
- [**21** Storage Tiers](labs/lab-21-storage-tiers.md)

</div>

### Phase 5: Domain Use Case

<div class="index-grid lab-index" markdown>

- [**14** Fraud Detection Analytics](labs/lab-14-fraud-detection.md)

</div>
