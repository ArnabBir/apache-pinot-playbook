# 22. Exercises

Learning Apache Pinot by reading alone will only take you so far. The exercises in this chapter are designed to bridge the gap between understanding concepts and applying them under realistic constraints. Each exercise maps back to one or more earlier chapters, so you can revisit the relevant material whenever you get stuck.

## How to use these exercises

These exercises serve three distinct audiences and you should pick the mode that fits your situation.

**Self-study.** Work through the exercises at your own pace after reading the corresponding chapters. Start with Section A to confirm your comprehension, then move through the remaining sections in order. Time estimates are provided so you can plan study sessions in advance.

**Workshop or training session.** A facilitator can assign one section per session and use the exercises as discussion prompts. Sections A and B work well for a 90-minute introductory workshop. Sections C through F are better suited for a full-day deep dive with practitioners who already run Pinot in production or are actively evaluating it.

**Design review pack.** Sections D, E and F double as a lightweight design review checklist. Before launching a new Pinot use case, walk through the relevant exercises with your team to pressure-test ingestion strategy, operational readiness and architectural fit.

Each exercise includes a difficulty rating, a time estimate and cross-references to the chapters where the underlying concepts are explained in detail.


## Section A: Comprehension

These exercises test whether you have internalized the core mental model of Pinot. If any answer feels uncertain, go back to the referenced chapter before moving on. A solid foundation here will make the design and operations exercises far more productive.

**Exercise 1.** Why does the repo maintain both `trip_events` and `trip_state`?

Difficulty: Beginner. Estimated time: 15 minutes. The capstone project deliberately separates append-only events from latest-state records. Your answer should explain what each table optimizes for and why a single table cannot serve both access patterns well. See Chapter 4 for schema design principles and Chapter 9 for upsert semantics.

**Exercise 2.** What does the broker do that the server does not?

Difficulty: Beginner. Estimated time: 15 minutes. This question targets the division of labor in Pinot's distributed architecture. Think about query routing, scatter gather coordination and result merging. See Chapter 2 for the full component breakdown and Chapter 16 for routing and partitioning details.

**Exercise 3.** Why is a segment more important than a single row for Pinot operations?

Difficulty: Beginner. Estimated time: 15 minutes. Pinot's unit of work is the segment, not the row. Your answer should cover how segments affect ingestion, replication, rebalancing and garbage collection. See Chapter 3 for the storage model and Chapter 16 for rebalancing.

**Exercise 4.** Why are message keys critical for the `trip-state` topic?

Difficulty: Beginner. Estimated time: 15 minutes. Upsert correctness depends on co-locating all updates for a given primary key on the same Kafka partition. Explain what breaks when keys are missing or inconsistent. See Chapter 8 for stream ingestion and Chapter 9 for upsert and dedup mechanics.

**Exercise 5.** What is the relationship between the JSON Schema contract and the Pinot schema?

Difficulty: Intermediate. Estimated time: 20 minutes. Data contracts govern what producers are allowed to send. The Pinot schema governs what the serving layer expects to receive. Your answer should describe how these two artifacts interact and what happens when they drift apart. See Chapter 4 for schema design and Chapter 13 for API contracts.


## Section B: Modeling

Data modeling is where most Pinot projects succeed or fail. A well-chosen schema with the right indexes will outperform a poorly modeled table by orders of magnitude, regardless of cluster size. These exercises force you to make concrete modeling decisions and defend them.

**Exercise 6.** Add three helper columns you would introduce for your own domain and justify each.

Difficulty: Intermediate. Estimated time: 30 minutes. Helper columns are derived or computed fields added at ingestion time to simplify downstream queries. For each column you propose, state the data type, explain what query pattern it accelerates and describe how you would populate it. See Chapter 4 for schema design patterns and Chapter 6 for how indexes interact with column choice.

**Exercise 7.** Pick one field you would denormalize and one field you would leave in a dimension table.

Difficulty: Intermediate. Estimated time: 20 minutes. Denormalization trades storage cost for query simplicity. Your answer should name a specific field, explain the cardinality and update frequency trade-offs and justify why the other field belongs in a separate dimension table. See Chapter 4 for denormalization guidance and Chapter 7 for batch ingestion of dimension tables.

**Exercise 8.** Explain when you would use a latest-state table rather than only an append-only fact table.

