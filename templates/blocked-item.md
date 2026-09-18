---
ticket_id: "BLOCKED-{{ COMPONENT }}-{{ NUM }}"
severity: "{{ SEVERITY }}" # LOW | MEDIUM | HIGH | CRITICAL | GLOBAL
type: "{{ TYPE }}" # COMPONENT | GLOBAL
component: "{{ COMPONENT }}"
agent: "{{ AGENT }}"
created_at: "{{ TIMESTAMP }}"
status: "ACTIVE"
affected_dependents: []
---

# Blocked Migration Item: {{ TICKET_ID }}

## 1. Executive Summary
- **Component**: `{{ COMPONENT }}`
- **Severity**: `{{ SEVERITY }}`
- **Source File**: `{{ SOURCE_FILE }}`
- **Target File**: `{{ TARGET_FILE }}`

---

## 2. Description of Impasse
- **Issue**:
- **Environmental Context**: [OBSERVED FACT]

---

## 3. Attempted Solutions & Failure Analysis
1. **Attempt 1**:
   - Approach:
   - Result / Error:
2. **Attempt 2**:
   - Approach:
   - Result / Error:

---

## 4. Impact Assessment
- **Component Impact**:
- **Downstream Dependent Modules Blocked**:
- **Can Other Migration Work Continue?**: YES / NO

---

## 5. Required Human Action / Information Needed
- **Action Required by Human Developer**:
- **Recommended Remediation Strategy**:
