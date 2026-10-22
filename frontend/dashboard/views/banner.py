"""Banner / apresentação do produto GitForesight (Streamlit + HTML/CSS)."""
from pathlib import Path
from components.sidebar import _logo_base64
import streamlit as st

REPO_URL = "https://github.com/Mariacmv/GitForesight/blob/main/README.md"
# frontend/dashboard/views/banner.py -> frontend/dashboard/styles/main.css
CSS_PATH = Path(__file__).resolve().parents[1] / "styles" / "banner.css"
FONTS = (
    "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700"
    "&family=JetBrains+Mono:wght@400;500&display=swap');"
)


def _h(html: str) -> str:
    """Remove indentação e linhas em branco: o markdown do Streamlit trataria
    4 espaços como bloco de código e linha vazia como fim do bloco HTML."""
    return "\n".join(l.strip() for l in html.splitlines() if l.strip())


def _num(n: int) -> str:
    return f'<span class="gf-n" style="--to:{n}"></span>'


def _head(eyebrow: str, title: str, sub: str = "") -> str:
    sub_html = f'<p class="gf-sub">{sub}</p>' if sub else ""
    return f'<div class="gf-rv"><span class="gf-mono gf-eyebrow">{eyebrow}</span><h2>{title}</h2>{sub_html}</div>'


def _cards(items) -> str:
    return "".join(
        f'<div class="gf-card"><span class="gf-mono">{i}</span><h3 style="margin-top:14px!important">{t}</h3><p>{d}</p></div>'
        for i, t, d in items
    )

def _nav(publico: bool = False) -> str: 
    entrar = '<a class="gf-btn pri" href="?entrar=1" target="_self">Entrar</a>' if publico else ""
    return f"""
    <header class="gf-nav"><div class="gf-wrap">
      <img class="auth-brand-logo-img" src="data:image/png;base64,{_logo_base64()}">
      <div class="auth-brand-text">
        <div class="auth-brand-name">Git Foresight</div>
      </div>
      <nav>
        <a href="#produto">O produto</a><a href="#como-funciona">Como funciona</a>
        <a href="#uso">Uso e limites</a><a href="#faq">Perguntas frequentes</a>
        <a class="gf-btn sec" href="{REPO_URL}" target="_blank">Ler o README ↗</a>
        {entrar}
      </nav>
    </div></header>"""


def _hero(publico: bool = False) -> str:
    entrar = '<a class="gf-btn pri gf-in" style="--d:4;margin-left:10px" href="?entrar=1" target="_self">Entrar no app</a>' if publico else ""
    rows = ["0120100312040030", "1000302000410200", "0301002040001320"]
    cells = "".join(
        f'<span class="c{v}" style="--i:{r * 16 + i}"></span>'
        for r, row in enumerate(rows)
        for i, v in enumerate(row)
    )
    return f"""
    <section class="gf-hero" id="topo"><div class="gf-wrap">
      <div>
        <span class="gf-tag gf-mono gf-in" style="--d:0">PROJETO ACADÊMICO · EM DESENVOLVIMENTO</span>
        <h1 class="gf-in" style="--d:1;margin-top:22px">Seu histórico Git.<br>Uma nova visão<em>dos riscos.</em></h1>
        <p class="lead gf-in" style="--d:2">Transformando o histórico do seu projeto em uma visão dos riscos que podem surgir amanhã.</p>
        <p class="gf-in" style="--d:3;margin-top:14px">O GitForesight analisa padrões de repositórios Git para explorar cenários hipotéticos e estimar impactos técnicos e organizacionais.</p>
        <a class="gf-btn pri gf-in" style="--d:4" href="{REPO_URL}" target="_blank">Conheça o projeto no GitHub ↗</a>
        <p class="gf-mono gf-in" style="--d:5;margin-top:26px">Análise histórica. Simulação. Apoio à decisão.</p>
      </div>
      <div class="gf-panel gf-scan gf-in" style="--d:3">
        <div style="display:flex;justify-content:space-between"><span class="gf-mono">⑂ histórico + cenários</span><span class="gf-tag gf-mono">VISÃO CONCEITUAL</span></div>
        <div class="gf-inner">
          <span class="gf-mono">01 / SINAIS DO REPOSITÓRIO</span>
          <div class="gf-heat">{cells}</div>
          <div class="gf-legend gf-mono"><span>commits</span><span>churn</span><span>contribuições</span></div>
        </div>
        <div class="gf-q"><span class="gf-mono" style="color:var(--gf-accent2)">02 / E SE ESSE PADRÃO CONTINUAR?</span>
          <h3>O que muda se uma pessoa-chave sair do projeto?</h3></div>
        <div class="gf-fork"></div>
        <div class="gf-chips"><span>Conhecimento</span><span>Manutenção</span><span>Prioridades</span></div>
        <p class="gf-mono" style="margin-top:16px">Ilustração da proposta. Hipóteses orientam a análise — não garantem eventos futuros.</p>
      </div>
    </div></section>
    <div class="gf-strip"><div class="gf-wrap">
      <span class="gf-mono">UM OLHAR ALÉM DAS MÉTRICAS PASSADAS</span>
      <span class="gf-mono"><b>• Padrões históricos</b><b>• Riscos potenciais</b><b>• Cenários hipotéticos</b></span>
    </div></div>"""


