# Neo4j local para a rede veículo–oficina

Este protótipo persiste em Neo4j a representação em grafo já investigada na dissertação. O serviço é vinculado somente a `127.0.0.1`; não é uma implantação em nuvem ou em produção.

## Dados e proteção

- Fonte: `dissertacao_frotas/dados/processados/os_consolidadas_processadas.parquet`.
- Inclui registros com `ds_os_status = COBRADAS` e identificadores de veículo e oficina preenchidos.
- Nós: `FleetVehicle` e `FleetWorkshop`.
- Relação `SERVICED_AT`: um vínculo por par veículo–oficina, agregando quantidade de registros, valor aprovado e datas mínima/máxima.
- Relação `SHARES_VEHICLE`: projeção não direcionada armazenada uma única vez por par de oficinas; o peso é o número de veículos compartilhados e são mantidos pares com pelo menos dois veículos em comum.
- Identificadores originais são transformados com HMAC-SHA-256 e um segredo local. Placas, nomes, CPF/CNPJ, notas livres, dados de abastecimento e identificadores de origem não são gravados.
- As contagens de registros representam linhas da fonte processada, não necessariamente ordens de serviço únicas. O conjunto de dados contém limitações de cobertura e qualidade descritas na dissertação.

## Executar

Requisitos: Docker Compose, Python 3 e acesso local aos dados processados.

```bash
python3 -m venv graphdb/.venv
graphdb/.venv/bin/pip install -r graphdb/requirements.txt
graphdb/.venv/bin/python -m graphdb.load_graph --init-env
DOCKER_API_VERSION=1.44 docker compose --env-file graphdb/.env -f graphdb/compose.yaml up -d
graphdb/.venv/bin/python -m graphdb.load_graph
```

O comando `--init-env` cria `graphdb/.env` com modo `0600`; esse arquivo é ignorado pelo Git e não deve ser compartilhado. O carregador verifica que o endereço Bolt é local, cria restrições de unicidade e confirma se as contagens persistidas correspondem ao lote de entrada. Reexecutar é idempotente para relações existentes. `--replace` substitui apenas nós com os rótulos `FleetVehicle` e `FleetWorkshop`.

No ambiente de desenvolvimento usado para validar este protótipo, o Docker Compose legado precisou de `DOCKER_API_VERSION=1.44` ao subir o serviço. Em instalações atualizadas, execute o comando sem essa variável.

A interface local do Neo4j Browser fica em <http://127.0.0.1:7474>. Use usuário `neo4j`, senha definida em `graphdb/.env` e banco padrão `neo4j`. Consultas analíticas de exemplo estão em [`queries.cypher`](./queries.cypher).

## Escopo científico

O grafo e as consultas Cypher tornam as relações navegáveis e auditáveis. As métricas de modularidade, comunidades de Louvain e centralidade reportadas no estudo original foram calculadas pelo pipeline de análise de grafos descrito no capítulo metodológico; este protótipo de persistência não declara que o Neo4j reproduziu esses algoritmos. Uma execução com Neo4j Graph Data Science exigiria validação separada de versões, projeção, pesos e parâmetros antes de comparar resultados.

O arquivo agregado `dissertacao_frotas/resultados/logs/relatorio_neo4j_grafo.json` registra as contagens efetivamente verificadas após a carga, a impressão digital da fonte e as salvaguardas de dados. Ele não contém os identificadores usados para construir o grafo.
