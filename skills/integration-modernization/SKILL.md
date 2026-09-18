---
name: integration-modernization
description: External Systems, API Endpoints & Third-Party Integration Modernization Playbook. Modernizes REST/SOAP clients, webhooks, external DB connections, and authentication protocols.
version: 1.0.0
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Grep, Find
---

# External Systems & Integration Modernization Skill

## Overview
This skill provides the architectural guidelines, modern client implementation patterns, and security practices for modernizing Drupal 7 external integrations (REST clients, SOAP services, outbound/inbound webhooks, payment gateways, and background queues) into clean, secure Drupal 10 and Drupal 11 services.

---

## Technical References
- [Drupal 10 Architecture Reference](../../references/drupal-10/architecture.md)
- [Drupal 10 & 11 Plugin Types & Modern Architecture](../../references/drupal-10/plugin-types.md)
- [Common Migration & Modernization Patterns](../../references/migration-patterns/common-conversions.md)

---

## Modern Integration Pattern Matrix

| Legacy D7 Integration | Target D10/D11 Modernization | Architectural Implementation | Security & Reliability Standard |
| :--- | :--- | :--- | :--- |
| `drupal_http_request()` | Guzzle `ClientInterface` | Injected service via `@http_client` | Explicit timeout (default 10s); try/catch on `GuzzleException`. |
| Native `curl_*` functions | Injected Guzzle HTTP Service | Abstracted behind custom service interface | Cleanly mockable in PHPUnit unit tests. |
| Native `SoapClient` | Modern Guzzle REST or Symfony SOAP | Encapsulated in isolated integration service | WSDL parsing isolated with graceful fallback on failure. |
| Inbound `hook_menu()` webhook | Route + Controller | `_controller` returning `JsonResponse` | Signature verification (HMAC-SHA256), token validation, rate limiting. |
| Outbound cron sync jobs | `QueueWorker` Plugin | `QueueWorkerBase` plugin processing items | Automatic retries, error logging, non-blocking cron execution. |
| Hardcoded API Keys in code | Environment Variables / Key Module | `getenv()` via `settings.php` or `key.repository` | **Mandatory Rule 10**: Zero credentials stored in code or config. |
| Secondary DB (`$databases`) | External connection in `settings.php` | `Database::getConnection('external_key')` | Parameterized SQL queries; never concatenate user inputs. |

---

## Outbound HTTP Client Pattern (Guzzle Injection)

```php
namespace Drupal\custom_integration\Service;

use GuzzleHttp\ClientInterface;
use GuzzleHttp\Exception\GuzzleException;
use Psr\Log\LoggerInterface;

class PaymentGatewayClient {

  public function __construct(
    protected ClientInterface $httpClient,
    protected LoggerInterface $logger,
    protected string $apiEndpoint,
    protected string $apiKey
  ) {}

  public function sendTransaction(array $payload): ?array {
    try {
      $response = $this->httpClient->request('POST', $this->apiEndpoint . '/transactions', [
        'timeout' => 15.0,
        'headers' => [
          'Authorization' => 'Bearer ' . $this->apiKey,
          'Content-Type' => 'application/json',
          'Accept' => 'application/json',
        ],
        'json' => $payload,
      ]);

      return json_decode($response->getBody()->getContents(), TRUE);
    }
    catch (GuzzleException $e) {
      $this->logger->error('External transaction failed: @message', [
        '@message' => $e->getMessage(),
      ]);
      return NULL;
    }
  }
}
```

---

## Inbound Webhook Pattern (Route + Controller)

### 1. Route Declaration (`custom_integration.routing.yml`)

```yaml
custom_integration.webhook:
  path: '/api/v1/webhooks/incoming'
  defaults:
    _controller: '\Drupal\custom_integration\Controller\WebhookController::handle'
  methods: [POST]
  requirements:
    _access: 'TRUE' # Custom access or header verification inside controller
```

### 2. Controller Handling

```php
namespace Drupal\custom_integration\Controller;

use Drupal\Core\Controller\ControllerBase;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;

class WebhookController extends ControllerBase {

  public function handle(Request $request): JsonResponse {
    $signature = $request->headers->get('X-Hub-Signature-256');
    $content = $request->getContent();

    // Verify HMAC signature against configured secret
    if (!$this->verifySignature($content, $signature)) {
      return new JsonResponse(['error' => 'Invalid signature'], Response::HTTP_UNAUTHORIZED);
    }

    $data = json_decode($content, TRUE);
    // Dispatch item to background queue for resilient processing
    \Drupal::queue('custom_external_sync_queue')->createItem($data);

    return new JsonResponse(['status' => 'received'], Response::HTTP_ACCEPTED);
  }

  protected function verifySignature(string $content, ?string $signature): bool {
    if (empty($signature)) {
      return FALSE;
    }
    $secret = getenv('WEBHOOK_SECRET') ?: '';
    $expected = 'sha256=' . hash_hmac('sha256', $content, $secret);
    return hash_equals($expected, $signature);
  }
}
```
