# On-Call Operations & Rotation Playbook

## 1. On-Call Shift Rotation
On-call rotations ensure 24/7 service availability.
*   **Shift Duration:** 7-day cycles (rotating weekly on Monday mornings).
*   **Rotation Schedule:**
    *   *Primary On-Call:* Assigned Infrastructure Developer.
    *   *Secondary Escalate:* Assigned Backend Lead Engineer.

---

## 2. Escalation Process & Responsibilities
When a monitoring tool fires an alert:
1.  **Acknowledge:** Primary on-call must acknowledge target alarms within 15 minutes of trigger.
2.  **Escalate:** If primary cannot mitigate within 30 minutes, alert escalates automatically to secondary lead.
3.  **Communication:** Operations update channel is posted with incident details.