def _produto() -> str:
    cards = _cards([
        ("◎", "Enxergue dependências humanas", "Entenda onde o conhecimento pode estar concentrado e discuta a continuidade da manutenção com a equipe."),
        ("◈", "Dê contexto ao retrabalho", "Investigue áreas com alterações recorrentes e alto churn antes de decidir onde dedicar atenção."),
        ("≡", "Priorize com mais contexto", "Use sinais históricos e hipóteses de impacto para apoiar decisões de manutenção, documentação e refatoração."),
    ])
    return f"""
    <section class="gf-sec" id="produto"><div class="gf-wrap">
      {_head("01 / O PRODUTO", "Não apenas o que aconteceu. O que pode acontecer.",
             "Uma ferramenta de análise de repositórios Git em desenvolvimento que busca conectar métricas, riscos e simulações. A proposta é transformar registros do passado em perguntas úteis para o próximo passo.")}
      <div class="gf-q2 gf-rv"><span class="gf-mono">“O que aconteceu?”</span><span>→</span>
        <span class="gf-mono hl">“O que pode acontecer se esse padrão continuar?”</span></div>
      <div class="gf-grid gf-g3 gf-rv">{cards}</div>
    </div></section>"""


def _pipeline() -> str:
    steps = [("Repositório Git", "O histórico como ponto de partida."), ("Coleta de dados", "Registros para a análise."),
             ("Métricas", "Sinais sobre a evolução."), ("Análise de risco", "Pontos que merecem atenção."),
             ("Simulação", "Hipóteses e seus impactos."), ("Relatório", "Achados para a decisão.")]
    cards = "".join(
        f'<div class="gf-card gf-step"><span class="gf-mono">0{i} +</span><h3>{t}</h3><p>{d}</p></div>'
        for i, (t, d) in enumerate(steps, 1)
    )
    return f"""
    <section class="gf-sec" id="como-funciona"><div class="gf-wrap">
      {_head("02 / COMO FUNCIONA", "Do repositório à discussão de riscos.",
             "O pipeline documentado organiza o histórico em sinais e conecta a análise de risco à simulação de cenários.")}
      <div class="gf-grid gf-g6 gf-rv">{cards}</div>
    </div></section>"""


def _metricas() -> str:
    data = [
        ("COMMITS / ARQUIVOS", "Evolução do código", "Frequência de commits, arquivos mais alterados, churn de código e histórico de alterações.", "Onde as mudanças se repetem?",
         [30, 40, 25, 70, 45, 85, 50, 60, 35, 90, 55, 75]),
        ("PESSOAS / CONTRIBUIÇÕES", "Conhecimento da equipe", "Distribuição de contribuições, participação de desenvolvedores e concentração de conhecimento.", "Quem sustenta cada parte do projeto?",
         [60, 50, 80, 45, 70, 90, 55, 65, 40, 75, 50, 60]),
        ("PROCESSO / DEPENDÊNCIAS", "Fluxo e componentes", "Pull requests, tempos de desenvolvimento e revisão e dependências entre componentes.", "Como o trabalho e os módulos se conectam?",
         [20, 30, 25, 40, 30, 55, 35, 90, 45, 60, 50, 85]),
    ]
    cards = ""
    for tag, title, desc, q, bars in data:
        b = "".join(f'<i class="{"on" if h > 70 else ""}" style="--h:{h};--i:{i}"></i>' for i, h in enumerate(bars))
        cards += f'<div class="gf-card"><span class="gf-mono">{tag}</span><h3 style="margin-top:12px!important">{title}</h3><div class="gf-bars">{b}</div><p>{desc}</p><p style="color:var(--gf-text)">{q}</p></div>'
    return f"""
    <section class="gf-sec"><div class="gf-wrap">
      {_head("03 / O QUE PODE SER ANALISADO", "Código, pessoas e fluxo de trabalho.",
             "O README descreve métricas que a análise pode utilizar. Elas representam possibilidades da proposta, não uma lista de funcionalidades já implementadas.")}
      <div class="gf-grid gf-g3 gf-rv">{cards}</div>
    </div></section>"""


