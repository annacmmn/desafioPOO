import textwrap
from abc import ABC, abstractmethod
from datetime import datetime


# ===================== MODELOS =====================

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        if valor <= 0:
            print("\n@@@ Valor inválido para saque. @@@")
            return False
        if valor > self._saldo:
            print("\n@@@ Saldo insuficiente. @@@")
            return False

        self._saldo -= valor
        print("\n=== Saque realizado com sucesso! ===")
        return True

    def depositar(self, valor):
        if valor <= 0:
            print("\n@@@ Valor inválido para depósito. @@@")
            return False

        self._saldo += valor
        print("\n=== Depósito realizado com sucesso! ===")
        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        saques_realizados = len([
            t for t in self.historico.transacoes if t["tipo"] == "Saque"
        ])
        if saques_realizados >= self._limite_saques:
            print("\n@@@ Limite de saques excedido. @@@")
            return False
        if valor > self._limite:
            print("\n@@@ Valor excede o limite permitido. @@@")
            return False

        return super().sacar(valor)

    def __str__(self):
        return f"""\
Agência:\t{self.agencia}
C/C:\t\t{self.numero}
Titular:\t{self.cliente.nome}
"""


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        })


class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao(self)


# ===================== FUNÇÕES =====================

def menu():
    opcoes = """\n
=============== MENU ===============
[d] Depositar
[s] Sacar
[e] Extrato
[nc] Nova conta
[lc] Listar contas
[nu] Novo usuário
[q] Sair
=> """
    return input(textwrap.dedent(opcoes))


def validar_cpf(cpf):
    return cpf.isdigit() and len(cpf) == 11


def filtrar_cliente(cpf, clientes):
    return next((c for c in clientes if c.cpf == cpf), None)


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n@@@ Cliente não possui contas. @@@")
        return None

    print("\nContas disponíveis:")
    for i, conta in enumerate(cliente.contas):
        print(f"[{i}] {conta}")

    try:
        indice = int(input("Escolha o número da conta: "))
        return cliente.contas[indice]
    except (ValueError, IndexError):
        print("\n@@@ Seleção inválida. @@@")
        return None


def criar_cliente(clientes):
    cpf = input("CPF (somente números): ")
    if not validar_cpf(cpf):
        print("\n@@@ CPF inválido. @@@")
        return

    if filtrar_cliente(cpf, clientes):
        print("\n@@@ Cliente já cadastrado. @@@")
        return

    nome = input("Nome completo: ")
    nascimento = input("Data de nascimento (dd-mm-aaaa): ")
    endereco = input("Endereço (logradouro, nro - bairro - cidade/UF): ")

    cliente = PessoaFisica(nome, nascimento, cpf, endereco)
    clientes.append(cliente)
    print("\n=== Cliente criado com sucesso! ===")


def criar_conta(numero_conta, clientes, contas):
    cpf = input("CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado. @@@")
        return

    conta = ContaCorrente.nova_conta(cliente, numero_conta)
    contas.append(conta)
    cliente.adicionar_conta(conta)
    print("\n=== Conta criada com sucesso! ===")


def listar_contas(contas):
    for conta in contas:
        print("=" * 50)
        print(conta)


def depositar(clientes):
    cpf = input("CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("\n@@@ Cliente não encontrado. @@@")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    valor = float(input("Valor do depósito: "))
    transacao = Deposito(valor)
    cliente.realizar_transacao(conta, transacao)


def sacar(clientes):
    cpf = input("CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("\n@@@ Cliente não encontrado. @@@")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    valor = float(input("Valor do saque: "))
    transacao = Saque(valor)
    cliente.realizar_transacao(conta, transacao)


def exibir_extrato(clientes):
    cpf = input("CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("\n@@@ Cliente não encontrado. @@@")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n=========== EXTRATO ===========")
    transacoes = conta.historico.transacoes
    if not transacoes:
        print("Não foram realizadas movimentações.")
    else:
        for t in transacoes:
            print(f"{t['data']} - {t['tipo']}: R$ {t['valor']:.2f}")
    print(f"\nSaldo atual: R$ {conta.saldo:.2f}")
    print("================================")


# ===================== EXECUÇÃO =====================

def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)
        elif opcao == "s":
            sacar(clientes)
        elif opcao == "e":
            exibir_extrato(clientes)
        elif opcao == "nu":
            criar_cliente(clientes)
        elif opcao == "nc":
            criar_conta(len(contas) + 1, clientes, contas)
        elif opcao == "lc":
            listar_contas(contas)
        elif opcao == "q":
            print("\n Saindo do sistema")
            
main()