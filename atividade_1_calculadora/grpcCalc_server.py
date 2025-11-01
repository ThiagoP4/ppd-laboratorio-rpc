import grpc
import time
from concurrent import futures
import grpcCalc_pb2
import grpcCalc_pb2_grpc


class CalculatorServicer(grpcCalc_pb2_grpc.apiServicer):
    def add(self, request, context):
        print(f"Requisião de adição recebida: {request.numOne} + {request.numTwo}")
        resultado = request.numOne + request.numTwo
        return grpcCalc_pb2.result(num=resultado)
    
    def sub(self, request, context):
        print(f"Requisição de subtração recebida: {request.numOne} - {request.numTwo}")
        resultado = request.numOne - request.numTwo
        return grpcCalc_pb2.result(num=resultado)
    
    def mul(self, request, context):
        print(f"Requisição de multiplicação recebida: {request.numOne} * {request.numTwo}")
        resultado = request.numOne * request.numTwo
        return grpcCalc_pb2.result(num=resultado)
    
    def div(self, request, context):
        print(f"Requisição de divisão recebida: {request.numOne} / {request.numTwo}")
        if request.numTwo == 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Divisão por zero não é permitida.")
            return grpcCalc_pb2.result()
        resultado = request.numOne / request.numTwo
        return grpcCalc_pb2.result(num=resultado)
    

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpcCalc_pb2_grpc.add_apiServicer_to_server(CalculatorServicer(), server)
    print("Servidor gRPC iniciado na porta 50051.")
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(86400) # Dorme por um dia
    except KeyboardInterrupt:
        print("Servidor gRPC encerrado.")
        server.stop(0)


if __name__ == '__main__':
    serve()