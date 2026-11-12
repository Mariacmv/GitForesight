
from io import BytesIO
from datetime import datetime
from xml.sax.saxutils import escape

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)


# Identidade visual do GitForesight
ROXO = colors.HexColor("#5F5CE5")
NAVY = colors.HexColor("#0F172A")
CINZA = colors.HexColor("#64748B")
CINZA_CLARO = colors.HexColor("#F1F5F9")
BRANCO = colors.white


def _formatar_numero(valor, casas=2):
    if valor is None or pd.isna(valor):
        return "N/D"
    return f"{float(valor):.{casas}f}".replace(".", ",")


def _formatar_data(valor):
    if valor is None or pd.isna(valor):
        return "N/D"

    data = pd.to_datetime(valor, errors="coerce", utc=True)

    if pd.isna(data):
        return str(valor)

    return data.strftime("%d/%m/%Y")


def _texto(valor):
    return escape(str(valor)) if valor is not None else "N/D"


def _criar_capa(
    estilos,
    repo_name,
    branch,
    data_relatorio,
    data_referencia,
    score,
    largura_util,
):
    conteudo_capa = []

    # Bloco principal da capa
    hero = [
        Paragraph("GITFORESIGHT", estilos["capa_marca"]),
        Paragraph(
            "Relatório de<br/>Análise de Riscos",
            estilos["capa_titulo"],
        ),
        Spacer(1, 12),
        Paragraph(
            "Visão técnica dos riscos, histórico do repositório "
            "e cenários de evolução.",
            estilos["capa_subtitulo"],
        ),
    ]

    painel = Table(
        [[hero]],
        colWidths=[largura_util],
        rowHeights=[8.2 * cm],
    )

    painel.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("BOX", (0, 0), (-1, -1), 0, NAVY),
        ("LEFTPADDING", (0, 0), (-1, -1), 25),
        ("RIGHTPADDING", (0, 0), (-1, -1), 25),
        ("TOPPADDING", (0, 0), (-1, -1), 28),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    conteudo_capa.append(Spacer(1, 1.3 * cm))
    conteudo_capa.append(painel)
    conteudo_capa.append(Spacer(1, 1.2 * cm))

    # Identificação do repositório
    identificacao = [
        [
            Paragraph("REPOSITÓRIO", estilos["capa_secao"]),
            Paragraph("BRANCH", estilos["capa_secao"]),
        ],
        [
            Paragraph(_texto(repo_name), estilos["capa_valor"]),
            Paragraph(_texto(branch), estilos["capa_valor"]),
        ],
        [
            Paragraph("DATA DO RELATÓRIO", estilos["capa_secao"]),
            Paragraph("ÚLTIMO REGISTRO DE RISCO", estilos["capa_secao"]),
        ],
        [
            Paragraph(_texto(data_relatorio), estilos["capa_valor"]),
            Paragraph(_texto(data_referencia), estilos["capa_valor"]),
        ],
    ]

    tabela = Table(
        identificacao,
        colWidths=[largura_util * 0.58, largura_util * 0.42],
    )

    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CINZA_CLARO),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 1), (-1, 1), 0.5, colors.HexColor("#CBD5E1")),
    ]))

    conteudo_capa.append(tabela)
    conteudo_capa.append(Spacer(1, 0.8 * cm))

    conteudo_capa.append(
        Paragraph(
            "DOCUMENTO TÉCNICO • ANÁLISE DE REPOSITÓRIO",
            estilos["capa_nota"],
        )
    )

    return conteudo_capa

