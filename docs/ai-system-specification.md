# AI System Specification & Discovery Plan

## 1. 🧠 Reframed Problem

### Core problem

Construir um sistema confiável para estimar e validar proximidade da falha muscular (percepção de esforço) durante treino de força, e transformar essa estimativa em recomendação de carga e execução, com segurança e utilidade prática para atleta que treina sozinho.

### Hidden problems

- Percepção de esforço não é um único sinal fisiológico; é variável latente com componentes periféricos, centrais, psicológicos e contextuais.
- BPM durante musculação tem baixa estabilidade como proxy isolada de esforço local (especialmente em exercícios multiarticulares e séries curtas).
- Auto-relato de RPE/RIR sofre viés de ego, memória e padrão de preenchimento.
- Vídeo pode capturar técnica, mas qualidade de inferência depende de ângulo, iluminação, oclusão e frame rate.
- Recomendação de carga sem modelar fadiga acumulada e recuperação pode elevar risco de overreaching/lesão.

### False assumptions to challenge

- "Se BPM subir, o esforço da série está alto" → incompleto/enganoso para força-hipertrofia.
- "RPE informado é verdade de chão" → precisa calibração longitudinal do próprio usuário.
- "100% cobertura de testes garante qualidade do sistema" → cobertura é métrica de alcance, não de validade das decisões do modelo.
- "RAG melhora qualquer decisão" → RAG só agrega quando há base de conhecimento curada e política de uso contextual definida.

### Hard constraints

- Segurança do usuário: sistema não pode induzir progressão de carga sem faixas de proteção.
- Latência: feedback pós-série deve ser próximo de tempo real para ser acionável.
- Qualidade de dados: sensores wearables e input manual são ruidosos por natureza.
- Compliance e privacidade: dados biométricos e vídeos são sensíveis.
- Adoção: UX mobile-first com baixa fricção é obrigatória.

## 2. 🏗️ Improved AI Agent Context Template

## 2.1 Context

- Produto: plataforma web/mobile-first para atleta de bodybuilding treinando sozinho.
- Objetivo operacional: melhorar qualidade de execução e acurácia de prescrição de carga por série.
- Cenário técnico: microservices Flask, arquitetura hexagonal + camada diplomat, processamento assíncrono orientado a eventos.

## 2.2 Problem Definition

- Decisão-alvo: estimar estado de esforço por série e recomendar ajuste (manter, subir, reduzir carga; ajustar execução).
- Unidade de decisão: exercício + série + contexto de sessão.
- Critério de valor: recomendação aumenta desempenho sem elevar risco de erro técnico/lesão.

## 2.3 System Decomposition

- Ingestion Service: recebe telemetria, logs de treino, vídeo metadados.
- Validation Service: valida qualidade/sanidade dos dados.
- Effort Intelligence Service: estima esforço e incerteza.
- Recommendation Service: gera próxima ação com guardrails.
- Feedback & Learning Service: fecha loop com resultado real da recomendação.
- Knowledge Service (RAG): serve contexto de treino, progressão, biomecânica e regras.

## 2.4 Agent Roles

- Data Ingestion Agent: normalização e enriquecimento inicial.
- Data Validation Agent: score de confiabilidade por sinal e por série.
- Effort Estimation Agent: inferência multimodal de esforço + intervalo de confiança.
- Recommendation Agent: política de decisão e explicabilidade.
- Feedback Loop Agent: recalibração individual, drift e ajuste de políticas.

## 2.5 Data Contracts (mínimo)

- SessionStarted
  - session_id, athlete_id, timestamp, readiness_score (opcional), planned_workout
- SetRecorded
  - set_id, session_id, exercise_id, load_kg, reps, rir_reported/rpe_reported, bpm_avg, bpm_peak, rest_seconds, tempo (se disponível), rom_score (se disponível)
- VideoAnalyzed
  - set_id, rom_score, rep_quality_score, velocity_proxy, posture_flags, confidence
