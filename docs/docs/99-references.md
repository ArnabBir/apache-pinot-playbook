# 99. References

This repository is designed to complement, not replace, the official Apache Pinot material. The links, videos, blog posts and cross-references collected here will help you go deeper on every topic covered in the Apache Pinot playbook. Start with the official resources for authoritative details and release-specific behavior, then branch out into the community content that best matches your learning style.


## Official Apache Pinot Resources

These are the canonical starting points for any Pinot practitioner.

| Resource | Description |
| :--- | :--- |
| [Pinot Documentation](https://docs.pinot.apache.org/) | Primary reference for configuration options, SQL syntax, ingestion specs and operational guidance. |
| [Apache Pinot GitHub](https://github.com/apache/pinot) | Source code, issue tracker and contributor discussions. Reading the source is often the fastest way to resolve behavioral ambiguity. |
| [Release Notes](https://github.com/apache/pinot/releases) | Changelogs, migration notes and new feature announcements for every release. |
| [Pinot Slack Community](https://docs.pinot.apache.org/) | The most active place for real-time Q&A. The `#general`, `#troubleshooting` and `#dev` channels are particularly useful. |
| [Mailing Lists](https://lists.apache.org/) | Subscribe to `dev@pinot.apache.org` for development discussions and `users@pinot.apache.org` for usage questions. |
| [Apache Pinot Wiki](https://cwiki.apache.org/confluence/display/PINOT) | Design documents, Pinot Enhancement Proposals (PEPs) and roadmap discussions. |


## YouTube Videos and Talks

Video content is one of the best ways to absorb architectural intuition and see Pinot in action.

| Talk | Description |
| :--- | :--- |
| [Apache Pinot: Realtime Distributed OLAP Datastore](https://www.youtube.com/watch?v=T70jnJzS2Ks) | Broad walkthrough of Pinot's architecture, use cases and positioning. Excellent starting point for newcomers. |
| [StarTree Technical Content](https://www.youtube.com/watch?v=JV0WxBwJqKE) | Practical considerations around deploying and tuning Pinot, with emphasis on production patterns from the StarTree team. |
| Real-Time Analytics at LinkedIn Using Apache Pinot | LinkedIn engineers walk through the evolution of Pinot from its origins to serving thousands of queries per second at planet scale. |
| Building Real-Time Analytics at Uber with Apache Pinot | Uber's data platform team explains how Pinot powers rider and driver analytics, surge pricing dashboards and operational metrics. |
| Apache Pinot Deep Dive: Multi-Stage Query Engine | Technical deep dive into the V2 multi-stage query engine covering distributed joins, resource management and query planning. |
| Indexing Strategies in Apache Pinot | Detailed exploration of inverted indexes, range indexes, sorted indexes and star-tree indexes with workload-based selection guidance. |
| Apache Pinot: Upsert and Dedup at Scale | Architecture of Pinot's upsert and deduplication features including comparison key management and metadata overhead. |
| Stream Ingestion with Apache Pinot and Kafka | Demonstrates realtime consumption from Kafka topics covering consumer configuration, offset management and exactly-once semantics. |

For the latest talks, search "Apache Pinot" on YouTube and filter by upload date. The StarTree YouTube channel publishes regular content.


## Blog Posts and Articles

Written deep dives are invaluable for understanding design decisions and real-world production lessons.

### StarTree Blog

The StarTree blog at [https://startree.ai/blog](https://startree.ai/blog) is the richest single source of Pinot-focused content. Notable articles include:

- **Understanding Star-Tree Index in Apache Pinot**. The pre-aggregation data structure that gives Pinot sub-second latency on high-cardinality dimensions.
- **Upsert in Apache Pinot: How It Works**. Internals of comparison-based upsert, partial upsert and the trade-offs with memory and segment management.
- **Indexing Deep Dive Series**. Multi-part series covering inverted indexes, range indexes, bloom filters, text indexes, JSON indexes and timestamp indexes.
- **Performance Tuning Apache Pinot**. Practical guidance on segment sizing, query optimization and resource allocation.
- **Real-Time Analytics Architecture Patterns** Lambda vs. Kappa architectures and where Pinot fits in each.

### LinkedIn Engineering Blog

- **Pinot: Realtime OLAP for 530 Million+ Users**. Foundational blog post describing why LinkedIn built Pinot and how it serves Who Viewed My Profile, ad analytics and content analytics at massive scale.
- **Building LinkedIn's Real-Time Activity Tracking Platform**. The activity tracking pipeline that feeds Pinot and the challenges of schema evolution at scale.

### Uber Engineering Blog

- **Real-Time Analytics at Uber** Uber's data platform architecture with emphasis on real-time dashboards, marketplace analytics and the role Pinot plays alongside Kafka and HDFS.
- **Scaling Apache Pinot at Uber**. Cluster management, multi-tenancy and operational lessons from running Pinot across multiple data centers.

### Other Engineering Blogs

- **Stripe Engineering**. Real-time fraud detection analytics touching on OLAP systems and columnar stores relevant to Pinot workloads.
- **Walmart Engineering**. Real-time inventory analytics that mirror the kinds of problems Pinot is designed to solve.
- **WePay (Chase)**. Real-time payment analytics and reconciliation dashboards built on Pinot.


## Books and Long-Form Reading

While there is no single book dedicated exclusively to Apache Pinot, the following titles provide essential background on the concepts and systems that underpin it.

| Book | Relevance to Pinot |
| :--- | :--- |
| **Designing Data-Intensive Applications** by Martin Kleppmann | The gold standard for understanding distributed systems, storage engines and stream processing. Chapters on OLAP and column-oriented storage are directly relevant. |
| **Streaming Systems** by Tyler Akidau, Slava Chernyak and Reuven Lax | Covers watermarks, windowing, triggers and exactly-once processing. Essential for understanding Pinot's real-time ingestion layer. |
| **The Data Warehouse Toolkit** by Ralph Kimball and Margy Ross | Foundational text on dimensional modeling and star schemas. Mental models here translate directly to Pinot schema design and star-tree index configuration. |
| **Database Internals** by Alex Petrov | Deep coverage of storage engines, B-trees, LSM trees, distributed consensus and replication. Explains the storage and coordination layers that Pinot builds on. |
| **Fundamentals of Data Engineering** by Joe Reis and Matt Housley | Modern survey of data engineering including batch vs. stream processing, data modeling and analytics serving layers. |


## Community and Ecosystem

Apache Pinot does not exist in isolation. Understanding the surrounding ecosystem makes you a more effective Pinot operator and architect.

### Related Apache Projects

| Project | Role in a Pinot Architecture |
| :--- | :--- |
| [Apache Kafka](https://kafka.apache.org/) | The most common streaming source for Pinot's real-time tables. Understanding Kafka's partition model, consumer groups and offset management is critical. |
| [Apache Helix](https://helix.apache.org/) | The cluster management framework Pinot uses for segment assignment, replica placement and state transitions. |
| [Apache ZooKeeper](https://zookeeper.apache.org/) | The coordination service underneath Helix. Stores cluster metadata, controller leader election state and segment assignment mappings. |

### Comparison and Alternative Systems

| System | Relationship to Pinot |
| :--- | :--- |
| [ClickHouse](https://clickhouse.com/) | High-performance columnar OLAP database strong in batch analytics with a rich SQL dialect. Differs from Pinot in its approach to real-time ingestion and multi-tenancy. |
| [Apache Druid](https://druid.apache.org/) | The system most architecturally similar to Pinot. Both support real-time ingestion from Kafka, segment-based storage and sub-second query latency. Druid uses a native JSON query language alongside SQL. |
| [Apache Doris](https://doris.apache.org/) | MPP analytical database with MySQL protocol compatibility, growing rapidly with increasing global adoption. |

### Tools That Integrate with Pinot

| Tool | Integration Point |
| :--- | :--- |
| [Apache Superset](https://superset.apache.org/) | Open-source BI platform with native Pinot connector support and the most popular visualization layer for Pinot deployments. |
| [Grafana](https://grafana.com/) | Monitoring and observability platform that connects to Pinot through its generic SQL data source or via a community plugin. |
| [Presto / Trino](https://trino.io/) | Distributed SQL query engines that can query Pinot as a catalog, enabling federated queries across Pinot and other sources like Hive or Iceberg. |


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

This section maps the directory structure of the Apache Pinot playbook repository to the concepts covered in each chapter.

| Path | Description | Referenced In |
| :--- | :--- | :--- |
| [`docker-compose.yml`](docker-compose.yml) | Local development stack: ZooKeeper, Pinot controller, broker, server and optionally Kafka. | Chapters 02, 08, 14, 21 |
| `contracts/` | Data contracts in OpenAPI, AsyncAPI and JSON Schema formats defining producer-consumer interfaces. | Chapter 13 |
| `schemas/` | Pinot schema configuration files defining dimension, metric and date-time fields. | Chapters 04, 05 |
| `tables/` | Pinot table configuration files defining type (OFFLINE, REALTIME, HYBRID), indexing and ingestion settings. | Chapters 05, 06, 07, 08, 09 |
| `sql/` | SQL query packs organized by topic, ready to run against the demo stack. | Chapters 10, 11, 12 |
| `src/pinot_playbook_demo/` | Python package with utility code for data generation, Pinot client wrappers and helper scripts. | Throughout labs |
| `labs/` | Hands-on lab exercises with step-by-step instructions, each mapping to one or more chapters. | Chapter 21, Exercises |
| `jobs/` | Batch ingestion job specifications (YAML and JSON) for offline table segment generation. | Chapter 07 |


## How to Stay Current

Apache Pinot is an actively developed project with a fast-moving release cadence. The following practices are the most effective ways to keep up.

- **Watch the GitHub repository** by starring and watching [https://github.com/apache/pinot](https://github.com/apache/pinot) to receive notifications about new releases, major pull requests and design discussions.
- **Join the Slack community** for real-time conversations with committers, contributors and fellow practitioners. This is the fastest path to answers when you hit unexpected behavior.
- **Subscribe to the dev mailing list** where major design decisions and Pinot Enhancement Proposals are discussed before implementation begins.
- **Follow the StarTree blog and YouTube channel.** StarTree, the company founded by Pinot's original creators, publishes the most consistent stream of Pinot-focused technical content.
- **Attend Apache Pinot meetups and conferences.** Community meetups happen regularly in major tech hubs and online. Check the Pinot website and Slack for announcements.


*This reference chapter will be updated as new resources become available. If you find a resource that belongs here, open an issue or pull request on the repository.*

*Previous chapter: [24. Glossary](./24-glossary.md)