def _cenarios() -> str:
    items = [("Saída de desenvolvedor", "Quais áreas ficariam com menos conhecimento disponível?"),
             ("Mais alterações", "Como um aumento no volume de mudanças pode afetar o projeto?"),
             ("Conhecimento concentrado", "Quais módulos dependem de poucas pessoas?"),
             ("Refatoração de módulo", "Que impactos uma intervenção pode trazer ao restante do código?"),
             ("Componentes críticos", "Quais partes podem ser afetadas por uma alteração importante?")]
    rows = "".join(f'<a href="#"><div><h3>{t}</h3><p>{d}</p></div><span class="gf-mono">↗</span></a>' for t, d in items)
    return f"""
    <section class="gf-sec"><div class="gf-wrap gf-split">
      <div class="gf-rv"><span class="gf-mono gf-eyebrow">04 / CENÁRIOS HIPOTÉTICOS</span>
        <h2>Faça perguntas antes de tomar decisões.</h2>
        <p style="margin:16px 0">A arquitetura permite explorar hipóteses técnicas e organizacionais. Cada cenário é uma lente de análise, não uma previsão garantida.</p>
        <span class="gf-tag gf-mono">E SE…</span></div>
      <div class="gf-list gf-rv">{rows}</div>
    </div></section>"""


def _exemplo() -> str:
    return f"""
    <section class="gf-sec"><div class="gf-wrap">
      <div style="display:flex;justify-content:space-between;align-items:flex-end;gap:20px">
        {_head("05 / UMA LEITURA NA PRÁTICA", "Do risco geral ao impacto de uma hipótese.",
               "Os números abaixo reproduzem um exemplo ilustrativo do README. Não são resultados reais de um repositório do visitante.")}
        <span class="gf-tag gf-mono">EXEMPLO ILUSTRATIVO</span></div>
      <div class="gf-ex gf-rv">
        <div class="gf-panel"><h3>▣ Panorama do repositório</h3>
          <div class="gf-nums"><div><b>{_num(12)}</b><span class="l">contribuidores</span></div>
            <div><b>{_num(487)}</b><span class="l">arquivos</span></div><div><b>2.341</b><span class="l">commits</span></div></div>
          <span class="gf-mono">SINAIS QUE MERECEM ATENÇÃO</span>
          <div class="gf-tm">
            <div class="h"><b>{_num(14)}</b>hotspots</div>
            <div class="m"><b>{_num(6)}</b>áreas de alto churn</div>
            <div class="k"><b>{_num(3)}</b>módulos com conhecimento concentrado</div></div>
          <div class="gf-med"><span style="font-size:.85rem">Risco geral do exemplo</span><em>MÉDIO</em></div></div>
        <div class="gf-panel hyp"><h3>⑂ Hipótese: saída de desenvolvedor</h3>
          <div class="gf-inner" style="font-family:'JetBrains Mono',monospace;font-size:.85rem">◉ desenvolvedor #03</div>
          <div class="gf-nums"><div><b>{_num(31)}</b><span class="l">arquivos afetados</span></div>
            <div><b>{_num(5)}</b><span class="l">módulos afetados</span></div>
            <div><b>{_num(9)}</b><span class="l">arquivos sem segundo mantenedor</span></div></div>
          <div class="gf-risk"><div><span class="gf-mono">Risco estimado no cenário</span><strong>CRÍTICO</strong></div><span style="color:var(--gf-red)">⚠</span></div>
          <p class="gf-mono" style="margin-top:18px">Principal área afetada</p>
          <p style="color:var(--gf-text);font-family:'JetBrains Mono',monospace">Authentication</p></div>
      </div>
      <p class="gf-note gf-rv">Uma possível discussão a partir desse exemplo: investigar a concentração de conhecimento, avaliar documentação e considerar o compartilhamento da manutenção. O relatório apoia a conversa; a decisão exige contexto.</p>
    </div></section>"""


def _fluxo() -> str:
    steps = [("Selecionar o repositório e o histórico", "Definir o projeto e o recorte de histórico que serão considerados."),
             ("Examinar métricas e hotspots", "Ler os sinais de mudança, retrabalho e concentração de conhecimento."),
             ("Escolher uma hipótese", "Formular uma pergunta técnica ou organizacional para explorar."),
             ("Comparar os impactos", "Observar como as estimativas mudam entre o contexto e o cenário."),
             ("Transformar achados em prioridades", "Discutir com a equipe o que investigar, documentar ou manter.")]
    rows = "".join(
        f'<div class="gf-card"><span class="n">0{i}</span><div><h3>{t}</h3><p>{d}</p></div></div>'
        for i, (t, d) in enumerate(steps, 1)
    )
    return f"""
    <section class="gf-sec" id="uso"><div class="gf-wrap gf-split">
      <div class="gf-rv"><span class="gf-mono gf-eyebrow">06 / ORIENTAÇÕES DE USO</span>
        <h2>Um fluxo para pensar com o GitForesight.</h2>
        <p style="margin:16px 0">Este é um fluxo conceitual de análise. O README não apresenta comandos de instalação, requisitos de ambiente, autenticação ou um passo a passo operacional.</p>
        <a class="gf-btn sec" href="{REPO_URL}" target="_blank">Consultar o README ↗</a></div>
      <div class="gf-steps gf-rv">{rows}</div>
    </div></section>"""


