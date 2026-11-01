#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador do Dicionário de Dados do Banco de Dados Relacional da Dissertação
PPGCAP / UDESC, Autor: Eduardo Lopes Jonker

Gera:
1. Tabela 'dicionario_dados' dentro de dados/resultados_dissertacao.db
2. Arquivo Markdown dados/dicionario_de_dados_banco.md
3. PDF acadêmico relatorios_pdf/dicionario_de_dados_banco.pdf
"""

import os
import sys
import json
import sqlite3
import shutil
from pathlib import Path
import markdown
import weasyprint

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "dados" / "resultados_dissertacao.db"
MD_PATH = BASE_DIR / "dados" / "dicionario_de_dados_banco.md"
PDF_PATH = BASE_DIR / "relatorios_pdf" / "dicionario_de_dados_banco.pdf"

# Mapeamento detalhado e semântico de todas as colunas de cada tabela
DICIONARIO_SEMANTICO = {
    "abastecimentos": {
        "descricao_tabela": "Microdados transacionais exaustivos de 1.000.000 de abastecimentos de combustível da frota pública de Santa Catarina (2019-2022).",
        "origem": "2161_abastecimentos_pg0001.xlsb (Higienizado e Anonimizado)",
        "volume": "1.000.000 registros",
        "colunas": {
            "cod_venda": ("Código numérico identificador único da transação no terminal eletrônico / POS do posto.", "REAL", "678912.0"),
            "horario": ("Horário do registro da transação no formato HH:MM:SS.", "TEXT", "14:35:10"),
            "prefixo": ("Prefixo operacional ou código de identificação interno da viatura no batalhão.", "TEXT", "PM 5853"),
            "placa": ("Placa identificadora do veículo padronizada no padrão Mercosul/Nacional.", "TEXT", "QIJ8944"),
            "unidade": ("Secretaria de Estado ou Órgão gestor principal responsável pelo bem.", "TEXT", "PMSC/CAEPM 1904 - 899"),
            "subunidade": ("Batalhão regional, delegacia, diretoria ou comarca usuária da viatura.", "TEXT", "PMSC/CAEPM/CHOQUE"),
            "combustivel": ("Tipo de combustível faturado (GASOLINA, DIESEL S10, ETANOL, GNV).", "TEXT", "GASOLINA"),
            "posto": ("Nome fantasia do estabelecimento credenciado que realizou o fornecimento.", "TEXT", "POSTO AGRICOPEL MIME"),
            "uf_posto": ("Unidade Federativa onde está situado o estabelecimento revendedor.", "TEXT", "SC"),
            "cidade_posto": ("Município catarinense em que ocorreu o abastecimento.", "TEXT", "FLORIANOPOLIS"),
            "tipo_frota": ("Natureza da frota (PROPRIA, LOCADA, CONCEDIDA).", "TEXT", "PROPRIA"),
            "marca": ("Fabricante ou montadora do veículo.", "TEXT", "YAMAHA / FIAT / CHEVROLET"),
            "modelo": ("Descrição comercial do modelo do veículo.", "TEXT", "XT 660R / WEEKEND ADVENTURE"),
            "tipo_veiculo": ("Classificação funcional do bem (MOTO, VIATURA, CAMINHAO, AMBULANCIA).", "TEXT", "MOTO / VIATURA"),
            "ano_veiculo": ("Ano de fabricação e modelo do veículo cadastrado no sistema.", "TEXT", "2017/2018"),
            "cnpj_posto": ("Cadastro Nacional da Pessoa Jurídica (CNPJ) do estabelecimento abastecedor.", "TEXT", "83.488.882/0054-15"),
            "odometro": ("Quilometragem informada no hodômetro no ato do abastecimento.", "REAL", "12899.0"),
            "litros": ("Volume de combustível fornecido em litros.", "REAL", "11.74"),
            "preco_unitario": ("Valor monetário faturado por litro de combustível (R$/L).", "REAL", "3.85"),
            "valor_total": ("Valor total financeiro liquidado na operação (R$).", "REAL", "45.21"),
            "km_l_sistema": ("Consumo médio calculado entre abastecimentos consecutivos (km/L).", "REAL", "14.2"),
            "km_rodados_sistema": ("Distância percorrida desde o abastecimento anterior registrada.", "REAL", "250.0"),
            "tipo_venda": ("Meio tecnológico de autorização e liquidação da transação (POS/TEF).", "TEXT", "POS/TEF"),
            "data": ("Data e hora formal da realização do abastecimento.", "TIMESTAMP", "2019-01-01 00:00:00"),
            "ano": ("Ano civil extraído da data do abastecimento para particionamento analítico.", "INTEGER", "2019"),
            "mes_ano": ("Competência mensal no formato YYYY-MM para séries temporais.", "TEXT", "2019-01"),
            "condutor_anon": ("Hash criptográfico SHA-256 anonimizado do condutor (Conformidade com LGPD).", "TEXT", "COND_61E948ABEB64"),
            "flag_anomalia_volume": ("Flag binária indicadora de volume atípico superior à capacidade do tanque (1=Sim, 0=Não).", "INTEGER", "0 ou 1"),
            "flag_anomalia_kml": ("Flag binária de consumo de combustível inverossímil (<1,5 ou >40 km/L) (1=Sim, 0=Não).", "INTEGER", "0 ou 1"),
            "flag_preco_discrepante": ("Flag binária indicadora de preço unitário excessivo ou inconsistente (1=Sim, 0=Não).", "INTEGER", "0 ou 1")
        }
    },
    "abastecimentos_ano": {
        "descricao_tabela": "Estatísticas anuais consolidadas de consumo e dispêndio de combustível.",
        "origem": "Agregação da tabela abastecimentos",
        "volume": "4 registros (2019 a 2022)",
        "colunas": {
            "ano": ("Ano do exercício financeiro analisado.", "INTEGER", "2021"),
            "gasto_total": ("Somatório financeiro liquidado em combustíveis no exercício (R$).", "REAL", "41520140.22"),
            "litros_total": ("Volume total em litros de combustível faturado no exercício.", "REAL", "9120400.10"),
            "preco_medio": ("Preço médio ponderado por litro no respectivo exercício (R$/L).", "REAL", "4.55"),
            "transacoes": ("Quantidade total de operações de abastecimento registradas no ano.", "INTEGER", "275410"),
            "veiculos_unicos": ("Quantidade de veículos distintos abastecidos no ano.", "INTEGER", "7120")
        }
    },
    "abastecimentos_categoria": {
        "descricao_tabela": "Distribuição agregada de despesas e volume de combustível por categoria veicular.",
        "origem": "Agregação da tabela abastecimentos por tipo_veiculo",
        "volume": "8 registros",
        "colunas": {
            "categoria_veiculo": ("Segmento veicular (AMBULANCIA, CAMINHAO, HATCH, MOTO, ONIBUS, SEDAN, SUV, UTILITARIO).", "TEXT", "SEDAN / SUV"),
            "gasto_total": ("Dispêndio total aprovado para o segmento veicular (R$).", "REAL", "51240890.10"),
            "litros_total": ("Volume total abastecido pelo segmento veicular (L).", "REAL", "11400200.00"),
            "transacoes": ("Número de abastecimentos realizados por veículos dessa categoria.", "INTEGER", "340120"),
            "veiculos_unicos": ("Total de placas distintas pertencentes a essa categoria.", "INTEGER", "3250"),
            "preco_medio": ("Preço médio por litro praticado nas operações dessa categoria (R$/L).", "REAL", "4.49"),
            "percentual_gasto": ("Participação percentual da categoria sobre o dispêndio total estadual (%).", "REAL", "33.38")
        }
    },
    "abastecimentos_secretaria": {
        "descricao_tabela": "Consolidação dos gastos e volumes de combustíveis por Secretaria de Estado e Órgão setorial.",
        "origem": "Agregação da tabela abastecimentos por secretaria gestora",
        "volume": "10 registros",
        "colunas": {
            "secretaria": ("Identificação da Pasta Governamental (PMSC, PCSC, SES, SAP, CBMSC, SED, etc.).", "TEXT", "PMSC / PCSC / SES"),
            "gasto_total": ("Montante financeiro liquidado pela pasta em combustíveis (R$).", "REAL", "74020150.80"),
            "litros_total": ("Litros totais de combustíveis alocados à pasta.", "REAL", "16540100.00"),
            "transacoes": ("Total de abastecimentos efetuados por viaturas da pasta.", "INTEGER", "495000"),
            "veiculos_unicos": ("Frota ativa da pasta com abastecimentos registrados.", "INTEGER", "5840"),
            "preco_medio": ("Custo médio do combustível faturado para a secretaria (R$/L).", "REAL", "4.47"),
            "percentual_gasto": ("Proporção dos dispêndios da pasta frente ao gasto global do Estado (%).", "REAL", "48.22")
        }
    },
    "abastecimentos_projecao_prophet": {
        "descricao_tabela": "Projeções preditivas mensais de gastos de combustível obtidas pelo modelo Facebook Prophet.",
        "origem": "Modelo Prophet treinado sobre a série temporal de abastecimentos (2019-2022)",
        "volume": "25 registros (competências futuras até 2025)",
        "colunas": {
            "ano_mes": ("Competência mensal projetada no formato YYYY-MM.", "TEXT", "2024-06"),
            "projecao_gasto": ("Valor pontual central estimado de gasto para o mês (R$).", "REAL", "4620100.50"),
            "projecao_min": ("Limite inferior do intervalo de incerteza preditiva de 95% (R$).", "REAL", "4150000.00"),
            "projecao_max": ("Limite superior do intervalo de incerteza preditiva de 95% (R$).", "REAL", "5090200.00")
        }
    },
    "manutencao_itens": {
        "descricao_tabela": "Microdados de itens de peças e mão de obra de ordens de serviço de manutenção mecânica da frota estadual.",
        "origem": "os_dataset_limpo.csv (Base higienizada para modelagem e auditoria)",
        "volume": "223.819 registros",
        "colunas": {
            "veiculo_id": ("Identificador unificado do veículo no cadastro patrimonial.", "TEXT", "VEIC_1042"),
            "ds_veiculomodelo": ("Descrição do modelo do veículo objeto do reparo.", "TEXT", "COROLLA GLI 1.8"),
            "ds_familia": ("Família da frota (POLICIA MILITAR, CIVIL, SAUDE, ADMINISTRATIVA).", "TEXT", "SEGURANCA PUBLICA"),
            "nr_anoveiculo": ("Ano de fabricação do veículo.", "REAL", "2018.0"),
            "nr_quilometragem": ("Hodômetro registrado na abertura da ordem de serviço.", "REAL", "115400.0"),
            "cd_manutencao_oficina": ("Código identificador da ordem de serviço na oficina credenciada.", "TEXT", "OS_99420"),
            "tipo_manutencao_oficina": ("Classificação da manutenção (PREVENTIVA ou CORRETIVA).", "TEXT", "CORRETIVA"),
            "cd_estabelecimento": ("Código cadastral do estabelecimento/oficina mecânica.", "TEXT", "OFIC_320"),
            "ds_tipoestabelecimento": ("Tipo de credenciamento da oficina (MECANICA GERAL, AUTO ELETRICA, CONCESSIONARIA).", "TEXT", "MECANICA"),
            "ds_os_status": ("Situação cadastral da OS (PAGO, REPROVADO, CANCELADO, BLOQUEADO).", "TEXT", "PAGO"),
            "ds_peca": ("Descrição padronizada do componente mecânico substituído.", "TEXT", "DISCO DE FREIO DIANTEIRO"),
            "ds_fabricante_peca": ("Fabricante ou marca da peça automotiva aplicada.", "TEXT", "TRW / BOSCH"),
            "ds_complemento_peca": ("Informações técnicas adicionais sobre a peça.", "TEXT", "VENTILADO ORIGINAL"),
            "ds_mao_de_obra": ("Descrição do serviço de mão de obra executado pelo mecânico.", "TEXT", "SUBSTITUICAO DE PASTILHAS E DISCOS"),
            "nr_quantidade_pecas": ("Quantidade de unidades da peça aplicadas no serviço.", "REAL", "2.0"),
            "valor_peca_orcado": ("Valor orçado inicialmente pelo fornecedor para a peça (R$).", "REAL", "450.00"),
            "Valor_Aprovado_Peca": ("Valor formalmente aprovado e liquidado pela fiscalização para a peça (R$).", "REAL", "380.00"),
            "vl_total_mao_de_obra": ("Valor total aprovado de mão de obra para o item (R$).", "REAL", "180.00"),
            "valor_mo_orcado": ("Valor orçado inicialmente pelo mecânico para a mão de obra (R$).", "REAL", "240.00"),
            "Valor_Aprovado_MaoDeObra": ("Valor de mão de obra liquidado após fiscalização técnica (R$).", "REAL", "180.00"),
            "vl_orcado": ("Somatório orçado inicial de peça + mão de obra (R$).", "REAL", "690.00"),
            "Valor_Aprovado": ("Somatório final liquidado de peça + mão de obra (R$).", "REAL", "560.00"),
            "vl_total_peca": ("Valor total de peças multiplicado pela quantidade (R$).", "REAL", "380.00"),
            "vl_unitario_peca": ("Preço unitário aprovado por componente mecânico (R$).", "REAL", "190.00"),
            "vl_unitario_mao_de_obra": ("Preço hora da mão de obra aprovada (R$/h).", "REAL", "90.00"),
            "nr_quantidade_hora_mao_de_obra": ("Quantidade de horas técnicas autorizadas para o serviço.", "REAL", "2.0"),
            "dt_aprovacao_item": ("Data em que a fiscalização técnica aprovou o item.", "TEXT", "2021-03-15"),
            "dt_reprovacao_item": ("Data em que o item foi formalmente glosado/reprovado.", "TEXT", "NULL"),
            "dt_cancelamento_item": ("Data de cancelamento do item por perda de objeto.", "TEXT", "NULL"),
            "dt_transacao": ("Data de registro da transação no sistema de gestão de frota.", "TEXT", "2021-03-12"),
            "dt_envio_orcamento": ("Data em que a oficina submeteu o orçamento à DITI/SEA.", "TEXT", "2021-03-13"),
            "dt_entrada_veiculo_oficina": ("Data de entrada física da viatura no pátio da oficina.", "TEXT", "2021-03-12"),
            "dt_aprovacao_os": ("Data de autorização formal da ordem de serviço pela diretoria.", "TEXT", "2021-03-15"),
            "dt_conclusao_servico": ("Data de finalização dos serviços mecânicos.", "TEXT", "2021-03-18"),
            "dt_retirada_veiculo": ("Data de saída da viatura para retorno à prontidão operacional.", "TEXT", "2021-03-19"),
            "dt_reprovacao_os": ("Data de reprovação integral da ordem de serviço.", "TEXT", "NULL"),
            "relato_gestor_auto": ("Parecer descritivo emitido pelo fiscal técnico estadual.", "TEXT", "AUTORIZADO CONFORME TABELA REFERENCIAL"),
            "fl_aprovacao_atipica": ("Indicador booleano de aprovação sob regime extraordinário.", "REAL", "0.0"),
            "ds_uf": ("Unidade Federativa da execução da manutenção.", "TEXT", "SC"),
            "ds_tipofrota": ("Segmento de frota do veículo atendido.", "TEXT", "PROPRIA"),
            "ds_complemento": ("Anotações cadastrais complementares do veículo.", "TEXT", "CHASSI CONFIRMADO"),
            "ds_informacao_adicional1": ("Metadado técnico adicional de auditoria 1.", "TEXT", "TEXTO_LIVRE"),
            "ds_informacao_adicional2": ("Metadado técnico adicional de auditoria 2.", "TEXT", "TEXTO_LIVRE"),
            "ds_informacao_adicional3": ("Metadado técnico adicional de auditoria 3.", "TEXT", "TEXTO_LIVRE"),
            "ds_informacao_adicional4": ("Metadado técnico adicional de auditoria 4.", "TEXT", "TEXTO_LIVRE"),
            "ds_informacao_adicional5": ("Metadado técnico adicional de auditoria 5.", "TEXT", "TEXTO_LIVRE")
        }
    },
    "kpis_gerenciais": {
        "descricao_tabela": "Indicadores de Governança e Gestão de Frota e Informação (GFI) catalogados e monitorados.",
        "origem": "indicadores_gfi_consolidados.json",
        "volume": "38 registros",
        "colunas": {
            "id_indicador": ("Identificador padronizado do indicador no modelo GFI (ex: GFI-01 a GFI-38).", "TEXT", "GFI-01"),
            "tema": ("Dimensão temática de gestão (Custos, Disponibilidade, Conformidade, etc.).", "TEXT", "Controle de Custos"),
            "nome_indicador": ("Nome técnico do indicador de desempenho monitorado.", "TEXT", "Taxa de Glosa Técnica"),
            "valor_apurado": ("Valor numérico ou percentual medido nos dados da frota estadual.", "TEXT", "46,93%"),
            "parametro_referencia": ("Meta ou limite normativo aceitável estabelecido pelos órgãos de controle.", "TEXT", "< 15,0%"),
            "status_conformidade": ("Veredito da auditoria técnica sobre o indicador.", "TEXT", "CRÍTICO - FORA DA META"),
            "criticidade": ("Grau de criticidade para tomada de decisão (NORMAL, ALERTA, CRITICA).", "TEXT", "CRITICA")
        }
    },
    "experimentos_modelos": {
        "descricao_tabela": "Resultados de acurácia, calibração e tempo computacional dos modelos preditivos de ML avaliados.",
        "origem": "Pipeline de treinamento e validação walk-forward (scripts/treinar_*.py)",
        "volume": "28 registros",
        "colunas": {
            "id": ("Identificador numérico sequencial do experimento de aprendizado de máquina.", "INTEGER", "1"),
            "tarefa": ("Tipo de problema supervisionado (classificacao_risco, regressao_custo, series_temporais).", "TEXT", "classificacao_risco"),
            "modelo": ("Nome do algoritmo testado (HistGradientBoosting, Random Forest, SVR, etc.).", "TEXT", "HistGradientBoosting"),
            "features": ("Subconjunto de variáveis empregadas (Multimodal M+P+A, Restrito M, etc.).", "TEXT", "Multimodal (M+P+A)"),
            "roc_auc": ("Área sob a Curva ROC obtida na partição out-of-time.", "REAL", "0.8743"),
            "pr_auc": ("Área sob a Curva Precision-Recall (métrica primária em dados desbalanceados).", "REAL", "0.9510"),
            "brier_score": ("Escore de Brier mensurando calibração probabilística (menor é melhor).", "REAL", "0.1043"),
            "f1_score": ("F1-Score máximo alcançado no ponto de corte ótimo.", "REAL", "0.9113"),
            "mae": ("Erro Médio Absoluto em reais nas tarefas de regressão (R$).", "REAL", "2236.06"),
            "rmse": ("Raiz do Erro Quadrático Médio em reais nas tarefas de regressão (R$).", "REAL", "3780.20"),
            "r2": ("Coeficiente de Determinação out-of-sample.", "REAL", "0.748"),
            "tempo_treinamento_s": ("Tempo computacional de treinamento e calibração em segundos.", "REAL", "1.8"),
            "observacao": ("Comentários técnicos e veredito do modelo (Campeão, Baseline, etc.).", "TEXT", "Modelo Campeão")
        }
    },
    "veiculos_leilao": {
        "descricao_tabela": "Veículos antieconômicos identificados para desincorporação e leilão com fulcro no Decreto Estadual nº 47.539/2018.",
        "origem": "relatorio_gerencial_frotas_sc.json (Critério: custo acumulado > 40% do valor venal FIPE)",
        "volume": "30 registros (Amostra dos 313 veículos auditados)",
        "colunas": {
            "placa": ("Placa identificadora do veículo público antieconômico.", "TEXT", "MIR7280"),
            "modelo": ("Modelo do veículo classificado para baixa patrimonial.", "TEXT", "FORD CARGO 815"),
            "familia": ("Segmento administrativo do bem patrimonial.", "TEXT", "PESADOS / SEGURANCA"),
            "orgao": ("Secretaria proprietária do bem.", "TEXT", "POLICIA MILITAR"),
            "idade_anos": ("Idade cronológica do bem em anos desde a fabricação.", "INTEGER", "14"),
            "quilometragem": ("Quilometragem total acumulada no hodômetro.", "INTEGER", "380450"),
            "valor_venal": ("Valor de mercado do veículo balizado pela Tabela FIPE (R$).", "REAL", "45000.00"),
            "gasto_acumulado": ("Somatório histórico de gastos com manutenção mecânica e peças (R$).", "REAL", "38400.00"),
            "razao_gasto_venal": ("Razão entre o gasto de manutenção e o valor venal (Gasto/FIPE).", "REAL", "0.853"),
            "status_decreto": ("Enquadramento legal no Art. 5º do Decreto 47.539/2018.", "TEXT", "SUPERIOR A 40% DO VENAL"),
            "decisao": ("Diretriz prescritiva gerada pelo algoritmo de auditoria.", "TEXT", "ALIENACAO IMEDIATA EM LEILAO")
        }
    },
    "auditoria_orgaos": {
        "descricao_tabela": "Estatísticas de fiscalização, gastos autorizados e valores glosados por órgão do Governo de Santa Catarina.",
        "origem": "Agregação da base de ordens de serviço por unidade orçamentária",
        "volume": "38 registros",
        "colunas": {
            "orgao": ("Nome do Órgão Governamental ou Secretaria de Estado.", "TEXT", "SECRETARIA DE ESTADO DA SAUDE"),
            "qtd_oss_auditadas": ("Total de ordens de serviço emitidas e fiscalizadas para o órgão.", "INTEGER", "14210"),
            "gasto_aprovado": ("Montante financeiro de manutenção efetivamente aprovado e liquidado (R$).", "REAL", "28500400.00"),
            "valor_orcado_inicial": ("Montante originalmente orçado pelas oficinas credenciadas (R$).", "REAL", "42100800.00"),
            "glosa_tecnica_economia": ("Economia pública proporcionada pela glosa de itens abusivos (R$).", "REAL", "13600400.00"),
            "pct_glosa": ("Percentual médio de redução obtido pela fiscalização técnica (%).", "REAL", "32.30"),
            "downtime_medio_dias": ("Tempo médio de paralisação das viaturas em oficinas (dias de imobilização).", "REAL", "5.4")
        }
    },
    "grafos_centralidade": {
        "descricao_tabela": "Métricas de centralidade e topologia da rede complexa bipartida de oficinas mecânicas credenciadas.",
        "origem": "Modelagem de grafos com NetworkX e algoritmo de Louvain",
        "volume": "10 registros (Top estabelecimentos de maior intermediação)",
        "colunas": {
            "id_estabelecimento": ("Código identificador único do estabelecimento fornecedor no cadastro estadual.", "TEXT", "OFIC_042"),
            "nome_estabelecimento": ("Razão social ou nome de fachada da oficina credenciada.", "TEXT", "AUTO MECANICA CENTRAL LTDA"),
            "grau_conexoes": ("Grau do nó (Degree): número de veículos distintos atendidos pelo estabelecimento.", "INTEGER", "840"),
            "betweenness_centrality": ("Centralidade de Intermediação: proporção de menores caminhos que cruzam a oficina.", "REAL", "0.0842"),
            "pagerank": ("Escore de autoridade e influência estrutural na rede pelo algoritmo PageRank.", "REAL", "0.0125"),
            "comunidade_louvain": ("Identificador numérico da comunidade modular detectada pelo algoritmo Louvain.", "INTEGER", "4"),
            "diagnostico_risco": ("Classificação forense de dependência estrutural e risco de gargalo operacional.", "TEXT", "HUB CRITICO REGIONAL")
        }
    },
    "projecao_trienal": {
        "descricao_tabela": "Projeções orçamentárias plurianuais de manutenção comparando o modelo inercial ao prescritivo MILP.",
        "origem": "Simulação de Monte Carlo com desgaste de Weibull e solver HiGHS (2027-2029)",
        "volume": "5 registros",
        "colunas": {
            "exercicio": ("Ano civil do exercício fiscal orçado.", "INTEGER", "2027"),
            "cenario_inercial": ("Gasto público projetado sob a manutenção reativa tradicional As-Is (R$).", "REAL", "56300400.00"),
            "prescritivo_milp": ("Dispêndio ótimo calculado pelo modelo prescritivo sob restrições (R$).", "REAL", "44120800.00"),
            "economia_anual": ("Redução líquida anual de despesas gerada pela otimização (R$).", "REAL", "12179600.00"),
            "inflacao_setorial_pct": ("Taxa de inflação de insumos automotivos incorporada no modelo (%).", "REAL", "6.08"),
            "premissas_normativas": ("Parâmetros legais e limites vinculados (LOA, Prontidão >= 95%, etc.).", "TEXT", "Prontidão PMSC >= 95%")
        }
    },
    "catalogo_figuras": {
        "descricao_tabela": "Catálogo analítico exaustivo das 101 figuras gráficas geradas na dissertação.",
        "origem": "scripts/gerar_todas_as_figuras.py e scripts/analise_abastecimentos_ml_prophet.py",
        "volume": "101 registros",
        "colunas": {
            "numero": ("Número ordinal da figura na dissertação de mestrado (1 a 101).", "INTEGER", "98"),
            "arquivo_imagem": ("Nome físico do arquivo PNG da figura salvo no diretório charts/.", "TEXT", "fig98_tendencia_prophet_abastecimento.png"),
            "titulo": ("Título técnico oficial da ilustração.", "TEXT", "Decomposição Temporal e Projeção Prophet"),
            "legenda_resumida": ("Descrição sintética do gráfico para o índice da dissertação.", "TEXT", "Projeção temporal de gastos mensais"),
            "diagnostico": ("Conclusão analítica extraída da evidência visual.", "TEXT", "Tendência de crescimento nos dispêndios"),
            "causa_raiz": ("Fator gerador ou etiologia do fenômeno identificado.", "TEXT", "Variação de preços de combustíveis"),
            "impacto_financeiro": ("Magnitude orçamentária associada ao fenômeno analisado.", "TEXT", "R$ 153.488.476,96 em dispêndio"),
            "diretriz_prescritiva": ("Ação governamental prescrita para mitigar o problema.", "TEXT", "Adotar compras programadas com preço teto")
        }
    },
    "resumo_executivo": {
        "descricao_tabela": "Principais métricas e indicadores globais certificados da dissertação de mestrado.",
        "origem": "tabela_unica_resultados_oficiais.json e abastecimentos_kpis.json",
        "volume": "17 registros",
        "colunas": {
            "chave": ("Identificador mnemônico da métrica no sistema de controle.", "TEXT", "total_dispendio_combustivel"),
            "valor_numerico": ("Valor numérico em ponto flutuante para cômputos analíticos.", "REAL", "153488476.96"),
            "valor_formatado": ("Valor formatado com pontuação nacional e unidades monetárias/litros.", "TEXT", "R$ 153.488.476,96"),
            "descricao": ("Explicação contextualizada do indicador certificado.", "TEXT", "Valor financeiro total liquidado em combustíveis")
        }
    }
}

def criar_tabela_dicionario_sqlite(conn):
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS dicionario_dados;")
    cur.execute("""
    CREATE TABLE dicionario_dados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tabela TEXT NOT NULL,
        coluna TEXT NOT NULL,
        tipo_sqlite TEXT NOT NULL,
        chave_primaria INTEGER NOT NULL,
        permite_nulo INTEGER NOT NULL,
        descricao TEXT NOT NULL,
        exemplo_formato TEXT,
        origem_dado TEXT
    );
    """)

    registros = []
    for tabela, tinfo in DICIONARIO_SEMANTICO.items():
        # Verifica se tabela existe no banco com consulta parametrizada
        exists = cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = ?;", (tabela,)).fetchone()
        if not exists:
            continue
        # Tabela validada contra sqlite_master antes de inspecionar pragma
        cols_pragma = {c[1]: (c[2], c[5], not c[3]) for c in cur.execute(f"PRAGMA table_info(\"{tabela}\");").fetchall()}  # nosec B608 (tabela validada contra sqlite_master)
        
        for col, col_meta in tinfo["colunas"].items():
            tipo_prg, pk, nullable = cols_pragma.get(col, (col_meta[1], 0, 1))
            registros.append((
                tabela,
                col,
                tipo_prg,
                1 if pk else 0,
                1 if nullable else 0,
                col_meta[0],
                col_meta[2],
                tinfo["origem"]
            ))

    cur.executemany("""
    INSERT INTO dicionario_dados 
    (tabela, coluna, tipo_sqlite, chave_primaria, permite_nulo, descricao, exemplo_formato, origem_dado)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, registros)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_dic_tabela ON dicionario_dados(tabela);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_dic_coluna ON dicionario_dados(coluna);")
    conn.commit()
    print(f"✔ Tabela 'dicionario_dados' criada com {len(registros)} atributos catalogados!")

