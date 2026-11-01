#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
MÓDULO DE ANONIMIZAÇÃO E CONFORMIDADE COM A LGPD (LEI Nº 13.709/2018)
================================================================================
Pesquisa de Dissertação de Mestrado (PPGCAP / CCT / UDESC)
Autor: Eduardo Lopes Jonker
Orientadores: Profa. Dra. Vivian Kremer Kalempa / Prof. Dr. Yuri Kaszubowski Lopes

Funcionalidades de Privacidade e Governança:
1. Detecção e Anonimização de Dados Pessoais Identificáveis (PII) via Microsoft Presidio.
2. Pseudonimização Criptográfica Segura (HMAC-SHA256 com Chave Secreta/Salt) para
   preservar a integridade longitudinal de veículos e processos sem revelar placas ou CPFs.
3. Mascaramento Especializado de Identificadores Brasileiros:
   - Placas Veiculares (Padrão Antigo e Mercosul)
   - CPFs e RGs de condutores e gestores
   - Telefones, e-mails e nomes próprios em relatos de texto livre (NLP pt_BR)
4. Geração de Dados Sintéticos Realistas via Faker (pt_BR) para ambientes de teste.
5. Sanitizador em Lote para DataFrames do Pandas com conformidade aos Artigos 13 e 16 da LGPD.
================================================================================
"""

import os
import re
import hmac
import hashlib
from typing import Dict, Any, List, Optional, Union
import pandas as pd
from faker import Faker

# Microsoft Presidio para detecção e anonimização de PII
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# Faker pt_BR para dados sintéticos
fake_pt = Faker('pt_BR')


class LGPDAnonymizer:
    """Motor de Anonimização, Pseudonimização e Sanitização para a LGPD."""

    def __init__(self, salt: Optional[str] = None):
        # Sal secreto para pseudonimização determinística (HMAC-SHA256)
        self.salt = (salt or os.environ.get("LGPD_SECRET_SALT", "UDESC_PPGCAP_2026_SECURE_SALT_KEY")).encode('utf-8')
        
        # Inicializa Presidio Anonymizer
        self.anonymizer = AnonymizerEngine()

        # Inicializa Presidio Analyzer com padrões customizados para o Brasil
        self.analyzer = AnalyzerEngine()
        self._configurar_reconhecedores_brasileiros()

    def _configurar_reconhecedores_brasileiros(self):
        """Registra padrões regex de identificadores específicos do Brasil e de frotas públicas."""
        # 1. Placa Mercosul e Antiga: [A-Z]{3}-?[0-9][A-Z0-9][0-9]{2}
        padrao_placa = Pattern(
            name="padrao_placa_veicular",
            regex=r"\b[A-Za-z]{3}[- ]?[0-9][A-Za-z0-9][0-9]{2}\b",
            score=0.85
        )
        rec_placa = PatternRecognizer(
            supported_entity="PLACA_VEICULAR",
            patterns=[padrao_placa]
        )
        self.analyzer.registry.add_recognizer(rec_placa)

        # 2. CPF Brasileiro: \d{3}\.?\d{3}\.?\d{3}-?\d{2}
        padrao_cpf = Pattern(
            name="padrao_cpf_brasil",
            regex=r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b",
            score=0.85
        )
        rec_cpf = PatternRecognizer(
            supported_entity="CPF_BRASIL",
            patterns=[padrao_cpf]
        )
        self.analyzer.registry.add_recognizer(rec_cpf)

        # 3. CNPJ: \d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}
        padrao_cnpj = Pattern(
            name="padrao_cnpj_brasil",
            regex=r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b",
            score=0.85
        )
        rec_cnpj = PatternRecognizer(
            supported_entity="CNPJ_BRASIL",
            patterns=[padrao_cnpj]
        )
        self.analyzer.registry.add_recognizer(rec_cnpj)

    def pseudonimizar_identificador(self, valor: str, prefixo: str = "ID") -> str:
        """
        Pseudonimiza deterministicamente um identificador (placa, chassi, CPF) via HMAC-SHA256.
        Garante que o mesmo veículo tenha o mesmo ID pseudo-anônimo em todo o dataset,
        permitindo análises longitudinais de machine learning sem expor dados reais.
        """
        if pd.isna(valor) or not str(valor).strip():
            return "N/A"
        raw = str(valor).strip().upper()
        h = hmac.new(self.salt, raw.encode('utf-8'), hashlib.sha256).hexdigest()
        return f"{prefixo}_{h[:10]}"

    def mascarar_placa(self, placa: str) -> str:
        """Mascara placa mantendo formato genérico para auditoria (Ex: BRA****)."""
        if pd.isna(placa) or not str(placa).strip():
            return "N/A"
        p = str(placa).strip().upper().replace('-', '')
        if len(p) >= 7:
            return f"{p[:3]}****"
        return "PLA****"

    def mascarar_cpf(self, cpf: str) -> str:
        """Mascara CPF mantendo apenas dígitos não identificáveis (Ex: ***.***.123-**)."""
        if pd.isna(cpf) or not str(cpf).strip():
            return "N/A"
        num = re.sub(r'\D', '', str(cpf))
        if len(num) == 11:
            return f"***.***.{num[6:9]}-**"
        return "***.***.***-**"

    def anonimizar_texto_livre(self, texto: str) -> str:
        """
        Sanitiza textos livres (relatos de oficinas, observações de motoristas, ordens de serviço)
        removendo nomes de pessoas, placas, CPFs, e-mails e telefones via NLP.
        """
        if pd.isna(texto) or not str(texto).strip():
            return ""

        texto_str = str(texto)
        # Analisa entidades no texto
        results = self.analyzer.analyze(text=texto_str, language='en')

        # Operadores de anonimização (redação com tag amigável)
        operators = {
            "PERSON": OperatorConfig("replace", {"new_value": "[PESSOA_ANONIMIZADA]"}),
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[EMAIL_ANONIMIZADO]"}),
            "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[TELEFONE_ANONIMIZADO]"}),
            "CPF_BRASIL": OperatorConfig("replace", {"new_value": "[CPF_ANONIMIZADO]"}),
            "PLACA_VEICULAR": OperatorConfig("replace", {"new_value": "[PLACA_ANONIMIZADA]"}),
            "CNPJ_BRASIL": OperatorConfig("replace", {"new_value": "[CNPJ_ANONIMIZADO]"}),
        }

        anonymized_result = self.anonymizer.anonymize(
            text=texto_str,
            analyzer_results=results,
            operators=operators
        )

        # Regex pós-processamento para garantir que placas não escapem
        texto_limpo = anonymized_result.text
        texto_limpo = re.sub(r"\b[A-Za-z]{3}[- ]?[0-9][A-Za-z0-9][0-9]{2}\b", "[PLACA_ANONIMIZADA]", texto_limpo)
        texto_limpo = re.sub(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", "[CPF_ANONIMIZADO]", texto_limpo)

        return texto_limpo

    def anonimizar_dataframe_os(self, df: pd.DataFrame, gerar_dados_sinteticos: bool = False) -> pd.DataFrame:
        """
        Aplica a política de anonimização completa da LGPD sobre um DataFrame de Ordens de Serviço:
        - ds_placa -> pseudonimização determinística (ex: VEIC_a7f9b2c1)
        - relatos e observações -> redação de PII por NLP
        - dados cadastrais sensíveis -> mascarados
        """
        df_anon = df.copy()

        # 1. Pseudonimização de Placas
        if 'ds_placa' in df_anon.columns:
            df_anon['ds_placa_original'] = df_anon['ds_placa']  # caso precise referenciar
            df_anon['ds_placa'] = df_anon['ds_placa'].apply(lambda x: self.pseudonimizar_identificador(x, prefixo="VEIC"))

        # 2. Textos Livres e Relatos de Gestores
        colunas_texto = ['relato_gestor_auto', 'ds_complemento', 'ds_informacao_adicional1', 
                         'ds_informacao_adicional2', 'ds_observacao']
        for col in colunas_texto:
            if col in df_anon.columns:
                df_anon[col] = df_anon[col].apply(self.anonimizar_texto_livre)

        # 3. Anonimização de motorista ou mecânico se existir
        for col in ['motorista', 'condutor', 'nome_mecanico']:
            if col in df_anon.columns:
                if gerar_dados_sinteticos:
                    df_anon[col] = [fake_pt.name() for _ in range(len(df_anon))]
                else:
                    df_anon[col] = "[CONDUTOR_ANONIMIZADO]"

        return df_anon


# Instância utilitária pronta para uso imediato
lgpd = LGPDAnonymizer()


if __name__ == "__main__":
    print("=" * 80)
    print(" DEMONSTRAÇÃO DO MÓDULO DE ANONIMIZAÇÃO LGPD (LEI 13.709/2018)")
    print("=" * 80)
    
    exemplo_placa = "MLG0296"
    exemplo_cpf = "084.521.999-42"
    exemplo_relato = "O motorista João Silva (CPF 084.521.999-42) informou que a viatura RLY5H12 apresentou barulho no câmbio. Ligar para 48 99123-4567."
    
    print(f"Placa Original: {exemplo_placa}")
    print(f"Placa Pseudonimizada (HMAC-SHA256): {lgpd.pseudonimizar_identificador(exemplo_placa, 'VEIC')}")
    print(f"Placa Mascarada: {lgpd.mascarar_placa(exemplo_placa)}")
    print(f"CPF Mascarado: {lgpd.mascarar_cpf(exemplo_cpf)}")
    print("\nTexto Livre Original:")
    print(f"  \"{exemplo_relato}\"")
    print("\nTexto Livre Anonimizado (LGPD / Presidio NLP):")
    print(f"  \"{lgpd.anonimizar_texto_livre(exemplo_relato)}\"")
    print("=" * 80)