def _limites() -> str:
    cols = [("O histórico é um recorte", "Os dados disponíveis e o período analisado condicionam a leitura dos padrões."),
            ("Contexto continua essencial", "Mudanças de equipe e de processo precisam ser interpretadas por quem conhece o projeto."),
            ("Proposta em desenvolvimento", "O README não comprova previsão nem garante redução de riscos ou resultados.")]
    c = "".join(f'<div><h3>{t}</h3><p>{d}</p></div>' for t, d in cols)
    return f"""
    <section class="gf-sec" id="faq"><div class="gf-wrap"><div class="gf-warn gf-rv">
      <span class="gf-mono gf-eyebrow">07 / LIMITAÇÕES</span><h2>Simular não é prever o futuro.</h2>
      <p style="margin-top:14px;color:var(--gf-text)">As simulações não são previsões determinísticas. São estimativas baseadas em padrões históricos e servem como apoio à decisão, não como garantia de eventos futuros.</p>
      <div class="gf-grid gf-g3">{c}</div></div></div></section>"""


def _roadmap() -> str:
    cols = [("[ 01 ]", "Base de análise", "Coleta de dados; análise de commits, contribuição, churn, hotspots e concentração de conhecimento por padrões."),
            ("[ 02 ]", "Riscos e cenários", "Classificação de risco; simulação de saída de desenvolvedores; cenários técnicos e comparação entre cenários."),
            ("[ 03 ]", "Visualização e integração", "Dashboard, exportação de relatórios e integração CI/CD.")]
    return f"""
    <section class="gf-sec"><div class="gf-wrap">
      <div style="display:flex;justify-content:space-between;align-items:flex-end;gap:20px;flex-wrap:wrap">
        {_head("08 / UM PROJETO EM EVOLUÇÃO", "Pesquisa aplicada à engenharia de software.",
               "Projeto acadêmico em desenvolvimento, reunindo desenvolvimento de sistemas, análise de dados, gerenciamento de projetos, Git/GitHub, DevOps e análise de riscos.")}
        <span><span class="gf-tag gf-mono">Python</span> <span class="gf-tag gf-mono">Git/GitHub</span> <span class="gf-tag gf-mono">API do GitHub</span></span></div>
      <div class="gf-panel gf-rv" style="margin-top:36px;padding:26px"><div style="display:flex;justify-content:space-between">
        <h3>Direções do roadmap</h3><span class="gf-mono">Sem datas ou confirmação de conclusão no README.</span></div>
        <div class="gf-grid gf-g3">{_cards(cols)}</div></div>
    </div></section>"""


def _cta() -> str:
    return f"""
    <section class="gf-sec"><div class="gf-wrap"><div class="gf-cta gf-rv">
      <div><span class="gf-mono gf-eyebrow">10 / CONTINUE NO REPOSITÓRIO</span><h2>Conheça a ideia. Acompanhe a evolução.</h2>
        <p style="margin-top:12px">Explore o README para entender a proposta, a arquitetura e o roadmap do GitForesight diretamente na fonte.</p></div>
      <div style="display:grid;gap:10px"><a class="gf-btn pri" href="{REPO_URL}" target="_blank">Conheça o projeto no GitHub ↗</a>
        <a class="gf-btn sec" href="{REPO_URL}" target="_blank" style="text-align:center">Ler o README ↗</a></div>
    </div></div></section>
    <footer class="gf-foot"><div class="gf-wrap">
      <div><a class="gf-logo" href="#topo"><i></i>Git Foresight</a><p class="gf-mono" style="margin-top:8px">Projeto acadêmico em desenvolvimento · Licença a definir</p></div>
      <div style="text-align:right"><a class="gf-mono" href="{REPO_URL}" target="_blank">github.com/Mariacev/GitForesight ↗</a>
        <p class="gf-mono">Apresentação baseada no README do projeto.</p></div>
    </div></footer>"""

def render(analysis, risk, publico: bool = False):
    css = CSS_PATH.read_text(encoding="utf-8") if CSS_PATH.exists() else ""
    st.markdown(f"<style>{FONTS}\n{css}</style>", unsafe_allow_html=True)

    page = "".join([_nav(publico), _hero(publico), _produto(), _pipeline(), _metricas(),
                    _cenarios(), _exemplo(), _fluxo(), _limites(), _roadmap(), _cta()])
    st.markdown(_h(f'<div class="gf-page">{page}</div>'), unsafe_allow_html=True)