# Python gRPC Track

This is an alternative implementation using **gRPC** instead of HTTP for inter-service communication.

## Architecture

```
┌─────────────────┐        gRPC Call          ┌─────────────────┐
│    Service B    │ ─────────────────────────▶│    Service A    │
│   (port 8081)   │                           │   (port 8080)   │
│                 │◀───────────────────────── │                 │
│  CallEchoService│      EchoResponse         │   EchoService   │
└─────────────────┘                           └─────────────────┘
        ▲
        │ gRPC request
        │
   [Test Client]
```

## Setup (One-time)

First, generate the Python code from the proto file:

```bash
cd python-grpc

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install grpcio grpcio-tools protobuf

# Generate Python code from proto
python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. ./protos/echo.proto
```

This generates `echo_pb2.py` and `echo_pb2_grpc.py` in the python-grpc directory.

## Run Service A (Terminal 1)

```bash
cd python-grpc
source .venv/bin/activate
cd service-a
python app.py
```

## Run Service B (Terminal 2)

```bash
cd python-grpc
source .venv/bin/activate
cd service-b
python app.py
```

## Test with the Test Client (Terminal 3)

```bash
cd python-grpc
source .venv/bin/activate

# Test the full flow (Service B calls Service A)
python test_client.py call-echo hello

# Test individual services
python test_client.py health-a      # Service A health
python test_client.py health-b      # Service B health
python test_client.py echo test     # Service A echo directly
```

## Success Proof

When both services are running:

```bash
$ python test_client.py call-echo hello
{"service_b": "ok", "service_a": {"echo": "hello"}}
```

**Service A Log:**
```
2026-02-04 10:00:00,000 service=A endpoint=/echo status=ok latency_ms=0
```

**Service B Log:**
```
2026-02-04 10:00:00,000 service=B endpoint=/call-echo status=ok latency_ms=5
```

**Success Screenshot:**

<img width="1278" height="724" alt="image" src="https://github.com/user-attachments/assets/a688b90a-d8a8-4796-8fcc-49c24ad01fc4" />

## Failure Proof (Independent Failure)

When Service A is stopped (Ctrl+C) and Service B is still running:

```bash
$ python test_client.py call-echo hello
{"service_b": "ok", "service_a": "unavailable", "error": "StatusCode.UNAVAILABLE: failed to connect to all addresses"}
```

**gRPC Status:** UNAVAILABLE (equivalent to HTTP 503)

**Service B Log:**
```
service=B endpoint=/call-echo status=error error="StatusCode.UNAVAILABLE: failed to connect..." latency_ms=1
```

**Failure Screenshots:**

<img width="2142" height="748" alt="image" src="https://github.com/user-attachments/assets/938bafb3-5124-4db7-acb5-c73687c8e524" />

## Key Differences from HTTP Track

| Aspect | HTTP | gRPC |
|--------|------|------|
| Protocol | HTTP/1.1 + JSON | HTTP/2 + Protocol Buffers |
| Contract | Implicit (URL patterns) | Explicit (`.proto` file) |
| Serialization | JSON (text) | Protobuf (binary, smaller) |
| Code Generation | None | Auto-generated stubs |
| Streaming | Limited | Built-in support |
| Testing | `curl` | Custom client needed |

## What Makes This Distributed?

This system is distributed because it consists of **two independent processes** that communicate over the network via gRPC (which runs over HTTP/2). Each service runs in its own process, has its own memory space, and can fail independently. Service A and Service B don't share state directly—they exchange data through network RPC calls defined by a shared protocol buffer contract. This demonstrates key distributed system properties: **network communication** (gRPC calls between services), **independent failure** (Service A can crash without taking down Service B), **strong contracts** (the `.proto` file defines the exact interface), and **loose coupling** (services only know each other's gRPC interface). When Service A fails, Service B gracefully handles the error and returns a meaningful gRPC status (UNAVAILABLE) rather than crashing itself, showing fault tolerance at the application level.

## Proto File Reference

The service contract is defined in `protos/echo.proto`:

- **HealthService**: `Check()` → returns status
- **EchoService** (Service A): `Echo(msg)` → returns echoed message
- **CallEchoService** (Service B): `CallEcho(msg)` → calls Service A and returns combined response
