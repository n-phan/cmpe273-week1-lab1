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


class HealthServicer(echo_pb2_grpc.HealthServiceServicer):
    def Check(self, request, context):
        return echo_pb2.HealthResponse(status="ok")


class EchoServicer(echo_pb2_grpc.EchoServiceServicer):
    def Echo(self, request, context):
        start = time.time()
        msg = request.msg
        response = echo_pb2.EchoResponse(echo=msg)
        latency_ms = int((time.time() - start) * 1000)
        logging.info(f'service=A endpoint=/echo status=ok latency_ms={latency_ms}')
        return response


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    echo_pb2_grpc.add_HealthServiceServicer_to_server(HealthServicer(), server)
    echo_pb2_grpc.add_EchoServiceServicer_to_server(EchoServicer(), server)
    server.add_insecure_port('[::]:8080')
    server.start()
    logging.info("service=A gRPC server listening on port 8080")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