def gerar_markdown():
    linhas = [
        "# Dicionário de Dados do Banco Relacional da Dissertação",
        "",
        "**Base de Dados:** `dados/resultados_dissertacao.db` (SQLite 3)  ",
        "**Projeto:** Framework de Decisão Pública Auditável (FDPA) para Gestão de Frotas  ",
        "**Programa:** Pós-Graduação em Computação Aplicada (PPGCAP), Universidade do Estado de Santa Catarina (UDESC)  ",
        "**Autor:** Eduardo Lopes Jonker  ",
        "**Orientação:** Vivian Kremer Kalempa | **Coorientação:** Yuri Kaszubowski Lopes  ",
        "",
        "---",
        "",
        "## 1. Visão Geral do Banco de Dados",
        "",
        "O banco de dados relacional `dados/resultados_dissertacao.db` centraliza todos os microdados administrativos, modelos de aprendizado de máquina, projeções prescritivas e auditorias contábeis desenvolvidas nesta dissertação de mestrado. Ele integra:",
        "",
        "1. **Módulo de Abastecimentos de Combustíveis:** 1.000.000 de lançamentos detalhados (R$ 153.488.476,96 e 34.311.319 L) higienizados, anonimizados conforme a LGPD e auditados por modelos de *Isolation Forest* e decomposição temporal *Prophet*.",
        "2. **Módulo de Manutenção Veicular:** 223.819 itens limpos de ordens de serviço contemplando peças, serviços mecânicos, glosas técnicas e tempos de imobilização (*downtime*).",
        "3. **Módulo de Inteligência Artificial e Governança:** Experimentos de acurácia, calibração (*Brier Score*, ECE), métricas de redes complexas bipartidas (*Louvain Modularity*), catálogo de 101 figuras e veículos antieconômicos elegíveis a leilão público (Decreto Estadual nº 47.539/2018).",
        "",
        "### Sumário das Tabelas Catalogadas",
        "",
        "| Tabela | Finalidade Semântica | Volume de Dados | Origem Primária |",
        "| :--- | :--- | :---: | :--- |",
    ]

    for tabela, tinfo in DICIONARIO_SEMANTICO.items():
        linhas.append(f"| [`{tabela}`](#tabela-{tabela.replace('_', '-')}) | {tinfo['descricao_tabela']} | {tinfo['volume']} | {tinfo['origem']} |")

    linhas.append("")
    linhas.append("---")
    linhas.append("")
    linhas.append("## 2. Especificação Detalhada das Tabelas e Atributos")
    linhas.append("")

    for tabela, tinfo in DICIONARIO_SEMANTICO.items():
        linhas.append(f"### Tabela: `{tabela}`")
        linhas.append(f"**Descrição:** {tinfo['descricao_tabela']}  ")
        linhas.append(f"**Origem do Dado:** {tinfo['origem']}  ")
        linhas.append(f"**Volume Registrado:** {tinfo['volume']}  ")
        linhas.append("")
        linhas.append("| Coluna | Tipo SQL | Chave | Permite Nulo | Descrição Semântica do Atributo | Exemplo de Valor |")
        linhas.append("| :--- | :---: | :---: | :---: | :--- | :--- |")
        
        for col, col_meta in tinfo["colunas"].items():
            pk_str = "PK" if col in ["cod_venda", "placa", "id_indicador", "id", "exercicio", "numero", "chave", "id_estabelecimento"] else "-"
            nullable_str = "Não" if pk_str == "PK" else "Sim"
            linhas.append(f"| `{col}` | `{col_meta[1]}` | {pk_str} | {nullable_str} | {col_meta[0]} | `{col_meta[2]}` |")
        
        linhas.append("")
        linhas.append("---")
        linhas.append("")

    linhas.append("## 3. Integridade Referencial e Relações entre Entidades")
    linhas.append("")
    linhas.append("```")
    linhas.append("        DIAGRAMA DE RELACIONAMENTOS DO BANCO DE DADOS (ER)")
    linhas.append("        ───────────────────────────────────────────────────")
    linhas.append("         [veiculos_leilao]               [abastecimentos]")
    linhas.append("              │ placa                          │ placa")
    linhas.append("              │                                │")
    linhas.append("              ▼                                ▼")
    linhas.append("        ┌───────────────┐               ┌───────────────┐")
    linhas.append("        │  VEÍCULOS DO  │◄─────────────►│ MANUTENÇÃO DE │")
    linhas.append("        │  PATRIMÔNIO   │   veiculo_id  │     ITENS     │")
    linhas.append("        └───────┬───────┘               └───┬───────────┘")
    linhas.append("                │ orgao                     │ cd_estabelecimento")
    linhas.append("                ▼                           ▼")
    linhas.append("        [auditoria_orgaos]              [grafos_centralidade]")
    linhas.append("        ───────────────────────────────────────────────────")
    linhas.append("```")
    linhas.append("")
    linhas.append("1. **Chave de Intersecção Veicular (`placa` / `veiculo_id`):** Articula os 1.000.000 de lançamentos de abastecimentos, as 223.819 ordens de manutenção e os veículos indicados para desfazimento em leilão.")
    linhas.append("2. **Chave Institucional (`orgao` / `secretaria` / `unidade`):** Agrupa os custos por Unidade Gestora Orçamentária vinculada à LOA e ao Decreto Estadual nº 47.539/2018.")
    linhas.append("3. **Chave de Prestador de Serviço (`cd_estabelecimento` / `id_estabelecimento`):** Conecta os itens de manutenção autorizados aos nós da rede complexa de oficinas para cálculo de modularidade de Louvain ($Q = 0,5646$) e centralidade de intermediação.")
    linhas.append("")

    texto_md = "\n".join(linhas)
    MD_PATH.write_text(texto_md, encoding="utf-8")
    
    # Copia para relatorios/ e dashboard/data/
    shutil.copy2(MD_PATH, BASE_DIR / "relatorios" / "dicionario_de_dados_banco.md")
    shutil.copy2(MD_PATH, BASE_DIR / "dashboard" / "data" / "dicionario_de_dados_banco.md")
    print(f"✔ Arquivo Markdown gerado em: {MD_PATH}")

