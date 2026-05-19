
# 📊  - Teoria das Filas em Python

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter-orange.svg)](https://docs.python.org/3/library/tkinter.html)

Sistema completo para análise e simulação de modelos de filas clássicos da Teoria das Filas. Implementa modelos M/M/s, M/G/1, filas com prioridade, capacidade finita e população finita, com interface gráfica moderna e suporte a OCR para resolução de exercícios a partir de imagens/PDFs.

## ✨ Funcionalidades

### 📈 Modelos Implementados
- **M/M/1 e M/M/s** - Fila com capacidade infinita
- **M/G/1** - Distribuição geral de serviço (Pollaczek-Khinchine)
- **Prioridades** - Com e sem interrupção (preemptivo/não-preemptivo)
- **Capacidade Finita (K)** - M/M/1/K e M/M/s/K
- **População Finita (N)** - M/M/1/N e M/M/s/N

### 🎯 Métricas Calculadas
- `ρ` (Taxa de utilização do sistema)
- `L` (Número médio de clientes no sistema)
- `Lq` (Número médio de clientes na fila)
- `W` (Tempo médio de permanência no sistema)
- `Wq` (Tempo médio de espera na fila)
- `P0`, `Pn` (Probabilidades de estados)
- `P(W > t)`, `P(Wq > t)` (Probabilidades de tempo de espera)

### 🖥️ Interfaces Disponíveis

| Interface | Descrição | Como acessar |
|-----------|-----------|--------------|
| **GUI Moderna** | Interface gráfica com Tkinter, abas organizadas, OCR integrado | `python app.py` |
| **CLI Interativa** | Linha de comando para testes rápidos | `python interface.py` |
| **Script de Exercícios** | Executa lista de exercícios pré-definidos | `python ListaExercicios.py` |
| **Biblioteca Python** | Importe as classes em seus próprios projetos | `from forms import *` |

### 🤖 OCR Solver (Novidade!)
- Reconhecimento de texto em imagens e PDFs
- Extração automática de parâmetros (λ, μ, s)
- Resolução automática de exercícios
- Suporte aos idiomas português e inglês

## 🚀 Instalação Rápida

### Requisitos
- Python 3.8 ou superior
- Pip (gerenciador de pacotes)

### Passo a Passo

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/QueueSim-Pro.git
cd QueueSim-Pro

# 2. (Opcional) Crie um ambiente virtual
python -m venv .venv

# 3. Ative o ambiente virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 4. Instale as dependências
pip install -r requirements.txt

# 5. Execute a aplicação
python app.py
Dependências Específicas
bash
# Para OCR (reconhecimento de imagem/PDF)
pip install Pillow pytesseract PyMuPDF

# Instalar Tesseract OCR no sistema:
# Windows: https://github.com/UB-Mannheim/tesseract/wiki
# Linux: sudo apt-get install tesseract-ocr tesseract-ocr-por
# Mac: brew install tesseract tesseract-lang
📖 Como Usar
Interface Gráfica (Recomendado)
bash
python app.py
A interface possui as seguintes abas:

📈 M/M/s - Sistema com capacidade infinita

📐 M/G/1 - Distribuição geral de serviço

⚡ Prioridades - Com/sem interrupção

🔒 Filas Finitas - Capacidade K ou População N

🔍 OCR Solver - Resolução por imagem/PDF

📝 Lista - Execução de exercícios

Linha de Comando
python
from forms import Mm, Mg1, Mm1k

# Exemplo M/M/1
modelo = Mm(lam=2.0, mi=3.0, s=1)
modelo.resultado()

# Exemplo M/G/1
modelo = Mg1(lam=8.0, mi=10.0, var=0.005)
modelo.mg1_print()

# Exemplo M/M/1/K (capacidade finita)
modelo = Mm1k(lam=1.0, mi=2.0, k=10)
modelo.resultado()
OCR Solver - Resolvendo Exercícios
Tire uma foto do exercício ou escaneie para PDF

Na aba "🔍 OCR Solver", clique em "Carregar Imagem/PDF"

Aguarde o processamento e extração do texto

O sistema identificará automaticamente λ, μ e outros parâmetros

Resultados serão exibidos automaticamente

📁 Estrutura do Projeto
text
QueueSim-Pro/
│
├── app.py                      # Interface gráfica principal (Tkinter)
├── interface.py                # Interface CLI interativa
├── ListaExercicios.py          # Script com exercícios resolvidos
├── requirements.txt            # Dependências do projeto
├── README.md                   # Documentação
│
├── forms/                      # Módulos dos modelos de fila
│   ├── __init__.py
│   ├── mg1.py                  # Modelo M/G/1
│   ├── mm.py                   # Modelo M/M/s
│   ├── mm1k.py                 # M/M/1/K (capacidade finita)
│   ├── mmsk.py                 # M/M/s/K (capacidade finita)
│   ├── mm1n.py                 # M/M/1/N (população finita)
│   ├── mmsn.py                 # M/M/s/N (população finita)
│   ├── prioridadesInterrupcao.py      # Prioridade com interrupção
│   └── prioridadesSemInterrup.py      # Prioridade sem interrupção
│
└── .venv/                      # Ambiente virtual (opcional)
💡 Exemplos Práticos
Exemplo 1: M/M/1 - Loja com um atendente
python
from forms import Mm

# λ = 30 clientes/hora, μ = 40 clientes/hora
modelo = Mm(lam=30, mi=40, s=1)
modelo.resultado()

# Resultados:
# ρ = 0.75 (75% de ocupação)
# L = 3.0 clientes no sistema
# W = 0.1 horas = 6 minutos no sistema
Exemplo 2: M/M/s - Call center com 3 atendentes
python
from forms import Mm

# λ = 60 chamadas/hora, μ = 25 chamadas/hora, s = 3
modelo = Mm(lam=60, mi=25, s=3)
modelo.resultado()
Exemplo 3: M/G/1 - Distribuição geral
python
from forms import Mg1

# λ = 8, μ = 10, variância = 0.005
modelo = Mg1(lam=8, mi=10, var=0.005)
modelo.mg1_print()
🧪 Executando Testes
bash
# Executar todos os exercícios da lista
python ListaExercicios.py

# Testar modelo específico via CLI
python interface.py
📊 Exemplos de Saída
text
═══════════════════════════════════════════════════════════
📊 RESULTADOS M/M/1
═══════════════════════════════════════════════════════════

📌 PARÂMETROS:
   λ = 2.000 clientes/hora
   μ = 3.000 clientes/hora
   s = 1 servidor

📈 MÉTRICAS DO SISTEMA:
   • ρ (Utilização): 0.6667 (66.67%)
   • L (clientes no sistema): 2.0000
   • Lq (clientes na fila): 1.3333
   • W (tempo no sistema): 1.0000 horas (60.00 min)
   • Wq (tempo na fila): 0.6667 horas (40.00 min)
   • P0 (sistema vazio): 0.3333 (33.33%)

📊 PROBABILIDADES Pn:
   • P0: 0.333333 (33.3333%)
   • P1: 0.222222 (22.2222%)
   • P2: 0.148148 (14.8148%)
🔧 Configuração Avançada
Variáveis de Ambiente
bash
# Para usar OCR com idioma específico
export TESSERACT_LANG="por"  # Português
Personalização da Interface
A interface gráfica suporta temas modernos (clam, alt, default, classic). Altere no arquivo app.py:

python
style.theme_use('clam')  # Opções: 'clam', 'alt', 'default', 'classic'
🐛 Solução de Problemas
Problema	Solução
ModuleNotFoundError: No module named 'forms'	Verifique se está executando na raiz do projeto
OCR não funciona	Instale o Tesseract no sistema (veja instruções acima)
Interface gráfica não abre	Instale o suporte Tkinter: sudo apt-get install python3-tk
Erro de importação	Execute pip install -r requirements.txt
📝 Licença
Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.