# 🚀 Guia de Integração — Kommo CRM ao Dashboard LHCRM

Este guia orienta passo a passo como conectar a sua conta do **Kommo CRM** à plataforma para permitir a sincronização automática de **Leads, Contatos, Empresas, Funis e Tarefas**.

---

## 📋 Passo 1: Criar a Integração no Kommo CRM

1. Acesse a sua conta no **Kommo CRM** (`https://suaempresa.kommo.com`).
2. No menu lateral esquerdo, navegue até **Configurações** ⚙️ > **Integrações**.
3. No canto superior direito, clique no botão **+ Criar Integração** *(ou "Teclas e integrações adicionais")*.
4. Preencha as informações básicas:
   - **Nome da Integração:** `Dashboard LHCRM` (ou o nome da sua preferência)
   - **Descrição:** `Integração de Métricas e Relatórios Executivos`
   - **URL de Redirecionamento (Redirect URI):**  
     `https://seu-backend.dominio.com/api/integrations/kommo/callback`  
     *(substitua pelo domínio oficial fornecido pelo suporte do sistema)*
   - **Conceder Acesso:** Selecione todas as permissões para leitura de Leads, Contatos, Empresas e Tarefas.
5. Clique em **Salvar**.

---

## 🔑 Passo 2: Copiar as Credenciais de Acesso

1. Após salvar a integração criada, abra a aba **Chaves e Escopo** *(Keys & Scopes)* dentro da própria integração.
2. Copie os seguintes códigos:
   - **ID da Integração** *(Client ID)*
   - **Chave Secreta** *(Secret Key / Client Secret)*

---

## 🔌 Passo 3: Conectar no Dashboard LHCRM

1. Acesse a plataforma **LHCRM**.
2. Abra a **Central de Integrações** no menu lateral *(ou pressione `Ctrl + K` e digite "Kommo CRM")*.
3. No card do **Kommo CRM**, clique no botão **Conectar Kommo CRM**.
4. No formulário que abrir, preencha:
   - **Subdomínio Kommo CRM:** Informe apenas o nome da sua conta (ex: se sua conta for `empresa.kommo.com`, digite apenas `empresa`).
   - **ID da Integração (Client ID):** Cole o ID gerado no Passo 2.
   - **Chave Secreta (Client Secret):** Cole a chave secreta gerada no Passo 2.
5. Clique em **Continuar Autorização OAuth**.
6. Uma janela do Kommo será exibida. Clique em **Autorizar** para confirmar a permissão de acesso.

---

## ✅ Passo 4: Sincronização Concluída

Após autorizar, você será redirecionado de volta ao Dashboard com o status **Conectado**.

- A partir deste momento, o sistema realizará a **sincronização automática** dos seus dados em segundo plano.
- Você também pode clicar a qualquer momento em **Sincronizar Agora** para atualizar métricas instantaneamente.

---

❓ **Dúvidas ou Suporte?**  
Se precisar de ajuda durante o processo, entre em contato com nossa equipe de suporte.
