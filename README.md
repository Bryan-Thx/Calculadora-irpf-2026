# Calculadora IRPF 2026 Auto-Update 🇧🇷

> CLI em Python que busca a tabela do Imposto de Renda direto da Receita Federal e calcula seu imposto automaticamente.

**Desenvolvida 100% em Galaxy A16 rodando Ubuntu + XFCE4 via Termux.**

### Por que esse projeto?

Todo ano 30 milhões de brasileiros precisam calcular IRPF. Essa CLI resolve a dor usando web scraping ético, cache offline e interface moderna no terminal. Prova que dá pra fazer dev backend sério direto do celular.

### Features

- **Auto-update**: Busca tabela IRPF 2026 direto do site da RFB
- **Funciona offline**: Salva cache local após primeira execução
- **Formato brasileiro**: Aceita entrada como `5.000,50` ou `5000.50`
- **Interface Rich**: Tabela colorida e formatada no terminal
- **Cálculo completo**: INSS, dependentes, outras deduções, base e alíquota
- **Zero dependências pesadas**: Roda em qualquer Termux/Android

### Como rodar

```bash
# 1. Instala dependências
pkg update && pkg install python -y
pip install requests beautifulsoup4 rich

# 2. Clona o repo
git clone https://github.com/SEUUSER/calculadora-irpf-2026
cd calculadora-irpf-2026

# 3. Executa
python main.py
