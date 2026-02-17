# Como Instalar Python no Windows

## Passo 1: Download
Acesse: https://www.python.org/downloads/

Baixe a versão 3.10 ou superior

## Passo 2: Instalação
1. Execute o instalador baixado
2. **IMPORTANTE**: Marque a opção "Add Python to PATH"
3. Clique em "Install Now"

## Passo 3: Verificar Instalação
Abra um novo terminal PowerShell e digite:
```bash
python --version
```

Deve mostrar algo como: `Python 3.10.x`

## Passo 4: Instalar pip
Se pip não estiver instalado:
```bash
python -m ensurepip --upgrade
```

## Depois siga os passos do README principal
1. Criar ambiente virtual
2. Instalar dependências
3. Gerar dataset e treinar modelo
4. Rodar a API
