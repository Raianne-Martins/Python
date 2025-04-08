from abc import ABC, abstractmethod
from datetime import datetime


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def efetuar_transacao(self, conta, operacao):
        operacao.processar(conta)

    def vincular_conta(self, conta):
        self.contas.append(conta)


class Pessoa(Cliente):
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
    def criar_conta(cls, cliente, numero):
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

    def retirar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("\n@@@ Retirada cancelada! Saldo insuficiente. @@@")

        elif valor > 0:
            self._saldo -= valor
            print("\n=== Saque realizado com sucesso! ===")
            return True

        else:
            print("\n@@@ Operação cancelada! Valor inválido. @@@")

        return False

    def adicionar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n=== Depósito realizado com sucesso! ===")
        else:
            print("\n@@@ Operação cancelada! Valor inválido. @@@")
            return False

        return True


class ContaSimples(Conta):
    def __init__(self, numero, cliente, limite=500, limite_retiradas=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_retiradas = limite_retiradas

    def retirar(self, valor):
        numero_retiradas = len(
            [operacao for operacao in self.historico.transacoes if operacao["tipo"] == Retirada.__name__]
        )

        excedeu_limite = valor > self.limite
        excedeu_retiradas = numero_retiradas >= self.limite_retiradas

        if excedeu_limite:
            print("\n@@@ Operação cancelada! Valor acima do limite permitido. @@@")

        elif excedeu_retiradas:
            print("\n@@@ Operação cancelada! Número de retiradas excedido. @@@")

        else:
            return super().retirar(valor)

        return False

    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            Conta:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def registrar_operacao(self, operacao):
        self._transacoes.append(
            {
                "tipo": operacao.__class__.__name__,
                "valor": operacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )


class Operacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def processar(self, conta):
        pass


class Retirada(Operacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def processar(self, conta):
        sucesso = conta.retirar(self.valor)

        if sucesso:
            conta.historico.registrar_operacao(self)


class Deposito(Operacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def processar(self, conta):
        sucesso = conta.adicionar(self.valor)

        if sucesso:
            conta.historico.registrar_operacao(self)
