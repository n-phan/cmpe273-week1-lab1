#!/usr/bin/env python3
"""
Test client for gRPC services.
Usage:
    python test_client.py health-a          # Check Service A health
    python test_client.py health-b          # Check Service B health  
    python test_client.py echo <msg>        # Call Service A echo directly
    python test_client.py call-echo <msg>   # Call Service B (which calls A)
"""

import grpc
import sys

import echo_pb2
import echo_pb2_grpc

SERVICE_A = "127.0.0.1:8080"
SERVICE_B = "127.0.0.1:8081"


def health_check(address, service_name):
    try:
        channel = grpc.insecure_channel(address)
        stub = echo_pb2_grpc.HealthServiceStub(channel)
        response = stub.Check(echo_pb2.HealthRequest(), timeout=1.0)
        print(f"Service {service_name} health: {response.status}")
    except grpc.RpcError as e:
        print(f"Service {service_name} unavailable: {e.code()}")


def echo(msg):
    try:
        channel = grpc.insecure_channel(SERVICE_A)
        stub = echo_pb2_grpc.EchoServiceStub(channel)
        response = stub.Echo(echo_pb2.EchoRequest(msg=msg), timeout=1.0)
        print(f'{{"echo": "{response.echo}"}}')
    except grpc.RpcError as e:
        print(f"Error: {e.code()}: {e.details()}")


def call_echo(msg):
    try:
        channel = grpc.insecure_channel(SERVICE_B)
        stub = echo_pb2_grpc.CallEchoServiceStub(channel)
        response = stub.CallEcho(echo_pb2.CallEchoRequest(msg=msg), timeout=2.0)
        
        if response.service_a_status == "ok":
            print(f'{{"service_b": "{response.service_b}", "service_a": {{"echo": "{response.service_a_echo}"}}}}')
        else:
            print(f'{{"service_b": "{response.service_b}", "service_a": "unavailable", "error": "{response.error}"}}')
    except grpc.RpcError as e:
        # Even on error, try to extract the trailing metadata/response
        print(f'{{"service_b": "ok", "service_a": "unavailable", "grpc_status": "{e.code()}", "error": "{e.details()}"}}')


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "health-a":
        health_check(SERVICE_A, "A")
    elif command == "health-b":
        health_check(SERVICE_B, "B")
    elif command == "echo" and len(sys.argv) >= 3:
        echo(sys.argv[2])
    elif command == "call-echo" and len(sys.argv) >= 3:
        call_echo(sys.argv[2])
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