def _criar_estilos():
    base = getSampleStyleSheet()

    return {
    "capa_marca": ParagraphStyle(
        "CapaMarca",
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#67E8F9"),
        spaceAfter=22,
    ),
    "capa_titulo": ParagraphStyle(
        "CapaTitulo",
        fontName="Helvetica-Bold",
        fontSize=27,
        leading=34,
        textColor=BRANCO,
    ),
    "capa_subtitulo": ParagraphStyle(
        "CapaSubtitulo",
        fontName="Helvetica",
        fontSize=11,
        leading=17,
        textColor=colors.HexColor("#CBD5E1"),
    ),
    "capa_secao": ParagraphStyle(
        "CapaSecao",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=ROXO,
    ),
    "capa_valor": ParagraphStyle(
        "CapaValor",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=NAVY,
    ),
    "capa_nota": ParagraphStyle(
        "CapaNota",
        fontName="Helvetica",
        fontSize=8,
        leading=12,
        textColor=CINZA,
    ),
        "titulo": ParagraphStyle(
            "TituloGF",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=25,
            leading=31,
            textColor=NAVY,
            alignment=TA_LEFT,
            spaceAfter=12,
        ),
        "subtitulo": ParagraphStyle(
            "SubtituloGF",
            parent=base["Normal"],
            fontSize=11,
            leading=16,
            textColor=CINZA,
            spaceAfter=8,
        ),
        "secao": ParagraphStyle(
            "SecaoGF",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=19,
            textColor=NAVY,
            spaceBefore=14,
            spaceAfter=9,
        ),
        "subsecao": ParagraphStyle(
            "SubsecaoGF",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=ROXO,
            spaceBefore=8,
            spaceAfter=5,
        ),
        "corpo": ParagraphStyle(
            "CorpoGF",
            parent=base["BodyText"],
            fontSize=9,
            leading=14,
            textColor=NAVY,
            spaceAfter=6,
        ),
        "pequeno": ParagraphStyle(
            "PequenoGF",
            parent=base["BodyText"],
            fontSize=7,
            leading=10,
            textColor=CINZA,
        ),
        "celula": ParagraphStyle(
            "CelulaGF",
            parent=base["BodyText"],
            fontSize=7,
            leading=9,
            textColor=NAVY,
        ),
        "celula_branca": ParagraphStyle(
            "CelulaBrancaGF",
            parent=base["BodyText"],
            fontSize=8,
            leading=10,
            textColor=BRANCO,
        ),
    }


def _tabela(dados, larguras, cabecalho=True):
    tabela = Table(
        dados,
        colWidths=larguras,
        repeatRows=1 if cabecalho else 0,
        hAlign="LEFT",
    )

    comandos = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#E2E8F0")),
    ]

    if cabecalho:
        comandos.extend([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), BRANCO),
        ])

        for linha in dados[1:]:
            pass

        for indice in range(1, len(dados)):
            if indice % 2 == 0:
                comandos.append(
                    ("BACKGROUND", (0, indice), (-1, indice), CINZA_CLARO)
                )

    tabela.setStyle(TableStyle(comandos))
    return tabela


def _cabecalho_rodape(canvas, doc):
    canvas.saveState()

    largura, altura = A4

    canvas.setStrokeColor(colors.HexColor("#E2E8F0"))
    canvas.setLineWidth(0.5)
    canvas.line(2 * cm, 1.55 * cm, largura - 2 * cm, 1.55 * cm)

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(CINZA)
    canvas.drawString(2 * cm, 1.15 * cm, "GitForesight | Relatório de análise")
    canvas.drawRightString(
        largura - 2 * cm,
        1.15 * cm,
        f"Página {doc.page}",
    )

    canvas.restoreState()


