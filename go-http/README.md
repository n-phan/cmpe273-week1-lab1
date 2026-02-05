# Go HTTP Track

## How to Run Locally

### Terminal 1 - Start Service A (port 8080)
```bash
cd service-a
go mod init service-a
go run .
```

### Terminal 2 - Start Service B (port 8081)
```bash
cd service-b
go mod init service-b
go run .
```

## Test Commands

```bash
# Test the full flow (Service B calls Service A)
curl "http://127.0.0.1:8081/call-echo?msg=hello"

# Test individual endpoints
curl "http://127.0.0.1:8080/health"        # Service A health
curl "http://127.0.0.1:8080/echo?msg=test" # Service A echo
curl "http://127.0.0.1:8081/health"        # Service B health
```

## Success Proof

When both services are running:

```bash
$ curl "http://127.0.0.1:8081/call-echo?msg=hello"
{"service_a":{"echo":"hello"},"service_b":"ok"}
```

**Service A Log:**
```
2026/02/04 09:51:57 service=A endpoint=/echo status=ok latency_ms=0
```

**Service B Log:**
```
2026/02/04 09:51:57 service=B endpoint=/call-echo status=ok latency_ms=5
```

## Failure Proof (Independent Failure)

When Service A is stopped (Ctrl+C) and Service B is still running:

```bash
$ curl "http://127.0.0.1:8081/call-echo?msg=hello"
{"error":"Get \"http://127.0.0.1:8080/echo?msg=hello\": dial tcp 127.0.0.1:8080: connect: connection refused","service_a":"unavailable","service_b":"ok"}
```

**HTTP Status:** 503 (Service Unavailable)

**Service B Log:**
```
service=B endpoint=/call-echo status=error error="dial tcp 127.0.0.1:8080: connect: connection refused" latency_ms=1
```

## What Makes This Distributed?

This system is distributed because it consists of **two independent processes** that communicate over the network via HTTP. Each service runs in its own process, has its own memory space, and can fail independently. Service A and Service B don't share state directly—they exchange data through network requests. This demonstrates key distributed system properties: **network communication** (HTTP requests between services), **independent failure** (Service A can crash without taking down Service B), and **loose coupling** (services only know each other's API contracts, not internal implementation). When Service A fails, Service B gracefully handles the error and returns a meaningful response (503) rather than crashing itself, showing fault tolerance at the application level.
