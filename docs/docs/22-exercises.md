# 22. Exercises

Learning Apache Pinot by reading alone will only take you so far. The exercises in this chapter are designed to bridge the gap between understanding concepts and applying them under realistic constraints. Each exercise maps back to one or more earlier chapters, so you can revisit the relevant material whenever you get stuck.

## How to Use These Exercises

| Audience | Recommended Approach |
| :--- | :--- |
| **Self-study** | Work through the exercises at your own pace after reading the corresponding chapters. Start with Section A to confirm comprehension, then move through the remaining sections in order. Time estimates help you plan study sessions in advance. |
| **Workshop or training session** | A facilitator can assign one section per session and use the exercises as discussion prompts. Sections A and B work well for a 90-minute introductory workshop. Sections C through F suit a full-day deep dive with practitioners who already run Pinot in production or are actively evaluating it. |
| **Design review pack** | Sections D, E and F double as a lightweight design review checklist. Before launching a new Pinot use case, walk through the relevant exercises with your team to pressure-test ingestion strategy, operational readiness and architectural fit. |


## Section A: Comprehension

These exercises test whether you have internalized the core mental model of Pinot. If any answer feels uncertain, go back to the referenced chapter before moving on. A solid foundation here will make the design and operations exercises far more productive.

---

**Exercise 1.** Why does the repo maintain both `trip_events` and `trip_state`?

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Beginner | 15 min | Chapter 4 (Schema Design), Chapter 9 (Upsert Semantics) |

The capstone project deliberately separates append-only events from latest-state records. Your answer should explain what each table optimizes for and why a single table cannot serve both access patterns well.

---

**Exercise 2.** What does the broker do that the server does not?

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Beginner | 15 min | Chapter 2 (Architecture), Chapter 16 (Routing) |

This question targets the division of labor in Pinot's distributed architecture. Think about query routing, scatter-gather coordination and result merging.

---

**Exercise 3.** Why is a segment more important than a single row for Pinot operations?

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Beginner | 15 min | Chapter 3 (Storage Model), Chapter 16 (Rebalancing) |

Pinot's unit of work is the segment, not the row. Your answer should cover how segments affect ingestion, replication, rebalancing and garbage collection.

---

**Exercise 4.** Why are message keys critical for the `trip-state` topic?

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Beginner | 15 min | Chapter 8 (Stream Ingestion), Chapter 9 (Upsert Mechanics) |

Upsert correctness depends on co-locating all updates for a given primary key on the same Kafka partition. Explain what breaks when keys are missing or inconsistent.

---

**Exercise 5.** What is the relationship between the JSON Schema contract and the Pinot schema?

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Intermediate | 20 min | Chapter 4 (Schema Design), Chapter 13 (API Contracts) |

Data contracts govern what producers are allowed to send. The Pinot schema governs what the serving layer expects to receive. Your answer should describe how these two artifacts interact and what happens when they drift apart.


## Section B: Modeling

Data modeling is where most Pinot projects succeed or fail. A well-chosen schema with the right indexes will outperform a poorly modeled table by orders of magnitude, regardless of cluster size. These exercises force you to make concrete modeling decisions and defend them.

---

**Exercise 6.** Add three helper columns you would introduce for your own domain and justify each.

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Intermediate | 30 min | Chapter 4 (Schema Design), Chapter 6 (Indexing) |

Helper columns are derived or computed fields added at ingestion time to simplify downstream queries. For each column you propose, state the data type, explain what query pattern it accelerates and describe how you would populate it.

---

**Exercise 7.** Pick one field you would denormalize and one field you would leave in a dimension table.

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Intermediate | 20 min | Chapter 4 (Denormalization), Chapter 7 (Batch Ingestion) |

Denormalization trades storage cost for query simplicity. Your answer should name a specific field, explain the cardinality and update frequency trade-offs and justify why the other field belongs in a separate dimension table.

---

**Exercise 8.** Explain when you would use a latest-state table rather than only an append-only fact table.

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Intermediate | 20 min | Chapter 9 (Upsert Design), Chapter 21 (Capstone) |

