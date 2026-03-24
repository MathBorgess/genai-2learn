# Project Template

0. Project Identity
Project Name:
Codename (optional):
Version:
Owner / Stakeholder:
Date:
One-liner (TL;DR):
Descreva em 1 frase o objetivo do projeto.

1. Context & Background
Descreva o contexto geral:
Quem é você (ou o stakeholder)?
Qual sua autoridade/experiência no domínio?
Qual o histórico relevante?
O que já existe hoje?
Objetivo: dar ao agente consciência situacional.
Exemplo do que incluir:
histórico profissional
projetos anteriores
canais existentes (blog, produto, app, etc.)
limitações atuais

2. Problem Statement
Defina claramente:
Qual problema você quer resolver?
Para quem?
Por quê isso importa?
Formato recomendado:
Problema principal
Problemas secundários
Impacto atual
Impacto esperado se resolvido

3. Goals & Success Criteria
Defina sucesso de forma objetiva:
3.1 Primary Goals
Objetivo principal do sistema
3.2 Secondary Goals
Objetivos complementares
3.3 Non-Goals (CRÍTICO)
O que NÃO será feito
3.4 Success Metrics
Métricas claras (ex: tempo, escala, qualidade, conversão)

4. System Overview
Divida o projeto em sub-sistemas claros (como no exemplo).
Para cada sistema:
4.X [Nome do Subsystem]
Descrição:
O que esse sistema faz
Responsabilidades:
Lista objetiva
Inputs:
O que entra
Outputs:
O que sai
Interações:
Com quais outros sistemas conversa

5. AI Agent Definition
Aqui é o coração do template.
5.1 Agent Role
O que o agente é?
Qual sua função principal?
5.2 Agent Personality
Defina comportamento de forma explícita:
Tom de voz
Estilo de escrita
Nível de formalidade
Bias intencional (ex: crítico, otimista, pragmático)
Limitações comportamentais
Exemplo de dimensões:
verbosity (curto vs detalhado)
truthfulness > creativity?
opinião vs neutralidade
5.3 Behavioral Rules
Regras claras:
Nunca inventar fatos
Sempre validar fontes
Preferir X ao invés de Y
Restrições de output
5.4 Agent Tasks
Liste exatamente o que o agente faz:
Task 1
Task 2
Task 3
5.5 Tooling (IMPORTANT)
Quais ferramentas o agente pode usar:
Web fetch
File system
APIs externas
Banco de dados
Para cada tool:
Nome
Função
Quando usar

6. Data Model & Structure
Como os dados são organizados.
6.1 Storage Strategy
File-based?
Database?
Hybrid?
6.2 File Structure
Exemplo:
/year/month/day/slug.md
6.3 Metadata Schema
Defina os campos obrigatórios:
title:
date:
tags:
author:
summary:
status:
6.4 Content Rules
Formato (markdown, JSON, etc.)
Estrutura interna dos arquivos
Convenções de naming

7. Workflows & Automation
Defina fluxos claros.
7.1 Input Flow
Como o sistema recebe dados:
Manual
API
Upload
Bot
7.2 Processing Flow
O que acontece depois:
parsing
validação
enriquecimento
geração
7.3 Output Flow
onde os dados vão parar
como são consumidos
7.4 Scheduling
eventos automáticos
cron jobs
gatilhos

8. Content / Output Specification
Como deve ser o output final.
8.1 Output Format
Markdown
HTML
JSON
8.2 Sections
Liste as seções obrigatórias:
Section A
Section B
Section C
8.3 Style Guidelines
Legibilidade
Tamanho dos textos
Uso de imagens
Estrutura visual
8.4 Variations
Se existirem múltiplos formatos:
Template 1
Template 2

9. Technical Architecture
9.1 Stack
Backend:
Frontend:
Infra:
AI Integration:
9.2 Engineering Principles
DRY
Test coverage
Performance
Escalabilidade
9.3 Constraints
Linguagem obrigatória
Framework obrigatório
Limitações técnicas

10. AI System Design
10.1 Prompt Management
Onde ficam os prompts
Como são versionados
10.2 Agent Orchestration
Single agent vs multi-agent
pipelines
10.3 Observability
logs
tracing
debugging

11. Open Questions
Liste tudo que ainda está ambíguo:
Pergunta 1
Pergunta 2

12. Risks & Edge Cases
Falhas possíveis
Casos extremos
Problemas de escala

13. Roadmap (Optional)
Fase 1
Fase 2
Fase 3

14. Execution Instruction (CRITICAL)
Defina como o agente deve agir:
Sempre gerar um PLAN.md antes de código
Nunca assumir requisitos implícitos
Fazer perguntas antes de implementar
Priorizar clareza sobre velocidade
🧠 Por que esse template é forte
Ele resolve os principais problemas de projetos com AI:

1. Evita ambiguidade
→ força explicitar contexto, objetivos e limites

2. Evita “AI alucinando arquitetura”
→ define sistemas e responsabilidades

3. Controla comportamento do agente
→ personalidade + regras + tasks

4. Facilita escala
→ separa claramente:
dados
processamento
output
infra

5. É reutilizável
→ serve pra:
produto SaaS
automação interna
bots
pipelines de conteúdo