- EffortEstimated
  - set_id, effort_score_0_100, rir_estimate, confidence, feature_contributions
- RecommendationIssued
  - set_id, action_type, load_delta_pct, cue_list, safety_reason_codes
- RecommendationOutcome
  - set_id, accepted, completed_reps, resulting_rir_reported, pain_flag, notes

## 2.6 Behavioral Rules for Agents

- Nunca emitir recomendação de aumento quando confidence < limiar.
- Sempre anexar justificativa legível (top fatores + nível de confiança).
- Escalar para modo conservador quando houver dados faltantes críticos.
- Nunca usar BPM isoladamente para decisão de carga.
- Priorizar segurança quando houver conflito entre sinais.

## 2.7 Output Expectations

- Para usuário: recomendação curta, acionável e segura em até 3 passos.
- Para treinador/sistema: trilha técnica completa (features, scores, confiança, motivo da decisão).
- Para observabilidade: evento versionado + correlation_id por pipeline.

## 3. 🔬 Product Discovery (Deep)

### 3.1 Effort perception modeling

Definição técnica: percepção de esforço em treino de força é uma variável latente associada à distância da falha momentânea, modulada por fadiga local, fadiga sistêmica, dor, motivação, técnica e contexto da sessão.

Sinais relativamente confiáveis:

- Reps executadas versus reps-alvo.
- Carga absoluta e relativa ao histórico do exercício.
- Tendência de RIR/RPE ao longo de semanas (calibração intra-indivíduo).
- Queda de qualidade de repetição (ROM, compensações, desaceleração visível).

Sinais ruidosos/ambíguos:

- BPM em séries curtas e com pausa.
- Auto-relato em usuários iniciantes sem treinamento de escala RPE/RIR.
- Vídeo de baixa qualidade/ângulo inadequado.

Inferência realista:

- Estimar faixa de esforço com incerteza (não valor absoluto exato).
- Recomendação probabilística e conservadora por exercício/série.
- Detectar tendência longitudinal de calibração do usuário.

### 3.2 Data validity analysis

Reps:

- Limitação: contagem manual tem erros, especialmente em rest-pause e reps parciais.
- Necessário: distinguir rep válida, parcial e falha técnica.

Load:

- Limitação: variações de máquina, alavanca e amplitude alteram estímulo sem mudar kg.
- Necessário: contexto de equipamento, unilateral/bilateral e range real de movimento.

BPM:

- Limitação: lag de sensor óptico, artefato de movimento, baixa especificidade para esforço local.
- Necessário: qualidade de sinal, janela temporal correta, baseline individual.

Variáveis faltantes críticas:

- Tempo sob tensão (TUT) e tempo por fase (excêntrica/concêntrica).
- ROM por repetição e consistência intra-série.
- Velocidade/queda de velocidade (proxy de fadiga neuromuscular).
- Tempo de descanso real.
- Ordem do exercício na sessão.
- Estado de recuperação (sono, dor, estresse, sessão anterior).

### 3.3 User behavior reality

- Treino solo aumenta variância técnica entre séries.
- Usuário pode superestimar capacidade por viés motivacional.
- Em dias de baixa recuperação, aderência ao plano cai e auto-relato piora.
- Intervenções devem ser simples e de baixa carga cognitiva durante treino.

### 3.4 Core hypotheses (testáveis)

- H1: combinação de reps + load + qualidade de execução prevê RIR melhor que BPM isolado.
- H2: calibração individual de RPE/RIR reduz erro de estimativa em 4-8 semanas.
- H3: recomendações conservadoras com explicação aumentam adesão sem reduzir progresso.
- H4: feedback técnico pós-série reduz variabilidade de execução no mesmo exercício.
- H5: score de confiança alto correlaciona com maior taxa de aceitação da recomendação.

## 4. 🤖 AI / Agent System Design

### 4.1 Data Ingestion Agent