This exercise is about choosing between REALTIME upsert tables and standard append-only tables. Consider scenarios where a dashboard needs to reflect current entity state rather than the full history of events.

---

**Exercise 9.** Identify a potential null-handling risk in your own event model.

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Intermediate | 20 min | Chapter 4 (Null Semantics), Chapter 10 (Query Behavior) |

Nulls in Pinot behave differently depending on the column type, the aggregation function and the query engine version. Pick a field from your domain that could plausibly arrive as null and explain what downstream query would produce a wrong or misleading result.

---

**Exercise 10.** Choose a field that deserves a range index and explain why.

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Intermediate | 20 min | Chapter 6 (Indexing Cookbook) |

Range indexes accelerate inequality predicates and are especially valuable for time-bounded or threshold-based queries. Name the field, describe the query pattern, estimate the cardinality and explain why an inverted index alone would not be sufficient.


## Section C: Query Design

Writing correct SQL is necessary but not sufficient. Writing SQL that Pinot can execute efficiently requires understanding the query engines, their limitations and the physical layout of your data. These exercises build that muscle.

---

**Exercise 11.** Rewrite a business KPI into a Pinot-friendly group-by query.

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Intermediate | 30 min | Chapter 10 (V1 Query Patterns), Chapter 5 (Table Configuration) |

Start with a real or realistic KPI from your domain, such as "average trip duration by city in the last hour." Write the SQL, identify which table and columns it hits and verify that the required indexes exist. Explain any transformations you applied to make the query efficient.

---

**Exercise 12.** Give an example of a query that should use MSE.

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Intermediate | 20 min | Chapter 11 (Multi-Stage Engine) |

The multi-stage engine (v2) supports joins, subqueries, window functions and other operations that the single-stage engine cannot handle. Describe a concrete analytical question, write the SQL and explain why the single-stage engine would reject or mishandle it.

---

**Exercise 13.** Give an example of a query that should probably not use MSE.

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Intermediate | 20 min | Chapter 11 (MSE Overhead), Chapter 10 (V1 Strengths) |

MSE adds coordination overhead that is unnecessary for simple aggregations the v1 engine handles natively. Write a query where forcing MSE would increase latency without adding analytical value. Explain the trade-off.

---

**Exercise 14.** Write a query that would benefit from time pruning.

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Intermediate | 20 min | Chapter 10 (Query Optimization), Chapter 3 (Segment Boundaries) |

Time pruning allows Pinot to skip entire segments based on time predicates, dramatically reducing the amount of data scanned. Write a query with an appropriate time filter, name the time column and explain how segment boundaries interact with your predicate.

---

**Exercise 15.** Write a query that would benefit from star-tree style pre-aggregation.

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Advanced | 30 min | Chapter 6 (Star-Tree), Chapter 17 (Performance Engineering) |

Star-tree indexes pre-aggregate metrics along configured dimension combinations. Write a query that would otherwise scan millions of rows but can be answered in constant time with a star-tree index. Specify the dimensions, the metric and the aggregation function.


## Section D: Ingestion and CDC

Ingestion is where data quality is won or lost. A misconfigured Kafka consumer, a missing message key or a poorly planned backfill can corrupt your serving layer in ways that are difficult to detect and expensive to repair. These exercises prepare you for the most common ingestion challenges.

---

**Exercise 16.** Explain the failure mode if `trip-state` messages are not keyed by `trip_id`.

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Intermediate | 20 min | Chapter 9 (Upsert Requirements), Chapter 8 (Kafka Partitioning) |

Walk through the sequence of events that occurs when two updates for the same trip land on different Kafka partitions and are consumed by different Pinot servers. Describe the resulting data inconsistency and how a user would observe it.

---

**Exercise 17.** What evidence would you gather before changing realtime flush thresholds?

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Intermediate | 30 min | Chapter 8 (Flush Thresholds), Chapter 18 (Observability) |

Flush thresholds control how large consuming segments grow before they are committed. Changing them affects memory usage, segment count, query latency and ingestion lag. List the metrics, logs and configuration values you would inspect before proposing a change.

---

