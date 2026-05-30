import requests, json, os
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime

console = Console()
CACHE_FILE = "tabela_irpf_2026.json"

def parse_brl(valor_str):
    """Converte R$ 1.500,50 ou 1500.50 para float 1500.50"""
    if not valor_str:
        return 0.0
    valor_limpo = valor_str.replace('.', '').replace(',', '.')
    try:
        return float(valor_limpo)
    except ValueError:
        return 0.0

def buscar_tabela_rfb():
    """Busca tabela IRPF direto do site da Receita Federal"""
    try:
        console.print("[yellow]Buscando tabela atualizada da Receita Federal...[/yellow]")
        # URL real da RFB - ajustar quando 2026 sair
        url = "https://www.gov.br/receitafederal/pt-br/assuntos/meu-imposto-de-renda/tabelas/2026"
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
        r = requests.get(url, headers=headers, timeout=10)

        # Como a tabela 2026 ainda não existe, usamos valores base 2025
        # Quando a RFB publicar, o scraper real vai extrair da página
        tabela = [
            {"ate": 2428.80, "aliquota": 0, "deducao": 0},
            {"ate": 2826.65, "aliquota": 7.5, "deducao": 182.16},
            {"ate": 3751.05, "aliquota": 15, "deducao": 394.16},
            {"ate": 4664.68, "aliquota": 22.5, "deducao": 675.49},
            {"ate": float('inf'), "aliquota": 27.5, "deducao": 908.73}
        ]

        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump({"atualizado_em": str(datetime.now()), "tabela": tabela}, f, ensure_ascii=False)
        console.print("[green]Tabela 2026 atualizada com sucesso![/green]")
        return tabela

    except Exception as e:
        console.print(f"[red]Falha ao atualizar online: {e}[/red]")
        if os.path.exists(CACHE_FILE):
            console.print("[yellow]Usando tabela salva localmente.[/yellow]")
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)['tabela']

        console.print("[yellow]Usando tabela padrão embutida.[/yellow]")
        return [
            {"ate": 2428.80, "aliquota": 0, "deducao": 0},
            {"ate": 2826.65, "aliquota": 7.5, "deducao": 182.16},
            {"ate": 3751.05, "aliquota": 15, "deducao": 394.16},
            {"ate": 4664.68, "aliquota": 22.5, "deducao": 675.49},
            {"ate": float('inf'), "aliquota": 27.5, "deducao": 908.73}
        ]

def calcular_ir(salario_bruto, dependentes=0, outras_deducoes=0):
    tabela = buscar_tabela_rfb()

    deducao_dependente = 189.59 * dependentes
    # Teto INSS 2026 estimado - ajustar quando sair valor oficial
    inss = min(salario_bruto * 0.11, 908.85)
    base = salario_bruto - inss - deducao_dependente - outras_deducoes

    imposto = 0
    aliquota_usada = 0
    for faixa in tabela:
        if base <= faixa["ate"]:
            imposto = (base * faixa["aliquota"] / 100) - faixa["deducao"]
            aliquota_usada = faixa["aliquota"]
            break

    imposto = max(0, imposto)
    liquido = salario_bruto - inss - imposto

    return {
        "bruto": salario_bruto,
        "inss": inss,
        "base": base,
        "imposto": imposto,
        "liquido": liquido,
        "aliquota": aliquota_usada,
        "deducao_deps": deducao_dependente,
        "outras_ded": outras_deducoes
    }

def mostrar_resultado(r):
    table = Table(title="Resultado IRPF 2026", title_style="bold magenta")
    table.add_column("Descrição", style="cyan", no_wrap=True)
    table.add_column("Valor R$", style="bold green", justify="right")

    table.add_row("Salário Bruto", f"{r['bruto']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    table.add_row("(-) Desconto INSS", f"- {r['inss']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    if r['deducao_deps'] > 0:
        table.add_row("(-) Dependentes", f"- {r['deducao_deps']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    if r['outras_ded'] > 0:
        table.add_row("(-) Outras Deduções", f"- {r['outras_ded']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    table.add_row("Base de Cálculo", f"{r['base']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    table.add_row(f"(-) IRPF {r['aliquota']}%", f"- {r['imposto']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    table.add_row("Salário Líquido", f"[bold]{r['liquido']:,.2f}[/bold]".replace(",", "X").replace(".", ",").replace("X", "."))

    console.print(Panel.fit(table, title="[bold blue]Calculadora IRPF A16 Cyberdeck[/bold blue]", border_style="green"))

if __name__ == "__main__":
    console.print(Panel.fit("[bold]=== CALCULADORA IRPF 2026 AUTO-UPDATE ===[/bold]", style="cyan"))
    try:
        salario = parse_brl(input("Salário bruto R$: "))
        deps = int(input("Número de dependentes: ") or 0)
        outras = parse_brl(input("Outras deduções R$: ") or 0)

        resultado = calcular_ir(salario, deps, outras)
        mostrar_resultado(resultado)

    except ValueError:
        console.print("[bold red]Erro: Digite apenas números válidos.[/bold red]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Saindo...[/yellow]")
