# CareerOS Infinity - Plugin Architecture Roadmap

This document outlines the strategic plugin-based architectural design recommended by the CTO to keep the core platform modular and decoupled.

---

## 1. Modular Core Architecture Mappings

As CareerOS Infinity expands beyond the alpha phase, features will shift into independent modular plugins:

```
                  +-----------------------------------+
                  |           CareerOS Core           |
                  +-----------------------------------+
                                    |
     +-----------+-----------+------+------+-----------+-----------+
     |           |           |             |           |           |
+----+----+ +----+----+ +----+----+   +----+----+ +----+----+ +----+----+
| Resume  | |   ATS   | | Interview|  |   Job   | |Recruiter| |Analytics|
| Plugin  | | Plugin  | |  Plugin  |  |Discovery| | Plugin  | | Plugin  |
+---------+ +---------+ +----------+  +---------+ +---------+ +---------+
```

---

## 2. Plugin Interfaces & Hooks Definition
*   **CareerOS Core API:** Exposes routing tables, database connection pools, audit log triggers, and LiteLLM AI Gateway connectors.
*   **Plugin Hooks:** Each plugin implements standard lifecycle hooks:
    *   `register_plugin()`: Binds FastAPI routers, repositories, and custom tables.
    *   `initialize_plugin()`: Sets up dependency injection resolvers.
    *   `teardown_plugin()`: Safely releases resources.
*   **Decoupled Database Schemas:** Each plugin owns its database tables (e.g. `ats_reports` table is created and managed inside the ATS Plugin using prefix prefixes, avoiding collisions in core migrations).
