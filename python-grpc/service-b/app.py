import grpc
from concurrent import futures
import time
import logging
import sys

# Add parent directory to path for proto imports
sys.path.insert(0, '..')

import echo_pb2
import echo_pb2_grpc

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

SERVICE_A_ADDRESS = "127.0.0.1:8080"
TIMEOUT_SECONDS = 1.0


class HealthServicer(echo_pb2_grpc.HealthServiceServicer):
    def Check(self, request, context):
        return echo_pb2.HealthResponse(status="ok")


class CallEchoServicer(echo_pb2_grpc.CallEchoServiceServicer):
    def CallEcho(self, request, context):
        start = time.time()
        msg = request.msg

        try:
            # Create channel and stub for Service A
            channel = grpc.insecure_channel(SERVICE_A_ADDRESS)
            stub = echo_pb2_grpc.EchoServiceStub(channel)

            # Call Service A with timeout
            echo_request = echo_pb2.EchoRequest(msg=msg)
            echo_response = stub.Echo(echo_request, timeout=TIMEOUT_SECONDS)

            latency_ms = int((time.time() - start) * 1000)
            logging.info(f'service=B endpoint=/call-echo status=ok latency_ms={latency_ms}')

            return echo_pb2.CallEchoResponse(
                service_b="ok",
                service_a_echo=echo_response.echo,
                service_a_status="ok"
            )

        except grpc.RpcError as e:
            latency_ms = int((time.time() - start) * 1000)
            error_msg = f"{e.code()}: {e.details()}"
            logging.info(f'service=B endpoint=/call-echo status=error error="{error_msg}" latency_ms={latency_ms}')

            # Set gRPC status to UNAVAILABLE (equivalent to HTTP 503)
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Service A is unavailable")

            return echo_pb2.CallEchoResponse(
                service_b="ok",
                service_a_status="unavailable",
                error=error_msg
            )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    echo_pb2_grpc.add_HealthServiceServicer_to_server(HealthServicer(), server)
    echo_pb2_grpc.add_CallEchoServiceServicer_to_server(CallEchoServicer(), server)
    server.add_insecure_port('[::]:8081')
    server.start()
    logging.info("service=B gRPC server listening on port 8081")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
