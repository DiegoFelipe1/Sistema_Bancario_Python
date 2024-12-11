from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime as dt
import textwrap


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)
        
class PessoaFisica(Cliente):
    def __init__(self, cpf, nome, data_nascimento, endereco):
        super().__init__(endereco)
        self._cpf = cpf
        self._nome = nome
        self._data_nascimento = data_nascimento

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = '0001'
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
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print('Operação falhou! Você não tem saldo suficiente.')

        elif valor > 0:
            self._saldo -= valor
            print('Saque realizado com sucesso!')
            return True

        else:
            print('Operação falhou! O valor informado é inválido.')
        
        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print('Deposito realizado com sucesso!')
            return True
        else:
            print('Operação falhou! O valor informado é inválido')
            return False

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            print('Operação falhou! O valor do saque excede o limite.')
        elif excedeu_saques:
            print('Operação falhou! Numero máximo de saques excedido.')
        else:
            return super().sacar(valor)
        
        return False

    def __str__(self):
        return f'''\
            Agência:\t{self._agencia}
            C/C:\t\t{self._numero}
            Titular:\t{self._cliente._nome}
        '''

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                'tipo': transacao.__class__.__name__,
                'valor': transacao.valor,
               # "data": dt.now().strftime("%d-%m-%Y %H:%M:%s"),
            }

        )

class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass
    @abstractclassmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

def menu():
    menu = '''\n
    =========================================
        Bem vindo ao banco XPTO

    Por favor digite uma das opções abaixo:

    [1]\tDepositar
    [2]\tSacar
    [3]\tExtrato
    [4]\tNovo Usuário
    [5]\tNova Conta
    [6]\tListar Contas
    [7]\tSair

    Sua opção é: '''
    return int(input(textwrap.dedent(menu)))

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print('Cliente não possui conta!')
        return
    return cliente.contas[0]

def depositar(clientes):
    cpf = input('Informe o CPF do cliente: ')
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print('Cliente não encontrado!')
        return
    
    valor = float(input('Informe o valor do depósito:'))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)

def sacar(clientes): 
    cpf = input('informe o CPF do cliente: ')
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print('Clinte não encontrado!')
        return
    
    valor = float(input('Informe o valor do saque: '))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)
    
def exibir_extrato(clientes):
    cpf = input('Informe o CPF do cliente: ')
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print('Cliente não encontrado!')
        return
    
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    print('\n ================ EXTRATO ================')
    transacoes = conta.historico.transacoes

    extrato = ''
    if not transacoes:
        extrato = 'Não foram realizadas movimentações.'
    else:
        for transacao in transacoes:
            extrato += f'\n{transacao['tipo']}:\n\tR${transacao['valor']:.2f}'
    
    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("==========================================")

def criar_usuario(clientes):
    cpf = input('Por favor, digite seu CPF: ')
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print('Ja existe um usuario com esse CPF')
        return
    
    nome = input('Por favor, digite seu nome completo: ')
    data_nascimento = input('Por favor, digite a sua data de nascimento (dd-mm-aaaa): ')
    endereço = input('Por favor, digite seu endereço (Rua, numero, bairro, cidade/sigla): ')

    cliente = PessoaFisica(nome=nome, cpf=cpf, data_nascimento=data_nascimento, endereco=endereço)
    clientes.append(cliente)
    
    print('\nUsario criado com sucesso!!')
    
def filtrar_cliente(cpf, clientes):
    cliente_filtrado = [cliente for cliente in clientes if cliente._cpf == cpf]
    return cliente_filtrado[0] if cliente_filtrado else None # dar uma olhada a respeito desse codigo

def criar_conta(clientes, contas, numero_conta,):
    cpf = input('Por favor, digite seu CPF: ')
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print('Cliente não encontrado!!')
        return
    
    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print('Conta criada com sucesso!')

def listar_contas(contas):
    for contas in contas:
        print('=' * 100)
        print(textwrap.dedent(str(contas)))

def main():
    clientes = []
    contas = []

    while True:
        
        opcao = menu()

        if opcao == 1: 
           depositar(clientes)

        elif opcao == 2:
            sacar(clientes)

        elif opcao == 3:
            exibir_extrato(clientes)

        elif opcao == 4:    
            criar_usuario(clientes)

        elif opcao == 5:
            numero_conta = len(contas) + 1
            criar_conta(clientes, contas, numero_conta)

        elif opcao == 6:
            listar_contas(contas)
        elif opcao == 7:
            break
        else:
            print('Operação invalida, por favor selecione novamente a operação desejada.')
        
main()