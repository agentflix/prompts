# Especificação Técnica Completa — PrecificaAI

Aqui está o documento completo. É extenso como deve ser — a espinha dorsal do seu sistema.

```markdown
# PrecificaAI — Especificação Técnica Completa

## Documento de Referência do Produto

**Versão:** 1.0
**Data:** Junho 2025
**Classificação:** Documento Interno — Espinha Dorsal do Sistema
**Nome de Trabalho:** PrecificaAI (nome definitivo a ser validado)

---

# SUMÁRIO

1. [Introdução](#1-introdução)
2. [Visão do Produto](#2-visão-do-produto)
3. [Requisitos Funcionais](#3-requisitos-funcionais)
4. [Requisitos Não-Funcionais](#4-requisitos-não-funcionais)
5. [Módulos do Sistema](#5-módulos-do-sistema)
6. [Stack Tecnológica](#6-stack-tecnológica)
7. [Arquitetura de Software](#7-arquitetura-de-software)
8. [Modelagem de Banco de Dados](#8-modelagem-de-banco-de-dados)
9. [Diagramas de Fluxo](#9-diagramas-de-fluxo)
10. [Diagramas de Sequência](#10-diagramas-de-sequência)
11. [Integrações Externas](#11-integrações-externas)
12. [Inteligência Artificial — Especificação de Uso de LLM](#12-inteligência-artificial)
13. [Segurança](#13-segurança)
14. [Performance e Escalabilidade](#14-performance-e-escalabilidade)
15. [Roadmap de Evolução](#15-roadmap-de-evolução)

---

# 1. INTRODUÇÃO

## 1.1 Objetivo do Documento

Este documento é a especificação técnica e funcional completa do sistema PrecificaAI.
Ele serve como referência central para todo o desenvolvimento, sendo o DNA do sistema.
Toda decisão técnica, funcional e arquitetural deve estar alinhada com o que está descrito aqui.

Este documento deve ser usado como contexto para ferramentas de desenvolvimento assistido
por IA (Cursor, Claude, ChatGPT) durante a construção do sistema.

## 1.2 Glossário

| Termo | Definição |
|-------|-----------|
| **Tenant** | Uma conta/organização no sistema. Cada cliente que assina o PrecificaAI é um tenant. |
| **Seller** | O lojista/vendedor que é cliente do PrecificaAI. Sinônimo de tenant no contexto de negócio. |
| **Produto** | Um item do catálogo do seller, com SKU, preço e custo. |
| **Listing** | Um anúncio específico de um produto em um marketplace (ex: anúncio no Mercado Livre). |
| **Concorrente** | Outro vendedor que vende o mesmo produto ou produto equivalente. |
| **Coleta** | O processo de buscar preços atualizados dos concorrentes via APIs ou outras fontes. |
| **Diagnóstico** | Análise gerada pela IA que interpreta os dados coletados e produz recomendações. |
| **Score de Saúde** | Indicador de 0 a 100 que representa quão bem otimizado está o catálogo do seller. |
| **Faixa Competitiva** | Intervalo de preço em que o produto é considerado competitivo (entre -5% e +5% da média do mercado). |
| **Margem** | Diferença percentual entre preço de venda e custo do produto. |
| **MVP** | Minimum Viable Product — versão mínima do produto com valor suficiente para cobrar. |
| **Buy Box** | Destaque que o marketplace dá ao vendedor com melhor combinação de preço, frete e reputação. |
| **DDD** | Domain-Driven Design — abordagem de arquitetura orientada ao domínio do negócio. |
| **SOLID** | Conjunto de cinco princípios de design orientado a objetos. |
| **Bounded Context** | Fronteira lógica no DDD que delimita um subdomínio com linguagem e regras próprias. |

## 1.3 Público-Alvo do Documento

- O próprio desenvolvedor (autor do sistema)
- Ferramentas de IA assistentes de código (Cursor, Claude, ChatGPT)
- Eventuais futuros sócios ou desenvolvedores que entrem no projeto

---

# 2. VISÃO DO PRODUTO

## 2.1 O Que É

O PrecificaAI é uma plataforma SaaS (Software as a Service) de inteligência de preços
voltada para lojistas online — especificamente sellers de marketplaces e donos de
e-commerce. A plataforma utiliza inteligência artificial para analisar o catálogo do
lojista, comparar com os preços praticados pelo mercado e gerar recomendações
acionáveis de precificação.

## 2.2 O Problema Que Resolve

A maioria dos lojistas online precifica seus produtos de forma intuitiva, sem
metodologia. Eles não sabem com segurança:

- Se seus preços estão acima, abaixo ou na média do mercado
- Quais produtos estão perdendo vendas por preço alto
- Quais produtos poderiam ter o preço aumentado sem perder competitividade
- Como os preços dos concorrentes se movimentam ao longo do tempo
- Qual o impacto real de cada decisão de preço na sua margem

O resultado é perda de vendas (preço alto demais) ou perda de margem (preço baixo
demais) — ambos invisíveis para o lojista.

## 2.3 Proposta de Valor

**Tagline:**
"Inteligência artificial que monitora o mercado, analisa seus concorrentes e
recomenda os melhores preços para você vender mais e lucrar mais — no piloto automático."

**Promessa Central:**
Transformar dados de mercado em decisões de preço claras e acionáveis, com linguagem
simples e recomendações justificadas, sem exigir conhecimento técnico de pricing.

**O que NÃO prometemos:**
- Garantia de aumento de vendas (vendas dependem de múltiplos fatores)
- Garantia de posição em ranking de marketplace
- Projeções financeiras exatas
- Automação de alteração de preços (no MVP)

**O que prometemos com segurança:**
- Visão clara de posicionamento competitivo de cada produto
- Identificação de oportunidades de melhoria de margem
- Identificação de produtos com preço fora da faixa competitiva
- Histórico de movimentação de preços do mercado
- Recomendações fundamentadas em dados reais

## 2.4 Público-Alvo

**Persona Primária (MVP):**
Seller de Mercado Livre, pessoa física ou pequena empresa, com catálogo entre 20 e
2.000 produtos, que gerencia preços manualmente (planilha ou intuição), faturamento
mensal entre R$ 10.000 e R$ 500.000, sem equipe dedicada a pricing.

**Persona Secundária (Pós-MVP):**
Dono de e-commerce próprio (Tray, Shopify, Nuvemshop, WooCommerce) que vende
produtos que também são vendidos por concorrentes em outros sites e marketplaces.

**Persona Terciária (Futuro):**
Seller de Shopee, Amazon Brasil e outros marketplaces.

## 2.5 Modelo de Negócio

**Tipo:** SaaS com assinatura mensal recorrente.

**Planos:**

| Plano | Preço Mensal | Produtos | Concorrentes Monitorados | Coletas/Dia | Diagnósticos IA/Mês | Histórico |
|-------|-------------|----------|-------------------------|-------------|---------------------|-----------|
| Free | R$ 0 | 10 | 3 por produto | 1 | 1 | 7 dias |
| Starter | R$ 99 | 100 | 10 por produto | 2 | 4 | 30 dias |
| Professional | R$ 199 | 500 | 20 por produto | 4 | Ilimitado | 90 dias |
| Business | R$ 399 | 2.000 | Ilimitado | 8 | Ilimitado | 365 dias |

**Trial:** 14 dias no plano Professional sem necessidade de cartão de crédito.

**Política de Limites:** Ao atingir o limite do plano, o sistema não bloqueia o acesso,
mas exibe aviso de upgrade e impede a adição de novos produtos ou concorrentes até
que o plano seja atualizado ou itens sejam removidos.

---

# 3. REQUISITOS FUNCIONAIS

## 3.1 Lista Completa de Requisitos Funcionais

### Identidade e Acesso

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-001 | O sistema deve permitir registro de novo usuário com email e senha | MVP |
| RF-002 | O sistema deve permitir login com email e senha | MVP |
| RF-003 | O sistema deve permitir recuperação de senha via email | MVP |
| RF-004 | O sistema deve criar automaticamente um tenant (organização) ao registrar o primeiro usuário | MVP |
| RF-005 | O sistema deve permitir que o dono do tenant convide outros usuários por email | Pós-MVP |
| RF-006 | O sistema deve suportar dois perfis: Administrador e Membro | Pós-MVP |
| RF-007 | O sistema deve manter sessão ativa por 7 dias com refresh token | MVP |
| RF-008 | O sistema deve permitir login via Google OAuth | Pós-MVP |
| RF-009 | O sistema deve registrar log de último acesso do usuário | MVP |

### Catálogo de Produtos

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-010 | O sistema deve permitir cadastro manual de produto com: nome, SKU (opcional), preço de venda, custo, categoria | MVP |
| RF-011 | O sistema deve permitir importação em massa de produtos via arquivo CSV | MVP |
| RF-012 | O sistema deve validar e exibir erros detalhados na importação CSV | MVP |
| RF-013 | O sistema deve permitir edição de qualquer campo do produto | MVP |
| RF-014 | O sistema deve permitir exclusão de produto (soft delete) | MVP |
| RF-015 | O sistema deve calcular e exibir automaticamente a margem de cada produto com base no preço e custo | MVP |
| RF-016 | O sistema deve permitir categorizar produtos em categorias criadas pelo usuário | MVP |
| RF-017 | O sistema deve permitir busca e filtro de produtos por nome, SKU, categoria, faixa de preço e status competitivo | MVP |
| RF-018 | O sistema deve permitir vincular um produto a um ou mais anúncios do Mercado Livre (via URL ou ID do anúncio) | MVP |
| RF-019 | O sistema deve importar automaticamente dados do anúncio do ML ao vincular (título, preço, categoria ML) | MVP |
| RF-020 | O sistema deve permitir importação de produtos diretamente do Mercado Livre via API (para sellers que vendem no ML) | MVP |
| RF-021 | O sistema deve exibir um indicador visual do status competitivo de cada produto (acima, abaixo, na faixa) | MVP |
| RF-022 | O sistema deve permitir exportação do catálogo em CSV | Pós-MVP |
| RF-023 | O sistema deve suportar importação via integração com plataformas (Tray, Shopify, Nuvemshop) | Futuro |

### Monitoramento de Concorrência

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-030 | O sistema deve permitir vincular concorrentes a um produto específico | MVP |
| RF-031 | O sistema deve permitir buscar concorrentes automaticamente no Mercado Livre por palavra-chave ou EAN/GTIN | MVP |
| RF-032 | O sistema deve exibir a lista de concorrentes encontrados com: nome do seller, preço, frete, reputação, unidades vendidas | MVP |
| RF-033 | O sistema deve permitir que o usuário selecione quais concorrentes quer monitorar | MVP |
| RF-034 | O sistema deve permitir adicionar concorrente manualmente informando URL do anúncio | MVP |
| RF-035 | O sistema deve permitir entrada manual de preço de concorrente quando não houver API disponível | MVP |
| RF-036 | O sistema deve exibir para cada produto: menor preço, maior preço, preço médio e quantidade de concorrentes | MVP |
| RF-037 | O sistema deve calcular e exibir a diferença percentual entre o preço do seller e o menor preço/média | MVP |
| RF-038 | O sistema deve permitir remover um concorrente do monitoramento de um produto | MVP |
| RF-039 | O sistema deve buscar concorrentes no Google Shopping como fonte complementar | Pós-MVP |

### Coleta de Dados

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-040 | O sistema deve coletar preços dos concorrentes automaticamente via API do Mercado Livre | MVP |
| RF-041 | O sistema deve agendar coletas automáticas conforme a frequência do plano do tenant | MVP |
| RF-042 | O sistema deve armazenar cada coleta no histórico de preços com data, hora e fonte | MVP |
| RF-043 | O sistema deve registrar falhas de coleta e tentar novamente automaticamente (até 3 tentativas) | MVP |
| RF-044 | O sistema deve permitir que o usuário dispare uma coleta manual sob demanda | MVP |
| RF-045 | O sistema deve respeitar rate limits das APIs externas | MVP |
| RF-046 | O sistema deve exibir o status da última coleta (sucesso, falha, em andamento) para cada produto | MVP |
| RF-047 | O sistema deve coletar dados do Google Shopping como fonte complementar | Pós-MVP |

### Histórico e Gráficos

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-050 | O sistema deve armazenar histórico de preços de cada concorrente por produto | MVP |
| RF-051 | O sistema deve armazenar histórico de preços do próprio seller | MVP |
| RF-052 | O sistema deve exibir gráfico de linha com evolução de preço ao longo do tempo (seller vs concorrentes) | MVP |
| RF-053 | O sistema deve permitir filtrar o gráfico por período (7d, 30d, 90d, 365d) conforme limite do plano | MVP |
| RF-054 | O sistema deve destacar no gráfico momentos de mudança significativa de preço | Pós-MVP |
| RF-055 | O sistema deve manter histórico respeitando o limite de retenção do plano (7, 30, 90 ou 365 dias) | MVP |

### Inteligência de Preços (IA)

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-060 | O sistema deve gerar um Diagnóstico Inteligente do Catálogo analisando todos os produtos monitorados | MVP |
| RF-061 | O diagnóstico deve classificar cada produto em: acima do mercado, abaixo do mercado ou na faixa competitiva | MVP |
| RF-062 | O diagnóstico deve identificar os 5-10 produtos com maior oportunidade de otimização de preço | MVP |
| RF-063 | O diagnóstico deve identificar produtos com preço abaixo do mercado onde a margem pode ser aumentada | MVP |
| RF-064 | O diagnóstico deve calcular um Score de Saúde do Catálogo de 0 a 100 | MVP |
| RF-065 | O diagnóstico deve ser gerado em linguagem natural, em português, com tom consultivo | MVP |
| RF-066 | O diagnóstico deve apresentar justificativas baseadas em dados concretos para cada recomendação | MVP |
| RF-067 | O sistema deve gerar sugestão de preço para cada produto baseado nas regras configuradas pelo seller e dados do mercado | MVP |
| RF-068 | A sugestão de preço deve respeitar a margem mínima configurada pelo seller | MVP |
| RF-069 | O sistema deve permitir que o seller aceite ou rejeite cada sugestão individualmente | MVP |
| RF-070 | O sistema deve manter histórico de diagnósticos gerados | MVP |
| RF-071 | O sistema deve limitar a quantidade de diagnósticos conforme o plano | MVP |
| RF-072 | O sistema deve identificar tendências de preço (subindo, descendo, estável) com base no histórico | Pós-MVP |
| RF-073 | O sistema deve identificar padrões sazonais após acumular 6+ meses de dados | Futuro |

### Dashboard

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-080 | O sistema deve exibir um dashboard principal com visão geral do catálogo | MVP |
| RF-081 | O dashboard deve exibir: total de produtos, produtos monitorados, produtos acima/abaixo/na faixa | MVP |
| RF-082 | O dashboard deve exibir o Score de Saúde do Catálogo com indicador visual | MVP |
| RF-083 | O dashboard deve exibir lista dos produtos com maior oportunidade (quick wins) | MVP |
| RF-084 | O dashboard deve exibir últimos alertas recebidos | MVP |
| RF-085 | O dashboard deve exibir resumo de economia/ganho potencial identificado | MVP |
| RF-086 | O dashboard deve carregar em menos de 3 segundos | MVP |

### Alertas e Notificações

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-090 | O sistema deve permitir configurar alertas por produto ou para todo o catálogo | MVP |
| RF-091 | O sistema deve enviar alerta quando um concorrente alterar o preço acima de um percentual definido | MVP |
| RF-092 | O sistema deve enviar alerta quando o preço do seller ficar X% acima do menor preço do mercado | MVP |
| RF-093 | O sistema deve enviar alerta quando um novo concorrente for detectado para um produto | Pós-MVP |
| RF-094 | O sistema deve enviar alertas por email | MVP |
| RF-095 | O sistema deve manter central de notificações dentro da plataforma | MVP |
| RF-096 | O sistema deve permitir marcar notificações como lidas | MVP |
| RF-097 | O sistema deve permitir configurar frequência de alertas (imediato, diário resumido, semanal resumido) | MVP |
| RF-098 | O sistema deve enviar alertas via webhook (para integração com WhatsApp/Telegram no futuro) | Futuro |

### Regras de Precificação

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-100 | O sistema deve permitir configurar margem mínima global (aplicada a todos os produtos) | MVP |
| RF-101 | O sistema deve permitir configurar margem mínima por produto (sobrescreve a global) | MVP |
| RF-102 | O sistema deve permitir configurar estratégia de posicionamento: "X% abaixo do menor", "na média", "X% acima do menor" | MVP |
| RF-103 | O sistema deve permitir configurar estratégia por categoria de produto | Pós-MVP |
| RF-104 | O sistema deve usar as regras configuradas como base para gerar sugestões de preço | MVP |
| RF-105 | O sistema deve alertar quando uma regra entra em conflito (ex: posição desejada resultaria em margem abaixo da mínima) | MVP |

### Assinatura e Billing

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-110 | O sistema deve oferecer plano gratuito com limites reduzidos | MVP |
| RF-111 | O sistema deve permitir assinatura de plano pago via cartão de crédito | MVP |
| RF-112 | O sistema deve oferecer trial de 14 dias do plano Professional | MVP |
| RF-113 | O sistema deve permitir upgrade e downgrade de plano | MVP |
| RF-114 | O sistema deve bloquear funcionalidades que excedam o limite do plano (sem bloquear acesso) | MVP |
| RF-115 | O sistema deve enviar email 3 dias antes do fim do trial | MVP |
| RF-116 | O sistema deve exibir tela de upgrade quando o seller atingir um limite | MVP |
| RF-117 | O sistema deve processar cancelamento de assinatura com acesso até o fim do período pago | MVP |
| RF-118 | O sistema deve gerar e disponibilizar faturas/recibos | Pós-MVP |
| RF-119 | O sistema deve aceitar pagamento via Pix | Pós-MVP |

---

# 4. REQUISITOS NÃO-FUNCIONAIS

## 4.1 Performance

| ID | Requisito |
|----|-----------|
| RNF-001 | O dashboard deve carregar em no máximo 3 segundos com até 2.000 produtos |
| RNF-002 | A importação CSV deve processar 1.000 linhas em no máximo 30 segundos |
| RNF-003 | A busca de produtos deve retornar resultados em no máximo 500ms |
| RNF-004 | O sistema de coleta deve processar até 10.000 produtos por hora |
| RNF-005 | O gráfico de histórico deve renderizar em no máximo 2 segundos |
| RNF-006 | A geração do diagnóstico IA deve completar em no máximo 60 segundos |

## 4.2 Disponibilidade e Confiabilidade

| ID | Requisito |
|----|-----------|
| RNF-010 | O sistema deve ter disponibilidade mínima de 99% (downtime máximo: ~7h/mês) |
| RNF-011 | O sistema deve fazer backup automático do banco de dados diariamente |
| RNF-012 | O sistema deve ser capaz de recuperar dados de backup em até 4 horas |
| RNF-013 | Falhas na coleta de dados não devem impactar o funcionamento do restante do sistema |
| RNF-014 | O sistema deve registrar e monitorar todos os erros automaticamente |

## 4.3 Segurança

| ID | Requisito |
|----|-----------|
| RNF-020 | Todas as senhas devem ser armazenadas com hash bcrypt (custo mínimo 12) |
| RNF-021 | Toda comunicação deve ser feita via HTTPS/TLS |
| RNF-022 | Tokens de API devem ser armazenados criptografados no banco |
| RNF-023 | O sistema deve implementar rate limiting em todos os endpoints (60 req/min para autenticados, 20 req/min para não autenticados) |
| RNF-024 | O sistema deve validar e sanitizar toda entrada de dados do usuário |
| RNF-025 | O sistema deve implementar isolamento completo entre tenants (um tenant jamais acessa dados de outro) |
| RNF-026 | O sistema deve estar em conformidade com a LGPD |
| RNF-027 | Tokens JWT devem ter expiração máxima de 1 hora com refresh token de 7 dias |

## 4.4 Escalabilidade

| ID | Requisito |
|----|-----------|
| RNF-030 | O banco de dados deve suportar crescimento de 10 milhões de registros de histórico de preço por mês sem degradação |
| RNF-031 | A arquitetura deve permitir migração futura para múltiplos servidores sem reescrita |
| RNF-032 | O sistema de filas deve permitir processamento paralelo com múltiplos workers |
| RNF-033 | A tabela de histórico de preços deve usar particionamento por mês |

## 4.5 Manutenibilidade

| ID | Requisito |
|----|-----------|
| RNF-040 | O código deve seguir os princípios DDD com bounded contexts bem definidos |
| RNF-041 | O código deve seguir os princípios SOLID |
| RNF-042 | Toda regra de negócio deve estar na camada de domínio, nunca em controllers ou views |
| RNF-043 | O sistema deve ter migrations versionadas para toda alteração de banco |
| RNF-044 | O sistema deve ter documentação de API atualizada (OpenAPI/Swagger) |
| RNF-045 | O sistema deve ter logs estruturados com contexto suficiente para debug |

## 4.6 Usabilidade

| ID | Requisito |
|----|-----------|
| RNF-050 | A interface deve ser responsiva (desktop e tablet — mobile é secundário) |
| RNF-051 | O onboarding do primeiro produto deve ser concluído em no máximo 5 minutos |
| RNF-052 | Mensagens de erro devem ser claras e indicar como resolver o problema |
| RNF-053 | O sistema deve fornecer tooltips e textos de ajuda em campos complexos |
| RNF-054 | A interface deve seguir padrão visual consistente em todas as telas |

---

# 5. MÓDULOS DO SISTEMA

## 5.1 Módulo de Identidade e Acesso

### Propósito
Gerenciar autenticação, autorização e multi-tenancy. Cada conta no sistema
é um tenant isolado. O primeiro usuário que se registra é automaticamente o
administrador do tenant. Todo dado no sistema pertence a um tenant.

### Recursos Detalhados

#### 5.1.1 Registro de Conta

**O que faz:** Permite que um novo usuário crie uma conta no PrecificaAI.

**Para que serve:** É a porta de entrada do sistema. Ao se registrar, o
sistema cria automaticamente um tenant (organização) e associa o
usuário como administrador.

**O que esperar que faça:**
- Exibir formulário com campos: nome completo, email, senha, confirmação de senha
- Validar formato de email, força da senha (mínimo 8 caracteres, ao menos uma
  letra e um número) e se o email já não está cadastrado
- Criar o registro do tenant com nome padrão "Minha Loja" (editável depois)
- Criar o registro do usuário vinculado ao tenant
- Atribuir o plano Free automaticamente
- Enviar email de boas-vindas com link de confirmação
- Redirecionar para o onboarding após confirmação do email
- Registrar log de criação da conta

**Regras de negócio:**
- Um email só pode estar vinculado a uma conta
- O tenant é criado automaticamente — o usuário não precisa saber que ele existe
- O plano Free é atribuído automaticamente com seus limites
- O trial de 14 dias do plano Professional pode ser ativado a qualquer momento
  pelo usuário, mas não é ativado automaticamente

#### 5.1.2 Autenticação (Login)

**O que faz:** Permite que o usuário acesse sua conta com email e senha.

**Para que serve:** Proteger o acesso aos dados e garantir que cada
pessoa acesse apenas seu próprio tenant.

**O que esperar que faça:**
- Exibir formulário com email e senha
- Validar credenciais contra o banco
- Gerar token JWT com payload contendo: user_id, tenant_id, role
- Gerar refresh token com validade de 7 dias
- Redirecionar para o dashboard após login
- Em caso de falha, exibir "Email ou senha incorretos" (sem especificar qual)
- Após 5 tentativas falhas, bloquear temporariamente por 15 minutos
- Registrar log de login (sucesso ou falha) com IP e user-agent

#### 5.1.3 Recuperação de Senha

**O que faz:** Permite redefinir a senha quando o usuário a esquece.

**Para que serve:** Garantir que o usuário não perca acesso à conta.

**O que esperar que faça:**
- Exibir formulário pedindo o email
- Enviar email com link de redefinição (token com validade de 1 hora)
- Exibir formulário de nova senha ao clicar no link
- Validar força da nova senha
- Invalidar todas as sessões ativas ao redefinir a senha
- Exibir confirmação de sucesso e redirecionar para login

#### 5.1.4 Gestão de Perfil

**O que faz:** Permite que o usuário edite seus dados pessoais e do tenant.

**Para que serve:** Manter informações atualizadas.

**O que esperar que faça:**
- Editar nome completo
- Editar nome do tenant (nome da loja)
- Alterar senha (exigindo senha atual)
- Visualizar plano atual e uso de recursos
- Visualizar data de criação da conta

---

## 5.2 Módulo de Catálogo de Produtos

### Propósito
Centralizar todos os produtos do seller em um catálogo organizado dentro do
PrecificaAI. É o coração do sistema — sem produtos cadastrados, nenhuma
funcionalidade funciona. Este módulo deve tornar o cadastro o mais rápido
e indolor possível.

### Recursos Detalhados

#### 5.2.1 Cadastro Manual de Produto

**O que faz:** Permite adicionar um produto ao catálogo preenchendo os campos manualmente.

**Para que serve:** Método mais direto para sellers com poucos produtos ou para
adicionar produtos pontuais.

**O que esperar que faça:**
- Exibir formulário com os seguintes campos:
  - Nome do produto (obrigatório, texto, máx 255 caracteres)
  - SKU (opcional, texto, máx 50 caracteres, único dentro do tenant)
  - EAN/GTIN (opcional, numérico, 13 dígitos — usado para matching automático)
  - Preço de venda atual (obrigatório, decimal, maior que zero)
  - Custo do produto (opcional mas recomendado, decimal, maior ou igual a zero)
  - Categoria (opcional, select com categorias do tenant ou criação de nova)
  - URL da imagem (opcional, para referência visual)
  - Notas/observações (opcional, texto livre)
- Calcular e exibir automaticamente a margem em reais e percentual quando
  preço e custo estiverem preenchidos
- Salvar o produto vinculado ao tenant
- Redirecionar para a tela de vincular concorrentes após salvar
- Exibir mensagem de sucesso

**Regras de negócio:**
- O SKU deve ser único dentro do tenant (se informado)
- O EAN/GTIN deve ter formato válido (se informado)
- O preço deve ser maior que zero
- Se o custo for maior que o preço, exibir aviso (mas permitir salvar)
- Respeitar o limite de produtos do plano. Se no limite, exibir mensagem
  de upgrade ao invés do formulário
- A margem é calculada como: ((preco - custo) / preco) * 100

#### 5.2.2 Importação via CSV

**O que faz:** Permite adicionar múltiplos produtos de uma vez através de upload
de arquivo CSV ou Excel.

**Para que serve:** Sellers com muitos produtos precisam de uma forma rápida
de popular o catálogo. A maioria já tem seus produtos em planilha.

**O que esperar que faça:**
- Disponibilizar template de CSV para download com as colunas esperadas
- O template deve conter: nome, sku, ean, preco_venda, custo, categoria
- Aceitar upload de arquivo .csv, .xlsx e .xls (tamanho máximo: 5MB)
- Processar o arquivo em background (fila) para não bloquear a interface
- Exibir barra de progresso durante o processamento
- Ao finalizar, exibir relatório com:
  - Total de linhas processadas
  - Total importadas com sucesso
  - Total com erro (com detalhamento: linha X, erro Y)
  - Total ignoradas (duplicatas por SKU)
- Permitir que o usuário corrija e reimporte apenas as linhas com erro
- Não importar parcialmente em caso de erro crítico no arquivo (formato inválido)

**Regras de negócio:**
- A coluna "nome" é obrigatória. Linhas sem nome são rejeitadas
- A coluna "preco_venda" é obrigatória. Linhas sem preço são rejeitadas
- Se o SKU já existe no catálogo, a linha é ignorada (não sobrescreve)
- O total de produtos importados + existentes não pode exceder o limite do plano
- Se o arquivo exceder o limite do plano, importar até o limite e avisar

#### 5.2.3 Importação via Mercado Livre

**O que faz:** Permite que sellers que vendem no Mercado Livre importem seus
anúncios diretamente como produtos no catálogo.

**Para que serve:** Eliminar o trabalho manual de cadastro para sellers do ML.
O sistema puxa os dados automaticamente.

**O que esperar que faça:**
- Exibir botão "Conectar Mercado Livre"
- Redirecionar para autenticação OAuth do Mercado Livre
- Após autorização, listar todos os anúncios ativos do seller
- Permitir que o seller selecione quais anúncios quer importar
- Para cada anúncio selecionado, importar: título, preço, categoria ML, imagem,
  ID do anúncio, SKU (se configurado no ML)
- Criar o produto no catálogo com os dados importados
- Vincular automaticamente o anúncio do ML como listing do produto
- O custo NÃO vem do ML (o seller precisa informar manualmente depois)
- Exibir aviso: "Importe seus produtos e depois informe o custo de cada um
  para que possamos calcular suas margens"

**Regras de negócio:**
- A autorização OAuth do ML expira. O sistema deve renovar automaticamente
- Se o seller já importou um anúncio antes, não duplicar
- Anúncios pausados ou finalizados não são importados (apenas ativos)
- Respeitar limite de produtos do plano

#### 5.2.4 Listagem e Busca de Produtos

**O que faz:** Exibe todos os produtos do catálogo com filtros e busca.

**Para que serve:** Permitir que o seller encontre rapidamente qualquer
produto e veja o status competitivo de cada um.

**O que esperar que faça:**
- Exibir tabela paginada (20 itens por página) com colunas:
  - Nome do produto
  - SKU
  - Preço de venda
  - Custo
  - Margem (%)
  - Menor preço do mercado
  - Preço médio do mercado
  - Status competitivo (ícone: verde/amarelo/vermelho)
  - Qtd de concorrentes monitorados
  - Última coleta (data/hora)
- Permitir ordenar por qualquer coluna
- Permitir busca por texto (nome e SKU)
- Permitir filtro por:
  - Categoria
  - Status competitivo (acima, abaixo, na faixa)
  - Com/sem custo informado
  - Com/sem concorrentes vinculados
- Exibir contador: "Mostrando X de Y produtos"

**Regras de negócio:**
- Status competitivo é calculado como:
  - Verde (na faixa): preço do seller está entre -5% e +5% da média
  - Amarelo (atenção): preço do seller está entre +5% e +15% acima da média
  - Vermelho (acima): preço do seller está mais de +15% acima da média
  - Azul (abaixo): preço do seller está mais de 5% abaixo da média (oportunidade de margem)
- Produtos sem concorrentes vinculados aparecem como "cinza" (não monitorado)
- Dados de mercado exibidos são da última coleta bem-sucedida

#### 5.2.5 Detalhes do Produto

**O que faz:** Exibe todas as informações de um produto específico, incluindo
concorrentes, histórico de preços e posição no mercado.

**Para que serve:** É a visão profunda de um produto. O seller usa essa tela
para entender a situação competitiva de um item específico e tomar decisões.

**O que esperar que faça:**
- Exibir cabeçalho com: nome, SKU, EAN, preço, custo, margem, categoria, imagem
- Exibir seção "Posição no Mercado" com:
  - Menor preço encontrado e nome do seller
  - Maior preço encontrado
  - Preço médio
  - Posição do seller (ex: "3º menor preço de 15 sellers")
  - Diferença percentual do seller para o menor e para a média
- Exibir gráfico de histórico de preços (linha do tempo):
  - Linha do preço do seller
  - Linha do menor preço do mercado
  - Linha do preço médio do mercado
  - Filtro de período
- Exibir tabela de concorrentes vinculados com:
  - Nome/ID do seller concorrente
  - Preço atual
  - Variação desde a última coleta
  - Frete (se disponível)
  - Unidades vendidas (se disponível)
  - Reputação (se disponível)
- Exibir sugestão de preço da IA (se disponível) com justificativa
- Exibir botão para aceitar/rejeitar a sugestão
- Exibir botão para adicionar/remover concorrentes

#### 5.2.6 Edição de Produto

**O que faz:** Permite alterar os dados de um produto existente.

**Para que serve:** Atualizar preço de venda, custo, categoria ou qualquer
outro campo quando houver mudanças.

**O que esperar que faça:**
- Exibir formulário preenchido com dados atuais
- Permitir edição de todos os campos
- Ao alterar o preço de venda, registrar o preço anterior no histórico
- Ao alterar o custo, recalcular a margem automaticamente
- Exibir confirmação antes de salvar
- Registrar log da alteração (quem, quando, o que mudou)

**Regras de negócio:**
- Alteração de preço gera um novo registro no histórico de preços do seller
- Não é possível alterar o tenant_id do produto

#### 5.2.7 Exclusão de Produto

**O que faz:** Remove um produto do catálogo.

**Para que serve:** Limpar produtos descontinuados ou cadastrados por engano.

**O que esperar que faça:**
- Exibir confirmação: "Tem certeza? O histórico de preços será mantido por
  X dias e depois removido permanentemente."
- Realizar soft delete (campo deleted_at)
- Remover vínculos com concorrentes ativos
- Cancelar coletas agendadas para este produto
- Liberar a vaga no limite de produtos do plano

**Regras de negócio:**
- Soft delete: o produto não aparece mais na listagem mas os dados
  permanecem no banco pelo período de retenção do plano
- Após o período de retenção, um job de limpeza remove os dados permanentemente

---

## 5.3 Módulo de Monitoramento de Concorrência

### Propósito
Permitir que o seller vincule concorrentes a cada produto do seu catálogo e
mantenha visibilidade sobre os preços praticados pelo mercado. Este módulo é
a ponte entre o catálogo do seller e os dados de mercado.

### Recursos Detalhados

#### 5.3.1 Busca Automática de Concorrentes no Mercado Livre

**O que faz:** Busca automaticamente anúncios de outros sellers no Mercado Livre
que vendem o mesmo produto ou produto equivalente.

**Para que serve:** Facilitar a descoberta de concorrentes. Ao invés do seller
ter que encontrar e copiar URLs manualmente, o sistema busca por ele.

**O que esperar que faça:**
- A partir de um produto do catálogo, o seller clica em "Buscar Concorrentes"
- O sistema busca no ML usando as seguintes estratégias (em ordem de prioridade):
  1. Se o produto tem EAN/GTIN: busca por EAN (match exato)
  2. Se o produto veio do ML: busca na mesma categoria com termos do título
  3. Busca por palavras-chave do nome do produto
- Exibir lista de resultados com:
  - Título do anúncio
  - Nome do seller
  - Preço
  - Tipo de frete (Full, normal)
  - Quantidade vendida
  - Reputação do seller
  - Thumbnail da imagem
  - Indicador de confiança do match (alta/média/baixa)
- Permitir que o seller marque quais resultados são realmente concorrentes
- Ao confirmar, vincular os anúncios selecionados como concorrentes do produto

**Regras de negócio:**
- A busca por EAN retorna matches exatos e tem confiança alta
- A busca por palavras-chave pode retornar produtos diferentes — por isso
  o seller deve confirmar manualmente cada match
- Resultados que claramente são produtos diferentes (categoria diferente)
  devem ser filtrados automaticamente
- Respeitar o limite de concorrentes por produto do plano
- A busca é feita sob demanda (não automática) para economizar chamadas de API

#### 5.3.2 Adição Manual de Concorrente

**O que faz:** Permite que o seller adicione um concorrente manualmente
informando a URL do anúncio ou dados do concorrente.

**Para que serve:** Para casos em que a busca automática não encontrou um
concorrente conhecido, ou para concorrentes que estão fora do Mercado Livre.

**O que esperar que faça:**
- Opção A — Via URL do Mercado Livre:
  - O seller cola a URL do anúncio
  - O sistema extrai o ID do anúncio da URL
  - O sistema busca os dados via API do ML
  - Exibir dados para confirmação
  - Vincular ao produto
- Opção B — Entrada manual (para concorrentes fora do ML):
  - O seller informa: nome do concorrente, preço, URL da loja (opcional)
  - O sistema salva como concorrente manual
  - A coleta automática não funciona para concorrentes manuais
  - O seller deve atualizar o preço manualmente
  - Exibir indicador: "Preço informado manualmente em DD/MM/AAAA"

**Regras de negócio:**
- Concorrentes manuais são claramente diferenciados dos automáticos na interface
- Concorrentes manuais não entram na fila de coleta automática
- A URL deve ser válida e pertencer ao domínio mercadolivre.com.br
  (se for do tipo ML)

#### 5.3.3 Gestão de Concorrentes por Produto

**O que faz:** Exibe e permite gerenciar todos os concorrentes vinculados a
um produto específico.

**Para que serve:** O seller precisa ver de forma rápida quem são seus
concorrentes em cada produto e como estão os preços.

**O que esperar que faça:**
- Exibir tabela de concorrentes do produto com:
  - Nome/ID do seller concorrente
  - Preço atual
  - Variação de preço desde a última coleta (% e R$)
  - Diferença para o preço do seller (% e R$)
  - Frete
  - Unidades vendidas
  - Reputação
  - Tipo (automático ML / manual)
  - Data da última atualização de preço
- Permitir ordenar por preço, variação ou vendas
- Permitir remover concorrente do monitoramento
- Exibir resumo: menor, maior, média, mediana dos preços
- Destacar visualmente o preço do seller na tabela para comparação rápida

---

## 5.4 Módulo de Coleta de Dados

### Propósito
Buscar e armazenar preços atualizados dos concorrentes de forma automatizada
e confiável. Este módulo é o motor silencioso do sistema — roda em background,
sem interação do usuário, alimentando todas as outras funcionalidades com
dados frescos.

### Recursos Detalhados

#### 5.4.1 Coleta Automática Agendada

**O que faz:** Executa jobs periódicos que buscam preços atualizados de todos
os concorrentes vinculados a produtos dos tenants ativos.

**Para que serve:** Manter os dados de preço atualizados sem que o seller
precise fazer nada.

**O que esperar que faça:**
- Um scheduler (cron) dispara jobs de coleta conforme a frequência do plano:
  - Free: 1x por dia (às 06:00)
  - Starter: 2x por dia (06:00 e 18:00)
  - Professional: 4x por dia (06:00, 12:00, 18:00, 00:00)
  - Business: 8x por dia (a cada 3 horas)
- Para cada tenant, o job:
  1. Lista todos os produtos com concorrentes vinculados do tipo automático
  2. Para cada concorrente, faz chamada à API do Mercado Livre
  3. Extrai: preço atual, frete, estoque, vendas
  4. Compara com o último preço coletado
  5. Se houve mudança, registra no histórico
  6. Se não houve mudança, atualiza apenas o timestamp da última verificação
  7. Se houve erro, registra a falha e agenda retry
- O processamento deve ser feito via fila (queue) para não bloquear o sistema
- Cada coleta individual deve ser um job separado na fila (paralelismo)

**Regras de negócio:**
- Respeitar o rate limit da API do Mercado Livre (máximo de chamadas por segundo)
- Implementar backoff exponencial em caso de rate limiting (429)
- Em caso de falha, tentar novamente até 3 vezes com intervalo crescente
  (1 min, 5 min, 15 min)
- Após 3 falhas consecutivas, marcar o concorrente como "com problema" e notificar
- Não coletar dados de tenants com assinatura expirada/cancelada
- Não coletar dados de produtos soft-deleted
- Priorizar coleta de tenants pagantes sobre tenants free

#### 5.4.2 Coleta Manual (Sob Demanda)

**O que faz:** Permite que o seller dispare uma atualização de preços imediatamente,
sem esperar a coleta automática.

**Para que serve:** Quando o seller precisa de dados frescos agora — por exemplo,
antes de tomar uma decisão de preço.

**O que esperar que faça:**
- Botão "Atualizar Preços" disponível na tela de detalhes do produto
- Botão "Atualizar Tudo" disponível no dashboard (atualiza todos os produtos)
- Ao clicar, enfileira jobs de coleta com prioridade alta
- Exibir indicador de "atualizando..." enquanto processa
- Ao finalizar, atualizar os dados na tela automaticamente
- Se houver erro, exibir mensagem: "Não foi possível atualizar X de Y concorrentes"

**Regras de negócio:**
- Limitar coletas manuais a 10 por dia no plano Free, ilimitado nos pagos
- Não permitir disparar nova coleta se já houver uma em andamento para o mesmo produto
- Coletas manuais não resetam o timer da coleta automática

#### 5.4.3 Armazenamento de Histórico

**O que faz:** Registra cada datapoint de preço coletado para construir
a linha do tempo.

**Para que serve:** O histórico é o que permite ver tendências, gráficos de
evolução e detectar padrões ao longo do tempo.

**O que esperar que faça:**
- Para cada coleta bem-sucedida, gravar um registro contendo:
  - ID do produto
  - ID do concorrente
  - Preço coletado
  - Preço de frete (se disponível)
  - Unidades vendidas no momento da coleta
  - Fonte dos dados (mercadolivre_api, google_shopping, manual)
  - Timestamp da coleta
- Os dados devem ser armazenados em tabela particionada por mês
- Dados mais antigos que o limite do plano devem ser agregados (média diária)
  ao invés de deletados, para manter tendências

**Regras de negócio:**
- Mesmo que o preço não tenha mudado, registrar pelo menos 1 datapoint por dia
  para manter a continuidade do gráfico
- Quando o preço muda, registrar imediatamente (não esperar o próximo ciclo)
- A retenção granular (cada coleta) respeita o plano. Após o período,
  os dados são consolidados em médias diárias

#### 5.4.4 Monitoramento de Saúde da Coleta

**O que faz:** Monitora se as coletas estão funcionando corretamente e
identifica problemas.

**Para que serve:** O seller precisa confiar que os dados estão atualizados.
Se a coleta falhar silenciosamente, toda a plataforma perde valor.

**O que esperar que faça:**
- Exibir na interface de cada produto a data/hora da última coleta bem-sucedida
- Se a última coleta tem mais de 24 horas, exibir aviso: "Dados podem estar desatualizados"
- Se um concorrente específico falhou 3 vezes consecutivas, exibir alerta
- Registrar métricas internas: taxa de sucesso, tempo médio de coleta, erros por tipo
- Alertar o administrador do sistema (você) em caso de falha sistêmica

---

## 5.5 Módulo de Inteligência de Preços (IA)

### Propósito
Este é o módulo diferencial do PrecificaAI. Ele transforma dados brutos (preços,
margens, concorrentes) em inteligência acionável usando LLM (Large Language Model).
O objetivo não é apenas mostrar números, mas interpretar os números e recomendar
ações como um consultor de pricing faria.

### Recursos Detalhados

#### 5.5.1 Diagnóstico Inteligente do Catálogo

**O que faz:** Gera uma análise completa e contextualizada de todo o catálogo
do seller, escrita em linguagem natural por IA.

**Para que serve:** É o principal entregável diferencial do produto. O seller
recebe um relatório que parece ter sido escrito por um consultor humano,
mas é gerado automaticamente.

**O que esperar que faça:**
- O seller clica em "Gerar Diagnóstico" ou o diagnóstico é gerado
  automaticamente (semanal para planos pagos)
- O sistema coleta os seguintes dados para enviar ao LLM:
  - Lista de todos os produtos com: preço, custo, margem, categoria
  - Para cada produto: menor preço do mercado, média, posição do seller,
    quantidade de concorrentes, volume de vendas do líder
  - Regras de precificação configuradas pelo seller (margem mínima, estratégia)
  - Dados do diagnóstico anterior (se houver) para comparação de evolução
- O LLM recebe esses dados estruturados e gera um relatório com as
  seguintes seções:

  **Seção 1 — Resumo Executivo**
  Visão geral em 3-4 parágrafos: como está o catálogo, quantos produtos foram
  analisados, situação geral.

  **Seção 2 — Score de Saúde do Catálogo**
  Nota de 0 a 100 com explicação do que compõe o score.
  O score é calculado pela aplicação (não pelo LLM) com a seguinte fórmula:
  - Percentual de produtos na faixa competitiva × 40
  - Percentual de produtos com margem acima da mínima × 30
  - Percentual de produtos com concorrentes monitorados × 20
  - Percentual de produtos com custo informado × 10
  O LLM recebe o score calculado e gera a explicação contextualizada.

  **Seção 3 — Produtos Perdendo Competitividade**
  Lista dos produtos com preço acima do mercado, priorizados por:
  - Maior diferença percentual em relação à média
  - Maior volume de vendas dos concorrentes (indica demanda alta)
  Para cada produto: descrição do problema, dados comparativos, impacto estimado.

  **Seção 4 — Oportunidades de Aumento de Margem**
  Lista dos produtos com preço abaixo do mercado onde o seller pode
  aumentar o preço sem perder competitividade.
  Para cada produto: preço atual, média do mercado, sugestão de novo preço,
  nova margem resultante.

  **Seção 5 — Visão por Categoria**
  Análise agrupada por categoria: quais categorias estão bem posicionadas
  e quais precisam de atenção.

  **Seção 6 — Recomendações Prioritárias**
  Lista de 3 a 5 ações concretas priorizadas por impacto estimado.
  Cada recomendação deve ter: o que fazer, por que fazer, resultado esperado.

- O relatório é salvo no banco e exibido na interface com formatação rica
- O seller pode gerar PDF do relatório para compartilhar

**Regras de negócio:**
- O diagnóstico só pode ser gerado se houver pelo menos 5 produtos com
  concorrentes monitorados e pelo menos 1 coleta realizada
- O LLM não inventa dados. Toda afirmação deve ser baseada nos dados
  fornecidos no prompt
- Projeções devem ser apresentadas como estimativas com linguagem cautelosa:
  "potencialmente", "estimamos", "é provável que"
- O diagnóstico nunca sugere preço abaixo da margem mínima configurada
- A quantidade de diagnósticos respeita o limite do plano
- O processamento é feito em background (fila) e o seller é notificado
  quando ficar pronto

#### 5.5.2 Sugestão de Preço por Produto

**O que faz:** Para cada produto individualmente, calcula e sugere um preço
otimizado com base nos dados do mercado e nas regras do seller.

**Para que serve:** Dar ao seller uma recomendação específica e acionável
para cada produto do catálogo.

**O que esperar que faça:**
- Para cada produto que tem concorrentes monitorados e pelo menos 1 coleta,
  o sistema calcula automaticamente um preço sugerido
- O cálculo segue esta lógica (executada pela aplicação, não pelo LLM):
  1. Buscar a regra de precificação aplicável (produto > categoria > global)
  2. Obter menor preço, média e mediana dos concorrentes
  3. Calcular o preço conforme a estratégia escolhida:
     - "X% abaixo do menor": menor_preco × (1 - X/100)
     - "Na média": media_precos
     - "X% acima do menor": menor_preco × (1 + X/100)
  4. Verificar se o preço calculado respeita a margem mínima:
     - preco_sugerido deve ser >= custo × (1 + margem_minima/100)
  5. Se não respeita, ajustar para o preço mínimo que garante a margem
     e sinalizar conflito de regras
  6. Calcular a nova margem resultante
- O resultado é exibido na tela do produto como:
  - Preço sugerido: R$ XXX
  - Margem resultante: XX%
  - Motivo: "Baseado na sua regra de ficar 5% abaixo do menor preço (R$ YYY)"
  - Se houver conflito: "A regra de posicionamento resultaria em R$ ZZZ,
    mas isso viola sua margem mínima de XX%. Sugerimos R$ WWW."
- O seller pode: aceitar (atualiza o preço no catálogo) ou rejeitar (descarta)

**Regras de negócio:**
- A sugestão é recalculada automaticamente após cada coleta
- Aceitar a sugestão atualiza o preço no catálogo do PrecificaAI, NÃO altera
  o preço no marketplace automaticamente (no MVP)
- O histórico de sugestões aceitas e rejeitadas é mantido
- Produtos sem custo informado não recebem sugestão (pois não é possível
  calcular margem) — exibir aviso pedindo para informar o custo

#### 5.5.3 Score de Saúde do Catálogo

**O que faz:** Calcula e exibe um indicador numérico de 0 a 100 que representa
quão otimizado está o catálogo do seller.

**Para que serve:** Dar ao seller uma métrica única e fácil de entender sobre
a qualidade da sua precificação. Funciona como um "termômetro" motivacional
que incentiva o seller a otimizar continuamente.

**O que esperar que faça:**
- Calcular o score automaticamente após cada ciclo de coleta
- Exibir no dashboard com indicador visual:
  - 0-40: Vermelho — "Seu catálogo precisa de atenção urgente"
  - 41-60: Laranja — "Há oportunidades significativas de melhoria"
  - 61-80: Amarelo — "Seu catálogo está razoável, mas pode melhorar"
  - 81-100: Verde — "Seu catálogo está bem otimizado"
- Exibir evolução do score ao longo do tempo (mini-gráfico)
- Exibir breakdown do score: quais fatores estão puxando para cima/baixo

**Fórmula de cálculo:**
- Componente 1 (peso 40%): Percentual de produtos na faixa competitiva
  (entre -5% e +5% da média do mercado)
- Componente 2 (peso 30%): Percentual de produtos com margem acima da
  margem mínima configurada
- Componente 3 (peso 20%): Percentual de produtos com concorrentes monitorados
  (cobertura do monitoramento)
- Componente 4 (peso 10%): Percentual de produtos com custo informado
  (qualidade dos dados)

**Regras de negócio:**
- O score só é calculado se houver pelo menos 5 produtos no catálogo
- Produtos sem concorrentes não penalizam os componentes 1 e 2 (são ignorados)
  mas penalizam o componente 3
- O score é recalculado a cada ciclo de coleta e armazenado no histórico

---

## 5.6 Módulo de Dashboard

### Propósito
Ser a tela inicial do sistema — o lugar onde o seller pousa após fazer login.
Deve comunicar instantaneamente o estado geral do seu catálogo e direcionar
a atenção para o que é mais importante.

### Recursos Detalhados

#### 5.6.1 Painel Principal

**O que faz:** Exibe cards de resumo, gráficos e listas priorizadas que
dão ao seller uma visão instantânea do seu negócio sob a ótica de preço.

**Para que serve:** Responder em 10 segundos a pergunta: "Como estão
meus preços hoje?"

**O que esperar que faça:**

**Linha 1 — Cards de Resumo:**
- Total de produtos no catálogo
- Total de produtos monitorados (com concorrentes)
- Score de Saúde do Catálogo (com cor e mini-trend)
- Margem média do catálogo

**Linha 2 — Distribuição Competitiva:**
- Gráfico de donut mostrando:
  - X% na faixa competitiva (verde)
  - X% acima do mercado (vermelho)
  - X% abaixo do mercado (azul)
  - X% não monitorados (cinza)
- Cada fatia é clicável e filtra a lista de produtos

**Linha 3 — Quick Wins (Oportunidades Rápidas):**
- Lista dos 5 produtos com maior oportunidade de otimização
- Para cada um: nome, preço atual, preço sugerido, ganho potencial de margem
- Botão "Ver detalhes" em cada item
- Lógica de priorização:
  1. Produtos abaixo do mercado com maior margem desperdiçada
  2. Produtos acima do mercado com maior volume de vendas nos concorrentes

**Linha 4 — Últimos Alertas:**
- Lista dos 5 alertas mais recentes
- Para cada um: tipo, produto afetado, resumo, data/hora
- Link "Ver todos os alertas"

**Linha 5 — Último Diagnóstico:**
- Resumo do último diagnóstico gerado (primeiros 2-3 parágrafos)
- Data de geração
- Botão "Ver diagnóstico completo"
- Botão "Gerar novo diagnóstico" (se disponível no plano)

---

## 5.7 Módulo de Alertas e Notificações

### Propósito
Informar o seller proativamente quando algo relevante acontece no mercado,
sem que ele precise entrar no sistema para verificar. Alertas são o recurso
que mantém o seller engajado e percebendo valor contínuo.

### Recursos Detalhados

#### 5.7.1 Configuração de Regras de Alerta

**O que faz:** Permite que o seller defina em quais situações quer ser alertado.

**Para que serve:** Cada seller tem sensibilidades diferentes. Alguns querem
saber de qualquer mudança, outros só querem saber de mudanças grandes.

**O que esperar que faça:**
- Exibir tela de configuração com os seguintes tipos de alerta:
  - **Queda de preço do concorrente:** Alertar quando qualquer concorrente
    baixar o preço em mais de X% (configurável, padrão: 5%)
  - **Aumento de preço do concorrente:** Alertar quando qualquer concorrente
    aumentar o preço em mais de X% (configurável, padrão: 10%)
  - **Produto fora da faixa:** Alertar quando meu produto ficar mais de X%
    acima da média do mercado (configurável, padrão: 10%)
  - **Oportunidade de margem:** Alertar quando meu produto estiver mais de X%
    abaixo da média (configurável, padrão: 10%)
- Para cada tipo, permitir: ativar/desativar e configurar o threshold
- Configurar escopo: aplicar a todos os produtos ou a produtos/categorias específicas
- Configurar frequência de entrega:
  - Imediato (a cada coleta que detectar a condição)
  - Resumo diário (1 email por dia com todos os alertas do dia)
  - Resumo semanal (1 email por semana)

#### 5.7.2 Central de Notificações

**O que faz:** Lista todas as notificações geradas dentro do sistema.

**Para que serve:** Registro histórico de tudo que aconteceu, acessível
a qualquer momento dentro da plataforma.

**O que esperar que faça:**
- Exibir ícone de sino no header com badge de contagem de não-lidas
- Ao clicar, exibir dropdown com as 10 notificações mais recentes
- Link "Ver todas" que abre página completa de notificações
- Cada notificação contém: tipo (ícone), título resumido, data/hora
- Clicar na notificação redireciona para o produto relacionado
- Permitir marcar como lida (individual e "marcar todas como lidas")
- Paginação na página completa

#### 5.7.3 Envio de Alertas por Email

**O que faz:** Envia emails quando condições de alerta são detectadas.

**Para que serve:** O seller não precisa estar logado para saber o que
está acontecendo.

**O que esperar que faça:**
- Emails com template profissional e responsivo
- Para alertas imediatos: 1 email por alerta
- Para resumo diário: 1 email consolidado às 08:00 com todos os
  alertas das últimas 24 horas
- Para resumo semanal: 1 email às segundas-feiras 08:00
- Cada email contém: nome do produto, o que mudou, dados comparativos,
  link direto para o produto no sistema
- Link de unsubscribe em todos os emails
- Opção de configurar alertas no perfil do usuário

**Regras de negócio:**
- Não enviar email se não houver alertas no período (diário/semanal)
- Máximo de 50 emails imediatos por dia por tenant (para evitar spam)
- Se exceder, agrupar em um resumo

---

## 5.8 Módulo de Relatórios

### Propósito
Disponibilizar o diagnóstico e análises de forma organizada e acessível,
com histórico de diagnósticos anteriores.

### Recursos Detalhados

#### 5.8.1 Lista de Diagnósticos

**O que faz:** Exibe o histórico de todos os diagnósticos IA gerados.

**Para que serve:** Permitir que o seller compare a evolução do seu
catálogo ao longo do tempo.

**O que esperar que faça:**
- Lista paginada com: data de geração, score na data, resumo (1 linha), status
- Clicar abre o diagnóstico completo
- Exibir gráfico de evolução do score ao longo dos diagnósticos

#### 5.8.2 Visualização do Diagnóstico

**O que faz:** Exibe o diagnóstico completo gerado pela IA.

**Para que serve:** É onde o seller consome a análise detalhada.

**O que esperar que faça:**
- Exibir o relatório completo com formatação rica (markdown renderizado)
- Todas as seções descritas no item 5.5.1
- Botão de exportar em PDF
- Botão de gerar novo diagnóstico (se disponível no plano)

---

## 5.9 Módulo de Assinatura e Billing

### Propósito
Gerenciar os planos de assinatura, pagamentos e limites de uso.
Toda a parte financeira é delegada ao Stripe — o sistema apenas
orquestra e controla limites.

### Recursos Detalhados

#### 5.9.1 Tela de Planos e Preços

**O que faz:** Exibe os planos disponíveis com comparativo de recursos.

**Para que serve:** Permitir que o seller escolha o plano adequado
ou faça upgrade quando atingir limites.

**O que esperar que faça:**
- Exibir tabela comparativa dos 4 planos com todos os limites
- Destacar o plano atual do seller
- Botão "Assinar" ou "Fazer Upgrade" em cada plano
- Ao clicar, redirecionar para checkout do Stripe
- Exibir banner de trial se disponível

#### 5.9.2 Controle de Limites

**O que faz:** Monitora o uso de recursos em relação ao plano contratado.

**Para que serve:** Impedir uso acima do plano e incentivar upgrade de
forma não-agressiva.

**O que esperar que faça:**
- Verificar limites antes de cada ação que consome recurso:
  - Cadastro de produto → verificar limite de produtos
  - Adição de concorrente → verificar limite de concorrentes
  - Gerar diagnóstico → verificar limite de diagnósticos
  - Coleta manual → verificar limite de coletas manuais
- Ao atingir limite:
  - Não bloquear o acesso ao sistema
  - Bloquear apenas a ação que excede o limite
  - Exibir modal amigável: "Você atingiu o limite de X do seu plano.
    Faça upgrade para continuar adicionando."
- Exibir barra de uso no menu lateral: "42/100 produtos utilizados"

#### 5.9.3 Gestão de Assinatura

**O que faz:** Permite que o seller gerencie sua assinatura.

**Para que serve:** Autonomia para upgrade, downgrade e cancelamento.

**O que esperar que faça:**
- Exibir plano atual, data de renovação, valor, método de pagamento
- Botão "Gerenciar assinatura" que abre o portal do Stripe
- No portal do Stripe, o seller pode:
  - Alterar cartão de crédito
  - Fazer upgrade ou downgrade
  - Cancelar assinatura
- Ao cancelar:
  - Acesso mantido até o fim do período pago
  - Após o período, conta rebaixada para plano Free
  - Dados não são deletados, mas funcionalidades ficam limitadas
  - Se o seller tinha mais produtos do que o Free permite, os dados são
    mantidos mas ele não pode adicionar novos até ficar dentro do limite

---

## 5.10 Módulo de Configurações e Regras

### Propósito
Centralizar todas as configurações do tenant: regras de precificação,
integrações e preferências.

### Recursos Detalhados

#### 5.10.1 Regras de Precificação

**O que faz:** Define as regras que o sistema usa para gerar sugestões de preço.

**Para que serve:** Cada seller tem uma estratégia diferente. As regras
permitem personalizar as sugestões.

**O que esperar que faça:**
- Configuração global (aplica a todos os produtos):
  - Margem mínima (%): o sistema nunca sugere preço com margem abaixo disso
  - Estratégia de posicionamento:
    - "X% abaixo do menor preço" (padrão)
    - "Na média do mercado"
    - "X% acima do menor preço"
  - Valor de X configurável (padrão: 5%)
- Configuração por categoria (sobrescreve global):
  - Mesmos campos, aplicados apenas à categoria selecionada
- Configuração por produto (sobrescreve categoria e global):
  - Mesmos campos, aplicados apenas ao produto selecionado
- Exibir hierarquia de regras: "Este produto usa a regra: [Produto > Categoria > Global]"

#### 5.10.2 Integrações

**O que faz:** Gerencia as conexões com serviços externos.

**Para que serve:** Configurar e manter as integrações com Mercado Livre
e futuras plataformas.

**O que esperar que faça:**
- Mercado Livre:
  - Status da conexão (conectado/desconectado)
  - Botão para conectar/reconectar
  - Data da última sincronização
  - Botão para resincronizar produtos
- Exibir seção "Em breve" com logos de: Shopee, Amazon, Shopify, Tray, Nuvemshop
  (para criar expectativa e validar interesse)

#### 5.10.3 Preferências

**O que faz:** Configurações gerais do tenant.

**Para que serve:** Personalizar a experiência.

**O que esperar que faça:**
- Nome da loja/empresa
- Fuso horário (para agendamento de coletas e alertas)
- Moeda (R$ por padrão, futuramente outras)
- Formato de número (1.234,56 padrão BR)

---

# 6. STACK TECNOLÓGICA

## 6.1 Decisão e Justificativa

A stack foi escolhida com base em três critérios: domínio do desenvolvedor
(20 anos de PHP/web), custo mínimo de infraestrutura e capacidade de rodar
em uma VPS de 2 vCPUs / 4GB RAM.

## 6.2 Backend

| Tecnologia | Versão | Função |
|------------|--------|--------|
| PHP | 8.3+ | Linguagem principal do backend |
| Laravel | 12 | Framework principal — API, filas, agendamento, ORM |
| Laravel Sanctum | Última | Autenticação via tokens (API stateless) |
| Laravel Horizon | Última | Monitoramento de filas (se usar Redis) |
| Composer | Última | Gerenciador de dependências PHP |

## 6.3 Frontend

| Tecnologia | Versão | Função |
|------------|--------|--------|
| Angular | 19+ | Framework SPA para