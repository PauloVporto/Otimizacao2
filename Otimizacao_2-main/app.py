"""Aplicação de Teoria das Filas com Interface Gráfica Moderna."""
import sys
import io
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional
import re

# Tentar importar bibliotecas para OCR e processamento de imagem
try:
    from PIL import Image, ImageTk
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("Aviso: Bibliotecas de OCR não instaladas. Instale com: pip install Pillow pytesseract")

try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Aviso: PyMuPDF não instalado. Instale com: pip install PyMuPDF")

# Importar os modelos de fila
try:
    from forms.mg1 import Mg1
    from forms.mm import Mm
    from forms.mm1k import Mm1k
    from forms.mmsk import Mmsk
    from forms.mm1n import Mm1n
    from forms.mmsn import Mmsn
    from forms.prioridadesInterrupcao import mms_prioridade_com_interrupcao
    from forms.prioridadesSemInterrup import mms_prioridade_sem_interrupcao
    from ListaExercicios import rodar_testes
    MODELS_AVAILABLE = True
except ImportError as e:
    MODELS_AVAILABLE = False
    print(f"Erro ao importar modelos: {e}")


class ModernStyle:
    """Configurações de estilo moderno."""
    
    COLORS = {
        'primary': '#1a1a2e',
        'secondary': '#16213e',
        'accent': '#0f3460',
        'success': '#00b894',
        'warning': '#f39c12',
        'danger': '#e74c3c',
        'background': '#f5f6fa',
        'surface': '#ffffff',
        'text': '#2d3436',
        'text_light': '#636e72',
        'border': '#dfe6e9',
    }
    
    @staticmethod
    def apply_theme():
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar notebook
        style.configure('TNotebook', background=ModernStyle.COLORS['background'])
        style.configure('TNotebook.Tab', padding=[20, 10],
                       font=('Segoe UI', 10, 'bold'))
        style.map('TNotebook.Tab',
                  background=[('selected', ModernStyle.COLORS['primary'])],
                  foreground=[('selected', 'white'), ('active', ModernStyle.COLORS['accent'])])
        
        # Configurar botões
        style.configure('Primary.TButton', font=('Segoe UI', 10, 'bold'),
                       padding=[25, 12], background=ModernStyle.COLORS['primary'])
        style.map('Primary.TButton',
                  background=[('active', ModernStyle.COLORS['accent'])])
        
        style.configure('Success.TButton', font=('Segoe UI', 11, 'bold'),
                       padding=[30, 12], background=ModernStyle.COLORS['success'])
        style.map('Success.TButton',
                  background=[('active', '#00a884')])
        
        # Configurar frames
        style.configure('Card.TLabelframe', background=ModernStyle.COLORS['surface'],
                       relief='solid', borderwidth=1, bordercolor=ModernStyle.COLORS['border'])
        style.configure('Card.TLabelframe.Label', foreground=ModernStyle.COLORS['primary'],
                       font=('Segoe UI', 11, 'bold'), background=ModernStyle.COLORS['surface'])


class TextRedirector:
    """Redireciona stdout para um widget Text."""
    def __init__(self, text_widget):
        self.text_widget = text_widget
    
    def write(self, text):
        self.text_widget.configure(state='normal')
        self.text_widget.insert('end', text)
        self.text_widget.see('end')
        self.text_widget.configure(state='disabled')
    
    def flush(self):
        pass


class OutputArea:
    """Área de saída com scroll e botão limpar."""
    def __init__(self, parent, title="RESULTADOS"):
        self.parent = parent
        self.frame = ttk.LabelFrame(parent, text=f"📊 {title}", padding=10, style='Card.TLabelframe')
        self.frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Botões
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill='x', pady=(0, 10))
        
        self.clear_btn = ttk.Button(btn_frame, text="🗑️ Limpar", command=self.clear,
                                    style='Primary.TButton')
        self.clear_btn.pack(side='right')
        
        self.copy_btn = ttk.Button(btn_frame, text="📋 Copiar", command=self.copy,
                                   style='Primary.TButton')
        self.copy_btn.pack(side='right', padx=5)
        
        # Área de texto com scroll
        text_frame = ttk.Frame(self.frame)
        text_frame.pack(fill='both', expand=True)
        
        self.text_area = tk.Text(text_frame, height=28, wrap='word',
                                 font=('Consolas', 10),
                                 bg=ModernStyle.COLORS['background'],
                                 fg=ModernStyle.COLORS['text'],
                                 relief='flat', borderwidth=0,
                                 selectbackground=ModernStyle.COLORS['accent'])
        
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', 
                                  command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side='right', fill='y')
        self.text_area.pack(side='left', fill='both', expand=True)
    
    def clear(self):
        self.text_area.configure(state='normal')
        self.text_area.delete(1.0, tk.END)
        self.text_area.configure(state='disabled')
    
    def copy(self):
        text = self.text_area.get(1.0, tk.END).strip()
        if text:
            self.parent.clipboard_clear()
            self.parent.clipboard_append(text)
            messagebox.showinfo("Copiado", "Resultados copiados para área de transferência!")
    
    def write(self, text):
        self.text_area.configure(state='normal')
        self.text_area.insert(tk.END, text)
        self.text_area.see(tk.END)
        self.text_area.configure(state='disabled')