**Exercise 18.** How would you backfill a missing dimension table?

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Advanced | 30 min | Chapter 7 (Batch Ingestion), Chapter 4 (Dimension Table Design) |

Suppose a dimension table was never loaded or was accidentally deleted. Describe the steps to rebuild it from the source of truth, load it into Pinot and verify that lookup joins produce correct results. Consider the ordering constraints and potential downtime.

---

**Exercise 19.** What data contract change would force a schema and table review?

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Intermediate | 20 min | Chapter 4 (Schema Evolution), Chapter 13 (Contract Management) |

Not all contract changes are equal. Adding an optional field is usually safe. Renaming a field, changing a data type or removing a field can break ingestion, queries or both. Give three concrete examples ranked by severity and explain the review process each would trigger.

---

**Exercise 20.** How would you model logical deletes?

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Advanced | 30 min | Chapter 9 (Upsert and Dedup), Chapter 5 (Retention Configuration) |

Pinot does not support physical row deletion in the way a transactional database does. Describe a strategy for marking records as deleted so that queries can filter them out while preserving the event history. Consider the implications for upsert tables, retention policies and query performance.


## Section E: Operations

Running Pinot in production is a discipline distinct from designing schemas and writing queries. These exercises focus on defining SLOs, diagnosing incidents and validating changes.

---

**Exercise 21.** Define a freshness SLO for `trip_state`.

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Intermediate | 20 min | Chapter 18 (Observability), Chapter 8 (Ingestion Lag) |

Freshness is the maximum acceptable delay between an event occurring and that event being queryable in Pinot. State the SLO in concrete terms (for example, "p99 freshness under 30 seconds"), identify the measurement points in the pipeline and explain what alert you would fire when the SLO is violated.

---

**Exercise 22.** Define a query latency SLO for one dashboard path.

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Intermediate | 20 min | Chapter 18 (Metrics Collection), Chapter 17 (Performance Tuning) |

Pick a specific dashboard query and define the latency SLO at p50, p95 and p99. Explain how you would measure latency at the broker, identify the factors that could cause a breach and describe the escalation path when the SLO is violated.

---

**Exercise 23.** What would you inspect first in a stale-data incident?

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Intermediate | 20 min | Chapter 19 (Failure Modes), Chapter 18 (Observability Stack) |

A user reports that the dashboard is showing data that is 10 minutes old instead of the expected 30 seconds. Walk through your investigation in order. Consider Kafka consumer lag, consuming segment status, controller health and ZooKeeper state.

---

**Exercise 24.** What would you inspect first after a rebalance?

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Intermediate | 20 min | Chapter 16 (Rebalancing), Chapter 19 (Troubleshooting) |

A rebalance just completed and query latency has increased. Describe the checks you would perform, including segment distribution, replica group alignment and server resource utilization.

---

**Exercise 25.** How would you prove an index change improved the hot path?

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Advanced | 30 min | Chapter 6 (Index Types), Chapter 17 (Benchmarking) |

You added a bloom filter to a high-cardinality column and want to demonstrate that it reduced query latency on the primary dashboard query. Describe the before-and-after measurement methodology, the metrics you would compare and how you would control for confounding variables like cluster load or data volume changes.


## Section F: Architecture

These exercises zoom out from individual tables and queries to the system level. They ask you to reason about when Pinot is the right tool, how it fits into a broader data platform and how to manage a multi-team deployment. Answering them well requires synthesizing material from across the entire book.

---

**Exercise 26.** Build a decision tree that says when Pinot is the right serving layer for your workload.

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Advanced | 60 min | Chapter 20 (Decision Framework), Chapter 1 (Pinot Overview) |

Create a flowchart or decision tree with at least six decision nodes. Inputs should include query latency requirements, data freshness needs, query complexity, data volume and whether the workload is user-facing or internal. Terminal nodes should recommend Pinot, a warehouse, a cache or a transactional database.

---

**Exercise 27.** Name two reasons to keep a warehouse or lakehouse alongside Pinot.

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Intermediate | 20 min | Chapter 20 (Patterns and Anti-Patterns), Chapter 1 (Pinot Overview) |

