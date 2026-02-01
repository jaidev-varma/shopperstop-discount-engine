# System Design Document

## 1. Architecture Overview
The application follows a **Clean Architecture** approach, separating concerns into three distinct layers:
* **API Layer (`app/api`)**: Handles HTTP requests, input validation (Pydantic), and response formatting.
* **Core Layer (`app/core`)**: Contains the business logic and the "Discount Engine".
* **Data Layer (`app/models`)**: Manages in-memory data storage and schema definitions.

## 2. Key Design Decisions

### A. Strategy Pattern for Extensibility
I used the **Strategy Pattern** for the discount logic.
* **Why?** New discount types (e.g., "Season Pass") can be added by simply creating a new class inheriting from `DiscountRule` without modifying the core engine.
* **Implementation:** `SlabDiscount`, `BogoDiscount`, and `FlatDiscount` all share a common interface.

### B. Configuration-Driven Behavior
Business rules are **not hardcoded**.
* Promotions are stored as data objects (JSON).
* The "Premium Customer" logic is dynamically configured via the `/promotions` API rather than being stuck in `if/else` statements.

### C. Concurrency & Thread Safety
* **Problem:** In a real-world scenario, multiple admins might update rules while cashiers are calculating bills.
* **Solution:** Implemented `asyncio.Lock` in the `InMemoryDB`. This ensures atomic updates to the rule set, preventing race conditions (Read-Write conflicts).

### D. Precision Arithmetic
* **Decision:** Used Python's `Decimal` type instead of `float` for all monetary calculations.
* **Reason:** To prevent floating-point rounding errors (e.g., `0.1 + 0.2 != 0.3`) which are unacceptable in financial systems.

## 3. Trade-offs
* **In-Memory Database:**
    * *Pro:* Extremely fast, easy to set up, no external dependencies (Docker friendly).
    * *Con:* Data is lost on restart.
    * *Mitigation:* Seed data is loaded on startup to facilitate testing.