- Responsabilidade: ingestão de eventos de treino, sensor e vídeo metadados; padronização de schema.
- Input: SessionStarted, SetRecorded, telemetria wearable, referências de vídeo.
- Output: eventos normalizados + enriched_features iniciais.
- Failure modes:
  - Duplicidade de evento
  - Timestamp fora de ordem
  - Falha de sincronização wearable/app
- Mitigação: idempotency key, event-time watermark, retry com DLQ.

### 4.2 Validation Agent

- Responsabilidade: validar integridade, consistência fisiológica e qualidade de sinal.
- Input: eventos normalizados.
- Output: data_quality_score, validity_flags, missingness_profile.
- Failure modes:
  - Falso positivo de dado inválido
  - Falha em detectar outlier fisiológico
- Mitigação: regras híbridas (hard rules + modelos de detecção), auditoria de limiares.

### 4.3 Effort Estimation Agent

- Responsabilidade: estimar esforço, RIR provável e incerteza por série.
- Input: set features validadas + histórico individual.
- Output: effort_score, rir_estimate, confidence, explanation.
- Failure modes:
  - Overfitting ao usuário early-stage
  - Drift por mudança de rotina/exercício
- Mitigação: modelo baseline global + fine-tuning gradual + detector de drift.

### 4.4 Recommendation Agent

- Responsabilidade: recomendar ajuste de carga/execução com guardrails de segurança.
- Input: EffortEstimated + policy rules + objetivos de sessão.
- Output: action_type, load_delta_pct, coaching_cues, rationale.
- Failure modes:
  - Recomendações agressivas em baixa confiança
  - Conflito entre objetivo de performance e segurança
- Mitigação: política restritiva por confidence tiers; fallback para "manter carga".

### 4.5 Feedback Loop Agent

- Responsabilidade: medir resultado real, atualizar calibração e política.
- Input: RecommendationOutcome + eventos subsequentes.
- Output: calibration_update, policy_adjustment, experiment telemetry.
- Failure modes:
  - Feedback atrasado/incompleto
  - Contaminação por fatores externos não observados
- Mitigação: janelas de atualização, pesos por completude, causal logging.

## 5. ⚙️ Technical Architecture

### 5.1 Backend (Flask + microservices)

Serviços sugeridos:

- api-gateway-service (BFF + autenticação + rate limiting)
- workout-command-service (registro de sessão/séries)
- telemetry-service (wearable ingest)
- video-analysis-service (pipeline assíncrono de análise)
- effort-intelligence-service (estimativa de esforço)
- recommendation-service (motor de política)
- user-profile-service (perfil, histórico, preferências)
- experiment-observability-service (feature flags, métricas, tracing)

Hexagonal + Diplomat:

- Entradas (wire-in): REST, fila, webhooks.
- Núcleo: casos de uso + entidades de domínio.
- Saídas (wire-out): banco, broker, provedores externos.
- Diplomat: camada de anti-corruption para interfaces externas e contratos de integração.

### 5.2 Async processing

Broker:

- RabbitMQ (bom para roteamento flexível e maturidade operacional).
- Alternativa futura: Kafka se volume/event replay crescer substancialmente.

Padrões:

- Outbox pattern para consistência entre banco e publicação de evento.
- DLQ por domínio (telemetry.dlq, recommendation.dlq).
- Retry exponencial com limite.
- Correlation ID e causation ID por pipeline.

### 5.3 AI layer

Orquestração multiagente:

- LangGraph/LangChain para coordenação de estado e transições.
- Política de execução por estágio (validate -> estimate -> recommend -> learn).

RAG (onde e por quê):

- Onde usar:
  - Explicações e coaching cues contextualizados.
  - Regras de progressão e segurança por exercício.
- Onde não usar:
  - Cálculo direto de esforço em tempo real crítico.
- Base vetorial:
  - Conteúdo curado: guias de técnica, princípios de periodização, protocolos de segurança.

### 5.4 Frontend

