
- [x] Clarify Project Requirements
- [x] Scaffold the Project
- [ ] Customize the Project
  - Implemente o banco de dados SQLite, criando as tabelas necessárias para usuários, lançamentos (gastos/investimentos), objetivos, configurações, orçamento, etc. O banco deve ser inicializado ao iniciar o app.
- [ ] Install Required Extensions
- [ ] Compile the Project
- [ ] Create and Run Task
- [ ] Launch the Project
- [ ] Ensure Documentation is Complete

Resumo: Projeto de controle de finanças pessoais em Python com interface gráfica moderna (Tkinter ou PyQt), SQLite, matplotlib, dashboard, relatórios CSV, login, notificações, validação, layout responsivo, módulos organizados e código comentado.

Instruções para evolução do app:

1. BANCO DE DADOS:
   - Expanda as tabelas atuais para incluir: id, tipo, valor, data, descricao, categoria, forma_pagamento, status, recorrente, objetivo_id.
   - Crie tabelas adicionais:
     - objetivos (sonhos/metas financeiras)
     - usuarios (múltiplos perfis)
     - configuracoes (preferências do usuário)
     - orcamento (valores planejados por categoria/mês)
   - Suporte a lançamentos recorrentes (ex: aluguel todo mês)
   - Suporte a anexos (comprovantes/fotos em diretório vinculado)

2. INTERFACE GRÁFICA:
   - Layout moderno com abas ou menu lateral:
     - Dashboard (saldo, gastos, gráficos)
     - Lançamentos (registros com filtros)
     - Investimentos (inserir, acompanhar rentabilidade)
     - Sonhos/Objetivos (planejar e acompanhar evolução)
     - Orçamento Mensal (limites por categoria e comparação)
     - Relatórios (extrato mensal, anual, comparativos)
     - Configurações (usuário, tema, preferências)
   - Em cada aba: formulários amigáveis, validação, filtros avançados

3. DASHBOARD:
   - Exibir saldo atual (gastos - receitas + investimentos)
   - Gráfico de pizza (distribuição por categoria)
   - Gráfico de barras (evolução mensal, últimos 6 meses)
   - Alertas de orçamento (gasto acima do limite)
   - Progresso de objetivos/sonhos

4. LANÇAMENTOS:
   - Cadastro detalhado: valor, tipo, categoria, forma de pagamento, data, descrição
   - Campo de recorrência (mensal, semanal)
   - Upload de comprovante/anexo (imagem/PDF)
   - Tabela com filtros, ordenação, busca

5. INVESTIMENTOS:
   - Cadastro de investimentos (renda fixa, ações, cripto)
   - Campos: valor, data, tipo, rendimento esperado (%)
   - Calcular crescimento ao longo do tempo
   - Gráfico de evolução do patrimônio investido

6. SONHOS/OBJETIVOS:
    - Tela para cadastrar metas financeiras (ex: carro, viagem)
    - Definir meta (valor final), prazo e prioridade.
    - Mostrar progresso (% do valor já atingido).
    - Permitir aporte direto nos sonhos.
    - Barra de progresso visual para cada objetivo.

7. ORÇAMENTO:
    - Criar tela para definir limite mensal por categoria (alimentação, lazer, transporte, etc).
    - Comparar automaticamente com os lançamentos reais.
    - Mostrar alertas visuais quando estiver perto de estourar o limite.

8. RELATÓRIOS:
    - Gerar relatórios mensais e anuais em formato:
       - Tabela estilo extrato bancário (data, descrição, valor, saldo acumulado).
       - Relatório de orçamento (planejado vs real).
       - Relatório de investimentos (rentabilidade por período).
    - Exportar em **Excel, PDF e CSV**.
    - Criar gráficos:
       - Pizza → categorias de gastos.
       - Barras → evolução mensal.
       - Linha → saldo acumulado.

9. CONFIGURAÇÕES:
    - Sistema multiusuário (login simples).
    - Tema claro/escuro.
    - Idioma (pt-br, en).
    - Opção de backup/restauração do banco de dados.

10. INTELIGÊNCIA FINANCEIRA:
      - Adicionar **alertas automáticos**:
         - Quando gastos em uma categoria ultrapassarem o orçamento.
         - Quando saldo ficar negativo.
         - Quando objetivos não estiverem sendo atingidos no prazo.
      - Adicionar dicas automáticas:
         - “Você gastou 30% a mais em alimentação neste mês comparado ao anterior.”
         - “Faltam R$ X para atingir 80% do seu objetivo Viagem.”
      - Criar uma projeção simples:
         - Prever saldo para os próximos meses com base nos gastos recorrentes.

11. ORGANIZAÇÃO DO CÓDIGO:
      - Estruture em módulos separados:
         - `database.py` → gerencia conexão e queries.
         - `models.py` → classes que representam entidades (Lançamento, Objetivo, Investimento).
         - `ui.py` → telas e componentes gráficos.
         - `reports.py` → relatórios e gráficos.
         - `utils.py` → funções auxiliares.
         - `main.py` → inicialização.
      - Utilize POO para organização.
      - Comente bem o código.

12. EXTRA (se possível):
      - Adicionar sistema de **tags** nos lançamentos.
      - Criar **atalhos no teclado** (ex: Ctrl+N para novo lançamento).
      - Possibilidade de sincronizar com Google Sheets ou exportar dados automaticamente.
      - Criar **widgets no Dashboard** configuráveis pelo usuário.