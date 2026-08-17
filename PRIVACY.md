# Diretrizes de Privacidade e Conformidade LGPD / GDPR — LHCRM Pro

## 1. Princípios de Privacidade por Design (Privacy by Design)

O LHCRM Pro processa dados de contatos, leads e histórico de interações comerciais em estrita observância à **Lei Geral de Proteção de Dados (LGPD - Lei nº 13.709/2018)**:

1. **Minimização de Dados:** O sistema coleta estritamente os dados necessários para o atendimento comercial e análise executiva (Nome, E-mail, Telefone, Histórico de Status).
2. **Segregação de Dados:** Dados pertencentes a uma organização são rigorosamente isolados de outras empresas.
3. **Anonimização & Mascaramento:** Logs de aplicação não imprimem senhas, tokens de acesso completos ou detalhes de segredos de autenticação.

---

## 2. Direitos dos Titulares de Dados

- **Direito de Acesso e Exportação:** Os relatórios analíticos e dados do cliente podem ser exportados nos formatos JSON, CSV e HTML executivo a qualquer momento.
- **Direito ao Esquecimento / Exclusão de Tenant:**
  - A exclusão de uma organização (`Organization`) aciona a exclusão em cascata (`ON DELETE CASCADE`) no banco de dados, removendo integralmente membros, contatos, leads, tarefas, eventos e integrações associadas, sem deixar dados órfãos.

---

## 3. Segurança dos Dados em Repouso e em Trânsito

- **Em Trânsito:** Toda comunicação externa entre Frontend, Backend e Kommo CRM é realizada exclusivamente sobre **HTTPS / TLS 1.3**.
- **Em Repouso:** Senhas de usuários são cifradas com hash unidirecional **bcrypt** com salt individual. Tokens OAuth e segredos são armazenados em colunas dedicadas com permissões de leitura restritas no banco de dados.