Difficulty: Intermediate. Estimated time: 20 minutes. This exercise is about choosing between REALTIME upsert tables and standard append-only tables. Consider scenarios where a dashboard needs to reflect the current state of an entity rather than the full history of events. See Chapter 9 for upsert design and Chapter 21 for the capstone's use of both patterns.

**Exercise 9.** Identify a potential null-handling risk in your own event model.

Difficulty: Intermediate. Estimated time: 20 minutes. Nulls in Pinot behave differently depending on the column type, the aggregation function and the query engine version. Pick a field from your domain that could plausibly arrive as null and explain what downstream query would produce a wrong or misleading result. See Chapter 4 for null semantics and Chapter 10 for query behavior with nulls.

**Exercise 10.** Choose a field that deserves a range index and explain why.

Difficulty: Intermediate. Estimated time: 20 minutes. Range indexes accelerate inequality predicates and are especially valuable for time-bounded or threshold-based queries. Name the field, describe the query pattern, estimate the cardinality and explain why an inverted index alone would not be sufficient. See Chapter 6 for the full indexing cookbook.


## Section C: Query Design

Writing correct SQL is necessary but not sufficient. Writing SQL that Pinot can execute efficiently requires understanding the query engines, their limitations and the physical layout of your data. These exercises build that muscle.

**Exercise 11.** Rewrite a business KPI into a Pinot-friendly group-by query.

Difficulty: Intermediate. Estimated time: 30 minutes. Start with a real or realistic KPI from your domain, such as "average trip duration by city in the last hour." Write the SQL, identify which table and columns it hits and verify that the required indexes exist. Explain any transformations you applied to make the query efficient. See Chapter 10 for v1 query patterns and Chapter 5 for table configuration that affects query performance.

**Exercise 12.** Give an example of a query that should use MSE.

Difficulty: Intermediate. Estimated time: 20 minutes. The multi stage engine (v2) supports joins, subqueries, window functions and other operations that the single stage engine cannot handle. Describe a concrete analytical question, write the SQL and explain why the single stage engine would reject or mishandle it. See Chapter 11 for MSE capabilities and limitations.

**Exercise 13.** Give an example of a query that should probably not use MSE.

Difficulty: Intermediate. Estimated time: 20 minutes. MSE adds coordination overhead that is unnecessary for simple aggregations the v1 engine handles natively. Write a query where forcing MSE would increase latency without adding analytical value. Explain the trade-off. See Chapter 11 for MSE overhead considerations and Chapter 10 for v1 strengths.

**Exercise 14.** Write a query that would benefit from time pruning.

Difficulty: Intermediate. Estimated time: 20 minutes. Time pruning allows Pinot to skip entire segments based on time predicates, dramatically reducing the amount of data scanned. Write a query with an appropriate time filter, name the time column and explain how segment boundaries interact with your predicate. See Chapter 10 for query optimization and Chapter 3 for segment time boundaries.

**Exercise 15.** Write a query that would benefit from star-tree style pre-aggregation.

Difficulty: Advanced. Estimated time: 30 minutes. Star-tree indexes pre-aggregate metrics along configured dimension combinations. Write a query that would otherwise scan millions of rows but can be answered in constant time with a star-tree index. Specify the dimensions, the metric and the aggregation function. See Chapter 6 for star-tree configuration and Chapter 17 for performance engineering trade-offs.


## Section D: Ingestion and CDC

Ingestion is where data quality is won or lost. A misconfigured Kafka consumer, a missing message key or a poorly planned backfill can corrupt your serving layer in ways that are difficult to detect and expensive to repair. These exercises prepare you for the most common ingestion challenges.

**Exercise 16.** Explain the failure mode if `trip-state` messages are not keyed by `trip_id`.

Difficulty: Intermediate. Estimated time: 20 minutes. Walk through the sequence of events that occurs when two updates for the same trip land on different Kafka partitions and are consumed by different Pinot servers. Describe the resulting data inconsistency and how a user would observe it. See Chapter 9 for upsert requirements and Chapter 8 for Kafka partitioning.

**Exercise 17.** What evidence would you gather before changing realtime flush thresholds?

Difficulty: Intermediate. Estimated time: 30 minutes. Flush thresholds control how large consuming segments grow before they are committed. Changing them affects memory usage, segment count, query latency and ingestion lag. List the metrics, logs and configuration values you would inspect before proposing a change. See Chapter 8 for flush threshold tuning and Chapter 18 for the observability signals that inform the decision.