- React mobile-first com liquid design.
- Fluxos curtos por série (input < 10s).
- Feedback em 2 camadas:
  - Imediata: ação recomendada.
  - Expandida: justificativa e confiança.
- Estado offline-first para logging local e sync posterior.

## 6. 📊 Data & Model Strategy

### 6.1 Event model

- Event sourcing parcial para trilha de decisão.
- Contratos versionados (v1, v2...) com compatibilidade backward.

### 6.2 Storage strategy

- OLTP (PostgreSQL): usuários, sessões, séries, recomendações, outcomes.
- Time-series (TimescaleDB ou tabela particionada): telemetria BPM.
- Object storage (S3 compatível): vídeos e artefatos de visão.
- Vector DB (Pinecone): conhecimento técnico para RAG.
- Analytics warehouse (BigQuery/Snowflake/Postgres read replica): experimentos e BI.

### 6.3 Persistir vs derivar

Persistir (raw):

- Eventos originais de treino, telemetria, metadados de vídeo, decisões emitidas.

Persistir (curated):

- Features validadas, effort estimates, recomendações, outcomes, scores de confiança.

Derivar sob demanda:

- Tendências semanais, score de consistência, ranking de exercícios críticos.

### 6.4 Schema mínimo (entidades)

- Athlete
- WorkoutSession
- ExerciseSet
- SensorStreamWindow
- VideoAssessment
- EffortEstimate
- Recommendation
- RecommendationOutcome
- CalibrationProfile
- ExperimentAssignment

## 7. 🧪 Experimentation Plan

### 7.1 Experimentos de precisão

- Objetivo: validar erro de estimativa de esforço.
- Métrica primária: MAE entre RIR estimado e referência de validação (com protocolo controlado).
- Critério de sucesso MVP: MAE <= 1.5 RIR em exercícios prioritários.

### 7.2 Experimentos de utilidade

- Objetivo: medir valor prático da recomendação.
- Métricas:
  - Taxa de aceitação da recomendação.
  - Delta de performance (reps efetivas com técnica aceitável).
  - Queda em flags de execução ruim.
- Critério de sucesso: +15% em aceitação útil sem aumento de pain_flag.

### 7.3 Experimentos de adesão

- Objetivo: retenção e consistência de uso.
- Métricas:
  - Sessões/semana.
  - % de séries com dados completos.
  - Retenção D30.
- Critério de sucesso: D30 >= 35% em cohort alvo inicial.

### 7.4 Experimentos de segurança

- Objetivo: evitar recomendações danosas.
- Métricas:
  - Taxa de rollback manual da recomendação.
  - Incidência de pain_flag pós-recomendação.
- Critério de sucesso: pain_flag não superior ao baseline pré-sistema.

## 8. 🚧 Risks & Edge Cases

- Variabilidade fisiológica alta entre usuários e entre dias do mesmo usuário.
- Artefatos de sensor (movimento, contato de pele, atraso de leitura).
- Vídeo com ângulo ruim inviabilizando inferência de ROM/postura.
- Recomendação otimizada para curto prazo e ruim para progressão de longo prazo.
- Usuário manipula input para “ganhar” recomendação de carga maior.
- Cold start sem histórico suficiente para personalização confiável.
- Mudança de equipamento/academia altera baseline mecânico.
- Dependência excessiva de um único proxy (BPM).

## 9. 🗺️ Execution Plan (PLAN.md)

## Phase 1 — Discovery & Validation

Deliverables:

- PRD técnico + taxonomia de sinais + protocolo de coleta.
- Contratos de eventos v1 e dicionário de dados.
- Blueprint arquitetural (C4 + eventos).
- Plano de experimentos e baseline manual.

Technical milestones:

- Serviço de ingestão básico + storage raw.
- Pipeline de validação com regras hard.
- Instrumentação inicial (logs estruturados + tracing).

Validation checkpoints:

- Qualidade mínima de dados (completude > 85% em séries piloto).
- Confirmação de hipóteses H1/H2 em estudo piloto.

