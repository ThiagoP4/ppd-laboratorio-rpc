import grpc
import time
import hashlib
import random
import threading
import sys
import os

# importe dos stubs gerados pelo gRPC
import mine_grpc_pb2
import mine_grpc_pb2_grpc

# um ID aleatório para o cliente
MY_CLIENT_ID = random.randint(1000, 9999)

# --- Funções de Mineração (Multi_thread) ---
# Evento global para as threads
g_solution_found_event = threading.Event()
g_found_solution = None # Armazena a solução encontrada

def _miner_thread_worker(challenge_zeros, transaction_id):
    """Função que cada thread de mineração irá executar."""
    global g_found_solution

    target_prefix = '0' * challenge_zeros

    print(f"[Thread {threading.current_thread().name}] Iniciando mineração para transação {transaction_id} com desafio {target_prefix}.")

    nonce = 0 # Um nonce para variar a solução
    
    while not g_solution_found_event.is_set():
        solution_attempt = f"{transaction_id}:{nonce}:{MY_CLIENT_ID}"
        hash_hex = hashlib.sha1(solution_attempt.encode()).hexdigest()

        if hash_hex.startswith(target_prefix):
            print(f"\n[Thread {threading.current_thread().name}] SOLUÇÃO ENCONTRADA: {solution_attempt}\n")
            g_found_solution = solution_attempt
            g_solution_found_event.set()
            return # Encerra esta thread

        nonce += 1

        # time.sleep(0.0001) # Comentado para usar 100% da CPU

        if nonce % 1000000 == 0:
            print(f"[Thread {threading.current_thread().name}] {nonce} tentativas...")

def run_mine(stub):
    """Implementa o passo-a-passo do cliente minerador."""
    global g_solution_found_event
    global g_found_solution

    print("\nBuscando novo trabalho do servidor...")
    try:
        response = stub.getTransactionId(mine_grpc_pb2.void())
        current_trans_id = response.result

        req_challenge = mine_grpc_pb2.transactionId(transactionId=current_trans_id)
        response = stub.getChallenge(req_challenge)
        challenge_level = response.result

        if challenge_level == -1:
            print("Transação inválida. Encerrando.")
            return
        print(f"Desafio recebido: Encontrar um hash SHA-1 começando com {challenge_level} zeros.")

        g_solution_found_event.clear()
        g_found_solution = None

        num_threads = 4  # Número de threads de mineração
        threads = [] 
        for i in range(num_threads):
            t = threading.Thread(
                target=_miner_thread_worker, 
                args=(challenge_level, current_trans_id),
                name=f"Worker-{i+1}"
            )
            threads.append(t)
            t.start()
        
        g_solution_found_event.wait()  # Espera até que uma solução seja encontrada
        for t in threads:
            t.join()  # Aguarda todas as threads terminarem

        print(f"Mineração concluída, solução encontrada: {g_found_solution}")
        print("Enviando solução ao servidor para validação...")
        
        req_submit = mine_grpc_pb2.challengeArgs(
            transactionId=current_trans_id,
            clientId=MY_CLIENT_ID,
            solution=g_found_solution
        )
        response = stub.submitChallenge(req_submit)
        
        result_code = response.result
        if result_code == 1:
            print(">>> SUCESSO! O servidor aceitou sua solução! Você venceu esta rodada!")
        elif result_code == 0:
            print(">>> FALHA. O servidor disse que sua solution é inválida.")
        elif result_code == 2:
            print(">>> QUE PENA! O servidor disse que outro minerador resolveu este desafio primeiro.")
        elif result_code == -1:
            print(">>> ERRO. O servidor disse que o TransactionID é inválido.")

    except grpc.RpcError as e:
        print(f"Erro de RPC ao tentar minerar: {e.details()}")
    
    # Adiciona uma pausa para o usuário ler o resultado
    input("\nPressione ENTER para continuar...")


# --- Funções do Menu Principal ---

def clear_screen():
    """Limpa a tela do terminal (funciona em Windows 'cls' e Linux/Mac 'clear')."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu():
    """Imprime o menu de opções."""
    clear_screen()
    

    print(f"--- Cliente Minerador RPC (ID: {MY_CLIENT_ID}) ---")
    print("Escolha uma opção:")
    print("1. getTransactionId (Ver transação atual)")
    print("2. getChallenge (Ver desafio de uma transação)")
    print("3. getTransactionStatus (Ver status de uma transação)")
    print("4. getWinner (Ver vencedor de uma transação)")
    print("5. getSolution (Ver solução de uma transação)")
    print("6. Mine (Tentar minerar a transação atual)")
    print("7. Sair")
    return input("Digite sua escolha (1-7): ")


def get_transaction_id_input():
    """Solicita ao usuário o ID da transação."""
    try:
        return int(input("Digite o TransactionID: "))
    except ValueError:
        print("ID inválido. Deve ser um número inteiro.")
        return -1
    
def run_client():
    """Função principal do cliente minerador."""
    with grpc.insecure_channel('localhost:8081') as channel:
        stub = mine_grpc_pb2_grpc.apiStub(channel)

        while True:
            choice = print_menu()

            try:
                if choice == '1': # getTransactionId
                    response = stub.getTransactionId(mine_grpc_pb2.void())
                    print(f"\nID da transação atual (pendente): {response.result}")

                elif choice == '2': # getChallenge
                    trans_id = get_transaction_id_input()
                    if trans_id != -1:
                        req = mine_grpc_pb2.transactionId(transactionId=trans_id)
                        response = stub.getChallenge(req)
                        print(f"\nDesafio: {response.result}")

                elif choice == '3': # getTransactionStatus
                    trans_id = get_transaction_id_input()
                    if trans_id != -1:
                        req = mine_grpc_pb2.transactionId(transactionId=trans_id)
                        response = stub.getTransactionStatus(req)
                        if response.result == 1:
                            print("\nStatus: 1 (Pendente)")
                        elif response.result == 0:
                            print("\nStatus: 0 (Resolvido)")
                        else:
                            print("\nStatus: -1 (Inválido)")

                elif choice == '4': # getWinner
                    trans_id = get_transaction_id_input()
                    if trans_id != -1:
                        req = mine_grpc_pb2.transactionId(transactionId=trans_id)
                        response = stub.getWinner(req)
                        if response.result == 0:
                            print("\nVencedor: 0 (Ainda sem vencedor)")
                        elif response.result == -1:
                            print("\nVencedor: -1 (Transação inválida)")
                        else:
                            print(f"\nVencedor: Cliente ID {response.result}")

                elif choice == '5': # getSolution
                    trans_id = get_transaction_id_input()
                    if trans_id != -1:
                        req = mine_grpc_pb2.transactionId(transactionId=trans_id)
                        response = stub.getSolution(req)
                        print(f"\nStatus: {response.status}")
                        print(f"Solução: '{response.solution}'")
                        print(f"Desafio: {response.challenge}")

                elif choice == '6': # Mine
                    run_mine(stub)
                    # A pausa já está dentro do run_mine()

                elif choice == '7':
                    print("Saindo...")
                    break
                else:
                    print("\nEscolha inválida, tente novamente.")

            except grpc.RpcError as e:
                print(f"\nErro de RPC: O servidor pode estar offline. ({e.details()})")

            # Adiciona uma pausa para o usuário ler a saída antes de limpar a tela
            if choice not in ['6', '7']:
                input("\nPressione ENTER para continuar...")

if __name__ == '__main__':
    run_client()