**Exercise 18.** How would you backfill a missing dimension table?

Difficulty: Advanced. Estimated time: 30 minutes. Suppose a dimension table was never loaded or was accidentally deleted. Describe the steps to rebuild it from the source of truth, load it into Pinot and verify that lookup joins produce correct results. Consider the ordering constraints and potential downtime. See Chapter 7 for batch ingestion and Chapter 4 for dimension table design.

**Exercise 19.** What data contract change would force a schema and table review?

Difficulty: Intermediate. Estimated time: 20 minutes. Not all contract changes are equal. Adding an optional field is usually safe. Renaming a field, changing a data type or removing a field can break ingestion, queries or both. Give three concrete examples ranked by severity and explain the review process each would trigger. See Chapter 4 for schema evolution and Chapter 13 for contract management.

**Exercise 20.** How would you model logical deletes?

Difficulty: Advanced. Estimated time: 30 minutes. Pinot does not support physical row deletion in the way a transactional database does. Describe a strategy for marking records as deleted so that queries can filter them out while still preserving the event history. Consider the implications for upsert tables, retention policies and query performance. See Chapter 9 for upsert and dedup patterns and Chapter 5 for retention configuration.


## Section E: Operations

Running Pinot in production is a discipline distinct from designing schemas and writing queries. These exercises focus on defining SLOs, diagnosing incidents and validating changes, which are the day-to-day concerns of a Pinot operator.

**Exercise 21.** Define a freshness SLO for `trip_state`.

Difficulty: Intermediate. Estimated time: 20 minutes. Freshness is the maximum acceptable delay between an event occurring and that event being queryable in Pinot. State the SLO in concrete terms (for example, "p99 freshness under 30 seconds"), identify the measurement points in the pipeline and explain what alert you would fire when the SLO is violated. See Chapter 18 for observability and Chapter 8 for ingestion lag metrics.

**Exercise 22.** Define a query latency SLO for one dashboard path.

Difficulty: Intermediate. Estimated time: 20 minutes. Pick a specific dashboard query and define the latency SLO at p50, p95 and p99. Explain how you would measure latency at the broker, identify the factors that could cause a breach and describe the escalation path when the SLO is violated. See Chapter 18 for metrics collection and Chapter 17 for performance tuning.

**Exercise 23.** What would you inspect first in a stale-data incident?

Difficulty: Intermediate. Estimated time: 20 minutes. A user reports that the dashboard is showing data that is 10 minutes old instead of the expected 30 seconds. Walk through your investigation in order. Consider Kafka consumer lag, consuming segment status, controller health and Zookeeper state. See Chapter 19 for failure modes and Chapter 18 for the observability stack.

**Exercise 24.** What would you inspect first after a rebalance?

Difficulty: Intermediate. Estimated time: 20 minutes. A rebalance just completed and query latency has increased. Describe the checks you would perform, including segment distribution, replica group alignment and server resource utilization. See Chapter 16 for rebalancing mechanics and Chapter 19 for post-rebalance troubleshooting.

**Exercise 25.** How would you prove an index change improved the hot path?

Difficulty: Advanced. Estimated time: 30 minutes. You added a bloom filter to a high cardinality column and want to demonstrate that it reduced query latency on the primary dashboard query. Describe the before-and-after measurement methodology, the metrics you would compare and how you would control for confounding variables like cluster load or data volume changes. See Chapter 6 for index types and Chapter 17 for performance benchmarking.


## Section F: Architecture

These exercises zoom out from individual tables and queries to the system level. They ask you to reason about when Pinot is the right tool, how it fits into a broader data platform and how to manage a multi-team deployment. Answering them well requires synthesizing material from across the entire book.

**Exercise 26.** Build a decision tree that says when Pinot is the right serving layer for your workload.

Difficulty: Advanced. Estimated time: 60 minutes. Create a flowchart or decision tree with at least six decision nodes. Inputs should include query latency requirements, data freshness needs, query complexity, data volume and whether the workload is user facing or internal. Terminal nodes should recommend Pinot, a warehouse, a cache or a transactional database. See Chapter 20 for the decision framework and Chapter 1 for Pinot's positioning.

**Exercise 27.** Name two reasons to keep a warehouse or lakehouse alongside Pinot.

