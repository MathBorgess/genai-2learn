# Discovery

## Background

Um atleta praticante de academia com foco em bodybuilding, que tem como objetivo maximizar a eficiência e os resultados dos treinos, mesmo treinando sozinho, especialmente para as pernas. Ele utiliza um aplicativo para registrar repetições, carga e percepção de esforço, além de uma band que monitora o bpm durante os exercícios.
Quero iniciar um projeto web com a utilização de arquitetura de processamento assíncrono e pipeline de agente para criar um sistema de validação de perceção de esforço e recomendação de carga para os exercícios.
Utilizando framework web com liquid design e mobile first, backend em Flask e dividido em microservices, com cobertura 100% de testes unitários e integração, integração com mensageria assíncrona, ferramenta de CI/CD para teste e deploy automático, e ferramenta multiagente para o pipeline de agente e rag para aumento de contexto.
O sistema deve ser capaz de validar a percepção de esforço do usuário com base nos dados coletados, como repetições, carga e bpm, e melhoria da execução dos exercícios. O sistema deve ser escalável, seguro e fácil de usar, com uma interface intuitiva e responsiva.

## Objectives

1. Criar um sistema web para validar a percepção de esforço do usuário durante os treinos.
2. Implementar um pipeline de agente para processar os dados coletados e fornecer recomendações de melhoria de execução dos exercícios.
3. Garantir que o sistema seja escalável, seguro e fácil de usar, com uma interface intuitiva e responsiva.
4. Integrar o sistema com ferramentas de CI/CD para garantir testes e deploy automáticos.
5. Utilizar uma arquitetura de microservices para garantir a modularidade e escalabilidade do sistema.
6. Implementar testes unitários e de integração para garantir a qualidade do código e a confiabilidade do sistema.
7. Utilizar uma ferramenta multiagente para o pipeline de agente e rag para aumento de contexto, garantindo que o sistema possa lidar com grandes volumes de dados e fornecer recomendações precisas e personalizadas para os usuários.
8. Utilizar arquitetura diplomat do projeto backend, junto com arquitetura hexagonal, para garantir a separação de preocupações e facilitar a manutenção do código.

## Fluxo de uso

### 1. O usuário acessa o sistema web e se registra.

### 2. O usuário conecta a band de monitoramento de bpm e grava um vídeo do treino, registrando as repetições e a carga utilizada.

### 3. O sistema valida os vídeos das séries e retorna feedback sobre a execução dos exercícios, como amplitude de movimento, velocidade e postura.

### 4. O usuário consulta treinos anteriores e recebe recomendações personalizadas para melhorar a execução dos exercícios, com base nos dados coletados.

### 5. O sistema utiliza o pipeline de agente para processar os dados coletados e fornecer recomendações de melhoria de execução dos exercícios, com base na percepção de esforço do usuário.

### 6. O usuário pode acompanhar seu progresso ao longo do tempo, visualizando gráficos e estatísticas sobre seus treinos e melhorias na execução dos exercícios.

## Tech Stack

- Frontend: React LTM com liquid design e mobile first.
- Backend: Flask, dividido em microservices.
- Arquitetura: Arquitetura diplomat do projeto backend, junto com arquitetura hexagonal. Diplomat separa a última camada do backend, que é a interface com o mundo externo, da lógica de negócio e da camada de dados. Hexagonal é uma arquitetura que promove a separação de preocupações e facilita a manutenção do código, com o uso de wire in e wire out para comunicação entre a camada externa e o diplomat, mas para comunicação interna utiliza-se dtos e domain models.
- Comunicação assíncrona: RabbitMQ para mensageria assíncrona.
- CI/CD: GitHub Actions para teste e deploy automático.
- Pipeline de agente: Utilização de uma ferramenta multiagente LangChain para o pipeline de agente e Banco Vetorial RAG Pinecone para aumento de contexto, garantindo que o sistema possa lidar com grandes volumes de dados e fornecer recomendações precisas e personalizadas para os usuários.
- Testes: Cobertura 100% de testes unitários e integração utilizando pytest.
- Huawei Health Kit para integração com a band de monitoramento de bpm.

In terms of AI:

- Crie um diretório separado para organizar os prompts do sistema, como a validação da percepção de esforço e a configuração de chamadas de ferramentas. Organize quais ferramentas você acha que o sistema precisará para trabalhar no conteúdo de treino e proximidade com a falha conforme descrito acima.
