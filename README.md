# Fraud Shield

Sistema anti-fraude baseado em Machine Learning para detecção em tempo real de transações financeiras suspeitas.

## Visão Geral

Fraud Shield é uma engine de detecção de fraude que analisa padrões comportamentais em transações financeiras para identificar anomalias antes que causem danos. O sistema utiliza um modelo Random Forest treinado com técnicas avançadas de Feature Engineering para capturar desvios de comportamento do usuário.

A arquitetura foi desenvolvida seguindo princípios de Clean Architecture para garantir separação de responsabilidades, testabilidade e manutenibilidade. O projeto demonstra desde a geração de dados sintéticos até a exposição via API REST pronta para produção.

## Por que este projeto existe?

Fraudes em transações financeiras representam bilhões em perdas anuais. Este projeto nasceu da necessidade de criar um sistema escalável que possa:
- Detectar fraudes em tempo real sem adicionar latência perceptível
- Adaptar-se a novos padrões através de retreinamento contínuo
- Fornecer explicabilidade nas decisões através de confidence scores

## Tecnologias Utilizadas

**Backend & API**
- Flask 3.0 - Framework web leve e flexível
- Pydantic - Validação robusta de dados de entrada
- Gunicorn - WSGI server para produção

**Machine Learning & Data Science**
- Scikit-Learn - Algoritmo Random Forest com class balancing
- Pandas & NumPy - Processamento e manipulação de dados
- Matplotlib - Geração de dashboards analíticos

**Desenvolvimento**
- Python 3.10+ com Type Hints completas
- python-dotenv para gestão de configurações

## Arquitetura do Sistema

```
┌─────────────────────────────────────────────────┐
│              API Layer (Flask)                  │
│  /v1/analyze  │  /v1/dashboard  │  /health     │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│           Application Core                      │
│  ┌──────────────┐  ┌─────────────────────┐     │
│  │   Feature    │  │   Fraud Detector    │     │
│  │  Engineering │  │   (Random Forest)   │     │
│  └──────────────┘  └─────────────────────┘     │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│              Domain Layer                       │
│    Entities  │  Interfaces  │  Business Logic  │
└─────────────────────────────────────────────────┘
```

## Features Principais

**Análise Comportamental**
O sistema não apenas avalia a transação isolada, mas considera:
- Histórico de gastos do usuário
- Desvio em relação ao ticket médio
- Frequência de transações em janelas temporais
- Padrões geográficos e categorias preferidas

**API REST Completa**
- Endpoint de análise com validação Pydantic
- Geração automática de dashboards visuais
- Health checks para monitoramento
- Tratamento robusto de erros

**Engineering Excellence**
- Logging estruturado com rotação de arquivos
- Type hints em todas as funções
- Separação clara de responsabilidades
- Pronto para containerização

## Setup e Instalação

**Clone o repositório**
```bash
git clone https://github.com/maperotto/Fraud-Shield.git
cd Fraud-Shield
```

**Crie um ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

**Instale as dependências**
```bash
pip install -r requirements.txt
```

**Configure as variáveis de ambiente**
```bash
cp .env.example .env
```

**Gere o dataset sintético**
```bash
python scripts/generate_dataset.py
```

**Treine o modelo**
```bash
python scripts/train_model.py
```

**Inicie a API**
```bash
python src/entrypoints/app.py
```

A API estará disponível em `http://localhost:5000`

## Como Usar

**Análise de Transação**

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

**Resposta Esperada**
```json
{
  "transaction_id": "tx_12345",
  "is_fraud": true,
  "confidence_score": 0.8234,
  "risk_level": "HIGH",
  "analysis_timestamp": "2024-01-15T14:30:05"
}
```

**Dashboard Visual**
```bash
curl -X GET http://localhost:5000/v1/dashboard \
  --output dashboard.png
```

## Estrutura do Projeto

```
Fraud-Shield/
├── src/
│   ├── domain/          # Entidades e interfaces
│   ├── core/            # Lógica de negócio e ML
│   └── entrypoints/     # API Flask
├── scripts/             # Utilitários de treinamento
├── models/              # Modelos treinados
├── data/                # Datasets
├── tests/               # Testes unitários
└── requirements.txt
```

## Decisões Técnicas

**Por que Random Forest?**
Escolhi Random Forest ao invés de Isolation Forest pela capacidade superior de lidar com dados desbalanceados através do parâmetro class_weight='balanced'. Além disso, oferece feature importance para debugging.

**Feature Engineering como diferencial**
As features comportamentais como desvio do valor médio e frequência em janelas de tempo capturam anomalias que features brutas não conseguiriam. Isso reduz falsos positivos.

**Clean Architecture**
A separação em camadas permite trocar o modelo de ML ou o framework web sem alterar a lógica de negócio. Facilita testes unitários e manutenção a longo prazo.

## Perguntas Frequentes para Entrevistas

**Como você lidaria com concept drift?**
Implementaria um pipeline de retreinamento agendado que compara performance do modelo atual vs novo modelo em dados recentes. Se houver degradação, o novo modelo substitui o antigo automaticamente.

**E se a API receber 10000 requisições por segundo?**
Adicionaria um message broker como RabbitMQ para fila de análises, múltiplos workers processando em paralelo, cache Redis para históricos de usuários frequentes, e sharding do banco por user_id.

**Como garantir que o modelo não é discriminatório?**
Auditoria regular de decisões usando fairness metrics do scikit-fairness, análise de disparate impact por grupos demográficos se os dados permitirem, e documentação clara de todas as features usadas.

**Explique o trade-off entre falsos positivos e negativos**
Em fraude, falsos negativos custam dinheiro real, então prefiro um threshold mais conservador que gera alguns falsos positivos. Estes podem ser resolvidos com verificações secundárias sem bloquear o usuário imediatamente.

## Próximos Passos

- [ ] Adicionar suporte a análise em batch
- [ ] Implementar A/B testing de modelos
- [ ] Criar testes unitários e de integração
- [ ] Dockerizar aplicação
- [ ] Adicionar métricas de observabilidade

## Licença

MIT License - Sinta-se livre para usar este projeto como base para seus estudos.

## Autor

Desenvolvido como projeto de portfólio demonstrando expertise em ML Engineering e desenvolvimento de APIs de alto desempenho.