## Phase 2 — MVP

Deliverables:

- App mobile-first com logging de treino e feedback pós-série.
- Estimador de esforço v1 (híbrido regra + modelo simples).
- Motor de recomendação conservador com guardrails.

Technical milestones:

- Microservices Flask operando via RabbitMQ.
- CI/CD GitHub Actions com testes unitários + integração + quality gates.
- Observabilidade mínima (SLO, erro por serviço, DLQ monitorada).

Validation checkpoints:

- Estimador dentro da meta de MAE em exercícios prioritários.
- Taxa de aceitação útil acima do baseline definido.

## Phase 3 — Intelligent System

Deliverables:

- Pipeline multiagente completo com loop de recalibração.
- Integração RAG para explicações e coaching técnico.
- Módulo de qualidade de execução via vídeo v1.

Technical milestones:

- Feature store/curated layer.
- Framework de experimentação A/B.
- Detector de drift + retraining policy.

Validation checkpoints:

- Ganho estatisticamente significativo em aderência e qualidade técnica.
- Segurança mantida sem aumento de pain_flag.

## Phase 4 — Scale

Deliverables:

- Hardening de segurança, privacidade e governança de modelo.
- Suporte multi-tenant e regionalização.
- Playbooks operacionais e runbooks de incidentes.

Technical milestones:

- Escala horizontal de serviços críticos.
- Observabilidade avançada (traces ponta-a-ponta + error budgets).
- Otimização de custo por evento inferido.

Validation checkpoints:

- SLOs cumpridos sob carga alvo.
- Estabilidade de modelo e recomendação em novas coortes.

## 10. ✅ Engineering Governance (Husky + TDD AI + Spec-Driven + Micro ADRs)

### 10.1 Validação da proposta

- A proposta é válida e recomendada para este produto, com um ajuste: Husky valida qualidade e conformidade do commit, mas não “origem AI” por si só.
- Para rastrear origem de mudanças por AI, adotar convenção explícita em commit metadata (exemplo: trailer AI-Generated: true) e escopo de branch por feature.
- “Grande commit” deve ser interpretado como commit atômico orientado a feature completa (código + testes + micro-docs), evitando mistura de múltiplas features.

### 10.2 Política de commit orientada a feature

- Regra principal: 1 commit atômico por feature concluída contendo implementação + testes + decisão arquitetural mínima.
- Estrutura mínima do commit:
  - Código de produção da feature.
  - Testes unitários e de integração da feature.
  - Micro ADR da decisão de IA relacionada (quando aplicável).
  - Atualização do spec da feature (Spec-Driven).
- Padrão de mensagem de commit:
  - Tipo: feat/fix/refactor/test/docs/chore.
  - Escopo: serviço ou domínio (exemplo: effort-intelligence).
  - Footer obrigatório: Spec-ID, ADR-ID (se houver), AI-Generated.

### 10.3 Husky gate obrigatório

- pre-commit:
  - lint e formatação.
  - testes unitários impactados (ou suíte mínima por pacote).
  - verificação de cobertura mínima por módulo alterado.
  - validação de contrato de eventos modificados (schema check).
- commit-msg:
  - valida Conventional Commits.
  - exige footer Spec-ID.
  - exige footer AI-Generated (true/false).
  - exige footer ADR-ID quando houver mudança de comportamento de agente/modelo.
- pre-push:
  - suíte de integração relevante.
  - checagem de compatibilidade backward em contratos de eventos.
  - smoke tests da pipeline assíncrona.

### 10.4 Metodologia de desenvolvimento: TDD AI + Spec-Driven

- Fluxo padrão por feature:
  1. Especificar comportamento (Spec-Driven) com critérios de aceite mensuráveis.
  2. Criar testes de falha primeiro (TDD red).
  3. Implementar com apoio de AI até testes passarem (TDD green).
  4. Refatorar preservando contrato e comportamento (TDD refactor).
  5. Gerar micro-doc da decisão e rationale.
  6. Commit atômico validado por Husky.
