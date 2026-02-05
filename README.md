# CMPE 273 – Week 1 Lab 1: Your First Distributed System (Starter)

This starter provides three implementation tracks:
- `python-http/` (Flask + requests) — Screenshots provided
- `go-http/` (net/http) — Screenshots provided
- `python-grpc/` (gRPC + Protobuf) — Initial attempt, screenshots provided

Pick **one** track for Week 1.

## Lab Goal
Build **two services** that communicate over the network:
- **Service A** (port 8080): `/health`, `/echo?msg=...`
- **Service B** (port 8081): `/health`, `/call-echo?msg=...` calls Service A

Minimum requirements:
- Two independent processes
- HTTP (or gRPC if you choose stretch)
- Basic logging per request (service name, endpoint, status, latency)
- Timeout handling in Service B
- Demonstrate independent failure (stop A; B returns 503 and logs error)

## Deliverables
1. Repo link
2. README updates:
   - how to run locally
   - success + failure proof (curl output or screenshot)
   - 1 short paragraph: "What makes this distributed?"

## Implementation Status

| Track | Protocol | Screenshots | Status |
|-------|----------|-------------|--------|
| `python-http/` | HTTP + JSON | Provided | Complete |
| `go-http/` | HTTP + JSON | Provided | Complete |
| `python-grpc/` | gRPC + Protobuf | Provided | Initial attempt |

See individual track READMEs for detailed instructions and proof of success/failure handling.
Following is short paragraph addressing "What makes this distributed":
This system is distributed because it consists of **two independent processes** that communicate over the network via HTTP. Each service runs in its own process, has its own memory space, and can fail independently. Service A and Service B don't share state directly—they exchange data through network requests. This demonstrates key distributed system properties: **network communication** (HTTP requests between services), **independent failure** (Service A can crash without taking down Service B), and **loose coupling** (services only know each other's API contracts, not internal implementation). When Service A fails, Service B gracefully handles the error and returns a meaningful response (503) rather than crashing itself, showing fault tolerance at the application level.