def compilar_pdf():
    text = MD_PATH.read_text(encoding="utf-8")
    html_body = markdown.markdown(text, extensions=['tables', 'fenced_code', 'toc'])

    html_doc = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Dicionário de Dados do Banco de Dados Relacional</title>
<style>
    @page {{
        size: A4 portrait;
        margin: 2.2cm 2.0cm 2.2cm 2.0cm;
        @top-right {{
            content: "Dicionário de Dados • Banco Relacional SQLite";
            font-size: 8pt;
            color: #64748b;
            font-family: 'Liberation Sans', sans-serif;
            font-style: italic;
        }}
        @bottom-right {{
            content: "Página " counter(page) " de " counter(pages);
            font-size: 8pt;
            color: #64748b;
            font-family: 'Liberation Sans', sans-serif;
        }}
        @bottom-left {{
            content: "PPGCAP / UDESC • Eduardo Lopes Jonker (2026)";
            font-size: 8pt;
            color: #64748b;
            font-family: 'Liberation Sans', sans-serif;
        }}
    }}
    body {{
        font-family: 'Liberation Serif', 'Times New Roman', serif;
        font-size: 9pt;
        line-height: 1.45;
        color: #111827;
        margin: 0;
        padding: 0;
        text-align: justify;
    }}
    h1 {{
        font-family: 'Liberation Sans', Arial, sans-serif;
        font-size: 16pt;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.25;
        margin-bottom: 6px;
    }}
    h2 {{
        font-family: 'Liberation Sans', Arial, sans-serif;
        font-size: 11pt;
        font-weight: 700;
        color: #1e3a8a;
        border-bottom: 1.5px solid #cbd5e1;
        padding-bottom: 3px;
        margin-top: 16px;
        margin-bottom: 8px;
        text-transform: uppercase;
    }}
    h3 {{
        font-family: 'Liberation Sans', Arial, sans-serif;
        font-size: 9.5pt;
        font-weight: 700;
        color: #0f172a;
        margin-top: 12px;
        margin-bottom: 4px;
    }}
    p {{
        margin-bottom: 6px;
        text-indent: 1.0em;
    }}
    p:first-of-type {{
        text-indent: 0;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 7.5pt;
        margin: 10px 0;
        font-family: 'Liberation Sans', Arial, sans-serif;
    }}
    th {{
        background: #0f172a;
        color: #ffffff;
        padding: 5px 6px;
        font-weight: 600;
        border: 1px solid #0f172a;
        text-align: left;
    }}
    td {{
        padding: 4px 6px;
        border: 1px solid #cbd5e1;
        vertical-align: top;
    }}
    tr:nth-child(even) td {{
        background: #f8fafc;
    }}
    pre, code {{
        font-family: 'Liberation Mono', monospace;
        font-size: 7.5pt;
        background: #f1f5f9;
    }}
    pre {{
        padding: 8px;
        border-radius: 4px;
        border: 1px solid #e2e8f0;
        overflow-x: auto;
    }}
    hr {{
        border: none;
        border-top: 1px solid #cbd5e1;
        margin: 14px 0;
    }}
</style>
</head>
<body>
{html_body}
</body>
</html>
"""
    html = weasyprint.HTML(string=html_doc, base_url=str(BASE_DIR))
    html.write_pdf(target=str(PDF_PATH))
    print(f"✔ PDF compilado com sucesso: {PDF_PATH} ({PDF_PATH.stat().st_size / 1024:.1f} KB)")

def main():
    print("=" * 80)
    print("GERANDO DICIONÁRIO DE DADOS DO BANCO RELACIONAL DA DISSERTAÇÃO")
    print(f"Banco de Origem: {DB_PATH}")
    print("=" * 80)

    conn = sqlite3.connect(DB_PATH)
    criar_tabela_dicionario_sqlite(conn)
    conn.close()

    gerar_markdown()
    compilar_pdf()
    print("=" * 80)

if __name__ == "__main__":
    main()
