# Contrato de Agente para o Projeto Aurora

Este arquivo define as regras e diretrizes que você, ChatGPT Codex, deve seguir ao trabalhar no repositório do Projeto Aurora. O cumprimento destas diretrizes não é opcional; é um requisito para a conclusão de qualquer tarefa e para a criação de Pull Requests.

Este documento traduz os padrões do nosso "Manual de Boas Práticas" e da "Visão 360º da Aurora" para instruções diretas e acionáveis para você.

## 1. Estilo de Código (Code Style)

A consistência do estilo de código é crucial para a manutenibilidade do projeto.

* **Formatador de Código:** Todo o código Python DEVE ser formatado com `black` antes de ser submetido. Execute `black .` na raiz do projeto para garantir a formatação completa. Código não formatado será rejeitado.
* **Linter:** O código DEVE passar na verificação do `flake8` sem erros. Execute `flake8 .` para verificar violações de estilo, erros lógicos e complexidade excessiva.

## 2. Execução de Testes (Test Execution)

Um código só é considerado funcional se for comprovadamente testado.

* **Comando de Teste:** A suíte de testes completa, localizada no diretório `tests/`, DEVE ser executada com o comando `pytest tests/`.
* **Condição de Sucesso:** TODOS os testes DEVEM passar (exit code 0) para que uma tarefa seja considerada concluída e um Pull Request (PR) possa ser aberto. Se um teste falhar, sua prioridade é corrigir o código ou o teste.

## 3. Diretrizes de Refatoração e Design

Buscamos um código limpo, previsível e fácil de raciocinar a respeito. Ao refatorar ou criar novas funcionalidades, siga estes princípios de design:

* **Priorize a Imutabilidade:** Evite a modificação de estado de objetos e estruturas de dados sempre que possível. Em vez de alterar um objeto existente, crie uma nova instância com os valores atualizados.
* **Favoreça Funções Puras:** Construa funções que, para a mesma entrada, sempre produzem a mesma saída e não possuem efeitos colaterais observáveis (como modificar variáveis globais ou realizar I/O não explícito).
* **Padrão Repository:** Para toda lógica de acesso a dados (interação com bancos de dados, APIs externas de dados), utilize o padrão Repository. A lógica de negócio nos serviços DEVE interagir com as interfaces do repositório, não diretamente com ORMs ou drivers de banco de dados.

## 4. Padrão de Mensagens de Commit (Commit Message Standard)

Mensagens de commit claras são essenciais para a rastreabilidade e a geração automática de changelogs.

* **Padrão Obrigatório:** Todas as mensagens de commit DEVEM seguir o padrão de Commits Convencionais.
* **Formato:** `type(scope): description`
* **Exemplos:**
    * `feat(crm): adiciona endpoint para busca de clientes por email`
    * `fix(api): corrige tratamento de erro para CNPJs inválidos`
    * `refactor(auth): simplifica lógica de validação de token JWT`
    * `test(crm): adiciona testes de unidade para o novo serviço de cliente`
    * `docs(readme): atualiza instruções de instalação local`

## 5. Diretrizes de Implementação de Inteligência Artificial

A Aurora é uma IA. Seu código deve refletir essa natureza.

* **RAG (Retrieval-Augmented Generation):** Ao desenvolver funcionalidades que dependem de conhecimento externo ou para mitigar alucinações, projete componentes para integrar RAG. Isso implica:
    * Uso de **Bancos de Dados Vetoriais** para armazenamento e recuperação de embeddings.
    * Separação clara entre a lógica de `retrieval` (recuperação de contexto) e a de `generation` (geração de resposta pelo LLM/SLM).
    * Considerar mecanismos de cache para resultados de recuperação.
* **CoT (Chain-of-Thought):** Para tarefas complexas que exigem raciocínio multi-passo ou decomposição de problemas, estruture as interações com os modelos de linguagem para guiar o raciocínio explícito (e.g., "Passo 1:...", "Passo 2:...").
* **Agentes ReAct (Reason+Act):** Ao projetar funcionalidades que exigem autonomia e uso de ferramentas (APIs, funções internas, etc.), utilize o framework ReAct. Isso significa que o agente deve ser capaz de:
    * `Reason`: Planejar a sequência de ações com base na observação e no objetivo.
    * `Act`: Executar ferramentas ou funções externas.
    * Logar o processo de raciocínio e ação para depuração e auditoria.
* **Processamento de Linguagem Natural (PLN):**
    * Implemente as funcionalidades de PLN (NER, Classificação de Intenção, Análise de Sentimento, Sumarização) nos `services/nlp_service.py` ou módulos relacionados.
    * Priorize o uso de modelos **Small Language Models (SLMs)** ou modelos pré-treinados otimizados para Português (ex: BERTimbau) sempre que possível para tarefas específicas, visando otimização de custo e latência.
    * Garanta que a preparação e limpeza de texto (`utils/nlp_helpers.py`) sejam robustas.

## 6. Segurança e Gerenciamento de Segredos

A segurança é um pilar fundamental da Aurora.

* **NÃO HARDCODAR CREDENCIAIS:** NUNCA inclua chaves de API, senhas, tokens ou quaisquer informações sensíveis diretamente no código.
* **Variáveis de Ambiente:** Carregue todas as configurações sensíveis de variáveis de ambiente (ex: `os.getenv()`) ou sistemas de gerenciamento de segredos (ex: Azure Key Vault). O arquivo `config/settings.py` deve refletir isso.
* **Validação de Entrada:** Valide rigorosamente todas as entradas de usuário e de APIs externas para prevenir vulnerabilidades (ex: injeção de SQL, XSS, etc.).

## 7. Performance e Otimização de Custos

Desenvolva com a eficiência em mente.

* **Caching:** Implemente mecanismos de cache (ex: Redis) para resultados de chamadas caras (APIs externas, respostas de LLMs, resultados de recuperação de RAG) sempre que a estaticidade dos dados permitir.
* **Processamento em Lote (Batching):** Onde for aplicável, agrupe requisições para LLMs/APIs em lotes para reduzir latência e custos.
* **Escolha Estratégica de Modelos:** Para cada tarefa de IA, considere se um LLM grande e caro é realmente necessário, ou se um SLM menor, mais rápido e mais barato pode atender aos requisitos de desempenho e precisão. Use SLMs como primeira opção.

## 8. Tratamento de Erros e Logs

Garanta a robustez e a rastreabilidade.

* **Tratamento de Exceções:** Utilize blocos `try-except` para capturar e tratar exceções de forma controlada, seguindo o padrão definido em `core/exceptions.py`. Evite `except Exception: pass` genéricos.
* **Middleware de Erros:** As exceções devem ser capturadas e tratadas pelo middleware global de tratamento de erros (`core/middleware.py`), retornando respostas padronizadas e informativas para o cliente.
* **Logging Detalhado:** Implemente um logging robusto (ex: biblioteca `logging` do Python) para registrar eventos importantes, erros e informações de depuração. Logs de nível apropriado (DEBUG, INFO, WARNING, ERROR, CRITICAL) devem ser usados.
* **Logs de Raciocínio de IA:** Para componentes de IA (especialmente agentes ReAct e CoT), registre as etapas de raciocínio e as decisões tomadas para facilitar a depuração e o entendimento do comportamento do modelo.

Ao seguir estas diretrizes expandidas, o Codex terá um mapa muito mais claro e detalhado para construir a inteligência da Aurora de forma alinhada com os padrões de excelência que buscamos.

Por favor, substitua o conteúdo do seu `AGENTS.md` por esta versão e confirme quando o fizer.