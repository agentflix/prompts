1. Requisitos: O que a IA deve extrair da sua documentação
Para que a IA (atuando como profissional de UX/UI) gere o documento final, ela precisará analisar seus "docs" e identificar/inferir os seguintes requisitos:

Módulos Principais: As grandes áreas funcionais do seu sistema (ex: "Gestão de Usuários", "Checkout", "Dashboard Principal").

Jornadas/Fluxos do Usuário: As sequências de ações que um usuário realiza para atingir um objetivo dentro de um módulo (ex: "Fluxo de Cadastro", "Fluxo de Recuperação de Senha", "Fluxo de Adicionar Produto ao Carrinho").

Telas (Views): Cada "parada" ou interface visual necessária dentro de um fluxo.

Componentes de UI por Tela: Os blocos de construção de cada tela (ex: botões, formulários, modais, tabelas, cabeçalhos, menus de navegação).

Ações e Interações: O que acontece quando o usuário interage com um componente (ex: "Cliar no botão 'Salvar' dispara a validação do formulário e envia os dados para a API").

Estados da Tela/Componente: As diferentes aparências que uma tela ou componente pode ter (ex: estado de carregamento, estado de erro, estado vazio/inicial, estado de sucesso).

Dependências (Bibliotecas/Tecnologias): Quais ferramentas (sugeridas ou existentes) são necessárias para construir esses componentes (ex: "React", "Material-UI", "Font Awesome para ícones").

2. Modelo de Documento Técnico de UI/UX (.md)
Aqui está um modelo de documento que a IA pode preencher com base no prompt que você criou. Este modelo organiza as informações por Módulo, depois por Fluxo, e detalha cada Tela.


Modelo:
# Documentação Técnica de Layout, UI & UX

Este documento detalha as telas, componentes e fluxos de usuário necessários para a construção do **AgentFlix SaaS Web**.

---

## Módulo: Autenticação (Exemplo)

*Descrição breve do objetivo deste módulo: Gerenciamento de autenticação, login, cadastro e perfis de usuário.*

### Fluxo 1.1: Cadastro de Novo Usuário (Exemplo)

*Objetivo do fluxo: Permitir que um novo usuário crie uma conta na plataforma.*

#### Passo 1: Tela de Cadastro (View: `/cadastro`)

* **Objetivo da Tela:** Coletar as informações básicas do usuário para criação da conta.
* **Componentes de UI (daisyUI/Tailwind):**
    * `Navbar`: Cabeçalho padrão (componente `navbar` da daisyUI).
    * `Card`: Container principal do formulário (componente `card` com `card-body` e shadow `shadow-xl`).
    * `FormCadastro`: (usando `form-control` e `gap-4` do Tailwind).
        * `Input`: Campo "Nome Completo" (componente `input input-bordered w-full`).
        * `Input`: Campo "E-mail" (componente `input input-bordered w-full`).
        * `Input`: Campo "Senha" (componente `input input-bordered w-full` tipo password).
        * `Input`: Campo "Confirmar Senha" (componente `input input-bordered w-full`).
        * `Checkbox`: "Aceito os Termos de Uso" (componente `checkbox checkbox-primary`).
    * `Button`: Botão "Criar Conta" (componente `btn btn-primary w-full`).
    * `Link`: "Já tem uma conta? Faça login" (componente `link link-hover`).
    * `Footer`: Rodapé padrão (componente `footer footer-center`).

* **Ações e Interações (UX):**
    * **Ao Carregar:** Foco automático no campo "Nome Completo".
    * **Validação (Angular):** Uso de **Reactive Forms** para validação em tempo real (onBlur/onChange).
    * **Clique em "Criar Conta":**
        1.  Exibe um estado de `loading` no botão (classe `loading` no componente `btn`).
        2.  Envia dados (via `HttpClient` do Angular).
        3.  **Sucesso:** Redireciona para a Tela "Dashboard" (usando `Router` do Angular).
        4.  **Erro:** Exibe um `Alert` (componente `alert alert-error`).

* **Estados da Tela:**
    * **Padrão:** Formulário limpo.
    * **Carregando (Loading):** Botão "Criar Conta" com spinner (`loading`).
    * **Erro:** Exibição de mensagens de erro nos campos (ex: classes `input-error`) ou no `Alert` global.

---

#### Passo 2: Tela de Verificação de E-mail (View: `/cadastro/verificar`)

* **Objetivo da Tela:** Informar ao usuário que um e-mail foi enviado.
* **Componentes de UI (daisyUI/Tailwind):**
    * `Card`: Container centralizado (`card`).
    * `Icon`: Ícone de "E-mail Enviado" (ex: Heroicons, integrado via Tailwind).
    * `Text`: "Verifique sua caixa de entrada" (classes de tipografia do Tailwind).
    * `Link`: "Reenviar e-mail" (componente `link link-secondary`).
* **Ações e Interações (UX):**
    * **Verificação Confirmada:** Redireciona automaticamente para o "Dashboard" (`/dashboard`).

---

### Fluxo 1.2: Login de Usuário (Exemplo)

#### Passo 1: Tela de Login (View: `/login`)

* **Objetivo da Tela:** Permitir que usuários existentes acessem suas contas.
* **Componentes de UI (daisyUI/Tailwind):**
    * `Card` com `form-control`.
    * `Input`: Campo "E-mail" (`input input-bordered`).
    * `Input`: Campo "Senha" (`input input-bordered`).
    * `Link`: "Esqueci minha senha" (`link`).
    * `Button`: "Entrar" (`btn btn-primary`).
* **Ações e Interações (UX):**
    * **Clique em "Entrar":**
        1.  Estado de `loading` (`btn loading`).
        2.  **Sucesso:** Redireciona para `/dashboard`.
        3.  **Erro:** Exibe `Alert` (ex: `alert alert-warning`).

---

## Módulo: Dashboard (Exemplo)

*Descrição breve do objetivo deste módulo: Exibição principal de dados após o login.*

### Fluxo 2.1: Visualizar Dashboard Principal

#### Passo 1: Tela de Dashboard (View: `/dashboard`)

* **Objetivo da Tela:** Exibir um resumo das atividades ou dados do usuário.
* **Componentes de UI (daisyUI/Tailwind):**
    * `Layout`: Estrutura principal com `Sidebar` (pode usar o componente `Drawer` da daisyUI para mobile) e `Navbar`.
    * `Stats`: Componentes de estatísticas (componente `stats stats-vertical lg:stats-horizontal`).
    * `Table`: Tabela de dados recentes (componente `table w-full`).
    * `Button`: "Criar Novo Relatório" (componente `btn btn-secondary`).
* **Ações e Interações (UX):**
    * **Estado Vazio (Sem dados):** Exibir um "Empty State" (Placeholder) no lugar da tabela (um `Card` simples com texto).
    * **Estado Carregando:** Exibir `Skeletons` (componente `skeleton`) enquanto os dados carregam (ex: `skeleton h-4 w-full` para linhas da tabela).

---

## Considerações Técnicas e Bibliotecas

* **Framework/Biblioteca de UI:**
    * **Framework:** **Angular 19+** (Standalone Components, Signals).
    * **CSS:** **Tailwind CSS 4**.
    * **Biblioteca de Componentes:** **daisyUI 5** (rodando sobre o Tailwind).
* **Gerenciamento de Estado:** **Angular Signals** (padrão) e/ou **RxJS** para fluxos de dados complexos.
* **Biblioteca de Ícones:** **ng-lucide** (Lucide Icons para Angular).
* **Princípios de Design:** Mobile-first, uso do sistema de temas (Theming) da daisyUI para fácil customização (ex: light/dark).