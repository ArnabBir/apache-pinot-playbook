# 99. References

This repository is designed to complement, not replace, the official Apache Pinot material. The links, videos, blog posts and cross-references collected here will help you go deeper on every topic covered in the Apache Pinot playbook. Start with the official resources for authoritative details and release-specific behavior, then branch out into the community content that best matches your learning style.


## Official Apache Pinot Resources

These are the canonical starting points for any Pinot practitioner.

**Pinot documentation home:** [https://docs.pinot.apache.org/](https://docs.pinot.apache.org/) is the primary reference for configuration options, SQL syntax, ingestion specs and operational guidance.

**Apache Pinot GitHub repository:** [https://github.com/apache/pinot](https://github.com/apache/pinot) contains the source code, issue tracker and contributor discussions. Reading the source is often the fastest way to resolve ambiguity in behavior.

**Apache Pinot releases:** [https://github.com/apache/pinot/releases](https://github.com/apache/pinot/releases) is where you will find changelogs, migration notes and new feature announcements with every release.

**Pinot Slack community:** The Apache Pinot Slack workspace is the most active place for real time Q&A. You can join through the link on the official docs site. The `#general`, `#troubleshooting` and `#dev` channels are particularly useful.

**Pinot mailing lists:** The traditional Apache communication channel. Subscribe to `dev@pinot.apache.org` for development discussions and `users@pinot.apache.org` for usage questions. Archives are available at [https://lists.apache.org/](https://lists.apache.org/).

**Apache Pinot Wiki:** [https://cwiki.apache.org/confluence/display/PINOT](https://cwiki.apache.org/confluence/display/PINOT) contains design documents, Pinot Enhancement Proposals (PEPs) and roadmap discussions.


## YouTube Videos and Talks

Video content is one of the best ways to absorb architectural intuition and see Pinot in action. The following talks cover a range of depth from introductory overviews to advanced internals.

1. **Apache Pinot: Realtime Distributed OLAP Datastore** - [https://www.youtube.com/watch?v=T70jnJzS2Ks](https://www.youtube.com/watch?v=T70jnJzS2Ks). A broad walkthrough of Pinot's architecture, use cases and positioning in the real time analytics landscape. Excellent starting point for newcomers.

2. **StarTree Technical Content** - [https://www.youtube.com/watch?v=JV0WxBwJqKE](https://www.youtube.com/watch?v=JV0WxBwJqKE). Covers practical considerations around deploying and tuning Pinot, with emphasis on production patterns from the StarTree team.

3. **Real-Time Analytics at LinkedIn Using Apache Pinot.** LinkedIn engineers walk through the evolution of Pinot from its origins as an internal tool to a planet-scale analytics engine serving thousands of queries per second.

4. **Building Real-Time Analytics at Uber with Apache Pinot.** Uber's data platform team explains how they use Pinot for rider and driver analytics, surge pricing dashboards and operational metrics.

5. **Apache Pinot Deep Dive: Multi-Stage Query Engine.** A technical deep dive into the V2 multi stage query engine, covering distributed joins, resource management and query planning.

6. **Indexing Strategies in Apache Pinot.** Detailed exploration of inverted indexes, range indexes, sorted indexes, star-tree indexes and how to choose the right index for your workload.

7. **Apache Pinot: Upsert and Dedup at Scale.** Walks through the architecture of Pinot's upsert and deduplication features, including comparison key management and metadata overhead.

8. **Stream Ingestion with Apache Pinot and Kafka.** Demonstrates how Pinot consumes from Kafka topics in real time, covering consumer configuration, offset management and exactly-once semantics.

For the latest talks, search "Apache Pinot" on YouTube and filter by upload date. The StarTree YouTube channel also publishes regular content.


## Blog Posts and Articles

Written deep dives are invaluable for understanding design decisions and real-world production lessons.

### StarTree Blog

The StarTree blog at [https://startree.ai/blog](https://startree.ai/blog) is the richest single source of Pinot-focused content. Notable articles include the following.

**Understanding Star-Tree Index in Apache Pinot** explains the pre-aggregation data structure that gives Pinot its sub second latency on high cardinality dimensions. **Upsert in Apache Pinot: How It Works** covers the internals of comparison-based upsert, partial upsert and the trade-offs with memory and segment management. The **Indexing Deep Dive Series** is a multi-part series covering inverted indexes, range indexes, bloom filters, text indexes with Lucene, JSON indexes and timestamp indexes. **Performance Tuning Apache Pinot** provides practical guidance on segment sizing, query optimization and resource allocation. **Real-Time Analytics Architecture Patterns** explores Lambda vs. Kappa architectures and where Pinot fits in each.

### LinkedIn Engineering Blog

**Pinot: Realtime OLAP for 530 Million+ Users** is the foundational blog post describing why LinkedIn built Pinot and how it serves Who Viewed My Profile, ad analytics and content analytics at massive scale. **Building LinkedIn's Real-Time Activity Tracking Platform** describes the activity tracking pipeline that feeds Pinot and the challenges of schema evolution at scale.

### Uber Engineering Blog

**Real-Time Analytics at Uber** covers the data platform architecture at Uber with emphasis on real time dashboards, marketplace analytics and the role Pinot plays alongside Kafka and HDFS. **Scaling Apache Pinot at Uber** discusses cluster management, multi-tenancy and operational lessons learned from running Pinot across multiple data centers.

### Other Engineering Blogs

Stripe Engineering has published content on real time fraud detection analytics, touching on OLAP systems and columnar stores relevant to Pinot workloads. Walmart Engineering has shared insights on real time inventory analytics that mirror the kinds of problems Pinot is designed to solve. WePay (Chase) has written about using Pinot for real time payment analytics and reconciliation dashboards.


## Books and Long-Form Reading

While there is no single book dedicated exclusively to Apache Pinot at the time of writing, the following titles provide essential background on the concepts, architectures and systems that underpin Pinot.

**"Designing Data-Intensive Applications" by Martin Kleppmann** is the gold standard for understanding distributed systems, storage engines, stream processing and batch processing. Chapters on OLAP, column-oriented storage and stream processing are directly relevant.

**"Streaming Systems" by Tyler Akidau, Slava Chernyak and Reuven Lax** covers watermarks, windowing, triggers and exactly-once processing. Essential reading for understanding how Pinot's real time ingestion layer interacts with streaming sources.

**"The Data Warehouse Toolkit" by Ralph Kimball and Margy Ross** is the foundational text on dimensional modeling, star schemas and OLAP design. The mental models here translate directly to Pinot schema design and star-tree index configuration.

**"Database Internals" by Alex Petrov** provides deep coverage of storage engines, B-trees, LSM trees, distributed consensus and replication. Helps you understand the storage and coordination layers that Pinot builds on.

**"Fundamentals of Data Engineering" by Joe Reis and Matt Housley** is a modern survey of data engineering concepts including batch vs. stream processing, data modeling and analytics serving layers.


## Community and Ecosystem

Apache Pinot does not exist in isolation. Understanding the surrounding ecosystem makes you a more effective Pinot operator and architect.

### Related Apache Projects

**Apache Kafka** ([https://kafka.apache.org/](https://kafka.apache.org/)) is the most common streaming source for Pinot's real time tables. Understanding Kafka's partition model, consumer groups and offset management is critical. **Apache Helix** ([https://helix.apache.org/](https://helix.apache.org/)) is the cluster management and resource allocation framework that Pinot uses. Helix handles segment assignment, replica placement and state transitions. **Apache ZooKeeper** ([https://zookeeper.apache.org/](https://zookeeper.apache.org/)) is the coordination service underneath Helix. ZooKeeper stores cluster metadata, controller leader election state and segment assignment mappings.

### Comparison and Alternative Systems

Understanding how Pinot compares to similar systems helps you make informed technology choices. **ClickHouse** ([https://clickhouse.com/](https://clickhouse.com/)) is a high-performance columnar OLAP database strong in batch analytics workloads with a rich SQL dialect. It differs from Pinot in its approach to real time ingestion and multi-tenancy. **Apache Druid** ([https://druid.apache.org/](https://druid.apache.org/)) is the system most architecturally similar to Pinot. Both support real time ingestion from Kafka, segment-based storage and sub second query latency. Druid uses a different query language (native JSON) alongside SQL. **Apache Doris** ([https://doris.apache.org/](https://doris.apache.org/)) is an MPP analytical database with MySQL protocol compatibility, growing rapidly in the Chinese engineering community with increasing global adoption.

### Tools That Integrate with Pinot

**Apache Superset** ([https://superset.apache.org/](https://superset.apache.org/)) is the open-source business intelligence platform with native Pinot connector support and is the most popular visualization layer for Pinot. **Grafana** ([https://grafana.com/](https://grafana.com/)) is a monitoring and observability platform that can connect to Pinot through its generic SQL data source or via a community plugin. **Presto / Trino** ([https://trino.io/](https://trino.io/)) are distributed SQL query engines that can query Pinot as a catalog, enabling federated queries across Pinot and other data sources like Hive or Iceberg.


## Per-Chapter Cross-References

Each chapter in the Apache Pinot playbook maps to specific areas of the official documentation and external resources. Use this index to quickly find deeper material on any topic.

| Chapter | Title | Key Official Docs and Resources |
|---------|-------|---------------------------------|
| 00 | Preface | Project README, Apache Pinot landing page |
| 01 | Apache Pinot at a Glance | Docs: "Getting Started", Pinot overview talks on YouTube |
| 02 | Architecture and Components | Docs: "Architecture Overview", Helix documentation |
| 03 | Storage Model, Segments, Tenants, Clusters | Docs: "Segments", "Tenants", Helix resource model |
| 04 | Schema Design and Data Modeling | Docs: "Schema Configuration", Kimball dimensional modeling |
| 05 | Table Config Deep Dive | Docs: "Table Configuration Reference" |
| 06 | Indexing Cookbook | Docs: "Indexing", StarTree blog indexing series |
| 07 | Batch Ingestion | Docs: "Batch Ingestion", ingestion job spec reference |
| 08 | Stream Ingestion | Docs: "Stream Ingestion", Kafka connector configuration |
| 09 | Upsert, Dedup, CDC | Docs: "Upsert", StarTree upsert blog posts |
| 10 | Querying (V1) and SQL | Docs: "Query Syntax", "Query Options", SQL reference |
| 11 | Multi-Stage Engine (V2) | Docs: "Multi-Stage Query Engine", V2 design proposals |
| 12 | Time Series Engine | Docs: "Time Series Functions", time-bucketed queries |
| 13 | APIs, Clients and Contracts | Docs: "REST API Reference", Pinot client libraries |
| 14 | Deployment: Docker, Kubernetes, Cloud | Docs: "Deployment", Helm charts on GitHub |
| 15 | Security and Governance | Docs: "Security", TLS and auth configuration |
| 16 | Routing, Partitioning, Rebalancing | Docs: "Routing", "Partitioning", segment rebalance API |
| 17 | Performance Engineering | Docs: "Performance Tuning", StarTree performance blog |
| 18 | Observability, Operations and Minions | Docs: "Monitoring", "Minion Tasks", JMX metrics |
| 19 | Failure Modes and Troubleshooting | Docs: "Troubleshooting", Pinot Slack `#troubleshooting` |
| 20 | Patterns, Antipatterns, Decision Framework | StarTree architecture blog posts, community case studies |
| 21 | Capstone: Building a Rides Platform | All of the above, plus the `labs/` directory in this repo |


## Repository Cross-Reference

This section maps the directory structure of the Apache Pinot playbook repository to the concepts covered in each chapter. Use it as a quick navigation aid.

[`docker-compose.yml`](docker-compose.yml) provides the local development stack. It brings up ZooKeeper, a Pinot controller, broker, server and optionally Kafka. Referenced heavily in Chapters 02, 08, 14 and 21.

The `contracts/` directory contains data contracts in OpenAPI, AsyncAPI and JSON Schema formats. These contracts define the interfaces between producers and consumers of Pinot data. Referenced in Chapter 13.

The `schemas/` directory holds Pinot schema configuration files. Each file defines dimension fields, metric fields and date-time fields for a specific table. Referenced in Chapters 04 and 05.

The `tables/` directory contains Pinot table configuration files. These define table type (OFFLINE, REALTIME, HYBRID), indexing configuration, routing strategy and ingestion settings. Referenced in Chapters 05, 06, 07, 08 and 09.

The `sql/` directory houses SQL query packs organized by topic. These are ready-to-run queries that demonstrate features covered in Chapters 10, 11 and 12.

The `src/pinot_playbook_demo/` directory is the Python package that accompanies the book. It includes utility code for data generation, Pinot client wrappers and helper scripts used throughout the labs.

The `labs/` directory contains hands on lab exercises with step by step instructions. Each lab is self-contained and maps to one or more chapters. The capstone lab in Chapter 21 ties everything together.

The `jobs/` directory stores batch ingestion job specifications. These are the YAML and JSON files that define segment generation and push tasks for offline tables. Referenced in Chapter 07.


## How to Stay Current

Apache Pinot is an actively developed project with a fast-moving release cadence. The following practices are the most effective ways to keep up.

Watch the GitHub repository by starring and watching [https://github.com/apache/pinot](https://github.com/apache/pinot) to receive notifications about new releases, major pull requests and design discussions.

Join the Slack community for real-time conversations with committers, contributors and fellow practitioners. This is the fastest path to answers when you hit an unexpected behavior.

Subscribe to the dev mailing list, where major design decisions and Pinot Enhancement Proposals are discussed before implementation begins.

Follow the StarTree blog and YouTube channel. StarTree, the company founded by Pinot's original creators, publishes the most consistent stream of Pinot-focused technical content.

Attend Apache Pinot meetups and conferences. Community meetups happen regularly in major tech hubs and online. Check the Pinot website and Slack for announcements.


*This reference chapter will be updated as new resources become available. If you find a resource that belongs here, open an issue or pull request on the repository.*

*Previous chapter: [24. Glossary](./24-glossary.md)
