# GitForesight — Política de Privacidade e Diretrizes Legais (LGPD / GDPR)

**Última Atualização:** Outubro de 2026  
**Versão:** 1.0  

---

## 1. Visão Geral e Propósito

O **GitForesight** é uma ferramenta analítica e preditiva projetada para transformar dados históricos de repositórios Git em simulações de risco técnico e organizacional (ex.: gargalos de conhecimento, hotspots de código e impacto na rotação de equipes). 

Este documento detalha o compromisso do GitForesight com a proteção de dados pessoais, privacidade dos desenvolvedores e conformidade com a **Lei Geral de Proteção de Dados (LGPD - Lei nº 13.709/2018)** e o **Regulamento Geral de Proteção de Dados (GDPR - Regulamento UE 2016/679)**.

---

## 2. Categorias de Dados Coletados e Processados

O GitForesight processa exclusivamente metadados contidos nos históricos de controle de versão (Git) e informações de autenticação do usuário do sistema:

1. **Dados Pessoais de Autores de Commits:**
   - Nome público do desenvolvedor/colaborador.
   - Endereço de e-mail associado às contribuições Git.
   - Timestamps (data e hora das alterações no repositório).

2. **Metadados Teconológicos e de Repositório:**
   - Hash dos commits, branchs, nomes de arquivos e trechos de diffs.
   - Volume de linhas adicionadas/removidas (*churn* de código).
   - Estatísticas agregadas de participação e dependência de módulos.

3. **Dados de Autenticação na Aplicação:**
   - Tokens de acesso OAuth / GitHub App (armazenados de forma segura e criptografada).
   - Permissões de escopo estritamente limitadas a acesso de leitura (`read-only`).

---

## 3. Hipóteses Legais de Tratamento (Bases Legais)

O processamento dos metadados de desenvolvedores pelo GitForesight baseia-se nas seguintes hipóteses legais previstas no Art. 7º da LGPD:

* **Legítimo Interesse da Organização (Art. 7º, IX):** Avaliação preventiva da saúde técnica do código-fonte, mitigação de riscos operacionais e continuidade de negócios da organização responsável pelo projeto de software.
* **Execução de Contrato de Trabalho ou Prestação de Serviços (Art. 7º, V):** Gestão e acompanhamento das entregas do ciclo de vida de desenvolvimento do sistema no âmbito profissional.

---

## 4. Princípios da Privacidade por Design (Privacy by Design)

O GitForesight adota as melhores práticas de *Privacy by Design* e segurança em sua arquitetura:

* **Minimização de Dados:** O sistema não extrai nem armazena o conteúdo integral de arquivos do repositório, focando estritamente em metadados necessários para cálculo de métricas e simulações.
* **Criptografia e Armazenamento Seguro:** Todos os tokens de acesso via GitHub App e dados de integração são criptografados em trânsito (TLS 1.3) e em repouso.
* **Escopo Estrito de Leitura:** O aplicativo requer apenas permissões de leitura nos repositórios, garantindo que não possa realizar alterações, merges ou pushes no código original.
* **Pseudonimização e Anonimização:** Suporte a opções de exibição pseudonimizada de autores de commits em dashboards compartilhados, protegendo a privacidade individual dos membros da equipe.

---

## 5. Uso Adequado e Restrições (Anti-Vigilância)

O GitForesight foi concebido estritamente para **análise de risco técnico e saúde arquitetural do software**. 

* **Proibição de Vigilância Individual:** É expressamente desencorajado o uso das métricas do GitForesight para ranqueamento punitivo, vigilância abusiva ou avaliação de desempenho individual descontextualizada de colaboradores.
* **Foco Organizacional:** As métricas de "concentração de conhecimento" visam identificar necessidade de *pairing*, documentação ou redistribuição de tarefas, e não responsabilização individual.

---

## 6. Direitos dos Titulares dos Dados

Em conformidade com o Art. 18 da LGPD, os colaboradores cujos e-mails/nomes figuram no histórico dos repositórios analisados possuem os seguintes direitos:

1. **Confirmação e Acesso:** Saber se seus metadados de commits estão sendo analisados pela instância do GitForesight.
2. **Pseudonimização em Relatórios:** Solicitar à organização administradora que seus dados identificáveis sejam mascarados em visualizações ou exportações públicas/gerenciais do dashboard.
3. **Exclusão de Dados de Autenticação:** Solicitar a remoção completa de credenciais e tokens de acesso associados à sua conta no sistema ao descontinuar a integração.

---

## 7. Isenção de Responsabilidade sobre Repositórios Terceirizados

O GitForesight opera com base nos repositórios expressamente autorizados pelo usuário ou pela empresa contratante. A garantia de que a análise dos repositórios cumpre as políticas internas de privacidade e os contratos de trabalho cabe à entidade controladora que autorizou o acesso do GitForesight aos projetos.
