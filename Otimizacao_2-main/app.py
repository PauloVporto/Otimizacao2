"""Calculadora - Teoria das Filas | Interface PySide6 Moderna."""
import sys
import io
import os
import re
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QTabWidget,
    QFrame, QGridLayout, QButtonGroup, QRadioButton, QFileDialog,
    QScrollArea, QSizePolicy, QSpacerItem, QMessageBox, QGroupBox,
    QSplitter
)
from PySide6.QtCore import Qt, QThread, Signal, QPropertyAnimation, QEasingCurve, QSize, QTimer
from PySide6.QtGui import (
    QFont, QColor, QPalette, QLinearGradient, QPainter, QPixmap,
    QIcon, QTextCursor, QFontDatabase, QGradient
)

# ─── Tentativa de imports dos modelos ────────────────────────────────────────
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import fitz
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

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
    print(f"[aviso] modelos não encontrados: {e}")

# ─── Paleta de cores ──────────────────────────────────────────────────────────
C = {
    "bg":        "#0D1117",
    "surface":   "#161B22",
    "surface2":  "#1C2333",
    "border":    "#30363D",
    "border2":   "#484F58",
    "accent":    "#58A6FF",
    "accent2":   "#1F6FEB",
    "green":     "#3FB950",
    "green_dk":  "#238636",
    "yellow":    "#D29922",
    "red":       "#F85149",
    "text":      "#E6EDF3",
    "text2":     "#8B949E",
    "text3":     "#484F58",
    "header_bg": "#010409",
}

# ─── Stylesheet global ───────────────────────────────────────────────────────
STYLE = f"""
QMainWindow, QWidget {{
    background-color: {C['bg']};
    color: {C['text']};
    font-family: 'JetBrains Mono', 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
}}

QTabWidget::pane {{
    background: {C['surface']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    top: -1px;
}}

QTabBar {{
    background: transparent;
}}

QTabBar::tab {{
    background: {C['surface2']};
    color: {C['text2']};
    border: 1px solid {C['border']};
    border-bottom: none;
    padding: 10px 22px;
    margin-right: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.3px;
}}

QTabBar::tab:selected {{
    background: {C['surface']};
    color: {C['accent']};
    border-color: {C['accent']};
    border-bottom: 2px solid {C['accent']};
}}

QTabBar::tab:hover:!selected {{
    background: {C['surface']};
    color: {C['text']};
}}

QLineEdit {{
    background: {C['bg']};
    color: {C['text']};
    border: 1px solid {C['border']};
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 13px;
    selection-background-color: {C['accent2']};
}}

QLineEdit:focus {{
    border: 1px solid {C['accent']};
    background: #0D1421;
}}

QLineEdit:hover {{
    border: 1px solid {C['border2']};
}}

QTextEdit {{
    background: {C['bg']};
    color: {C['text']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    padding: 14px;
    font-size: 13px;
    line-height: 1.6;
    selection-background-color: {C['accent2']};
}}

QTextEdit:focus {{
    border: 1px solid {C['border2']};
}}

QPushButton {{
    background: {C['surface2']};
    color: {C['text']};
    border: 1px solid {C['border']};
    border-radius: 6px;
    padding: 10px 20px;
    font-size: 12px;
    font-weight: 600;
}}

QPushButton:hover {{
    background: {C['surface']};
    border-color: {C['border2']};
    color: {C['accent']};
}}

QPushButton:pressed {{
    background: {C['bg']};
}}

QPushButton#primary {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1F6FEB, stop:1 #1158C7);
    color: white;
    border: 1px solid {C['accent2']};
}}

QPushButton#primary:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #388BFD, stop:1 #1F6FEB);
    color: white;
}}

QPushButton#success {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #2EA043, stop:1 #1A7431);
    color: white;
    border: 1px solid {C['green_dk']};
    padding: 12px 36px;
    font-size: 13px;
    letter-spacing: 0.5px;
}}

QPushButton#success:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #3FB950, stop:1 #2EA043);
    color: white;
}}

QPushButton#danger {{
    background: {C['surface2']};
    color: {C['red']};
    border: 1px solid {C['red']};
}}

QPushButton#danger:hover {{
    background: rgba(248, 81, 73, 0.15);
}}

QRadioButton {{
    color: {C['text2']};
    font-size: 12px;
    spacing: 8px;
}}

QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border-radius: 8px;
    border: 2px solid {C['border2']};
    background: {C['bg']};
}}

QRadioButton::indicator:checked {{
    background: {C['accent']};
    border-color: {C['accent']};
}}

QRadioButton:hover {{
    color: {C['text']};
}}

QScrollBar:vertical {{
    background: {C['bg']};
    width: 8px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical {{
    background: {C['border2']};
    border-radius: 4px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: {C['text2']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QLabel#section_title {{
    color: {C['text2']};
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding-bottom: 4px;
}}

QLabel#field_label {{
    color: {C['text2']};
    font-size: 11px;
    font-weight: 500;
    padding-bottom: 2px;
}}

QLabel#unit_label {{
    color: {C['text3']};
    font-size: 11px;
    padding-left: 6px;
    padding-right: 10px;
}}

QGroupBox {{
    color: {C['text2']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 14px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.8px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    color: {C['text2']};
    background: {C['surface']};
}}

QSplitter::handle:horizontal {{
    width: 4px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {C['border']}, stop:0.5 {C['accent2']}, stop:1 {C['border']});
    border-radius: 2px;
    margin: 8px 0px;
}}

QSplitter::handle:horizontal:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {C['border2']}, stop:0.5 {C['accent']}, stop:1 {C['border2']});
}}
"""

