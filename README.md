# Fraud Shield

Engine de detecção de fraude em transações financeiras usando Machine Learning e análise comportamental.

## Sobre o Projeto

Fraud Shield analisa transações financeiras em tempo real para identificar possíveis fraudes. O sistema vai além de simplesmente avaliar valores isolados - ele constrói um perfil comportamental de cada usuário e detecta desvios que podem indicar atividade suspeita.

Desenvolvi este projeto explorando como seria construir um sistema anti-fraude que realmente funcionasse em cenários reais. Não adianta ter um modelo de ML bom se o sistema cair quando o modelo falhar, ou se não houver forma de auditar as decisões tomadas.

## Funcionalidades Principais

**Análise Comportamental**
- Histórico de gastos do usuário
- Padrões de frequência de transações
- Desvio em relação ao comportamento normal
- Análise temporal e geográfica

**Infraestrutura**
- API REST para integração
- Banco de dados SQLite para auditoria
- Sistema de fallback baseado em regras
- Geração de relatórios em PDF

**Ferramentas de Desenvolvimento**
- Simulador de tráfego para testes
- Dashboard visual de análises
- Logs estruturados para debugging
- Estatísticas em tempo real

## Stack Tecnológica

**Backend & API**
- Flask 3.0 - Framework web
- Pydantic - Validação de schemas
- Gunicorn - WSGI server

**Machine Learning & Data**
- Scikit-Learn - Random Forest classifier
- Pandas & NumPy - Manipulação de dados
- Matplotlib + ReportLab - Visualizações e relatórios

**Infraestrutura**
- SQLite - Persistência e auditoria
- Python 3.10+ com Type Hints
- Logging com rotação de arquivos

## Arquitetura

O projeto segue uma separação em camadas para facilitar manutenção e testes:

```
┌─────────────────────────────────────┐
│         API (Flask)                 │
│  /analyze │ /dashboard │ /report    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Core & ML                      │
│  Feature Engineering │ Detector     │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│    Infrastructure                   │
│  Database │ Feature Store │ Reports │
└─────────────────────────────────────┘
```

**Camadas:**
- `domain/` - Entidades e interfaces do negócio
- `core/` - Lógica de ML e feature engineering
- `infrastructure/` - Banco de dados, persistência e relatórios
- `entrypoints/` - API REST e rotas

## Como Rodar

### Pré-requisitos
- Python 3.10 ou superior

### Setup

**1. Clone o repositório**
```bash
git clone https://github.com/maperotto/Fraud-Shield.git
cd Fraud-Shield
```

**2. Crie e ative o ambiente virtual**

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

Linux/Mac:
```bash
python -m venv venv
source venv/bin/activate
```

**3. Instale as dependências**
```bash
pip install -r requirements.txt
```

**4. Gere dados e treine o modelo**
```bash
python scripts/generate_dataset.py
python scripts/train_model.py
```

**5. Inicie a API**
```bash
python run.py
```

API rodando em `http://localhost:5000`

## Uso

### Analisar uma transação

```bash
curl -X POST http://localhost:5000/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "tx_12345",
    "amount": 1500.00,
    "timestamp": "2024-01-15T14:30:00",
    "merchant_category": "online_shopping",
    "location": "New York",
    "user_id": "user_0042"
  }'
```

Resposta:
```json
{
  "transaction_id": "tx_12345",
  "is_fraud": true,
  "confidence_score": 0.8234,
  "risk_level": "HIGH",
  "analysis_timestamp": "2024-01-15T14:30:05.123456"
}
```

### Obter estatísticas gerais

```bash
curl http://localhost:5000/v1/stats
```

### Gerar dashboard visual

```bash
curl http://localhost:5000/v1/dashboard --output dashboard.png
```

### Gerar relatório PDF

```bash
curl http://localhost:5000/v1/report --output report.pdf
```

### Simular tráfego

```bash
python scripts/stream_simulator.py --tps 5 --duration 30
```

## Estrutura do Projeto

```
Fraud-Shield/
├── src/
│   ├── domain/              # Entidades e interfaces do negócio
│   │   ├── entities.py
│   │   └── interfaces.py
│   ├── core/                # Lógica de ML e feature engineering
│   │   ├── fraud_detector.py
│   │   ├── feature_engineering.py
│   │   ├── dashboard.py
│   │   └── logger.py
│   ├── infrastructure/      # Persistência e serviços externos
│   │   ├── database.py
│   │   ├── feature_store.py
│   │   ├── fallback.py
│   │   └── report_generator.py
│   └── entrypoints/         # API Flask
│       ├── app.py
│       ├── routes.py
│       ├── schemas.py
│       └── config.py
├── scripts/
│   ├── generate_dataset.py  # Cria dados sintéticos
│   ├── train_model.py       # Treina o modelo
│   └── stream_simulator.py  # Simula carga de produção
├── models/                  # Modelos treinados (.pkl)
├── data/                    # Datasets e banco SQLite
├── tests/                   # Testes unitários
├── run.py                   # Entry point da aplicação
├── Dockerfile               # Para containerização
└── requirements.txt
```

## Decisões Técnicas

**Random Forest vs Isolation Forest**
Escolhi Random Forest porque oferece melhor controle sobre dados desbalanceados com o parâmetro `class_weight='balanced'`. Também gera feature importance que é útil para debugging.

**Feature Engineering**
Features comportamentais como desvio do valor médio e frequência temporal capturam anomalias que dados brutos não conseguiriam. Um valor de R$ 500 pode ser normal ou suspeito dependendo do histórico do usuário.

**Clean Architecture**
Separar em camadas facilita trocar componentes sem impactar o resto do código. Posso mudar o banco de dados ou o framework web mantendo a lógica de negócio intacta.

**SQLite**
Para este projeto, SQLite é suficiente e não precisa de configuração. Em um cenário com mais throughput, seria só trocar a connection string para PostgreSQL sem mudar as queries.

**Sistema de Fallback**
Se o modelo ML falhar por qualquer motivo, regras de negócio assumem automaticamente. Isso garante que a API sempre responde, mesmo que com confiança menor.

## Possíveis Melhorias

Algumas ideias que pensei mas não implementei ainda:

**Retreinamento Automático**
Criar um pipeline que periodicamente pega novas transações do banco, treina um novo modelo e compara a performance antes de substituir o modelo atual.

**Escalabilidade**
Para tráfego muito alto, seria interessante adicionar um message broker tipo RabbitMQ para processar análises de forma assíncrona, e usar Redis para cachear estatísticas de usuários frequentes.

**Fairness**
Implementar métricas de fairness para garantir que o modelo não discrimina grupos específicos de usuários inadvertidamente.

**Threshold Dinâmico**
Ao invés de usar threshold fixo, ajustar baseado no custo de falsos positivos vs falsos negativos para cada categoria de merchant.

## Deploy com Docker

```bash
docker build -t fraud-shield .
docker run -p 5000:5000 fraud-shield
```

## Licença

MIT License
