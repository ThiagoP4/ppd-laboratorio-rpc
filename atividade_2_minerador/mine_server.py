import grpc
import time
import hashlib
import random
import threading
from concurrent import futures

# Importe dos stubs gerados pelo gRPC
import mine_grpc_pb2
import mine_grpc_pb2_grpc

# -- Estado Global do Servidor --
g_transaction_table = []
g_table_lock = threading.Lock()
g_current_transaction_id = 0
# -------------------------------

def _generate_new_challenge():
    """Função auxiliar para criar um novo desafio de mineração."""
    global g_current_transaction_id

    new_challenge = random.randint(4, 5)

    new_transaction = {
        "id": g_current_transaction_id,
        "challenge": new_challenge,
        "solution": None,
        "winner": -1 # Nenhum vencedor inicialmente
    }

    g_transaction_table.append(new_transaction)
    print(f"[Servidor] Novo desafio criado: ID {g_current_transaction_id}, Desafio {new_challenge}")
    g_current_transaction_id += 1


def _validate_solution(challenge, solution):
    """Verifica se a solução fornecida é válida para o desafio."""

    if not solution:
        return False
    
    # Calcula o hash SHA-1 da solução
    hash_hex = hashlib.sha1(solution.encode()).hexdigest()
    target_prefix = '0' * challenge

    return hash_hex.startswith(target_prefix)

class MineService(mine_grpc_pb2_grpc.apiServicer):

    def getTransactionId(self, request, context):
        """Retorna a transação com desafio pendente."""
        with g_table_lock:
            current_id = g_transaction_table[-1]['id']
        return mine_grpc_pb2.intResult(result=current_id)
    
    def getChallenge(self, request, context):
        """Retorna o desafio associado a uma transação específica."""
        trans_id = request.transactionId
        
        with g_table_lock:
            for t in g_transaction_table:
                if t['id'] == trans_id:
                    return mine_grpc_pb2.intResult(result=t['challenge'])
                
        return mine_grpc_pb2.intResult(result=-1)  # Transação não encontrada
    
    def getTransactionStatus(self, request, context):
        """Retorna 1 se pendente, 0 se resolvido, -1 se inválido."""
        trans_id = request.transactionId

        with g_table_lock:
            for t in g_transaction_table:
                if t['id'] == trans_id:
                    if t['winner'] == -1:
                        return mine_grpc_pb2.intResult(result=1) # Pendente
                    else:
                        return mine_grpc_pb2.intResult(result=0) # Resolvido

        return mine_grpc_pb2.intResult(result=-1) # Inválido
    

    def submitChallenge(self, request, context):
        """Submete uma solução para um desafio específico."""
        trans_id = request.transactionId
        client_id = request.clientId
        solution = request.solution
        
        with g_table_lock:
            transaction = None
            for t in g_transaction_table:
                if t['id'] == trans_id:
                    transaction = t
                    break
            if transaction is None:
                return mine_grpc_pb2.intResult(result=-1)  # Transação inválida
            if transaction['winner'] != -1:
                print(f"[Servidor] Solução recebida para ID={trans_id}, mas já foi resolvido.")
                return mine_grpc_pb2.intResult(result=2)  # Já resolvido
            
            is_valid = _validate_solution(transaction['challenge'], solution)
            if is_valid:
                transaction['solution'] = solution
                transaction['winner'] = client_id
                print(f"[Servidor] Solução válida recebida para ID={trans_id} do Cliente {client_id}.")
                _generate_new_challenge()
                return mine_grpc_pb2.intResult(result=1)  # Solução válida
            else:
                print(f"[Servidor] Solução inválida recebida para ID={trans_id} do Cliente {client_id}.")
                return mine_grpc_pb2.intResult(result=0)  # Solução inválida
            
    def getSolution(self, request, context):
        """Retorna o status, solução e desafio """
        trans_id = request.transactionId

        with g_table_lock:
            for t in g_transaction_table:
                if t['id'] == trans_id:
                    status = 0 if t['winner'] != -1 else 1 # 0=resolvido, 1=pendente
                    solution_str = t['solution'] if t['solution'] else ""
                    challenge_val = t['challenge']

                    return mine_grpc_pb2.structResult(
                        status=status,
                        solution=solution_str,
                        challenge=challenge_val
                    )

        # Se não encontrou, retorna dados "vazios" ou de erro
        return mine_grpc_pb2.structResult(status=-1, solution="", challenge=-1)
    
    def getWinner(self, request, context):
        """Retorna o ID do vencedor de uma transação"""
        trans_id = request.transactionId
        
        with g_table_lock:
            for t in g_transaction_table:
                if t['id'] == trans_id:
                    # Encontrou a transação
                    if t['winner'] != -1:
                        # Se já tem vencedor, retorna o ID dele
                        return mine_grpc_pb2.intResult(result=t['winner'])
                    else:
                        # Se não tem vencedor, retorna 0
                        return mine_grpc_pb2.intResult(result=0)
            
            # Se a transação não existe, retorna -1
            return mine_grpc_pb2.intResult(result=-1)
    
def serve():
    _generate_new_challenge()  # Gera o primeiro desafio
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mine_grpc_pb2_grpc.add_apiServicer_to_server(MineService(), server)
    server.add_insecure_port('[::]:8081')
    server.start()
    print("[Servidor] Servidor de mineração iniciado na porta 8081.")
    try:
        while True:
            time.sleep(86400)  # Mantém o servidor rodando
    except KeyboardInterrupt:
        server.stop(0)
        print("[Servidor] Servidor de mineração encerrado.")

if __name__ == '__main__':
    serve()