class ModernEntry(ttk.Frame):
    """Campo de entrada estilizado."""
    def __init__(self, parent, label_text, default="", unit="", tooltip="", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.label = ttk.Label(self, text=label_text, font=('Segoe UI', 10),
                               foreground=ModernStyle.COLORS['text'])
        self.label.pack(anchor='w')
        
        entry_frame = ttk.Frame(self)
        entry_frame.pack(fill='x', pady=(5, 0))
        
        self.entry = ttk.Entry(entry_frame, font=('Segoe UI', 10))
        self.entry.insert(0, default)
        self.entry.pack(side='left', fill='x', expand=True, ipady=5)
        
        if unit:
            unit_label = ttk.Label(entry_frame, text=unit, font=('Segoe UI', 9), 
                                  foreground=ModernStyle.COLORS['text_light'])
            unit_label.pack(side='left', padx=(8, 0))
        
        # Tooltip
        if tooltip:
            self._create_tooltip(tooltip)
    
    def _create_tooltip(self, text):
        def show_tooltip(event):
            tooltip = tk.Toplevel(self)
            tooltip.wm_overrideredirect(True)
            x = event.widget.winfo_rootx() + 20
            y = event.widget.winfo_rooty() + 20
            tooltip.wm_geometry(f"+{x}+{y}")
            
            label = tk.Label(tooltip, text=text, background='#ffffe0',
                           relief='solid', borderwidth=1, padx=5, pady=2,
                           font=('Segoe UI', 9))
            label.pack()
            self.after(3000, lambda: tooltip.destroy())
        
        self.label.bind("<Enter>", show_tooltip)
    
    def get(self):
        return self.entry.get()
    
    def get_float(self):
        try:
            return float(self.get().replace(',', '.'))
        except ValueError:
            return None
    
    def get_int(self):
        try:
            return int(self.get())
        except ValueError:
            return None


class ExerciseSolver:
    """Resolver exercícios a partir de imagem/PDF usando OCR."""
    
    def __init__(self):
        self.extracted_text = ""
    
    def extract_text_from_image(self, image_path):
        if not TESSERACT_AVAILABLE:
            return "❌ Bibliotecas de OCR não instaladas.\n\nPara instalar:\n1. pip install pytesseract pillow\n2. Instale o Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki"
        
        try:
            # Abrir e pré-processar imagem
            image = Image.open(image_path)
            # Converter para escala de cinza para melhor OCR
            image = image.convert('L')
            
            # Configurar Tesseract para português e inglês
            text = pytesseract.image_to_string(image, lang='por+eng')
            
            if not text.strip():
                return "❌ Nenhum texto identificado na imagem.\n\nVerifique se a imagem está clara e legível."
            
            return text
        except Exception as e:
            return f"❌ Erro ao processar imagem: {str(e)}"
    
    def extract_text_from_pdf(self, pdf_path):
        if not PDF_AVAILABLE:
            return "❌ Biblioteca PyMuPDF não instalada.\n\nInstale com: pip install PyMuPDF"
        
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page_num, page in enumerate(doc, 1):
                page_text = page.get_text()
                if page_text.strip():
                    text += f"--- Página {page_num} ---\n{page_text}\n"
            
            return text if text.strip() else "❌ Nenhum texto encontrado no PDF."
        except Exception as e:
            return f"❌ Erro ao ler PDF: {str(e)}"
    
    def parse_exercise(self, text):
        """Extrai parâmetros do texto usando regex."""
        params = {
            'lam': None,
            'mi': None,
            's': 1,
            'k': None,
            'n': None,
            't': None,
            'var': None
        }
        
        text_lower = text.lower()
        
        # Padrões para extração
        patterns = {
            'lam': [
                r'λ\s*=\s*([\d,\.]+)',
                r'lambda\s*=\s*([\d,\.]+)',
                r'taxa de chegada\s*[:=]\s*([\d,\.]+)',
                r'chegada\s*[:=]\s*([\d,\.]+)',
                r'λ\s*([\d,\.]+)',
            ],
            'mi': [
                r'μ\s*=\s*([\d,\.]+)',
                r'mi\s*=\s*([\d,\.]+)',
                r'taxa de atendimento\s*[:=]\s*([\d,\.]+)',
                r'servi[cç]o\s*[:=]\s*([\d,\.]+)',
                r'μ\s*([\d,\.]+)',
            ],
            's': [
                r'servidores?\s*[:=]\s*(\d+)',
                r's\s*=\s*(\d+)',
                r'canais?\s*[:=]\s*(\d+)',
            ],
            'k': [
                r'capacidade\s*[:=]\s*(\d+)',
                r'k\s*=\s*(\d+)',
                r'tamanho máximo\s*[:=]\s*(\d+)',
            ],
            'n': [
                r'popula[cç][aã]o\s*[:=]\s*(\d+)',
                r'n\s*=\s*(\d+)',
            ]
        }
        
        for key, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, text_lower)
                if match:
                    value = match.group(1).replace(',', '.')
                    if key in ['s', 'k', 'n']:
                        params[key] = int(float(value))
                    else:
                        params[key] = float(value)
                    break
        
        return params
    
    def solve(self, params, original_text=""):
        """Resolve o exercício com os parâmetros extraídos."""
        if not MODELS_AVAILABLE:
            return "❌ Módulos de modelo não disponíveis.\n\nVerifique se os arquivos forms estão na pasta correta."
        
        output = []
        output.append("═" * 70)
        output.append("🧮 RESOLUÇÃO DO EXERCÍCIO")
        output.append("═" * 70)
        
        if params['lam'] and params['mi']:
            lam = params['lam']
            mi = params['mi']
            s = params['s']
            
            output.append(f"\n📌 PARÂMETROS IDENTIFICADOS:")
            output.append(f"   • λ (taxa de chegada) = {lam} clientes/hora")
            output.append(f"   • μ (taxa de atendimento) = {mi} clientes/hora")
            output.append(f"   • s (servidores) = {s}")
            
            # Verificar estabilidade
            rho = lam / (s * mi)
            output.append(f"\n📈 UTILIZAÇÃO DO SISTEMA:")
            output.append(f"   • ρ = λ/(s·μ) = {rho:.4f} ({rho*100:.2f}%)")
            
            if rho >= 1:
                output.append(f"\n⚠️  ATENÇÃO: ρ ≥ 1, o sistema é instável!")
                output.append(f"   A fila tenderá a crescer infinitamente.")
                return "\n".join(output)
            
            if s == 1:
                # M/M/1
                output.append(f"\n📊 MÉTRICAS - MODELO M/M/1:")
                output.append(f"   {'─' * 50}")
                
                L = rho / (1 - rho)
                Lq = rho**2 / (1 - rho)
                W = 1 / (mi - lam)
                Wq = lam / (mi * (mi - lam))
                P0 = 1 - rho
                
                output.append(f"   • L (médio no sistema):      {L:.4f} clientes")
                output.append(f"   • Lq (médio na fila):        {Lq:.4f} clientes")
                output.append(f"   • W (tempo no sistema):      {W:.4f} h = {W*60:.2f} min")
                output.append(f"   • Wq (tempo na fila):        {Wq:.4f} h = {Wq*60:.2f} min")
                output.append(f"   • P0 (sistema vazio):        {P0:.4f} ({P0*100:.2f}%)")
                
                output.append(f"\n📊 PROBABILIDADES Pn:")
                for n in [0, 1, 2, 3, 4, 5]:
                    Pn = (1 - rho) * (rho ** n)
                    output.append(f"   • P{n}: {Pn:.6f} ({Pn*100:.4f}%)")
            
            else:
                # M/M/s
                try:
                    modelo = Mm(lam=lam, mi=mi, s=s)
                    old_stdout = sys.stdout
                    sys.stdout = io.StringIO()
                    modelo.resultado()
                    result = sys.stdout.getvalue()
                    sys.stdout = old_stdout
                    output.append(f"\n{result}")
                except Exception as e:
                    output.append(f"\n❌ Erro no cálculo: {str(e)}")
        else:
            output.append("\n⚠️  NÃO FOI POSSÍVEL IDENTIFICAR OS PARÂMETROS")
            output.append("\n   Parâmetros necessários: λ (taxa de chegada) e μ (taxa de atendimento)")
            output.append("\n📝 TEXTO EXTRAÍDO DO ARQUIVO:")
            output.append("─" * 50)
            preview = original_text[:800] if len(original_text) > 800 else original_text
            output.append(preview)
            if len(original_text) > 800:
                output.append(f"\n... (mais {len(original_text)-800} caracteres)")
            
            output.append("\n\n💡 DICAS:")
            output.append("   • Certifique-se que a imagem está legível")
            output.append("   • Use números no formato: λ = 2.5, μ = 3.0")
            output.append("   • Para servidores: s = 2")
        
        return "\n".join(output)


