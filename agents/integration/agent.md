# Agent Specification: Integration Agent

## 1. Identity & Scope
- **Agent Name**: `integration`
- **Role**: External Systems, API Endpoints, and Third-Party Integrations Specialist.
- **Scope**: Discovers, analyzes, and modernizes all external communication boundaries in the Drupal 7 project: REST clients, SOAP services, outbound/inbound webhooks, payment gateways, external SQL/NoSQL databases, CRM integrations, and SSO/OAuth authentication protocols.

---

## 2. Handoff Contract

### Preconditions
- Third-party integration points identified during Discovery in `state/migration-manifest.yml`.
- Target custom module scaffold exists.
- Target path verified and writable.

### Inputs
- Source D7 integration code (cURL, `drupal_http_request()`, SOAP client, custom DB connections)
- API endpoint specifications or documentation if available
- `templates/migration-plan.md`

### Outputs
- Integration Modernization Plan: `reports/integrations/PLAN-INTEGRATION-<SYSTEM>.md`
- Modernized integration services using Guzzle HTTP client or typed plugins in `target.path`
- Security and credentials handling plan (referencing environment variables, never hardcoded secrets)
- Implementation Report: `reports/integrations/REPORT-INTEGRATION-<SYSTEM>.md`
- Manifest updates for integrations

### Postconditions
- All HTTP calls utilize injected Guzzle `ClientInterface`.
- All authentication secrets use environment variables or Key module integrations; zero hardcoded secrets.
- Inbound webhooks use Symfony `Route` and `ControllerBase` with explicit request validation and CSRF protection.
- Outbound calls include appropriate timeout handling, retries, and error logging.
- Zero writes to `source.path`.

### Failure & Blocked Conditions
- Proprietary SOAP/RPC service with deprecated/unsupported WSDL library -> Raise `BLOCKED-INTEGRATION-SOAP-<SYSTEM>.md`.
- Undocumented external authentication token mechanism -> Raise `BLOCKED-INTEGRATION-AUTH-<SYSTEM>.md`.

---

## 3. Integration Patterns Modernization

| D7 Integration Pattern | D10 Modern Equivalent | Security & Reliability Standard |
|---|---|---|
| `drupal_http_request()` | Guzzle `ClientInterface` | Timeout (default 10s), try/catch on `GuzzleException` |
| Native PHP `curl_*` functions | Injected Guzzle HTTP Service | Abstracted behind interface for mock unit testing |
| Native `SoapClient` | Modern Symfony SOAP or modern Guzzle REST | Encapsulated in isolated integration service |
| Inbound `hook_menu()` webhook | Route + Controller with JSON response | Token validation, signature verification, rate limiting |
| Hardcoded API Keys in code/variable | `settings.php` / Environment variables / Key module | Mandatory Rule 10: Never commit credentials |
| Secondary DB connection (`$databases`) | External connection defined in `settings.php` | Accessed via `Database::getConnection('external')` |
| Custom cron sync jobs | Drupal `QueueWorker` plugins | Resilient processing with automatic retry handling |