Difficulty: Intermediate. Estimated time: 20 minutes. Pinot excels at low-latency analytical queries on fresh data, but it does not replace every component in a data platform. Your answer should identify specific workloads or access patterns that a warehouse handles better and explain why running them in Pinot would be impractical or wasteful. See Chapter 20 for patterns and antipatterns and Chapter 1 for the Pinot overview.

**Exercise 28.** What cluster isolation boundary would you introduce first in a multi-team environment?

Difficulty: Advanced. Estimated time: 30 minutes. Suppose three teams share a single Pinot cluster. One team's heavy ingestion workload is degrading query performance for the others. Describe the isolation mechanism you would implement first, whether that is tenant tagging, separate server pools, query quotas or something else entirely. Justify your choice in terms of complexity, cost and effectiveness. See Chapter 16 for tenant and server isolation, Chapter 14 for deployment topology and Chapter 15 for governance controls.

**Exercise 29.** Which part of the capstone would you reuse unchanged in a production deployment?

Difficulty: Intermediate. Estimated time: 20 minutes. Review the capstone architecture in Chapter 21. Identify one component that is already production grade and explain why it requires no modification. Consider schemas, contracts, simulation logic and infrastructure configuration.

**Exercise 30.** Which part would you replace first?

Difficulty: Intermediate. Estimated time: 20 minutes. From the same capstone review, identify the component that is most clearly a prototype shortcut and explain what you would replace it with. Describe the production grade alternative and the effort involved. See Chapter 21 for the capstone design and Chapter 14 for production deployment patterns.


## Stretch Exercise

This final exercise ties together every skill from the book. It is designed for practitioners who want to prove they can extend a working system, not just understand one. Plan for a half-day of focused work.

**Exercise 31.** Extend the capstone repository with four additions and one piece of documentation.

Difficulty: Advanced. Estimated time: 4 hours. This exercise asks you to make five concrete changes to the codebase.

1. **Add a new dimension table.** Choose a real-world entity (for example, driver profiles or vehicle metadata), define the schema, create the table configuration and load it via batch ingestion. Verify that lookup joins against the new table return correct results. See Chapter 4 for schema design, Chapter 5 for table configuration and Chapter 7 for batch ingestion.

2. **Add one new API endpoint.** Expose a new analytical query through the API layer. The endpoint should accept at least one filter parameter, query Pinot and return a structured response. See Chapter 13 for API design patterns and contract validation.

3. **Add one simulation.** Extend the event simulator to produce records for your new dimension or a new event type. The simulation should generate realistic data distributions and respect the JSON Schema contract. See Chapter 21 for the existing simulation design.

4. **Add one contract validation test.** Write a test that verifies incoming events conform to the JSON Schema contract. The test should catch at least one type of schema violation, such as a missing required field or an invalid enum value. See Chapter 13 for contract testing patterns.

5. **Document the trade-off.** Write a short chapter note (one to two pages) explaining the design decisions you made, the alternatives you considered and the trade-offs you accepted. This note should be useful to a future team member who needs to understand why the system is shaped the way it is.


## Further Practice

After completing these exercises, there are several ways to continue deepening your Pinot expertise.

Running the capstone under load involves deploying the full capstone stack and pushing the simulator to produce thousands of events per second. Observe how segment creation, query latency and memory usage change under sustained throughput. This will give you an intuition for capacity planning that reading alone cannot provide. See Chapter 17 for performance engineering and Chapter 18 for observability.

Breaking things on purpose involves killing a server mid-rebalance, corrupting a segment and publishing events with a scrambled schema. Practice diagnosing and recovering from each failure in a safe environment before you encounter it in production. See Chapter 19 for failure modes and recovery procedures.

Reviewing real-world case studies means reading publications from the Apache Pinot community at companies like LinkedIn, Uber and Stripe. Read two or three case studies and compare their architectural choices to the patterns described in Chapter 20. Note where they diverge and think about why.

Contributing to the project means picking a small bug or documentation improvement in the Apache Pinot open source codebase, submitting a pull request and going through the review process. There is no faster way to learn how the internals work than reading and modifying the source code.

*Previous chapter: [21. Capstone: Building a Rides and Commerce Analytics Platform](./21-capstone-building-a-rides-platform.md)

*Next chapter: [23. Solution Key](./23-solution-key.md)