class FilaApp:
    """Aplicação principal."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora - Teoria das Filas")
        self.root.geometry("1280x900")
        self.root.minsize(1100, 800)
        self.root.configure(bg=ModernStyle.COLORS['background'])
        
        # Inicializar solver
        self.solver = ExerciseSolver()
        
        # Aplicar estilo
        ModernStyle.apply_theme()
        
        # Criar interface
        self._create_header()
        self._create_notebook()
        self._create_footer()
    
    def _create_header(self):
        """Cabeçalho da aplicação."""
        header = tk.Frame(self.root, bg=ModernStyle.COLORS['primary'], height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        # Logo e título
        title_frame = tk.Frame(header, bg=ModernStyle.COLORS['primary'])
        title_frame.pack(side='left', padx=30, pady=15)
        
        title = tk.Label(title_frame, text="📊 Calculadora - Teoria das Filas", 
                        font=('Segoe UI', 22, 'bold'),
                        bg=ModernStyle.COLORS['primary'], fg='white')
        title.pack()
        
        subtitle = tk.Label(title_frame, text="Sistema de Análise de Filas | M/M/s | M/G/1 | Prioridades",
                           font=('Segoe UI', 9),
                           bg=ModernStyle.COLORS['primary'], fg='#b2bec3')
        subtitle.pack()
        
        # Versão
        version = tk.Label(header, text="v2.0",
                          font=('Segoe UI', 10),
                          bg=ModernStyle.COLORS['primary'], fg='#b2bec3')
        version.pack(side='right', padx=20)
    
    def _create_footer(self):
        """Rodapé da aplicação."""
        footer = tk.Frame(self.root, bg=ModernStyle.COLORS['surface'], height=30)
        footer.pack(side='bottom', fill='x')
        footer.pack_propagate(False)
        
        status = tk.Label(footer, text="✅ Pronto | OCR com Tesseract | Suporte a Imagens e PDFs",
                         font=('Segoe UI', 8),
                         bg=ModernStyle.COLORS['surface'], fg=ModernStyle.COLORS['text_light'])
        status.pack(pady=5)
    
    def _create_notebook(self):
        """Cria o notebook com as abas."""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=15, pady=(10, 15))
        
        # Criar abas
        self._create_tab_mms()
        self._create_tab_mg1()
        self._create_tab_priority()
        self._create_tab_finite()
        self._create_tab_ocr()
        self._create_tab_exercises()
    
    def _create_card(self, parent, title):
        """Cria um card estilizado."""
        card = ttk.LabelFrame(parent, text=title, padding=15, style='Card.TLabelframe')
        return card
    
    def _create_tab_mms(self):
        """Aba M/M/s."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📈 M/M/s")
        
        # Layout principal
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill='both', expand=True)
        
        # Card de entrada
        input_card = self._create_card(main_frame, "Parâmetros do Sistema")
        input_card.pack(fill='x', padx=20, pady=15)
        
        # Grid de campos
        fields_frame = ttk.Frame(input_card)
        fields_frame.pack(fill='x')
        
        self.mms_lam = ModernEntry(fields_frame, "Taxa de Chegada (λ)", "1.0", "clientes/h", 
                                   "Taxa média de chegada de clientes")
        self.mms_lam.grid(row=0, column=0, padx=10, pady=5, sticky='ew')
        
        self.mms_mi = ModernEntry(fields_frame, "Taxa de Atendimento (μ)", "2.0", "clientes/h",
                                  "Taxa média de atendimento por servidor")
        self.mms_mi.grid(row=0, column=1, padx=10, pady=5, sticky='ew')
        
        self.mms_s = ModernEntry(fields_frame, "Servidores (s)", "1", "",
                                 "Número de servidores no sistema")
        self.mms_s.grid(row=1, column=0, padx=10, pady=5, sticky='ew')
        
        self.mms_t = ModernEntry(fields_frame, "Tempo t (min)", "60", "min",
                                 "Para calcular P(W>t) e P(Wq>t)")
        self.mms_t.grid(row=1, column=1, padx=10, pady=5, sticky='ew')
        
        self.mms_n = ModernEntry(fields_frame, "Clientes (n)", "5", "",
                                 "Para calcular probabilidade P(n)")
        self.mms_n.grid(row=2, column=0, padx=10, pady=5, sticky='ew')
        
        fields_frame.columnconfigure(0, weight=1)
        fields_frame.columnconfigure(1, weight=1)
        
        # Botão calcular
        btn_frame = ttk.Frame(input_card)
        btn_frame.pack(pady=15)
        
        self.mms_output = OutputArea(main_frame, "RESULTADOS M/M/s")
        
        def calcular():
            lam = self.mms_lam.get_float()
            mi = self.mms_mi.get_float()
            s = self.mms_s.get_int()
            t = self.mms_t.get_float()
            n = self.mms_n.get_int()
            
            if not lam or not mi or not s:
                messagebox.showerror("Erro", "Preencha λ, μ e s corretamente")
                return
            
            if not MODELS_AVAILABLE:
                self.mms_output.write("❌ Módulos de modelo não disponíveis.\n")
                return
            
            try:
                modelo = Mm(lam=lam, mi=mi, s=s)
                
                old_stdout = sys.stdout
                sys.stdout = io.StringIO()
                modelo.resultado()
                result = sys.stdout.getvalue()
                sys.stdout = old_stdout
                
                self.mms_output.write("═" * 70 + "\n")
                self.mms_output.write("📊 RESULTADOS DO SISTEMA\n")
                self.mms_output.write("═" * 70 + "\n\n")
                self.mms_output.write(result + "\n")
                
                if n:
                    prob_n = modelo.prob_n_clientes(n=n)
                    self.mms_output.write(f"📌 P({n}) = {prob_n:.6f} ({prob_n*100:.4f}%)\n")
                
                if t:
                    t_horas = t / 60.0
                    prob_wq = modelo.prob_wq_maior_que_t(t=t_horas)
                    self.mms_output.write(f"📌 P(Wq > {t:.2f} min) = {prob_wq:.6f} ({prob_wq*100:.4f}%)\n")
                    
                    if s == 1:
                        prob_w = modelo.prob_w_maior_que_t(t=t_horas)
                        self.mms_output.write(f"📌 P(W > {t:.2f} min) = {prob_w:.6f} ({prob_w*100:.4f}%)\n")
            except Exception as e:
                self.mms_output.write(f"❌ Erro: {str(e)}\n")
        
        calc_btn = ttk.Button(btn_frame, text="▶ CALCULAR", command=calcular, style='Success.TButton')
        calc_btn.pack(ipadx=30, ipady=5)
    
    def _create_tab_mg1(self):
        """Aba M/G/1."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📐 M/G/1")
        
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill='both', expand=True)
        
        input_card = self._create_card(main_frame, "Parâmetros M/G/1")
        input_card.pack(fill='x', padx=20, pady=15)
        
        fields_frame = ttk.Frame(input_card)
        fields_frame.pack(fill='x')
        
        self.mg1_lam = ModernEntry(fields_frame, "Taxa de Chegada (λ)", "8.0", "clientes/h",
                                   "Taxa média de chegada de clientes")
        self.mg1_lam.grid(row=0, column=0, padx=10, pady=5, sticky='ew')
        
        self.mg1_mi = ModernEntry(fields_frame, "Taxa de Atendimento (μ)", "10.0", "clientes/h",
                                  "Taxa média de atendimento")
        self.mg1_mi.grid(row=0, column=1, padx=10, pady=5, sticky='ew')
        
        self.mg1_var = ModernEntry(fields_frame, "Variância (σ²)", "0.005", "",
                                   "Variância do tempo de serviço")
        self.mg1_var.grid(row=1, column=0, padx=10, pady=5, sticky='ew')
        
        fields_frame.columnconfigure(0, weight=1)
        fields_frame.columnconfigure(1, weight=1)
        
        btn_frame = ttk.Frame(input_card)
        btn_frame.pack(pady=15)
        
        self.mg1_output = OutputArea(main_frame, "RESULTADOS M/G/1")
        
        def calcular():
            lam = self.mg1_lam.get_float()
            mi = self.mg1_mi.get_float()
            var = self.mg1_var.get_float()
            
            if not lam or not mi or var is None:
                messagebox.showerror("Erro", "Preencha todos os campos corretamente")
                return
            
            if not MODELS_AVAILABLE:
                self.mg1_output.write("❌ Módulos de modelo não disponíveis.\n")
                return
            
            try:
                modelo = Mg1(lam=lam, mi=mi, var=var)
                
                old_stdout = sys.stdout
                sys.stdout = io.StringIO()
                modelo.mg1_print()
                result = sys.stdout.getvalue()
                sys.stdout = old_stdout
                
                self.mg1_output.write("═" * 70 + "\n")
                self.mg1_output.write("📊 RESULTADOS M/G/1\n")
                self.mg1_output.write("═" * 70 + "\n\n")
                self.mg1_output.write(result + "\n")
            except Exception as e:
                self.mg1_output.write(f"❌ Erro: {str(e)}\n")
        
        calc_btn = ttk.Button(btn_frame, text="▶ CALCULAR", command=calcular, style='Success.TButton')
        calc_btn.pack(ipadx=30, ipady=5)
    
    def _create_tab_priority(self):
        """Aba de prioridades."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="⚡ Prioridades")
        
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill='both', expand=True)
        
        input_card = self._create_card(main_frame, "Parâmetros de Prioridade")
        input_card.pack(fill='x', padx=20, pady=15)
        
        # Taxas de chegada
        ttk.Label(input_card, text="Taxas de Chegada (λi):  (separados por vírgula, ex: 1.5, 2.0, 0.5)",
                 font=('Segoe UI', 10)).pack(anchor='w')
        self.pri_lambdas = tk.Entry(input_card, font=('Segoe UI', 10))
        self.pri_lambdas.insert(0, "1.5, 2.0, 0.5")
        self.pri_lambdas.pack(fill='x', pady=(3, 8), ipady=4)

        # Outros campos
        fields_frame = ttk.Frame(input_card)
        fields_frame.pack(fill='x', pady=5)

        self.pri_mi = ModernEntry(fields_frame, "Taxa de Atendimento (μ)", "4.0", "clientes/h")
        self.pri_mi.pack(side='left', expand=True, fill='x', padx=5)

        self.pri_s = ModernEntry(fields_frame, "Servidores (s)", "2", "")
        self.pri_s.pack(side='left', expand=True, fill='x', padx=5)

        # Tipo de prioridade (lado a lado, sem labelframe extra)
        type_frame = ttk.Frame(input_card)
        type_frame.pack(fill='x', pady=(8, 0))

        ttk.Label(type_frame, text="Tipo:", font=('Segoe UI', 10, 'bold')).pack(side='left', padx=(0, 10))
        self.pri_type = tk.StringVar(value="nonpreemptive")
        ttk.Radiobutton(type_frame, text="Sem Interrupção",
                       variable=self.pri_type, value="nonpreemptive").pack(side='left', padx=8)
        ttk.Radiobutton(type_frame, text="Com Interrupção",
                       variable=self.pri_type, value="preemptive").pack(side='left', padx=8)

        btn_frame = ttk.Frame(input_card)
        btn_frame.pack(pady=8)
        
        self.pri_output = OutputArea(main_frame, "RESULTADOS PRIORIDADES")
        
        def calcular():
            lambdas_text = self.pri_lambdas.get()
            lambdas = []
            for x in lambdas_text.split(','):
                try:
                    lambdas.append(float(x.strip().replace(',', '.')))
                except:
                    pass
            
            mi = self.pri_mi.get_float()
            s = self.pri_s.get_int()
            
            if not lambdas or not mi or not s:
                messagebox.showerror("Erro", "Preencha todos os campos corretamente")
                return
            
            if not MODELS_AVAILABLE:
                self.pri_output.write("❌ Módulos de modelo não disponíveis.\n")
                return
            
            try:
                if self.pri_type.get() == "nonpreemptive":
                    resultado = mms_prioridade_sem_interrupcao(lambdas_=lambdas, mi=mi, servidores=s)
                else:
                    resultado = mms_prioridade_com_interrupcao(lambdas_=lambdas, mi=mi, servidores=s)
                
                self.pri_output.write("═" * 70 + "\n")
                self.pri_output.write("📊 RESULTADOS\n")
                self.pri_output.write("═" * 70 + "\n\n")
                
                for classe, vals in resultado.items():
                    if classe == "Erro":
                        self.pri_output.write(f"❌ {vals}\n")
                        return
                    self.pri_output.write(f"📦 {classe}\n")
                    self.pri_output.write("─" * 40 + "\n")
                    for key, value in vals.items():
                        if isinstance(value, float):
                            self.pri_output.write(f"   {key}: {value:.6f}\n")
                        else:
                            self.pri_output.write(f"   {key}: {value}\n")
                    self.pri_output.write("\n")
            except Exception as e:
                self.pri_output.write(f"❌ Erro: {str(e)}\n")
        
        calc_btn = ttk.Button(btn_frame, text="▶ CALCULAR", command=calcular, style='Success.TButton')
        calc_btn.pack(ipadx=30, ipady=5)
    
    def _create_tab_finite(self):
        """Aba de filas finitas."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🔒 Filas Finitas")
        
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill='both', expand=True)
        
        input_card = self._create_card(main_frame, "Parâmetros")
        input_card.pack(fill='x', padx=20, pady=15)
        
        # Tipo de fila
        type_frame = ttk.Frame(input_card)
        type_frame.pack(fill='x', pady=5)
        
        self.fin_type = tk.StringVar(value="k")
        ttk.Radiobutton(type_frame, text="Capacidade Finita (K)", 
                       variable=self.fin_type, value="k").pack(side='left', padx=10)
        ttk.Radiobutton(type_frame, text="População Finita (N)", 
                       variable=self.fin_type, value="n").pack(side='left', padx=10)
        
        ttk.Separator(input_card, orient='horizontal').pack(fill='x', pady=10)
        
        # Campos
        fields_frame = ttk.Frame(input_card)
        fields_frame.pack(fill='x')
        
        self.fin_lam = ModernEntry(fields_frame, "Taxa de Chegada (λ)", "1.0", "clientes/h")
        self.fin_lam.grid(row=0, column=0, padx=10, pady=5, sticky='ew')
        
        self.fin_mi = ModernEntry(fields_frame, "Taxa de Atendimento (μ)", "2.0", "clientes/h")
        self.fin_mi.grid(row=0, column=1, padx=10, pady=5, sticky='ew')
        
        self.fin_s = ModernEntry(fields_frame, "Servidores (s)", "1", "")
        self.fin_s.grid(row=1, column=0, padx=10, pady=5, sticky='ew')
        
        self.fin_limit = ModernEntry(fields_frame, "Limite (K ou N)", "10", "")
        self.fin_limit.grid(row=1, column=1, padx=10, pady=5, sticky='ew')
        
        fields_frame.columnconfigure(0, weight=1)
        fields_frame.columnconfigure(1, weight=1)
        
        btn_frame = ttk.Frame(input_card)
        btn_frame.pack(pady=15)
        
        self.fin_output = OutputArea(main_frame, "RESULTADOS FILAS FINITAS")
        
        def calcular():
            lam = self.fin_lam.get_float()
            mi = self.fin_mi.get_float()
            s = self.fin_s.get_int()
            limit = self.fin_limit.get_int()
            
            if not lam or not mi or not s or not limit:
                messagebox.showerror("Erro", "Preencha todos os campos corretamente")
                return
            
            if not MODELS_AVAILABLE:
                self.fin_output.write("❌ Módulos de modelo não disponíveis.\n")
                return
            
            try:
                if self.fin_type.get() == "k":
                    if s == 1:
                        modelo = Mm1k(lam=lam, mi=mi, k=limit)
                    else:
                        modelo = Mmsk(lam=lam, mi=mi, s=s, k=limit)
                else:
                    if s == 1:
                        modelo = Mm1n(lam_por_cliente=lam, mi=mi, n_pop=limit)
                    else:
                        modelo = Mmsn(lam_por_cliente=lam, mi=mi, s=s, n_pop=limit)
                
                old_stdout = sys.stdout
                sys.stdout = io.StringIO()
                modelo.resultado()
                result = sys.stdout.getvalue()
                sys.stdout = old_stdout
                
                self.fin_output.write("═" * 70 + "\n")
                tipo = "Capacidade K" if self.fin_type.get() == "k" else "População N"
                self.fin_output.write(f"📊 RESULTADOS - {tipo}\n")
                self.fin_output.write("═" * 70 + "\n\n")
                self.fin_output.write(result + "\n")
            except Exception as e:
                self.fin_output.write(f"❌ Erro: {str(e)}\n")
        
        calc_btn = ttk.Button(btn_frame, text="▶ CALCULAR", command=calcular, style='Success.TButton')
        calc_btn.pack(ipadx=30, ipady=5)
    
    def _create_tab_ocr(self):
        """Aba OCR para resolver exercícios de imagem/PDF."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🔍 OCR Solver")
        
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill='both', expand=True)
        
        # Card de upload
        upload_card = self._create_card(main_frame, "Upload do Exercício")
        upload_card.pack(fill='x', padx=20, pady=15)
        
        # Área de preview
        preview_frame = ttk.LabelFrame(upload_card, text="Preview", padding=10)
        preview_frame.pack(fill='x', pady=10)
        
        self.preview_label = tk.Label(preview_frame, text="🖼️ Nenhum arquivo carregado",
                                     bg=ModernStyle.COLORS['background'],
                                     height=8, relief='solid', borderwidth=1,
                                     font=('Segoe UI', 10))
        self.preview_label.pack(fill='x')
        
        self.current_file = None
        
        def upload_image():
            file_path = filedialog.askopenfilename(
                title="Selecione uma imagem",
                filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp"), ("Todos", "*.*")]
            )
            if file_path:
                self.current_file = file_path
                try:
                    img = Image.open(file_path)
                    # Redimensionar para preview
                    img.thumbnail((500, 200))
                    photo = ImageTk.PhotoImage(img)
                    self.preview_label.configure(image=photo, text="")
                    self.preview_label.image = photo
                except Exception as e:
                    self.preview_label.configure(text=f"📁 {os.path.basename(file_path)}", image='')
        
        def upload_pdf():
            file_path = filedialog.askopenfilename(
                title="Selecione um PDF",
                filetypes=[("PDF", "*.pdf"), ("Todos", "*.*")]
            )
            if file_path:
                self.current_file = file_path
                self.preview_label.configure(text=f"📄 PDF: {os.path.basename(file_path)}\n\nClique em 'Processar' para extrair o texto", image='')
        
        def process_and_solve():
            if not self.current_file:
                messagebox.showwarning("Aviso", "Carregue uma imagem ou PDF primeiro!")
                return
            
            self.ocr_output.clear()
            self.ocr_output.write("═" * 70 + "\n")
            self.ocr_output.write("🔄 PROCESSANDO ARQUIVO...\n")
            self.ocr_output.write("═" * 70 + "\n\n")
            
            # Extrair texto
            ext = os.path.splitext(self.current_file)[1].lower()
            
            self.ocr_output.write("📝 EXTRAINDO TEXTO...\n")
            self.ocr_output.write("─" * 40 + "\n")
            
            if ext in ['.png', '.jpg', '.jpeg', '.bmp']:
                text = self.solver.extract_text_from_image(self.current_file)
            elif ext == '.pdf':
                text = self.solver.extract_text_from_pdf(self.current_file)
            else:
                text = "❌ Formato de arquivo não suportado. Use imagem (PNG, JPG) ou PDF."
            
            self.ocr_output.write(text + "\n\n")
            
            # Se extraiu texto, tentar resolver
            if not text.startswith("❌"):
                self.ocr_output.write("🔍 ANALISANDO EXERCÍCIO...\n")
                self.ocr_output.write("─" * 40 + "\n")
                
                params = self.solver.parse_exercise(text)
                result = self.solver.solve(params, text)
                self.ocr_output.write(result + "\n")
            else:
                self.ocr_output.write("\n" + text + "\n")
        
        # Botões
        btn_frame = ttk.Frame(upload_card)
        btn_frame.pack(pady=15)
        
        ttk.Button(btn_frame, text="📷 Carregar Imagem", command=upload_image,
                  style='Primary.TButton').pack(side='left', padx=5, ipadx=10)
        ttk.Button(btn_frame, text="📄 Carregar PDF", command=upload_pdf,
                  style='Primary.TButton').pack(side='left', padx=5, ipadx=10)
        ttk.Button(btn_frame, text="🔍 Processar e Resolver", command=process_and_solve,
                  style='Success.TButton').pack(side='left', padx=5, ipadx=10)
        
        # Área de resultados
        self.ocr_output = OutputArea(main_frame, "RESULTADOS OCR")
    
    def _create_tab_exercises(self):
        """Aba lista de exercícios."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📝 Lista")
        
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill='both', expand=True)
        
        # Card de informações
        info_card = self._create_card(main_frame, "Informações")
        info_card.pack(fill='x', padx=20, pady=15)
        
        info_text = """🎓 LISTA DE EXERCÍCIOS - TEORIA DAS FILAS

