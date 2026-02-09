# SCAC — PocketBase Collection Hand-off

**Purpose**: Instructions for creating the SCAC persistence layer.
**Recipient**: PocketBase Admin Agent

---

## 1. Collection: `scac_access_logs`
*Stores granular intercepted events for trajectory reconstruction.*

| Field Name | Type | Options |
| :--- | :--- | :--- |
| `actor_id` | Plain text | Required |
| `action` | Plain text | Required (e.g., 'login', 'read', 'exec') |
| `resource` | Plain text | Required (e.g., 'file_path', 'db_record') |
| `context` | JSON | Optional (IP, user-agent, permissions) |
| `trajectory_id` | Relation | Collection: `scac_trajectories` |

**API Rules**:
*   Admin only (or specific `scac_service` user)

---

## 2. Collection: `scac_trajectories`
*Groups related logs into a single behavioral path.*

| Field Name | Type | Options |
| :--- | :--- | :--- |
| `actor_id` | Plain text | Required |
| `is_active` | Bool | Default: `true` |
| `summary` | Plain text | Optional (Filled by LLM later) |
| `last_event` | Date | Auto-update on sub-log creation |

---

## 3. Collection: `scac_incidents`
*Flags high-threat events and stores cognitive reasoning.*

| Field Name | Type | Options |
| :--- | :--- | :--- |
| `trajectory` | Relation | Collection: `scac_trajectories` (Required) |
| `actor_id` | Plain text | Required |
| `intent_type` | Select | 'BENIGN', 'SUSPICIOUS', 'ADVERSARIAL' |
| `threat_level` | Number | Min: 0, Max: 5 |
| `reasoning` | Plain text | Required (LLM output) |
| `suggested_action` | Plain text | Optional |

---

## 4. Collection: `scac_actor_profiles`
*Long-term behavioral memory for specific actors.*

| Field Name | Type | Options |
| :--- | :--- | :--- |
| `actor_id` | Plain text | Required, Unique |
| `incident_count` | Number | Default: 0 |
| `avg_threat_level` | Number | Default: 0 |
| `behavioral_signature` | JSON | Optional (Vector summary or pattern bits) |
| `status` | Select | 'CLEAN', 'WATCHLIST', 'BLOCKED' |

---

## 5. Collection: `scac_global_signatures`
*Cross-node shared intelligence for adversarial actors.*

| Field Name | Type | Options |
| :--- | :--- | :--- |
| `actor_id` | Plain text | Required, Unique |
| `confidence_score` | Number | Min: 0, Max: 1 |
| `origin_node` | Plain text | Required (e.g., 'node-alpha') |
| `signature_type` | Select | 'BEHAVIOR', 'IP', 'UA' |
| `reason` | Plain text | Optional |
| `last_seen` | Date | Required |