# ─── Helpers ─────────────────────────────────────────────────────────────────

def divider():
    """Linha divisória horizontal."""
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet(f"color: {C['border']}; border: none; border-top: 1px solid {C['border']};")
    return line


def make_label(text: str, kind: str = "field_label", font_size: int = 0) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName(kind)
    if font_size:
        f = lbl.font()
        f.setPointSize(font_size)
        lbl.setFont(f)
    return lbl


# ─── Campo de entrada ─────────────────────────────────────────────────────────

class FieldEntry(QWidget):
    def __init__(self, label: str, default: str = "", unit: str = "", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        lbl = make_label(label)
        layout.addWidget(lbl)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        self.entry = QLineEdit(default)
        row.addWidget(self.entry)

        if unit:
            u = make_label(unit, "unit_label")
            row.addWidget(u)

        layout.addLayout(row)

    def get(self) -> str:
        return self.entry.text().strip()

    def get_float(self) -> Optional[float]:
        try:
            return float(self.get().replace(",", "."))
        except ValueError:
            return None

    def get_int(self) -> Optional[int]:
        try:
            return int(self.get())
        except ValueError:
            return None


# ─── Área de saída ────────────────────────────────────────────────────────────

class OutputArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Barra superior
        bar = QHBoxLayout()
        bar.setSpacing(6)

        lbl = make_label("SAÍDA", "section_title")
        bar.addWidget(lbl)
        bar.addStretch()

        self.copy_btn = QPushButton("⎘  Copiar")
        self.copy_btn.setObjectName("primary")
        self.copy_btn.setFixedHeight(30)
        self.copy_btn.clicked.connect(self._copy)
        bar.addWidget(self.copy_btn)

        self.clear_btn = QPushButton("✕  Limpar")
        self.clear_btn.setObjectName("danger")
        self.clear_btn.setFixedHeight(30)
        self.clear_btn.clicked.connect(self.clear)
        bar.addWidget(self.clear_btn)

        layout.addLayout(bar)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setFont(QFont("JetBrains Mono, Cascadia Code, Fira Code, Consolas", 12))
        self.text.setMinimumHeight(500)
        layout.addWidget(self.text, 1)

    def write(self, content: str):
        self.text.moveCursor(QTextCursor.End)
        self.text.insertPlainText(content)
        self.text.moveCursor(QTextCursor.End)

    def clear(self):
        self.text.clear()

    def _copy(self):
        txt = self.text.toPlainText().strip()
        if txt:
            QApplication.clipboard().setText(txt)
            self.copy_btn.setText("✓  Copiado!")
            QTimer.singleShot(2000, lambda: self.copy_btn.setText("⎘  Copiar"))


# ─── Cabeçalho ────────────────────────────────────────────────────────────────

class Header(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(88)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(32, 0, 32, 0)
        layout.setSpacing(0)

        # ── Lado esquerdo: ícone + textos ────────────────────────────
        left = QHBoxLayout()
        left.setSpacing(16)

        # Ícone circular
        icon_lbl = QLabel("∑")
        icon_lbl.setFixedSize(44, 44)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            "stop:0 #1F6FEB, stop:1 #58A6FF);"
            "border-radius: 22px;"
            "color: white;"
            "font-size: 20px;"
            "font-weight: 900;"
        )
        left.addWidget(icon_lbl)

        texts = QVBoxLayout()
        texts.setSpacing(3)

        title = QLabel("Teoria das Filas")
        title.setStyleSheet(
            "color: #E6EDF3; font-size: 20px; font-weight: 800;"
            "letter-spacing: -0.5px; background: transparent;"
        )
        texts.addWidget(title)

        sub = QLabel("Calculadora de Desempenho  ·  Modelos Estocásticos")
        sub.setStyleSheet(
            "color: #8B949E; font-size: 11px; letter-spacing: 0.5px; background: transparent;"
        )
        texts.addWidget(sub)

        left.addLayout(texts)
        layout.addLayout(left)
        layout.addStretch()

        # ── Lado direito: pill badges ─────────────────────────────────
        right = QHBoxLayout()
        right.setSpacing(8)

        pill_style = (
            "border-radius: 10px; padding: 4px 12px;"
            "font-size: 10px; font-weight: 700; letter-spacing: 0.8px;"
            "background: transparent;"
        )

        for label, color in [
            ("M/M/s",      "#58A6FF"),
            ("M/G/1",      "#3FB950"),
            ("PRIORIDADES","#D29922"),
            ("OCR",        "#BC8CFF"),
        ]:
            p = QLabel(label)
            p.setStyleSheet(
                f"{pill_style} color: {color};"
                f"border: 1px solid {color};"
            )
            right.addWidget(p)

        right.addSpacing(16)

        badge = QLabel("v2.0")
        badge.setStyleSheet(
            "background: #1C2333; color: #8B949E; border: 1px solid #30363D;"
            "border-radius: 10px; padding: 4px 12px; font-size: 10px; font-weight: 700;"
        )
        right.addWidget(badge)

        layout.addLayout(right)

    def paintEvent(self, event):
        """Fundo com gradiente sutil + linha accent inferior."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Gradiente de fundo
        grad = QLinearGradient(0, 0, self.width(), 0)
        grad.setColorAt(0.0,  QColor("#0A0F1A"))
        grad.setColorAt(0.4,  QColor("#0D1117"))
        grad.setColorAt(1.0,  QColor("#0A0F1A"))
        painter.fillRect(self.rect(), grad)

        # Linha inferior de separação (neutra)
        painter.setPen(QColor("#30363D"))
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)

        # Accent line colorida no topo
        accent_grad = QLinearGradient(0, 0, self.width(), 0)
        accent_grad.setColorAt(0.0,  QColor("#1F6FEB"))
        accent_grad.setColorAt(0.5,  QColor("#58A6FF"))
        accent_grad.setColorAt(1.0,  QColor("#BC8CFF"))
        painter.setPen(Qt.NoPen)
        from PySide6.QtGui import QBrush
        painter.setBrush(QBrush(accent_grad))
        painter.drawRect(0, 0, self.width(), 3)


# ─── Rodapé ───────────────────────────────────────────────────────────────────

class Footer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(28)
        self.setStyleSheet(f"background: {C['header_bg']}; border-top: 1px solid {C['border']};")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(28, 0, 28, 0)

        ocr_ok = "✓ OCR" if (PILLOW_AVAILABLE and TESSERACT_AVAILABLE) else "✗ OCR indisponível"
        pdf_ok = "✓ PDF" if PDF_AVAILABLE else "✗ PDF indisponível"
        mod_ok = "✓ Modelos carregados" if MODELS_AVAILABLE else "✗ Modelos não encontrados"

        status = QLabel(f"{mod_ok}   {ocr_ok}   {pdf_ok}")
        status.setStyleSheet(f"color: {C['text3']}; font-size: 10px;")
        layout.addWidget(status)
        layout.addStretch()


# ─── Abas ─────────────────────────────────────────────────────────────────────

def _capture(fn) -> str:
    """Captura stdout de uma chamada."""
    old = sys.stdout
    sys.stdout = io.StringIO()
    try:
        fn()
        return sys.stdout.getvalue()
    finally:
        sys.stdout = old


def _header(title: str) -> str:
    bar = "═" * 68
    return f"{bar}\n  {title}\n{bar}\n"


# ─── Painel esquerdo (entrada) com scroll ─────────────────────────────────────

def _left_panel(inner_widget: QWidget) -> QWidget:
    """Envolve o widget de entrada num QScrollArea estilizado."""
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    scroll.setStyleSheet(f"background: {C['surface']}; border: none;")

    wrapper = QWidget()
    wrapper.setStyleSheet(f"background: {C['surface']};")
    lay = QVBoxLayout(wrapper)
    lay.setContentsMargins(24, 24, 24, 24)
    lay.setSpacing(0)
    lay.addWidget(inner_widget)
    lay.addStretch()

    scroll.setWidget(wrapper)
    return scroll


def _right_panel(output: "OutputArea") -> QWidget:
    """Envolve a área de saída num container estilizado."""
    wrap = QWidget()
    wrap.setStyleSheet(f"background: {C['bg']};")
    lay = QVBoxLayout(wrap)
    lay.setContentsMargins(16, 24, 24, 24)
    lay.setSpacing(0)
    lay.addWidget(output)
    return wrap


def _make_splitter(left: QWidget, right: QWidget) -> QSplitter:
    sp = QSplitter(Qt.Horizontal)
    sp.setHandleWidth(5)
    sp.addWidget(left)
    sp.addWidget(right)
    sp.setSizes([1, 1])          # 50 / 50
    sp.setStretchFactor(0, 1)
    sp.setStretchFactor(1, 1)
    sp.setChildrenCollapsible(False)
    return sp


# ── M/M/s ─────────────────────────────────────────────────────────────────────

class MmsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── painel esquerdo ──────────────────────────────────────────
        form = QWidget()
        form_lay = QVBoxLayout(form)
        form_lay.setContentsMargins(0, 0, 0, 0)
        form_lay.setSpacing(20)

        grp = QGroupBox("PARÂMETROS  ·  M/M/s")
        grp_lay = QVBoxLayout(grp)
        grp_lay.setSpacing(16)

        row1 = QHBoxLayout()
        self.lam = FieldEntry("Taxa de Chegada (λ)", "1.0", "clientes/h")
        self.mi  = FieldEntry("Taxa de Atendimento (μ)", "2.0", "clientes/h")
        row1.addWidget(self.lam)
        row1.addSpacing(16)
        row1.addWidget(self.mi)
        grp_lay.addLayout(row1)

        row2 = QHBoxLayout()
        self.s = FieldEntry("Servidores (s)", "1")
        self.t = FieldEntry("Tempo t", "60", "min")
        self.n = FieldEntry("Clientes n  —  P(N=n)", "5")
        row2.addWidget(self.s)
        row2.addSpacing(16)
        row2.addWidget(self.t)
        row2.addSpacing(16)
        row2.addWidget(self.n)
        grp_lay.addLayout(row2)

        btn = QPushButton("▶   CALCULAR")
        btn.setObjectName("success")
        btn.clicked.connect(self._calc)
        grp_lay.addWidget(btn, alignment=Qt.AlignLeft)

        form_lay.addWidget(grp)

        # ── splitter ─────────────────────────────────────────────────
        self.output = OutputArea()
        sp = _make_splitter(_left_panel(form), _right_panel(self.output))
        root.addWidget(sp)

    def _calc(self):
        lam = self.lam.get_float()
        mi  = self.mi.get_float()
        s   = self.s.get_int()
        t   = self.t.get_float()
        n   = self.n.get_int()

        if not (lam and mi and s):
            QMessageBox.warning(self, "Campos inválidos", "Preencha λ, μ e s corretamente.")
            return
        if not MODELS_AVAILABLE:
            self.output.write("✗ Módulos de modelos não disponíveis.\n"); return

        self.output.clear()
        self.output.write(_header("MODELO  M/M/s"))

        try:
            modelo = Mm(lam=lam, mi=mi, s=s)
            result = _capture(modelo.resultado)
            self.output.write(result + "\n")

            if n:
                p = modelo.prob_n_clientes(n=n)
                self.output.write(f"  P({n})        = {p:.8f}   ({p*100:.4f}%)\n")
            if t:
                t_h = t / 60
                pwq = modelo.prob_wq_maior_que_t(t=t_h)
                self.output.write(f"  P(Wq>{t:.0f}min) = {pwq:.8f}   ({pwq*100:.4f}%)\n")
                if s == 1:
                    pw = modelo.prob_w_maior_que_t(t=t_h)
                    self.output.write(f"  P(W>{t:.0f}min)  = {pw:.8f}   ({pw*100:.4f}%)\n")
        except Exception as e:
            self.output.write(f"\n✗ Erro: {e}\n")


# ── M/G/1 ─────────────────────────────────────────────────────────────────────

class Mg1Tab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        form = QWidget()
        form_lay = QVBoxLayout(form)
        form_lay.setContentsMargins(0, 0, 0, 0)
        form_lay.setSpacing(20)

        grp = QGroupBox("PARÂMETROS  ·  M/G/1")
        grp_lay = QVBoxLayout(grp)
        grp_lay.setSpacing(16)

        row1 = QHBoxLayout()
        self.lam = FieldEntry("Taxa de Chegada (λ)", "8.0", "clientes/h")
        self.mi  = FieldEntry("Taxa de Atendimento (μ)", "10.0", "clientes/h")
        row1.addWidget(self.lam)
        row1.addSpacing(16)
        row1.addWidget(self.mi)
        grp_lay.addLayout(row1)

        self.var = FieldEntry("Variância do Serviço (σ²)", "0.005")
        grp_lay.addWidget(self.var)

        btn = QPushButton("▶   CALCULAR")
        btn.setObjectName("success")
        btn.clicked.connect(self._calc)
        grp_lay.addWidget(btn, alignment=Qt.AlignLeft)

        form_lay.addWidget(grp)

        self.output = OutputArea()
        sp = _make_splitter(_left_panel(form), _right_panel(self.output))
        root.addWidget(sp)

    def _calc(self):
        lam = self.lam.get_float()
        mi  = self.mi.get_float()
        var = self.var.get_float()

        if lam is None or mi is None or var is None:
            QMessageBox.warning(self, "Campos inválidos", "Preencha todos os campos.")
            return
        if not MODELS_AVAILABLE:
            self.output.write("✗ Módulos não disponíveis.\n"); return

        self.output.clear()
        self.output.write(_header("MODELO  M/G/1"))
        try:
            modelo = Mg1(lam=lam, mi=mi, var=var)
            result = _capture(modelo.mg1_print)
            self.output.write(result + "\n")
        except Exception as e:
            self.output.write(f"\n✗ Erro: {e}\n")


# ── Prioridades ───────────────────────────────────────────────────────────────

class PriorityTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        form = QWidget()
        form_lay = QVBoxLayout(form)
        form_lay.setContentsMargins(0, 0, 0, 0)
        form_lay.setSpacing(20)

        grp = QGroupBox("PARÂMETROS  ·  PRIORIDADES")
        grp_lay = QVBoxLayout(grp)
        grp_lay.setSpacing(14)

        lam_lbl = make_label("Taxas de Chegada (λ₁, λ₂, …  —  separadas por vírgula)")
        grp_lay.addWidget(lam_lbl)
        self.lambdas = QLineEdit("1.5, 2.0, 0.5")
        grp_lay.addWidget(self.lambdas)

        row = QHBoxLayout()
        self.mi = FieldEntry("Taxa de Atendimento (μ)", "4.0", "clientes/h")
        self.s  = FieldEntry("Servidores (s)", "2")
        row.addWidget(self.mi)
        row.addSpacing(16)
        row.addWidget(self.s)
        grp_lay.addLayout(row)

        type_row = QHBoxLayout()
        type_lbl = make_label("Tipo:", "section_title")
        type_row.addWidget(type_lbl)
        type_row.addSpacing(12)
        self.rg_preempt = QButtonGroup(self)
        self.rb_no  = QRadioButton("Sem Interrupção")
        self.rb_yes = QRadioButton("Com Interrupção")
        self.rb_no.setChecked(True)
        self.rg_preempt.addButton(self.rb_no, 0)
        self.rg_preempt.addButton(self.rb_yes, 1)
        type_row.addWidget(self.rb_no)
        type_row.addSpacing(12)
        type_row.addWidget(self.rb_yes)
        type_row.addStretch()
        grp_lay.addLayout(type_row)

        btn = QPushButton("▶   CALCULAR")
        btn.setObjectName("success")
        btn.clicked.connect(self._calc)
        grp_lay.addWidget(btn, alignment=Qt.AlignLeft)

        form_lay.addWidget(grp)

        self.output = OutputArea()
        sp = _make_splitter(_left_panel(form), _right_panel(self.output))
        root.addWidget(sp)

    def _calc(self):
        lambdas = []
        for x in self.lambdas.text().split(","):
            try:
                lambdas.append(float(x.strip().replace(",", ".")))
            except ValueError:
                pass

        mi = self.mi.get_float()
        s  = self.s.get_int()

        if not lambdas or not mi or not s:
            QMessageBox.warning(self, "Campos inválidos", "Preencha todos os campos.")
            return
        if not MODELS_AVAILABLE:
            self.output.write("✗ Módulos não disponíveis.\n"); return

        self.output.clear()
        tipo = "COM INTERRUPÇÃO" if self.rg_preempt.checkedId() == 1 else "SEM INTERRUPÇÃO"
        self.output.write(_header(f"PRIORIDADES  ·  {tipo}"))

        try:
            if self.rg_preempt.checkedId() == 0:
                res = mms_prioridade_sem_interrupcao(lambdas_=lambdas, mi=mi, servidores=s)
            else:
                res = mms_prioridade_com_interrupcao(lambdas_=lambdas, mi=mi, servidores=s)

            for classe, vals in res.items():
                if classe == "Erro":
                    self.output.write(f"✗ {vals}\n"); return
                self.output.write(f"\n  ── {classe} ──\n")
                for k, v in vals.items():
                    val_str = f"{v:.8f}" if isinstance(v, float) else str(v)
                    self.output.write(f"     {k:25s} {val_str}\n")
        except Exception as e:
            self.output.write(f"\n✗ Erro: {e}\n")


# ── Filas Finitas ─────────────────────────────────────────────────────────────

class FiniteTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        form = QWidget()
        form_lay = QVBoxLayout(form)
        form_lay.setContentsMargins(0, 0, 0, 0)
        form_lay.setSpacing(20)

        grp = QGroupBox("PARÂMETROS  ·  FILAS FINITAS")
        grp_lay = QVBoxLayout(grp)
        grp_lay.setSpacing(14)

        type_row = QHBoxLayout()
        type_lbl = make_label("Modelo:", "section_title")
        type_row.addWidget(type_lbl)
        type_row.addSpacing(12)
        self.rg_type = QButtonGroup(self)
        self.rb_k = QRadioButton("Capacidade Finita (K)")
        self.rb_n = QRadioButton("População Finita (N)")
        self.rb_k.setChecked(True)
        self.rg_type.addButton(self.rb_k, 0)
        self.rg_type.addButton(self.rb_n, 1)
        type_row.addWidget(self.rb_k)
        type_row.addSpacing(12)
        type_row.addWidget(self.rb_n)
        type_row.addStretch()
        grp_lay.addLayout(type_row)

        grp_lay.addWidget(divider())

        row1 = QHBoxLayout()
        self.lam   = FieldEntry("Taxa de Chegada (λ)", "1.0", "clientes/h")
        self.mi    = FieldEntry("Taxa de Atendimento (μ)", "2.0", "clientes/h")
        row1.addWidget(self.lam)
        row1.addSpacing(16)
        row1.addWidget(self.mi)
        grp_lay.addLayout(row1)

        row2 = QHBoxLayout()
        self.s     = FieldEntry("Servidores (s)", "1")
        self.limit = FieldEntry("Limite (K ou N)", "10")
        row2.addWidget(self.s)
        row2.addSpacing(16)
        row2.addWidget(self.limit)
        grp_lay.addLayout(row2)

        btn = QPushButton("▶   CALCULAR")
        btn.setObjectName("success")
        btn.clicked.connect(self._calc)
        grp_lay.addWidget(btn, alignment=Qt.AlignLeft)

        form_lay.addWidget(grp)

        self.output = OutputArea()
        sp = _make_splitter(_left_panel(form), _right_panel(self.output))
        root.addWidget(sp)

    def _calc(self):
        lam   = self.lam.get_float()
        mi    = self.mi.get_float()
        s     = self.s.get_int()
        limit = self.limit.get_int()

        if not (lam and mi and s and limit):
            QMessageBox.warning(self, "Campos inválidos", "Preencha todos os campos.")
            return
        if not MODELS_AVAILABLE:
            self.output.write("✗ Módulos não disponíveis.\n"); return

        self.output.clear()
        tipo_str = "CAPACIDADE FINITA K" if self.rg_type.checkedId() == 0 else "POPULAÇÃO FINITA N"
        self.output.write(_header(tipo_str))

        try:
            if self.rg_type.checkedId() == 0:
                modelo = Mm1k(lam=lam, mi=mi, k=limit) if s == 1 else Mmsk(lam=lam, mi=mi, s=s, k=limit)
            else:
                modelo = Mm1n(lam_por_cliente=lam, mi=mi, n_pop=limit) if s == 1 \
                    else Mmsn(lam_por_cliente=lam, mi=mi, s=s, n_pop=limit)

            result = _capture(modelo.resultado)
            self.output.write(result + "\n")
        except Exception as e:
            self.output.write(f"\n✗ Erro: {e}\n")


# ── OCR Solver ────────────────────────────────────────────────────────────────

class OCRTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = None

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        form = QWidget()
        form_lay = QVBoxLayout(form)
        form_lay.setContentsMargins(0, 0, 0, 0)
        form_lay.setSpacing(20)

        grp = QGroupBox("CARREGAR EXERCÍCIO  ·  OCR SOLVER")
        grp_lay = QVBoxLayout(grp)
        grp_lay.setSpacing(14)

        self.preview = QLabel("Nenhum arquivo carregado.\nAceita: PNG · JPG · BMP · PDF")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setFixedHeight(130)
        self.preview.setStyleSheet(
            f"background: {C['bg']}; border: 1px dashed {C['border2']}; border-radius: 8px;"
            f"color: {C['text3']}; font-size: 12px;"
        )
        grp_lay.addWidget(self.preview)

        btn_row = QHBoxLayout()
        b_img = QPushButton("🖼   Imagem")
        b_img.setObjectName("primary")
        b_img.clicked.connect(self._load_image)

        b_pdf = QPushButton("📄   PDF")
        b_pdf.setObjectName("primary")
        b_pdf.clicked.connect(self._load_pdf)

        b_run = QPushButton("🔍   Processar e Resolver")
        b_run.setObjectName("success")
        b_run.clicked.connect(self._process)

        btn_row.addWidget(b_img)
        btn_row.addSpacing(8)
        btn_row.addWidget(b_pdf)
        btn_row.addSpacing(16)
        btn_row.addWidget(b_run)
        btn_row.addStretch()
        grp_lay.addLayout(btn_row)

        form_lay.addWidget(grp)

        self.output = OutputArea()
        sp = _make_splitter(_left_panel(form), _right_panel(self.output))
        root.addWidget(sp)

    def _load_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecione imagem", "",
            "Imagens (*.png *.jpg *.jpeg *.bmp);;Todos (*)"
        )
        if path:
            self.current_file = path
            self.preview.setText(f"✓  {os.path.basename(path)}")
            self.preview.setStyleSheet(
                f"background: {C['bg']}; border: 1px solid {C['green']}; border-radius: 8px;"
                f"color: {C['green']}; font-size: 12px;"
            )

    def _load_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Selecione PDF", "", "PDF (*.pdf);;Todos (*)")
        if path:
            self.current_file = path
            self.preview.setText(f"✓  {os.path.basename(path)}")
            self.preview.setStyleSheet(
                f"background: {C['bg']}; border: 1px solid {C['green']}; border-radius: 8px;"
                f"color: {C['green']}; font-size: 12px;"
            )

    def _process(self):
        if not self.current_file:
            QMessageBox.warning(self, "Aviso", "Carregue um arquivo primeiro.")
            return

        self.output.clear()
        self.output.write(_header("OCR  ·  RESOLUÇÃO AUTOMÁTICA"))
        ext = os.path.splitext(self.current_file)[1].lower()
        self.output.write("  Extraindo texto...\n\n")

        if ext in ('.png', '.jpg', '.jpeg', '.bmp'):
            text = self._ocr_image(self.current_file)
        elif ext == '.pdf':
            text = self._read_pdf(self.current_file)
        else:
            text = "✗ Formato não suportado."

        self.output.write(text + "\n\n")

        if not text.startswith("✗"):
            self.output.write("─" * 68 + "\n")
            self.output.write("  Analisando parâmetros e resolvendo...\n\n")
            params = self._parse(text)
            self.output.write(self._solve(params, text) + "\n")

    def _ocr_image(self, path):
        if not (PILLOW_AVAILABLE and TESSERACT_AVAILABLE):
            return "✗ OCR não disponível. Instale: pip install pytesseract pillow"
        try:
            img = Image.open(path).convert("L")
            return pytesseract.image_to_string(img, lang="por+eng")
        except Exception as e:
            return f"✗ Erro OCR: {e}"

    def _read_pdf(self, path):
        if not PDF_AVAILABLE:
            return "✗ PyMuPDF não disponível. Instale: pip install PyMuPDF"
        try:
            doc = fitz.open(path)
            out = ""
            for i, pg in enumerate(doc, 1):
                t = pg.get_text()
                if t.strip():
                    out += f"[p.{i}]\n{t}\n"
            return out or "✗ Nenhum texto extraído do PDF."
        except Exception as e:
            return f"✗ Erro PDF: {e}"

    def _parse(self, text):
        t = text.lower()
        params = {"lam": None, "mi": None, "s": 1, "k": None, "n": None}
        patterns = {
            "lam": [r"λ\s*=\s*([\d,\.]+)", r"lambda\s*=\s*([\d,\.]+)", r"taxa de chegada\s*[:=]\s*([\d,\.]+)"],
            "mi":  [r"μ\s*=\s*([\d,\.]+)", r"mi\s*=\s*([\d,\.]+)", r"taxa de atendimento\s*[:=]\s*([\d,\.]+)"],
            "s":   [r"servidores?\s*[:=]\s*(\d+)", r"\bs\s*=\s*(\d+)", r"canais?\s*[:=]\s*(\d+)"],
            "k":   [r"capacidade\s*[:=]\s*(\d+)", r"\bk\s*=\s*(\d+)"],
            "n":   [r"popula[cç][aã]o\s*[:=]\s*(\d+)", r"\bn\s*=\s*(\d+)"],
        }
        for key, pats in patterns.items():
            for pat in pats:
                m = re.search(pat, t)
                if m:
                    v = m.group(1).replace(",", ".")
                    params[key] = int(float(v)) if key in ("s", "k", "n") else float(v)
                    break
        return params

    def _solve(self, p, original):
        lines = []
        if p["lam"] and p["mi"]:
            lam, mi, s = p["lam"], p["mi"], p["s"]
            rho = lam / (s * mi)
            lines.append(f"  λ = {lam},  μ = {mi},  s = {s}")
            lines.append(f"  ρ = {rho:.4f}  ({rho*100:.2f}%)\n")
            if rho >= 1:
                lines.append("  ⚠  Sistema instável (ρ ≥ 1)")
                return "\n".join(lines)
            if not MODELS_AVAILABLE:
                lines.append("  ✗ Modelos não disponíveis para cálculo completo.")
                return "\n".join(lines)
            try:
                modelo = Mm(lam=lam, mi=mi, s=s)
                res = _capture(modelo.resultado)
                lines.append(res)
            except Exception as e:
                lines.append(f"  ✗ Erro: {e}")
        else:
            lines.append("  ✗ Parâmetros insuficientes (precisa de λ e μ).\n")
            lines.append("  Texto extraído (prévia):\n  " + original[:600].replace("\n", "\n  "))
        return "\n".join(lines)


# ── Lista de Exercícios ───────────────────────────────────────────────────────

class ExercisesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        form = QWidget()
        form_lay = QVBoxLayout(form)
        form_lay.setContentsMargins(0, 0, 0, 0)
        form_lay.setSpacing(20)

        grp = QGroupBox("LISTA DE EXERCÍCIOS")
        grp_lay = QVBoxLayout(grp)
        grp_lay.setSpacing(16)

        info = QLabel(
            "Executa todos os testes definidos em  ListaExercicios.py.\n\n"
            "Certifique-se de que o arquivo está na mesma pasta do programa."
        )
        info.setStyleSheet(f"color: {C['text2']}; font-size: 12px;")
        info.setWordWrap(True)
        grp_lay.addWidget(info)

        btn = QPushButton("▶   RODAR TODOS OS EXERCÍCIOS")
        btn.setObjectName("success")
        btn.clicked.connect(self._run)
        grp_lay.addWidget(btn, alignment=Qt.AlignLeft)

        form_lay.addWidget(grp)

        self.output = OutputArea()
        sp = _make_splitter(_left_panel(form), _right_panel(self.output))
        root.addWidget(sp)

    def _run(self):
        if not MODELS_AVAILABLE:
            self.output.write("✗ Módulos não disponíveis.\n"); return

        self.output.clear()
        self.output.write(_header("LISTA DE EXERCÍCIOS"))

        class _Redirect:
            def __init__(self, out): self.out = out
            def write(self, t): self.out.write(t)
            def flush(self): pass

        old = sys.stdout
        sys.stdout = _Redirect(self.output)
        try:
            rodar_testes()
        except Exception as e:
            self.output.write(f"\n✗ Erro: {e}\n")
        finally:
            sys.stdout = old


# ─── Janela Principal ─────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Teoria das Filas")
        self.resize(1360, 940)
        self.setMinimumSize(1100, 780)
        self.setStyleSheet(STYLE)

        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(Header())

        # Notebook
        tabs = QTabWidget()
        tabs.setDocumentMode(True)

        tabs.addTab(MmsTab(),       "M/M/s")
        tabs.addTab(Mg1Tab(),       "M/G/1")
        tabs.addTab(PriorityTab(),  "Prioridades")
        tabs.addTab(FiniteTab(),    "Filas Finitas")
        tabs.addTab(OCRTab(),       "OCR Solver")
        tabs.addTab(ExercisesTab(), "Lista")

        wrap = QWidget()
        wrap.setStyleSheet(f"background: {C['bg']};")
        wl = QVBoxLayout(wrap)
        wl.setContentsMargins(16, 12, 16, 12)
        wl.addWidget(tabs)

        layout.addWidget(wrap, 1)
        layout.addWidget(Footer())


# ─── Entrypoint ──────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Teoria das Filas")

    # Centralizar
    win = MainWindow()
    screen = app.primaryScreen().geometry()
    x = (screen.width()  - win.width())  // 2
    y = (screen.height() - win.height()) // 2
    win.move(x, y)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
