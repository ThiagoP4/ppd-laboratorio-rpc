import grpc

import grpcCalc_pb2
import grpcCalc_pb2_grpc

def print_menu():
    print("Selecione a operação:")
    print("1. Adição")
    print("2. Subtração")
    print("3. Multiplicação")
    print("4. Divisão")
    print("5. Sair")
    return input("Digite sua escolha (1/2/3/4/5): ")


def get_numbers():
    while True:
        try:
            x = float(input("Digite o primeiro número: "))
            y = float(input("Digite o segundo número: "))
            return x, y
        except ValueError:
            print("Entrada inválida. Por favor, digite números válidos.")


def run_client():
    with grpc.insecure_channel('Localhost:50051') as channel:
        # Cria o Stub cliente
        stub = grpcCalc_pb2_grpc.apiStub(channel)

        while True:
            choice = print_menu()

            if choice == '5':
                print("Encerrando o cliente.")
                break

            if choice not in ['1', '2', '3', '4']:
                print("Escolha inválida. Tente novamente.")
                continue
            
            x, y = get_numbers()   

            args_request = grpcCalc_pb2.args(numOne=x, numTwo=y)

            try:
                if choice == '1':
                    response = stub.add(args_request)
                    print(f"Resultado: {x} + {y} = {response.num}")
                elif choice == '2':
                    response = stub.sub(args_request)
                    print(f"Resultado: {x} - {y} = {response.num}")
                elif choice == '3':
                    response = stub.mul(args_request)
                    print(f"Resultado: {x} * {y} = {response.num}")
                elif choice == '4':
                    response = stub.div(args_request)
                    print(f"Resultado: {x} / {y} = {response.num}")
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                    print(f"Erro: {e.details()}")
                else:
                    print(f"Erro inesperado: {e}")
     
if __name__ == '__main__':
    run_client()
        