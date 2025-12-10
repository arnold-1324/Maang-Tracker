    *   Achieved `<100ms p50 reads` for 60K daily lookups.
    *   Reduced API p50 latency by 30% (140ms → 95ms).
    *   Introduced CI performance gates to prevent regressions.
*   **Keywords**: Low-latency, Caching, Redis, SLA guarantees, CI/CD.

**2. Inventory Index & Ingestion Prototype**
*   **Tech Stack**: Node.js, Redis, Elasticsearch, Kafka-style pipeline.
*   **Impact**:
    *   Built resilient pipeline maintaining `<100ms p50 reads` during heavy writes/failures.
    *   Validated graceful recovery and replay semantics.
*   **Keywords**: Event-driven, Ingestion, Elasticsearch, Reliability, Backpressure.

**3. Distributed Caching System**
*   **Tech Stack**: Java, TCP/IP, P2P.
*   **Impact**:
    *   Implemented eventual consistency and replication.
    *   Tested under chaotic failure modes (split-brain, partitions).
*   **Keywords**: Distributed Systems, CAP theorem, Consistency, Networking.

---

## 2. Shortlisted "Live" Roles (Prioritized)

Based on December 2025 search results from Microsoft, Amazon, Uber, and Stripe careers pages.

### Match #1: Microsoft - Software Engineer II (Backend)
*   **Location**: Hyderabad / Bengaluru (Hybrid)
*   **Team**: Azure Cloud Services / M365 Core
*   **Compensation**: ₹50L - ₹68L (Estimated)
*   **Why**: Strong match for "Distributed Systems" and "Java/C#" skills. Your experience with "resilient pipelines" and "eventual consistency" fits Azure's reliability focus.
*   **Tech Match**: 90% (Java, Distributed Systems, High Availability).
*   **Gap**: C# (manageable switch from Java).

### Match #2: Amazon - SDE II (Consumer/Payments)
*   **Location**: Bangalore, Karnataka
*   **Team**: Amazon Pay / Consumer Engineering
*   **Compensation**: ₹53L - ₹65L + RSUs
*   **Why**: Your "Payments, Billing, Idempotency" domain knowledge is a direct hit. Amazon thrives on "Operational Excellence" (your CI gates/SLOs).
*   **Tech Match**: 95% (Java, DynamoDB/NoSQL, High Tech Scale).

### Match #3: Uber - Backend Engineer II (Risk/Payments)
*   **Location**: Bangalore
*   **Compensation**: ₹55L - ₹75L (High Base)
*   **Why**: Requires "Go" and high-concurrency experience. You are learning Go; your "Ingestion Prototype" shows the right mindset for their dispatch/ledger systems.
*   **Tech Match**: 80% (Strong Backend, but Go is listed as 'Learning').
*   **Action**: Needs "Go Ramp-up" plan emphasized.

### Match #4: Stripe - Backend Engineer (Infrastructure/Money)
*   **Location**: Bengaluru (Office-based)
*   **Compensation**: ₹60L - ₹80L (Top Tier)
*   **Why**: Premium product role. Heavily focused on reliability, idempotency, and ledger correctness.
*   **Tech Match**: 75% (Rub/Go required).
*   **Action**: High Reach. Needs strong cover letter on "Quality" and "Reliability".

---

## 3. Tailored Cover Letter Bullets

### For Amazon SDE II (Payments/Consumer)
*   "**Domain Fit**: I have direct experience building event-driven ingestion pipelines that handle financial-grade requirements like **idempotency**, **replayability**, and **data durability**—core challenges in Amazon's payment infrastructure."
*   "**Operational Excellence**: At Synthesis, I didn't just write code; I defined **SLOs**, built monitoring dashboards, and introduced **CI performance gates** that successfully prevented latency regressions in a 60K+ daily request system."
*   "**High Scale**: I optimized a critical indexing microservice to achieve **<100ms p50 latency**, reducing overall API response times by 30% through targeted schema and caching improvements."
*   "**Ownership**: I own features end-to-end, from the vague design phase through to deployment and **post-incident analysis**, mirroring Amazon's 'Ownership' and 'Bias for Action' leadership principles."

### For Microsoft Software Engineer II (Azure/Cloud)
*   "**Distributed Systems**: My recent work involves implementing a **peer-to-peer distributed cache** from scratch, handling complex failure modes like **network partitions** and **split-brain** scenarios, giving me a strong foundation for Azure's cloud reliability challenges."
*   "**Resilience Engineering**: I architected a Node.js ingestion prototype specifically designed to withstand **node crashes** and partial failures while maintaining data integrity, aligning with Microsoft's focus on trust and reliability."
*   "**Code Quality**: I led the initiative to standardize **PR checklists** and testing gates in my current team, significantly reducing post-merge defects and fostering a culture of engineering excellence."
*   "**Adaptability**: While my core strength is Java/Node.js, I have a strong grasp of OOP principles and am eager to apply my distributed systems knowledge to the **.NET/C#** ecosystem used in Azure Core."

---

## 4. Tracker Updates (Ready for `tracker_update` JSON)

*   **New Missing Skill**: **C# / .NET Core** (for Microsoft).
*   **Reinforced Skill**: **Go (Golang)** (Blocking for Uber/Stripe).
*   **Action Plan**:
    1.  **Go Mini-Project**: Complete "Payments Microservice in Go" (7 days).
    2.  **System Design**: Focus on "Distributed Locking" (Redis/Etcd) for the Amazon/Microsoft interviews.
    3.  **Observability**: Add OpenTelemetry to the Inventory Prototype (Resume booster).

