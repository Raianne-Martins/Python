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


def main():
    print("\n=== Bem-vindo ao sistema bancário! ===")
    clientes = []
    contas = []

    while True:
        print("\n### Menu Principal ###")
        print("1. Criar cliente")
        print("2. Criar conta")
        print("3. Efetuar depósito")
        print("4. Efetuar retirada")
        print("5. Exibir histórico de transações")
        print("6. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            nome = input("Digite o nome do cliente: ")
            cpf = input("Digite o CPF do cliente: ")
            data_nascimento = input("Digite a data de nascimento do cliente (dd-mm-aaaa): ")
            endereco = input("Digite o endereço do cliente: ")

            cliente = Pessoa(nome, data_nascimento, cpf, endereco)
            clientes.append(cliente)
            print("\n=== Cliente criado com sucesso! ===")

        elif opcao == "2":
            if not clientes:
                print("\n@@@ Nenhum cliente disponível. Crie um cliente primeiro. @@@")
                continue

            print("\nClientes disponíveis:")
            for i, cliente in enumerate(clientes):
                print(f"{i + 1}. {cliente.nome} (CPF: {cliente.cpf})")

            indice_cliente = int(input("Escolha o cliente pelo número: ")) - 1
            cliente_selecionado = clientes[indice_cliente]

            numero_conta = input("Digite o número da conta: ")
            conta = ContaSimples(numero_conta, cliente_selecionado)
            cliente_selecionado.vincular_conta(conta)
            contas.append(conta)
            print("\n=== Conta criada com sucesso! ===")

        elif opcao == "3":
            if not contas:
                print("\n@@@ Nenhuma conta disponível. Crie uma conta primeiro. @@@")
                continue

            print("\nContas disponíveis:")
            for i, conta in enumerate(contas):
                print(f"{i + 1}. {conta}")

            indice_conta = int(input("Escolha a conta pelo número: ")) - 1
            conta_selecionada = contas[indice_conta]

            valor = float(input("Digite o valor do depósito: "))
            deposito = Deposito(valor)
            conta_selecionada.cliente.efetuar_transacao(conta_selecionada, deposito)

        elif opcao == "4":
            if not contas:
                print("\n@@@ Nenhuma conta disponível. Crie uma conta primeiro. @@@")
                continue

            print("\nContas disponíveis:")
            for i, conta in enumerate(contas):
                print(f"{i + 1}. {conta}")

            indice_conta = int(input("Escolha a conta pelo número: ")) - 1
            conta_selecionada = contas[indice_conta]

            valor = float(input("Digite o valor da retirada: "))
            retirada = Retirada(valor)
            conta_selecionada.cliente.efetuar_transacao(conta_selecionada, retirada)

        elif opcao == "5":
            if not contas:
                print("\n@@@ Nenhuma conta disponível. Crie uma conta primeiro. @@@")
                continue

            print("\nContas disponíveis:")
            for i, conta in enumerate(contas):
                print(f"{i + 1}. {conta}")

            indice_conta = int(input("Escolha a conta pelo número: ")) - 1
            conta_selecionada = contas[indice_conta]

            print("\n=== Histórico de Transações ===")
            for transacao in conta_selecionada.historico.transacoes:
                print(f"Tipo: {transacao['tipo']} | Valor: {transacao['valor']} | Data: {transacao['data']}")

        elif opcao == "6":
            print("\n=== Saindo do sistema bancário. Até mais! ===")
            break

        else:
            print("\n@@@ Opção inválida! Tente novamente. @@@")


if __name__ == "__main__":
    main()
