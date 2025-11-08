# PPD - Laboratório II: Chamada de Procedimento Remoto (RPC)

**Programação Distribuida e Paralela 2025/2**

**Professor:** Breno Krohling

## Integrantes do Grupo

- Thiago D'Angellis Santana Silva - 2214222
- Olivia Buzzo Gaona - 2213372
- Pedro Henrique Araujo da Silva - 2212765

## 1. Configuração do Ambiente

Este projeto foi desenvolvido utilizando Python 3 e gRPC em um ambiente WSL (Ubuntu)

Para configurar o ambiente e instalar todas as dependências necessárias, execute os seguintes comandos:

1. **Acessar a pasta do projeto (via WSL):**
    Para acessar a pasta do projeto (localizada nos "Documentos" do Windows), utilize o comando:
    ```bash
    cd "/mnt/c/SeuCaminho/ppd_lab"
    ```

2.  **Instalar o módulo `venv` do Python (caso não exista):**

    ```bash
    sudo apt update
    sudo apt install python3.12-venv
    ```

3.  **Criar e ativar o ambiente virtual:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

4.  **Instalar as bibliotecas (grpc, pybreaker, etc):**
    ```bash
    pip install -r requirements.txt
    ```

## 2. Instruções de Execução

Para rodar o projeto completo, é necessário executar os **dois servidores** (Calculadora e Minerador) simultaneamente em terminais separados, pois eles operam em portas diferentes.

**IMPORTANTE:** Todos os comandos devem ser executados com o ambiente virtual (`venv`) ativado: `source venv/bin/activate`

### Atividade 1: Calculadora gRPC (30%)

1.  **Terminal 1: Iniciar o Servidor (Calculadora)**
    Na pasta do projeto, execute:

    ```bash
    python3 atividade_1_calculadora/grpcCalc_server.py
    ```

    O servidor será iniciado e ficará aguardando conexões na porta 50051.

2.  **Terminal 2: Iniciar o Cliente**
    Em um novo terminal WSL (com o `venv` ativado), execute:
    ```bash
    python3 atividade_1_calculadora/grpcCalc_client.py
    ```
    O cliente exibe um menu interativo permitindo realizar:
-	Soma
-	Subtração
-	Multiplicação
-	Divisão (com tratamento de divisão por zero)


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

### Atividade 2: Minerador de Criptomoedas gRPC (70%)

1.  **Terminal 3: Iniciar o Servidor (Minerador)**
    Na pasta `ppd_lab`, execute:
    ```bash
    python3 atividade_2_minerador/mine_server.py
    ```
    O servidor será iniciado na porta **8081** (para não conflitar com a Atividade 1).

2.  **Terminal 4: Iniciar o Cliente (Minerador)**
    Em um *novo terminal WSL* (com `venv` ativado), execute:
    ```bash
    python3 atividade_2_minerador/mine_client.py
    ```
    O cliente possui 6 funcionalidades, incluindo:
-	Consultar ID da transação
-	Consultar desafio
-	Verificar status
-	Consultar vencedor
-	Consultar solução
-	Minerar (com múltiplas threads)

3.  **Teste de Competição (Opcional):**
    Para simular a "corrida" da mineração, você pode abrir um *quinto terminal* e rodar um segundo `mine_client.py`. Ambos os clientes competirão para resolver o mesmo desafio.

## 3. Relatório Técnico e Metodologia
### 3.1 Atividade 1 (Calculadora)

### Metodologia de Implementação

A Atividade 1 foi implementada usando o framework **Python/gRPC**. A arquitetura segue o modelo Cliente/Servidor. Foi definido um "contrato" `.proto` com quatro RPCs (add, sub, mul, div). O servidor (`grpcCalc_server.py`) implementa a lógica de negócio de forma multi-thread. O cliente (`grpcCalc_client.py`) apresenta um menu interativo com limpeza de tela (`os.system('clear')`) para melhor usabilidade.

* **Testes e Resultados:** Foram realizados testes manuais para as 4 operações. O teste de **divisão por zero** foi validado: o servidor corretamente identifica a exceção, retorna um erro `INVALID_ARGUMENT`, e o cliente exibe a mensagem de erro ao usuário sem travar.

### 3.2 Atividade 2 (Minerador)

* **Metodologia:** A Atividade 2 (protótipo de minerador) foi implementada seguindo a especificação do `mine_grpc.proto`.
    * **Servidor:** O `mine_server.py` gerencia a tabela de transações em memória. Para garantir a integridade dos dados (evitar *race conditions*), o acesso à tabela é controlado por um `threading.Lock`. O servidor valida a Prova de Trabalho (PoW) usando a biblioteca `hashlib` (SHA-1).
    * **Cliente:** O `mine_client.py` implementa o menu de 6 opções. A função "Mine" (Opção 6) é a mais complexa: ela busca o desafio no servidor e, conforme sugerido no PDF, inicia múltiplas threads (`threading.Thread`) para buscar a solução por força bruta localmente, simulando o uso de hardware paralelo. O cliente também possui uma interface limpa com `clear_screen` e pausas para legibilidade.

* **Testes e Resultados:** Todas as 6 funções RPC foram testadas.
    * **Funções de Consulta (1-5):** `getTransactionId`, `getChallenge`, `getStatus`, `getWinner` e `getSolution` foram testadas, retornando os dados corretos da tabela do servidor.
    * **Função "Mine" (Opção 6):** O teste principal foi executado com sucesso. O cliente inicia as 4 threads, encontra uma solução válida (hash com o número correto de zeros), e a submete ao servidor. O servidor valida a solução, retorna `SUCESSO!` e gera a próxima transação (incrementando o ID).
    * **Teste de Competição:** Um teste com dois clientes minerando simultaneamente foi realizado. O primeiro cliente a encontrar a solução venceu a rodada; o segundo cliente, ao submeter sua solução logo depois, recebeu a mensagem "QUE PENA! Outro minerador resolveu este desafio primeiro." (código de retorno `2`).

* **Nota de Implementação (Sobre o Desafio):**
    A especificação do laboratório pedia um *range* de dificuldade de `[1..20]` para o desafio. Para fins de demonstração e para viabilizar a gravação do vídeo de 5 minutos, o *range* no `mine_server.py` foi ajustado para `[4, 5]`. Esta alteração permite comprovar a funcionalidade da Prova de Trabalho (PoW) sem exigir um tempo de espera excessivo para a mineração.


### Estrutura do Repositório
ppd-laboratorio-rpc/

```text
ppd-laboratorio-rpc/
├── atividade_1_calculadora/
│   ├── grpcCalc_server.py
│   ├── grpcCalc_client.py
│   └── grpcCalc.proto
├── atividade_2_minerador/
│   ├── mine_server.py
│   ├── mine_client.py
│   └── mine_grpc.proto
├── requirements.txt
├── VideoAtividade1.mp4
├── VideoAtividade2.mp4
└── README.md
```

### Tecnologias Utilizadas
- Python 3
- gRPC
- Protocol Buffers
- Threading (cliente e servidor)
- Hashlib (SHA-1)