Pinot excels at low-latency analytical queries on fresh data, but it does not replace every component in a data platform. Your answer should identify specific workloads or access patterns that a warehouse handles better and explain why running them in Pinot would be impractical or wasteful.

---

**Exercise 28.** What cluster isolation boundary would you introduce first in a multi-team environment?

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Advanced | 30 min | Chapter 16 (Tenant Isolation), Chapter 14 (Deployment), Chapter 15 (Governance) |

Suppose three teams share a single Pinot cluster. One team's heavy ingestion workload is degrading query performance for the others. Describe the isolation mechanism you would implement first, whether that is tenant tagging, separate server pools, query quotas or something else. Justify your choice in terms of complexity, cost and effectiveness.

---

**Exercise 29.** Which part of the capstone would you reuse unchanged in a production deployment?

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Intermediate | 20 min | Chapter 21 (Capstone) |

Review the capstone architecture in Chapter 21. Identify one component that is already production-grade and explain why it requires no modification. Consider schemas, contracts, simulation logic and infrastructure configuration.

---

**Exercise 30.** Which part would you replace first?

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Intermediate | 20 min | Chapter 21 (Capstone Design), Chapter 14 (Production Deployment) |

From the same capstone review, identify the component that is most clearly a prototype shortcut and explain what you would replace it with. Describe the production-grade alternative and the effort involved.


## Stretch Exercise

This final exercise ties together every skill from the book. It is designed for practitioners who want to prove they can extend a working system, not just understand one. Plan for a half-day of focused work.

---

**Exercise 31.** Extend the capstone repository with four additions and one piece of documentation.

| Difficulty | Time | Reference |
| :--- | :--- | :--- |
| Advanced | 4 hours | Chapters 4, 5, 7, 13, 21 |

This exercise asks you to make five concrete changes to the codebase.

1. **Add a new dimension table.** Choose a real-world entity (for example, driver profiles or vehicle metadata), define the schema, create the table configuration and load it via batch ingestion. Verify that lookup joins against the new table return correct results. See Chapter 4 for schema design, Chapter 5 for table configuration and Chapter 7 for batch ingestion.

2. **Add one new API endpoint.** Expose a new analytical query through the API layer. The endpoint should accept at least one filter parameter, query Pinot and return a structured response. See Chapter 13 for API design patterns and contract validation.

3. **Add one simulation.** Extend the event simulator to produce records for your new dimension or a new event type. The simulation should generate realistic data distributions and respect the JSON Schema contract. See Chapter 21 for the existing simulation design.

4. **Add one contract validation test.** Write a test that verifies incoming events conform to the JSON Schema contract. The test should catch at least one type of schema violation, such as a missing required field or an invalid enum value. See Chapter 13 for contract testing patterns.

5. **Document the trade-off.** Write a short chapter note (one to two pages) explaining the design decisions you made, the alternatives you considered and the trade-offs you accepted. This note should be useful to a future team member who needs to understand why the system is shaped the way it is.


## Further Practice

After completing these exercises, there are several ways to continue deepening your Pinot expertise.

- **Run the capstone under load.** Deploy the full capstone stack and push the simulator to produce thousands of events per second. Observe how segment creation, query latency and memory usage change under sustained throughput. This builds capacity planning intuition that reading alone cannot provide. See Chapter 17 and Chapter 18.

- **Break things on purpose.** Kill a server mid-rebalance, corrupt a segment and publish events with a scrambled schema. Practice diagnosing and recovering from each failure in a safe environment before you encounter it in production. See Chapter 19.

- **Review real-world case studies.** Read publications from the Apache Pinot community at companies like LinkedIn, Uber and Stripe. Read two or three case studies and compare their architectural choices to the patterns in Chapter 20. Note where they diverge and think about why.

- **Contribute to the project.** Pick a small bug or documentation improvement in the Apache Pinot open-source codebase, submit a pull request and go through the review process. There is no faster way to learn how the internals work than reading and modifying the source code.

*Previous chapter: [21. Capstone: Building a Rides and Commerce Analytics Platform](./21-capstone-building-a-rides-platform.md)

*Next chapter: [23. Solution Key](./23-solution-key.md)
