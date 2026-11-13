# GitForesight: Documento de Defesa Técnica, Arquitetural e Ética

## 1. Visão Geral e Propósito do Projeto
O **GitForesight** é uma ferramenta desenvolvida no contexto de Trabalho de Conclusão de Curso (TCC) voltada para a análise preditiva e diagnóstica de riscos técnicos e organizacionais a partir do histórico de repositórios de software. Diferente de linters tradicionais que avaliam apenas o estado estático do código atual, o GitForesight minera metadados do Git (como frequência de commits, distribuição de autoria e evolução temporal) para identificar concentração de conhecimento, gargalos de manutenção e riscos estruturais.

---

## 2. O Que Foi Implementado (Escopo do MVP)
O MVP (Minimum Viable Product) atual foi estruturado para garantir robustez funcional, separação de responsabilidades e segurança na manipulação de dados de código-fonte. Os principais módulos implementados compreendem:

1. **Mecanismo de Autenticação Dual:**
   * **Login Tradicional (E-mail e Senha):** Permite o acesso ao ambiente interno do GitForesight para consulta de painéis, relatórios e futuras interações de equipe.
   * **Login via OAuth do GitHub:** Estabelece a identidade digital do usuário conectada à plataforma.
2. **Camada de Autorização e Integração com GitHub App (`choose_repo.py` e `github_installation.py`):**
   * Módulo dedicado à listagem e seleção de repositórios elegíveis.
   * Validação de permissões por meio de uma **GitHub App**, garantindo que a aplicação só acesse repositórios explicitamente autorizados pelo proprietário ou organização.
3. **Motor de Análise de Histórico (Git Mining):**
   * Extração segura de metadados do histórico de commits para cálculo de métricas e indicadores de risco técnico e organizacional.
4. **Infraestrutura de Segurança e Persistência:**
   * Banco de dados local para persistência de identidades e vínculos validados de instalações, mantendo tokens sensíveis e chaves criptográficas restritas ao ambiente de backend.

---

## 3. Justificativas Tecnológicas e Arquiteturais

### 3.1. Por que Streamlit (Python) como Stack Principal?
* **Justificativa:** O Python oferece o ecossistema mais maduro para manipulação de dados, automação e bibliotecas de processamento de repositórios Git (como `GitPython` ou ferramentas nativas de parsing de log). O **Streamlit** foi escolhido por sua agilidade na construção de aplicações orientadas a dados e dashboards interativos diretamente em Python, permitindo integrar de forma fluida a visualização de métricas de risco, o controle de estado de sessão e os fluxos de escolha de repositórios (`choose_repo.py`) sem a sobrecarga de manter um frontend separado em JavaScript.

### 3.2. Por que adotar uma GitHub App em vez de OAuth puro?
* **Problema:** O login OAuth tradicional fornece apenas um token de acesso genérico com escopos amplos ou limitados à identidade do usuário, mas falha em prover controle granular sobre *quais* repositórios específicos (públicos ou privados) a aplicação tem permissão para auditar.
* **Solução e Justificativa:** A adoção de uma **GitHub App** transfere o controle de autorização para o nível do repositório ou da organização. O proprietário seleciona explicitamente quais projetos a ferramenta pode enxergar. Isso mitiga riscos de vazamento de propriedade intelectual e atende ao princípio da **minimização de privilégios** (Security by Design).

### 3.3. Separação entre Autenticação no Sistema e Autorização de Código
* **Justificativa:** Separar o fluxo de "E-mail e Senha" do fluxo de "GitHub App" evita falsas premissas de segurança. Um usuário autenticado no sistema via credenciais tradicionais **não possui acesso automático** a nenhum repositório de código de terceiros. Para auditar um projeto, a vinculação e a instalação da GitHub App são obrigatoriamente exigidas no backend, impedindo o acesso não autorizado.

---

## 4. Conformidade Legal, Privacidade e LGPD

### 4.1. Tratamento de Metadados e LGPD (Lei nº 13.709/2018)
* **Contexto:** O histórico de commits do Git armazena dados pessoais (nomes, endereços de e-mail e carimbos de data/hora de contribuição). O GitForesight processa esses dados para calcular indicadores de risco e concentração de conhecimento.
* **Justificativa de Conformidade:**
  1. **Finalidade Estrita:** Os dados são coletados exclusivamente para a geração de métricas de saúde organizacional e técnica do repositório autorizado.
  2. **Minimização e Não-Armazenamento Bruto:** A aplicação evita o armazenamento desnecessário de cópias integrais do código-fonte nos servidores.
  3. **Direito de Exclusão:** O sistema prevê a capacidade de desconectar repositórios e expurgar os dados analisados mediante solicitação do usuário.

### 4.2. Uso Ético dos Indicadores de Risco
* **Justificativa:** Para afastar qualquer viés punitivo ou de vigilância invasiva, a arquitetura e a documentação do GitForesight estipulam formalmente que **os indicadores de risco gerados não devem ser utilizados para avaliação de desempenho individual de desenvolvedores**. O foco da ferramenta é estritamente a melhoria de processos organizacionais, arquiteturais e a mitigação de gargalos técnicos (como o *Bus Factor*).

---

## 5. Referências Bibliográficas e Técnicas de Apoio

1. **GITHUB DOCS.** *Building GitHub Apps*. Disponível em: <https://docs.github.com/en/apps>. Acesso em: 2026.
   * *Uso no projeto:* Fundamentação para a implementação da autenticação baseada em instalação e tokens de acesso restritos.
2. **STREAMLIT DOCS.** *Streamlit Documentation*. Disponível em: <https://docs.streamlit.io>. Acesso em: 2026.
   * *Uso no projeto:* Base para o desenvolvimento da interface interativa, gerenciamento de sessão e visualização dos indicadores analíticos em Python.
3. **BRASIL.** *Lei nº 13.709, de 14 de agosto de 2018. Lei Geral de Proteção de Dados Pessoais (LGPD)*. Brasília, DF.
   * *Uso no projeto:* Diretrizes para o tratamento ético e legal de metadados contendo informações de identificação pessoal (e-mails e nomes em commits).
4. **BASS, Len; CLEMENTS, Paul; KAZMAN, Rick.** *Software Architecture in Practice*. 3ª ed. Addison-Wesley Professional, 2012.
   * *Uso no projeto:* Base para a separação de responsabilidades entre as camadas de autenticação, autorização e motor de análise.
5. **FOWLER, Martin.** *Patterns of Enterprise Application Architecture*. Addison-Wesley, 2002.
   * *Uso no projeto:* Estruturação modular da lógica de negócio e persistência no backend em Python/Streamlit.