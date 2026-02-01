# Submission: Promotional Pricing Engine (PPE)

**Candidate:** [D. Jaidev Varma]
**Date:** 2026-02-02

## ⏱️ Time Spent
* **Phase 1 (Architecture & Models):** 1.5 Hours
    * Defining Pydantic models and Strategy Pattern interfaces.
* **Phase 2 (Core Engine Logic):** 2 Hours
    * Implementing progressive slab math, decimal precision, and stacking rules.
* **Phase 3 (API & Extensibility):** 1.5 Hours
    * Building FastAPI endpoints, CRUD for promotions, and BOGO logic.
* **Phase 4 (Testing & Polish):** 1 Hour
    * Writing Unit/Integration tests and Docker setup.
* **Total:** ~6 Hours

## 🧠 Assumptions Made
1.  **Currency Precision:** All monetary calculations use `decimal.Decimal` with 2 places of precision to prevent floating-point errors.
2.  **Timezones:** The server assumes UTC for all `valid_from` and `valid_to` timestamps in promotion rules.
3.  **Stacking Logic:** If a promotion is marked `stackable=False`, it prevents *subsequent* lower-priority rules from running, but does not invalidate *higher-priority* rules that already ran.
4.  **BOGO Logic:** "Buy 2 Get 1" implies the customer pays for 2 items and gets a 3rd identical item for free. Logic applies to multiples (e.g., buy 4 get 2).
5.  **Exclusive Tiers:** A customer belongs to exactly one tier (REGULAR or PREMIUM) at a time.

## ⚠️ Known Limitations
1.  **Persistence:** The database is in-memory (`dict`). All data is lost when the application restarts.
2.  **Concurrency:** While FastAPI is async, the in-memory dictionary is not protected by mutex locks. Race conditions could occur if two admins update the same rule simultaneously.
3.  **Versioning:** Currently, updating a rule overwrites it. There is no historical record (v1, v2) of rule changes, only an audit log of the request.
4.  **Auth:** No authentication (JWT/OAuth) is implemented. APIs are open.

## 🚀 Improvements (With More Time)
1.  **Database Migration:** Replace `InMemoryDB` with PostgreSQL using SQLAlchemy for persistence and transaction safety.
2.  **Redis Caching:** Implement a cache layer for `get_active_promotions()` since rules are read often but written rarely.
3.  **Rule Engine UI:** A simple React frontend for Marketing Managers to drag-and-drop rule configurations.
4.  **Rate Limiting:** Add `slowapi` to prevent abuse of the calculation endpoint.
5.  **Event Bus:** Emit events (`PROMOTION_APPLIED`) to a message queue (RabbitMQ) for the Data Science team to analyze promotion effectiveness asynchronously.