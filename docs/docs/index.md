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