Esta função executa todos os testes definidos no arquivo 'ListaExercicios.py'.
Os resultados serão exibidos abaixo.

⚠️ Certifique-se de que o arquivo 'ListaExercicios.py' está na mesma pasta do programa."""
        
        info_label = tk.Label(info_card, text=info_text, justify='left',
                             font=('Segoe UI', 10), 
                             bg=ModernStyle.COLORS['surface'],
                             fg=ModernStyle.COLORS['text'])
        info_label.pack(pady=10)
        
        self.exercises_output = OutputArea(main_frame, "RESULTADOS LISTA")
        
        def run():
            if not MODELS_AVAILABLE:
                self.exercises_output.write("❌ Módulos de modelo não disponíveis.\n")
                return
            
            try:
                self.exercises_output.write("═" * 70 + "\n")
                self.exercises_output.write("🚀 EXECUTANDO LISTA DE EXERCÍCIOS\n")
                self.exercises_output.write("═" * 70 + "\n\n")
                
                old_stdout = sys.stdout
                sys.stdout = TextRedirector(self.exercises_output.text_area)
                rodar_testes()
                sys.stdout = old_stdout
            except Exception as e:
                self.exercises_output.write(f"❌ Erro ao executar lista: {str(e)}\n")
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        run_btn = ttk.Button(btn_frame, text="🚀 RODAR TODOS OS EXERCÍCIOS", 
                            command=run, style='Success.TButton')
        run_btn.pack(ipadx=40, ipady=8)


if __name__ == "__main__":
    root = tk.Tk()
    
    # Centralizar janela
    root.update_idletasks()
    width = 1280
    height = 900
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    app = FilaApp(root)
    root.mainloop()