#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
COMPILADOR DO RELATÓRIO GERENCIAL EXECUTIVO DE FROTAS EM DOCX (WORD)
Secretaria de Estado da Administração de Santa Catarina (SEA/SC)
Diretoria de Gestão Patrimonial • Gerência de Frotas Integradas (GFI/DITI)
================================================================================
"""

import sys
import os
import json
import shutil
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.compilar_dissertacao_mestrado_completa import fmt_moeda, fmt_numero
from scripts.compilar_relatorio_gerencial_frotas import carregar_dados_gerenciais

CHARTS_DIR = BASE_DIR / "charts"
GRAFICOS_DIR = BASE_DIR / "graficos"
RELATORIOS_DIR = BASE_DIR / "relatorios"
DOCS_DIR = BASE_DIR / "Documentos"
PDF_DIR = BASE_DIR / "relatorios_pdf"
DASH_DIR = BASE_DIR / "dashboard"
DASH_PDF_DIR = DASH_DIR / "relatorios_pdf"

def set_cell_margins(cell, top=80, bottom=80, left=100, right=100):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_background(cell, fill_hex):
    shading_xml = f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'
    cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))

def set_table_borders_clean(table):
    tblPr = table._tbl.tblPr
    borders_xml = f"""
    <w:tblBorders {nsdecls("w")}>
        <w:top w:val="single" w:sz="6" w:space="0" w:color="0284C7"/>
        <w:bottom w:val="single" w:sz="6" w:space="0" w:color="0284C7"/>
        <w:left w:val="none"/>
        <w:right w:val="none"/>
        <w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
        <w:insideV w:val="none"/>
    </w:tblBorders>
    """
    tblPr.append(parse_xml(borders_xml))

def configurar_documento(doc):
    for sec in doc.sections:
        sec.top_margin = Cm(2.5)
        sec.left_margin = Cm(2.5)
        sec.bottom_margin = Cm(2.0)
        sec.right_margin = Cm(2.0)
        sec.page_width = Cm(21.0)
        sec.page_height = Cm(29.7)

    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Arial'
    font.size = Pt(11)
    font.color.rgb = RGBColor(15, 23, 42)
    p_format = style_normal.paragraph_format
    p_format.line_spacing = 1.25
    p_format.space_after = Pt(4)
    p_format.space_before = Pt(0)
    p_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

def main():
    print("=" * 80)
    print("COMPILANDO RELATÓRIO GERENCIAL EXECUTIVO EM DOCX (WORD)")
    print("=" * 80)

    doc = docx.Document()
    configurar_documento(doc)

    # CABEÇALHO INSTITUCIONAL
    p_hdr = doc.add_paragraph()
    p_hdr.paragraph_format.space_before = Pt(0)
    p_hdr.paragraph_format.space_after = Pt(2)
    p_hdr.paragraph_format.first_line_indent = Inches(0)
    r_gov = p_hdr.add_run("GOVERNO DO ESTADO DE SANTA CATARINA • SECRETARIA DE ESTADO DA ADMINISTRAÇÃO\nDIRETORIA DE GESTÃO PATRIMONIAL • GERÊNCIA DE FROTAS INTEGRADAS (GFI/DITI)")
    r_gov.font.size = Pt(9.5)
    r_gov.font.bold = True
    r_gov.font.color.rgb = RGBColor(2, 132, 199)

    p_tit = doc.add_paragraph()
    p_tit.paragraph_format.space_before = Pt(10)
    p_tit.paragraph_format.space_after = Pt(4)
    p_tit.paragraph_format.first_line_indent = Inches(0)
    r_tit = p_tit.add_run("RELATÓRIO GERENCIAL EXECUTIVO DE GESTÃO E AUDITORIA DE FROTAS")
    r_tit.font.size = Pt(15)
    r_tit.font.bold = True
    r_tit.font.color.rgb = RGBColor(15, 23, 42)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(14)
    p_sub.paragraph_format.first_line_indent = Inches(0)
    r_sub = p_sub.add_run("Painel Executivo • 38 Indicadores GFI • Auditoria de 350.737 Ordens de Serviço • Projeção Orçamentária Trienal 2027–2029")
    r_sub.font.size = Pt(10)
    r_sub.font.color.rgb = RGBColor(100, 116, 139)

    # CARREGAR DADOS
    gfi, df_patr, df_anom = carregar_dados_gerenciais()

    df_leilao = pd.DataFrame()
    if not df_patr.empty and 'razao_gasto_venal' in df_patr.columns:
        df_leilao = df_patr[df_patr['razao_gasto_venal'] >= 0.40].sort_values(by='razao_gasto_venal', ascending=False)

    # RESUMO EXECUTIVO
    p_box = doc.add_paragraph()
    p_box.paragraph_format.space_before = Pt(6)
    p_box.paragraph_format.space_after = Pt(10)
    p_box.paragraph_format.first_line_indent = Inches(0)
    r_bx = p_box.add_run("Síntese Executiva do Período Auditado:\n"
                         "• Volume Total Processado: 350.737 Ordens de Serviço e 1.636.541 itens de manutenção mecânica.\n"
                         "• Dispêndio Global Aprovado: R$ 138.759.653,82 (68,21% em peças e 31,79% em mão de obra).\n"
                         "• Economia Direta por Glosas Técnicas: R$ 22.422.391,00 evitados em orçamentos suspeitos.\n"
                         "• Veículos Antieconômicos Identificados (Art. 5º Decreto 47.539/2018): 313 bens indicados a leilão.\n"
                         "• Economia Prescritiva Projetada (2027–2029): R$ 40.088.374,00 com solver MILP sob inflação setorial de 6,08% a.a.")
    r_bx.font.size = Pt(9.5)

    # TABELA DE 38 INDICADORES GFI
    p_s1 = doc.add_paragraph()
    p_s1.paragraph_format.space_before = Pt(16)
    p_s1.paragraph_format.space_after = Pt(6)
    p_s1.paragraph_format.first_line_indent = Inches(0)
    p_s1.paragraph_format.keep_with_next = True
    r = p_s1.add_run("1. MATRIZ CONSOLIDADA DOS 38 INDICADORES GFI (CARTILHA SEA 2026)")
    r.font.bold = True
    r.font.size = Pt(12)
    r.font.color.rgb = RGBColor(2, 132, 199)

    matriz_38 = gfi.get('matriz_exaustiva_38_indicadores', [])
    if matriz_38:
        tbl_gfi = doc.add_table(rows=1, cols=5)
        tbl_gfi.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders_clean(tbl_gfi)
        hdr = tbl_gfi.rows[0]
        col_names = ["Cód.", "Tema GFI", "Indicador Monitorado", "Valor Apurado", "Status"]
        for ci, cname in enumerate(col_names):
            c = hdr.cells[ci]
            set_cell_background(c, "F1F5F9")
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.first_line_indent = Inches(0)
            r = p.add_run(cname)
            r.font.bold = True
            r.font.size = Pt(8.5)

        for ind in matriz_38:
            row = tbl_gfi.add_row()
            vals = [
                str(ind.get('codigo', '')),
                str(ind.get('tema', ''))[:22],
                str(ind.get('nome', ''))[:35],
                str(ind.get('valor_formatado', ind.get('valor_apurado', ''))),
                str(ind.get('status', ''))
            ]
            for ci, val_txt in enumerate(vals):
                c = row.cells[ci]
                p = c.paragraphs[0]
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.first_line_indent = Inches(0)
                r = p.add_run(val_txt)
                r.font.size = Pt(8.0)
                if ci == 0:
                    r.font.bold = True

    # TABELA DE VEÍCULOS PARA LEILÃO (DADOS REAIS SEM ANONIMIZAÇÃO)
    doc.add_page_break()
    p_s2 = doc.add_paragraph()
    p_s2.paragraph_format.space_before = Pt(16)
    p_s2.paragraph_format.space_after = Pt(6)
    p_s2.paragraph_format.first_line_indent = Inches(0)
    p_s2.paragraph_format.keep_with_next = True
    r = p_s2.add_run("2. VEÍCULOS PRIORITÁRIOS PARA LEILÃO PÚBLICO (ART. 5º DECRETO ESTADUAL Nº 47.539/2018)")
    r.font.bold = True
    r.font.size = Pt(12)
    r.font.color.rgb = RGBColor(2, 132, 199)

    p_av = doc.add_paragraph()
    p_av.paragraph_format.first_line_indent = Inches(0)
    p_av.add_run("Nota Operacional: Relatório de circulação restrita aos auditores e fiscais de contrato da SEA DITI. Identificadores reais preservados para instrução formal de processos de desfazimento.").font.size = Pt(8.5)

    if not df_leilao.empty:
        tbl_l = doc.add_table(rows=1, cols=7)
        tbl_l.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders_clean(tbl_l)
        hdr = tbl_l.rows[0]
        col_names = ["Placa Real", "Modelo do Veículo", "Órgão / Secretaria", "Idade", "Gasto Manut.", "Valor Venal", "% Venal"]
        for ci, cname in enumerate(col_names):
            c = hdr.cells[ci]
            set_cell_background(c, "FEE2E2")
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.first_line_indent = Inches(0)
            r = p.add_run(cname)
            r.font.bold = True
            r.font.size = Pt(8.5)

        for _, v in df_leilao.head(25).iterrows():
            row = tbl_l.add_row()
            razao_val = v.get('razao_gasto_venal', 0)
            try:
                razao_pct = float(razao_val if pd.notna(razao_val) else 0) * 100
            except Exception:
                razao_pct = 0.0

            vals = [
                str(v.get('Placa_clean', v.get('Placa', 'N/A'))),
                str(v.get('ds_veiculomodelo', 'N/A'))[:22],
                str(v.get('ÓRGÃO', 'N/A'))[:20],
                f"{int(v.get('idade_veiculo', 10))} anos",
                fmt_moeda(v.get('Valor_Aprovado', 0)),
                fmt_moeda(v.get('valor_ref', 0)),
                f"{razao_pct:.1f}%"
            ]
            for ci, val_txt in enumerate(vals):
                c = row.cells[ci]
                p = c.paragraphs[0]
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.first_line_indent = Inches(0)
                r = p.add_run(val_txt)
                r.font.size = Pt(8.0)
                if ci == 0:
                    r.font.bold = True
                    r.font.color.rgb = RGBColor(185, 28, 28)

    # SALVAR ARQUIVO DOCX
    docx_out = RELATORIOS_DIR / "relatorio_gerencial_frotas_executivo.docx"
    print(f"Salvando DOCX gerencial em {docx_out}...")
    doc.save(str(docx_out))
    print(f"DOCX gerencial gerado com sucesso! Tamanho: {docx_out.stat().st_size / (1024 * 1024):.2f} MB")

    destinos = [
        DOCS_DIR / "relatorio_gerencial_frotas_executivo.docx",
        PDF_DIR / "relatorio_gerencial_frotas_executivo.docx",
        DASH_DIR / "relatorio_gerencial_frotas_executivo.docx",
        DASH_PDF_DIR / "relatorio_gerencial_frotas_executivo.docx"
    ]
    for d in destinos:
        try:
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(docx_out, d)
            print(f"Sincronizado em: {d}")
        except Exception as e:
            print(f"Nota na sincronização de {d}: {e}")

    print("=" * 80)
    print("COMPILAÇÃO DO RELATÓRIO GERENCIAL EM DOCX CONCLUÍDA COM ÊXITO!")
    print("=" * 80)

if __name__ == "__main__":
    main()