def gerar_relatorio_pdf(
    predictive_data,
    heatmap_items,
    repo_name,
    branch,
    analysis_date=None,
):
    """
    Gera o relatório completo da análise e retorna os bytes do PDF.

    predictive_data: resultado de build_predictive()
    heatmap_items: resultado de build_heatmap()
    repo_name: nome ou identificação do repositório
    branch: branch analisada
    analysis_date: data da análise
    """

    if predictive_data.get("status") != "ok":
        raise ValueError("Não há dados suficientes para gerar o relatório.")

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Relatório de Análise - GitForesight",
        author="GitForesight",
    )

    estilos = _criar_estilos()
    conteudo = []

    largura_util = A4[0] - 4 * cm

    current = predictive_data["current"]
    history = predictive_data["history"]
    projection = predictive_data["projection"]
    factors = predictive_data["factors"]

    data_relatorio = (
        _formatar_data(analysis_date)
        if analysis_date
        else datetime.now().strftime("%d/%m/%Y")
    )

    # 1. CAPA
    ata_relatorio = (
        _formatar_data(analysis_date)
        if analysis_date
        else datetime.now().strftime("%d/%m/%Y")
    )

    data_referencia = _formatar_data(current["reference_date"])

    conteudo.extend(
        _criar_capa(
            estilos=estilos,
            repo_name=repo_name or "Repositório não informado",
            branch=branch or "Não informada",
            data_relatorio=data_relatorio,
            data_referencia=data_referencia,
            score=current["score"],
            largura_util=largura_util,
        )
    )

    conteudo.append(PageBreak())

    # 2. RESUMO EXECUTIVO

    conteudo.append(
        Paragraph("1. Resumo executivo", estilos["secao"])
    )

    variation = current.get("variation")

    if variation is None:
        variacao_texto = "Sem comparação disponível"
    elif variation > 0:
        variacao_texto = f"Aumento de {_formatar_numero(variation)} pontos"
    elif variation < 0:
        variacao_texto = f"Redução de {_formatar_numero(abs(variation))} pontos"
    else:
        variacao_texto = "Sem variação"

    resumo = [
        ["Indicador", "Resultado"],
        ["Pontuação de risco atual", _formatar_numero(current["score"])],
        ["Variação em relação ao registro anterior", variacao_texto],
        ["Commits registrados", str(current["commits"])],
        ["Semanas com registros de risco", str(len(history))],
    ]

    conteudo.append(
        _tabela(
            resumo,
            [9 * cm, largura_util - 9 * cm],
        )
    )

    conteudo.append(Spacer(1, 10))

    conteudo.append(
        Paragraph(
            f"A última pontuação registrada foi "
            f"<b>{_formatar_numero(current['score'])}</b>, com "
            f"{_texto(current['trend']).lower()}. "
            f"Foram considerados {current['commits']} commits "
            f"registrados nas semanas analisadas.",
            estilos["corpo"],
        )
    )

    # --------------------------------------------------
    # 3. HISTÓRICO DE RISCO
    # --------------------------------------------------

    conteudo.append(
        Paragraph("2. Histórico de risco", estilos["secao"])
    )

    conteudo.append(
        Paragraph(
            "A tabela apresenta os registros mais recentes disponíveis "
            "no histórico de risco do repositório.",
            estilos["corpo"],
        )
    )

    historico_recente = history.tail(12).iloc[::-1]

    dados_historico = [[
        "Semana",
        "Risco",
        "Commits",
        "Arquivos",
        "Arquivos sensíveis",
    ]]

    for _, linha in historico_recente.iterrows():
        dados_historico.append([
            _formatar_data(linha["week"]),
            _formatar_numero(linha["risk_score"]),
            str(int(linha["commits"])),
            str(int(linha["files_changed"])),
            str(int(linha["security_files_changed"])),
        ])

    conteudo.append(
        _tabela(
            dados_historico,
            [
                3.2 * cm,
                2.2 * cm,
                2.2 * cm,
                2.6 * cm,
                largura_util - 10.2 * cm,
            ],
        )
    )

    conteudo.append(Spacer(1, 6))

    conteudo.append(
        Paragraph(
            "São exibidos até 12 registros, começando pelo mais recente. "
            "A pontuação representa o resultado do cálculo de risco "
            "implementado no GitForesight.",
            estilos["pequeno"],
        )
    )

    # --------------------------------------------------
    # 4. HEATMAP
    # --------------------------------------------------

    conteudo.append(
        Paragraph("3. Arquivos com maior pontuação de risco", estilos["secao"])
    )

    conteudo.append(
        Paragraph(
            "O heatmap classifica os arquivos com base no volume de "
            "alterações, frequência de commits, quantidade de "
            "contribuidores e identificação de arquivos sensíveis.",
            estilos["corpo"],
        )
    )

    if heatmap_items:
        dados_heatmap = [[
            "Arquivo",
            "Pontuação",
            "Commits",
            "Linhas",
            "Sensível",
        ]]

        for item in heatmap_items[:15]:
            dados_heatmap.append([
                Paragraph(_texto(item["path"]), estilos["celula"]),
                _formatar_numero(item["score"]),
                str(item["commits"]),
                str(item["linhas"]),
                "Sim" if item["sensivel"] else "Não",
            ])

        conteudo.append(
            _tabela(
                dados_heatmap,
                [
                    7.2 * cm,
                    2.2 * cm,
                    2 * cm,
                    2 * cm,
                    largura_util - 13.4 * cm,
                ],
            )
        )
    else:
        conteudo.append(
            Paragraph(
                "Não foram encontrados dados de arquivos para o heatmap.",
                estilos["corpo"],
            )
        )

    conteudo.append(Spacer(1, 6))

    conteudo.append(
        Paragraph(
            "A pontuação do heatmap é um indicador comparativo entre "
            "os arquivos analisados. Uma pontuação elevada não significa, "
            "isoladamente, que o arquivo contenha uma vulnerabilidade.",
            estilos["pequeno"],
        )
    )

    # --------------------------------------------------
    # 5. ANÁLISE PREDITIVA
    # --------------------------------------------------

    conteudo.append(
        Paragraph("4. Análise preditiva", estilos["secao"])
    )

    conteudo.append(
        Paragraph(
            "A simulação considera um horizonte de até 50 commits futuros "
            "e compara dois cenários: continuidade dos indicadores atuais "
            "e redução simulada dos indicadores após ações corretivas.",
            estilos["corpo"],
        )
    )

    if not projection.empty:
        primeiro = projection.iloc[0]
        ultimo = projection.iloc[-1]

        dados_projecao = [
            ["Cenário", "Situação atual", "Após 50 commits"],
            [
                "Continuidade",
                _formatar_numero(primeiro["continuidade"]),
                _formatar_numero(ultimo["continuidade"]),
            ],
            [
                "Com ações simuladas",
                _formatar_numero(primeiro["com_acoes"]),
                _formatar_numero(ultimo["com_acoes"]),
            ],
            [
                "Limite superior da sensibilidade",
                _formatar_numero(primeiro["faixa_max"]),
                _formatar_numero(ultimo["faixa_max"]),
            ],
        ]

        conteudo.append(
            _tabela(
                dados_projecao,
                [
                    6.5 * cm,
                    4.2 * cm,
                    largura_util - 10.7 * cm,
                ],
            )
        )

    conteudo.append(Spacer(1, 8))

    conteudo.append(
        Paragraph(
            "<b>Importante:</b> os cenários são simulações heurísticas. "
            "O cenário com ações considera uma redução de 20% nos "
            "indicadores utilizados pelo cálculo. A faixa de sensibilidade "
            "considera uma variação de até 20%. Esses valores não "
            "representam uma previsão estatística do comportamento futuro "
            "do repositório.",
            estilos["pequeno"],
        )
    )

    # --------------------------------------------------
    # 6. FATORES DE RISCO
    # --------------------------------------------------

    conteudo.append(
        Paragraph("5. Fatores de risco", estilos["secao"])
    )

    conteudo.append(
        Paragraph(
            "Os fatores abaixo representam os indicadores considerados "
            "pelo cálculo de risco e suas respectivas contribuições "
            "heurísticas.",
            estilos["corpo"],
        )
    )

    dados_fatores = [[
        "Fator",
        "Valor observado",
        "Contribuição",
        "Descrição",
    ]]

    for fator in factors:
        dados_fatores.append([
            Paragraph(_texto(fator["name"]), estilos["celula"]),
            _formatar_numero(fator["value"]),
            f"{_formatar_numero(fator['contribution'])}%",
            Paragraph(_texto(fator["description"]), estilos["celula"]),
        ])

    conteudo.append(
        _tabela(
            dados_fatores,
            [
                3.5 * cm,
                2.5 * cm,
                2.5 * cm,
                largura_util - 8.5 * cm,
            ],
        )
    )

    # --------------------------------------------------
    # 7. METODOLOGIA
    # --------------------------------------------------

    conteudo.append(
        Paragraph("6. Metodologia e limitações", estilos["secao"])
    )

    metodologia = [
        "O histórico de risco é construído a partir dos indicadores "
        "extraídos dos commits do repositório.",

        "O heatmap utiliza volume de linhas alteradas, frequência de "
        "commits e quantidade de contribuidores. Arquivos identificados "
        "como sensíveis recebem um acréscimo na pontuação.",

        "A análise preditiva simula cenários com base nos indicadores "
        "mais recentes. O cenário com ações aplica uma redução de 20% "
        "nos indicadores considerados pelo cálculo.",

        "As pontuações são indicadores heurísticos para apoiar a análise "
        "e priorização. Não substituem auditorias de segurança, análise "
        "estática de código ou testes de vulnerabilidade.",

        "Os resultados dependem da quantidade, qualidade e período dos "
        "dados disponíveis no histórico do repositório.",
    ]

    for item in metodologia:
        conteudo.append(
            Paragraph(f"• {_texto(item)}", estilos["corpo"])
        )

    # --------------------------------------------------
    # GERAÇÃO DO DOCUMENTO
    # --------------------------------------------------

    doc.build(
        conteudo,
        onFirstPage=lambda canvas, doc: None,
        onLaterPages=_cabecalho_rodape,
    )

    buffer.seek(0)
    return buffer.getvalue()
