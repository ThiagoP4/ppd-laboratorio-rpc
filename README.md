# PPD - Laboratório II: Chamada de Procedimento Remoto (RPC)

**Programação Distribuida e Paralela 2025/2**

**Professor:** Breno Krohling

## Integrantes do Grupo

- Thiago D'Angellis Santana Silva - 2214222

## 1. Configuração do Ambiente

Este projeto foi desenvolvido utilizando Python 3 e gRPC em um ambiente WSL (Ubuntu)

Para configurar o ambiente e instalar todas as dependências necessárias, execute os seguintes comandos:

1.  **Instalar o módulo `venv` do Python (caso não exista):**

    ```bash
    sudo apt update
    sudo apt install python3.12-venv
    ```

2.  **Criar e ativar o ambiente virtual:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instalar as bibliotecas (grpc, pybreaker, etc):**
    ```bash
    pip install -r requirements.txt
    ```

## 2. Instruções de Execução

### Atividade 1: Calculadora gRPC (30%)

Para executar a calculadora, é necessário abrir dois terminais:

1.  **Terminal 1: Iniciar o Servidor**
    Na pasta do projeto, execute:

    ```bash
    python3 atividade_1_calculadora/grpcCalc_server.py
    ```

    O servidor será iniciado e ficará aguardando conexões na porta 50051.

2.  **Terminal 2: Iniciar o Cliente**
    Em um novo terminal (com o `venv` ativado), execute:
    ```bash
    python3 atividade_1_calculadora/grpcCalc_client.py
    ```
    Um menu interativo aparecerá, permitindo ao usuário escolher a operação (Soma, Subtração, Multiplicação, Divisão) e inserir os operandos.

### Metodologia de Implementação

A Atividade 1 foi implementada usando o framework **Python/gRPC**. 
A arquitetura segue o modelo Cliente/Servidor, onde o servidor expõe remotamente as funcionalidades de uma calculadora.

1.  **Interface (`.proto`):** Primeiramente, foi definido um "contrato" de serviço usando a linguagem Protobuf (no arquivo `grpcCalc.proto`). Este contrato define as quatro RPCs (Soma, Subtração, Multiplicação, Divisão) e as estruturas das mensagens de requisição (contendo dois números `double`) e resposta (contendo um número `double`).

2.  **Geração de Stubs:** A partir do arquivo `.proto`, os stubs de cliente e servidor foram gerados automaticamente usando a ferramenta `python -m grpc_tools.protoc`.

3.  **Implementação do Servidor:** O servidor (`grpcCalc_server.py`) implementa a lógica de negócio para as quatro operações definidas na interface. Ele é multi-thread (usando `futures.ThreadPoolExecutor`) e trata especificamente o caso de **divisão por zero**, retornando um código de erro `INVALID_ARGUMENT` ao cliente, conforme a especificação do gRPC.

4.  **Implementação do Cliente:** O cliente (`grpcCalc_client.py`) é um programa de console interativo. Ele apresenta um menu de loop ao usuário. Com base na escolha, ele coleta os operandos, monta a mensagem de requisição e chama a função RPC correspondente no servidor. Ele também foi programado para capturar e exibir erros vindos do servidor (como a divisão por zero).

### Testes e Resultados

Foram realizados testes manuais para validar todas as funcionalidades:

- **Soma, Subtração e Multiplicação:** Testadas com números inteiros, decimais e negativos. Todas as operações retornaram os resultados matematicamente corretos.
- **Divisão:** Testada com sucesso.
- **Teste de Divisão por Zero:** Ao tentar dividir um número por zero (ex: `10 / 0`), o servidor corretamente identificou a exceção, não travou e retornou uma mensagem de erro clara ao cliente (`Erro do servidor: Não é possível dividir por zero.`), conforme esperado.
- **Teste de Usabilidade:** O menu interativo se mostrou funcional, permitindo múltiplas operações em sequência sem a necessidade de reiniciar o cliente.
