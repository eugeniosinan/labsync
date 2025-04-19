LABSYNC - Sistema de Atualização Automatizada de Dados Laboratoriais

================================================================================
RESUMO DO PROJETO
================================================================================

Este projeto tem como objetivo realizar a integração e atualização automatizada dos dados laboratoriais faltantes nos sistemas de notificação de saúde:

- DENGON (Dengue e Chikungunya)
- SIVEP (Síndrome Respiratória Aguda Grave)
- GAL (Sistema de Resultados Laboratoriais)

A aplicação é composta por múltiplos serviços organizados em containers Docker separados, com estrutura modular, pensada para suportar múltiplos locais (como Rio de Janeiro e Belo Horizonte), permitindo variações apenas na lógica de geração de correções. As credenciais dos sistemas (DENGON, SIVEP, GAL) são armazenadas de forma segura no banco de dados, e o painel administrativo permite a configuração e controle desses sistemas de forma centralizada.

================================================================================
ESTRUTURA DE DIRETÓRIOS
================================================================================

labsync/
├── core/                         # Código reutilizável entre todos os locais
│   ├── etl/
│   │   ├── gal/                  # ETL para importar resultados laboratoriais
│   │   ├── dengon/               # ETL para comparar DENGON com GAL
│   │   └── sivep/                # ETL para comparar SIVEP com GAL
│   │
│   ├── mapeamentos/              # Mapeamentos HTML ↔ campos do banco
│   │   ├── dengon_map.json
│   │   └── sivep_map.json
│   │
│   ├── robo/                     # Robôs genéricos, um por sistema
│   │   ├── bot_dengon/
│   │   │   └── aplicador_dengon.py
│   │   └── bot_sivep/
│   │       └── aplicador_sivep.py
│   │
│   ├── admin_panel/              # Painel Flask de configuração e acompanhamento
│   │   ├── app.py
│   │   ├── credenciais.json
│   │   ├── estado_servicos.json
│   │   └── templates/
│   │
│   ├── db_schema/                # Criação e migração das tabelas PostgreSQL
│   ├── docker/                   # Dockerfiles base para serviços
│   └── utils/                    # Funções auxiliares compartilhadas
│
├── locais/
│   └── rio_de_janeiro/           # Lógica específica para o Rio de Janeiro
│       ├── regras/
│       │   ├── regras_dengon.json
│       │   └── regras_sivep.json
│       └── gerar_correcoes.py    # Script local que gera as correções para cada sistema
│
├── docker-compose.yml            # Compose principal com todos os serviços
└── README.md                     # Este arquivo

================================================================================
COMPONENTES PRINCIPAIS
================================================================================

1. ETL (por sistema):
   - Lê os arquivos DBF exportados dos sistemas (ano a ano)
   - Converte e carrega os dados para staging no DuckDB
   - A lógica é específica por sistema (DENGON, SIVEP, GAL)

2. gerar_correcoes.py:
   - Executado por local (ex: Rio de Janeiro)
   - Carrega dados do DuckDB
   - Aplica regras personalizadas (`regras_*.json`)
   - Gera os registros com as correções e insere no PostgreSQL

3. PostgreSQL:
   - Contém uma tabela de correções para cada sistema:
     - tb_dengon_correcoes
     - tb_sivep_correcoes
   - Cada linha contém:
     - Campos para localizar o registro no sistema
     - JSONB "correcoes" com os campos a alterar
     - Flag "corrigido" (False por padrão)
   - As credenciais dos sistemas (DENGON, SIVEP, GAL) são armazenadas de forma segura e criptografada

4. Robôs (bot_dengon, bot_sivep):
   - Cada robô é um serviço separado
   - Lê a tabela de correções respectiva no PostgreSQL
   - Usa os mapeamentos HTML (`core/mapeamentos/*.json`)
   - Aplica as correções no sistema web via Selenium
   - Atualiza a flag "corrigido = true" após sucesso

5. Painel Administrativo:
   - Aplicação Flask
   - Interface para:
     - Cadastrar/editar credenciais dos sistemas de forma segura
     - Ver status de execução dos serviços
     - Ver quantidade de fichas alteradas por dia
     - Reverter alterações (futuramente)
     - Iniciar/parar serviços manualmente
     - Sistema de login com controle de usuários responsáveis pela administração

================================================================================
FLUXO DE EXECUÇÃO POR SISTEMA
================================================================================

DENGON:
1. Executa ETL DENGON → DuckDB
2. Executa ETL GAL (relacionado ao DENGON) → DuckDB
3. Script gerar_correcoes.py do local lê os dados no DuckDB
4. Aplica regras do `regras_dengon.json`
5. Insere/atualiza `tb_dengon_correcoes` no PostgreSQL
6. Robô `bot_dengon.py` lê correções pendentes (corrigido=false)
7. Aplica alterações no sistema via Selenium
8. Atualiza flag "corrigido = true"

SIVEP:
1. Executa ETL SIVEP → DuckDB
2. Executa ETL GAL (relacionado ao SIVEP) → DuckDB
3. Script gerar_correcoes.py do local lê os dados no DuckDB
4. Aplica regras do `regras_sivep.json`
5. Insere/atualiza `tb_sivep_correcoes` no PostgreSQL
6. Robô `bot_sivep.py` lê correções pendentes (corrigido=false)
7. Aplica alterações no sistema via Selenium
8. Atualiza flag "corrigido = true"

================================================================================
SEGURANÇA E GESTÃO DE CREDENCIAIS
================================================================================

- **Criptografia das credenciais**: As credenciais de acesso aos sistemas GAL, DENGON e SIVEP são armazenadas no banco de dados PostgreSQL de forma segura. Elas são criptografadas usando técnicas modernas de criptografia, como AES, para garantir que não sejam acessadas em texto claro.
  
- **Autenticação no painel**: O painel administrativo tem um sistema de login para usuários responsáveis pela administração. Apenas usuários autenticados podem acessar as configurações de credenciais e iniciar/parar os robôs.
  
- **Controle de acesso**: O painel permite cadastrar e editar as credenciais de acesso aos sistemas, mas somente usuários autorizados (administradores) podem realizar essas alterações. Todas as alterações realizadas no painel são registradas em logs para fins de auditoria.

================================================================================
OBSERVAÇÕES FINAIS
================================================================================

- Todos os sistemas rodam localmente via Docker
- O banco de dados PostgreSQL e o painel Flask são compartilhados
- Cada sistema (DENGON, SIVEP) possui robô e ETL próprios
- A única parte que varia entre locais é o conteúdo das regras de correção
- Os mapeamentos de elementos HTML dos sistemas são iguais para todos os locais

================================================================================
FUTURAS EXPANSÕES
================================================================================

- Criar subpastas dentro de `locais/` para novos locais (ex: `locais/belo_horizonte/`)
- Apenas copiar `gerar_correcoes.py` e definir novos arquivos `regras_*.json`
- O restante do sistema permanece exatamente igual

================================================================================
AUTOR
================================================================================

Este projeto é de uso interno. Todas as operações são automatizadas, mas controladas por painel local. Alterações devem ser feitas com atenção à estrutura modularizada entre o núcleo do projeto (`core/`) e as personalizações por local (`locais/`).