- Regra de qualidade:
  - Sem teste, sem merge.
  - Sem spec atualizado, sem merge.
  - Sem micro-ADR para mudança de decisão de IA, sem merge.

### 10.5 S.P.R.E.C.-Driven (Specification, Protocol, Risk, Experiment, Compliance)

- Specification:
  - comportamento esperado, dados de entrada/saída, limites de decisão.
- Protocol:
  - contrato de eventos, versão de schema, regras de compatibilidade.
- Risk:
  - riscos de segurança, viés, confiabilidade e impacto no usuário.
- Experiment:
  - hipótese, métrica, critério de sucesso, janela de avaliação.
- Compliance:
  - requisitos de privacidade, retenção, trilha de auditoria e explicabilidade.

### 10.6 Micro docs para ADRs de decisão de AI

- Objetivo: documentar decisões pequenas e frequentes sem sobrecarga documental.
- Formato recomendado (1 página):
  - Contexto
  - Decisão
  - Alternativas consideradas
  - Impacto esperado
  - Riscos e rollback
  - Evidência (teste/experimento)
- Quando obrigatório:
  - alteração de policy de recomendação de carga.
  - mudança de features do estimador de esforço.
  - ajuste de threshold de confiança/safety.
  - modificação de prompt/pipeline que altere comportamento final ao usuário.

### 10.7 Estrutura de diretórios recomendada

- docs/
  - specs/
    - SPEC-001-effort-estimation.md
    - SPEC-002-load-recommendation.md
  - adrs/
    - ADR-AI-001-confidence-threshold.md
    - ADR-AI-002-rir-calibration-policy.md
  - decisions/
    - DEC-YYYYMMDD-short-title.md

### 10.8 Critérios de aceite de governança

- 100% dos commits de feature passam por hooks Husky obrigatórios.
- 100% das features com mudança funcional possuem testes + Spec-ID.
- 100% das mudanças em lógica de IA possuem micro-ADR rastreável.
- 0 merges com contrato de evento quebrado sem versionamento.

## 11. ❓ Open Questions

- Qual definição operacional de “sucesso” para o usuário: hipertrofia, performance de carga, técnica, ou combinação ponderada?
- Qual protocolo de ground truth para RIR/RPE será usado na fase de validação?
- Quais exercícios entram no escopo inicial (e quais ficam fora por limitação de visão/sensor)?
- Qual nível de responsabilidade clínica/legal do produto ao sugerir carga?
- Qual janela de latência máxima aceitável para feedback pós-série?
- Qual estratégia para cold start sem histórico individual?
- Quais dados da Huawei Health Kit estarão realmente disponíveis e com que frequência/confiabilidade?
- Como será tratada privacidade de vídeo (retenção, anonimização, consentimento granular)?
- Qual baseline humano (treinador) será usado para comparar decisões da IA?
- Cobertura de testes “100%” será aplicada em quais camadas e com quais critérios de qualidade além de coverage?

## Apêndice A — Prompt & Tools Directory (recomendado)

Estrutura sugerida:

- ai/
  - prompts/
    - system/
      - effort_validation.prompt.md
      - load_recommendation.prompt.md
      - execution_feedback.prompt.md
    - policies/
      - safety_guardrails.prompt.md
      - confidence_fallbacks.prompt.md
  - tools/
    - contracts/
      - effort_estimation.schema.json
      - recommendation.schema.json
    - definitions/
      - validate_set_data.tool.json
      - estimate_effort.tool.json
      - generate_recommendation.tool.json
      - explain_decision.tool.json

Ferramentas mínimas do pipeline:

- validate_set_data: valida completude e consistência do set.
- estimate_effort: estima esforço + incerteza.
- generate_recommendation: aplica política e guardrails.
- explain_decision: traduz decisão técnica para linguagem do usuário.
- record_outcome: captura resultado real para aprendizado.
