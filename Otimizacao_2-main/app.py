"""Calculadora - Teoria das Filas | Interface PySide6 — Redesign v3 (Dashboard)."""
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
    QIcon, QTextCursor, QFontDatabase, QGradient, QPen, QBrush
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
    "bg":        "#0A0E14",
    "surface":   "#10151F",
    "surface2":  "#1A2230",
    "surface3":  "#212B3D",
    "border":    "#26303F",
    "border2":   "#3A4659",
    "accent":    "#58A6FF",
    "accent2":   "#1F6FEB",
    "cyan":      "#39D9D9",
    "lime":      "#7EE787",
    "gold":      "#E3B341",
    "green":     "#3FB950",
    "green_dk":  "#238636",
    "yellow":    "#D29922",
    "red":       "#F85149",
    "purple":    "#BC8CFF",
    "text":      "#E6EDF3",
    "text2":     "#8B949E",
    "text3":     "#56616F",
    "header_bg": "#05070C",
}

# ─── Stylesheet global ───────────────────────────────────────────────────────
STYLE = f"""
QMainWindow, QWidget {{
    background-color: {C['bg']};
    color: {C['text']};
    font-family: 'JetBrains Mono', 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
}}

/* ── Abas ───────────────────────────────────────────────────────────────── */
QTabWidget::pane {{
    background: {C['surface']};
    border: 1px solid {C['border']};
    border-radius: 10px;
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
    padding: 11px 24px;
    margin-right: 3px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.4px;
}}

QTabBar::tab:selected {{
    background: {C['surface']};
    color: {C['accent']};
    border-color: {C['accent2']};
    border-bottom: 3px solid {C['accent']};
}}

QTabBar::tab:hover:!selected {{
    background: {C['surface3']};
    color: {C['text']};
}}

/* ── Campos de entrada ──────────────────────────────────────────────────── */
QFrame#field_card {{
    background: {C['bg']};
    border: 1px solid {C['border']};
    border-radius: 8px;
}}

QFrame#field_card:hover {{
    border: 1px solid {C['border2']};
}}

QLineEdit#field_input {{
    background: transparent;
    color: {C['text']};
    border: none;
    border-radius: 0px;
    padding: 11px 12px;
    font-size: 13px;
    selection-background-color: {C['accent2']};
}}

QLineEdit#field_input:focus {{
    color: {C['accent']};
}}

QLabel#unit_pill {{
    color: {C['text2']};
    background: {C['surface2']};
    border-left: 1px solid {C['border']};
    border-top-right-radius: 7px;
    border-bottom-right-radius: 7px;
    padding: 11px 12px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.5px;
}}

/* QLineEdit padrão (campos sem unidade / OCR / prioridades) */
QLineEdit {{
    background: {C['bg']};
    color: {C['text']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    padding: 11px 14px;
    font-size: 13px;
    selection-background-color: {C['accent2']};
}}

QLineEdit:focus {{
    border: 1px solid {C['accent']};
    background: #0C1320;
}}

QLineEdit:hover {{
    border: 1px solid {C['border2']};
}}

QTextEdit {{
    background: {C['bg']};
    color: {C['text']};
    border: 1px solid {C['border']};
    border-radius: 10px;
    padding: 14px;
    font-size: 13px;
    line-height: 1.6;
    selection-background-color: {C['accent2']};
}}

QTextEdit:focus {{
    border: 1px solid {C['border2']};
}}

/* ── Botões ──────────────────────────────────────────────────────────────── */
QPushButton {{
    background: {C['surface2']};
    color: {C['text']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 12px;
    font-weight: 700;
}}

QPushButton:hover {{
    background: {C['surface3']};
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
        stop:0 #46D17A, stop:1 #238636);
    color: #03150A;
    border: 1px solid {C['green_dk']};
    padding: 13px 38px;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0.8px;
}}

QPushButton#success:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #5BE38F, stop:1 #2EA043);
    color: #03150A;
}}

QPushButton#danger {{
    background: {C['surface2']};
    color: {C['red']};
    border: 1px solid {C['red']};
}}

QPushButton#danger:hover {{
    background: rgba(248, 81, 73, 0.15);
}}

/* ── Pílulas de navegação no header ────────────────────────────────────── */
QPushButton#nav_pill {{
    background: transparent;
    color: {C['text2']};
    border: 1px solid {C['border']};
    border-radius: 14px;
    padding: 6px 16px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.8px;
}}

QPushButton#nav_pill:hover {{
    border-color: {C['accent']};
    color: {C['text']};
}}

QPushButton#nav_pill:checked {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #1F6FEB, stop:1 #58A6FF);
    color: #04101F;
    border-color: {C['accent']};
}}

/* ── Radio ───────────────────────────────────────────────────────────────── */
QRadioButton {{
    color: {C['text2']};
    font-size: 12px;
    font-weight: 600;
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

/* ── Scrollbar ───────────────────────────────────────────────────────────── */
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

/* ── Labels e títulos ───────────────────────────────────────────────────── */
QLabel#section_title {{
    color: {C['text2']};
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.6px;
    text-transform: uppercase;
    padding-bottom: 4px;
}}

QLabel#field_label {{
    color: {C['text2']};
    font-size: 11px;
    font-weight: 600;
    padding-bottom: 2px;
}}

QLabel#sub_section {{
    color: {C['text3']};
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 2px 0px 2px 2px;
}}

QGroupBox {{
    color: {C['text2']};
    border: 1px solid {C['border']};
    border-radius: 10px;
    margin-top: 10px;
    padding-top: 16px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 8px;
    color: {C['accent']};
    background: {C['surface']};
}}

/* ── Dashboard de resultados ────────────────────────────────────────────── */
QFrame#metric_card {{
    background: {C['surface2']};
    border: 1px solid {C['border']};
    border-radius: 10px;
}}

QFrame#metric_card:hover {{
    border-color: {C['accent2']};
}}

QFrame#prob_bar {{
    background: {C['surface2']};
    border: 1px solid {C['border']};
    border-radius: 10px;
}}

QFrame#notes_card {{
    background: {C['bg']};
    border: 1px solid {C['border']};
    border-radius: 10px;
}}

QFrame#hero_card {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {C['surface2']}, stop:1 {C['surface3']});
    border: 1px solid {C['accent2']};
    border-radius: 12px;
}}

QFrame#banner_error {{
    background: rgba(248, 81, 73, 0.10);
    border: 1px solid {C['red']};
    border-radius: 8px;
}}

QFrame#banner_warn {{
    background: rgba(210, 153, 34, 0.10);
    border: 1px solid {C['yellow']};
    border-radius: 8px;
}}

QFrame#banner_ok {{
    background: rgba(63, 185, 80, 0.10);
    border: 1px solid {C['green']};
    border-radius: 8px;
}}

QSplitter::handle:horizontal {{
    width: 5px;
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


# ─── Campo de entrada (card) ──────────────────────────────────────────────────

class FieldEntry(QWidget):
    """Campo de entrada em formato de card: rótulo acima + caixa fechada
    com placeholder e unidade integrada à direita."""

    def __init__(self, label: str, default: str = "", unit: str = "",
                 icon: str = "", placeholder: str = "", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        lbl_text = f"{icon}  {label}" if icon else label
        lbl = make_label(lbl_text)
        layout.addWidget(lbl)

        card = QFrame()
        card.setObjectName("field_card")
        row = QHBoxLayout(card)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        self.entry = QLineEdit(default)
        self.entry.setObjectName("field_input")
        if placeholder:
            self.entry.setPlaceholderText(placeholder)
        row.addWidget(self.entry, 1)

        if unit:
            u = QLabel(unit)
            u.setObjectName("unit_pill")
            row.addWidget(u, 0, Qt.AlignVCenter)

        layout.addWidget(card)

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


# ─── Widgets do dashboard de resultados ───────────────────────────────────────

class MetricCard(QFrame):
    """Cartão de valor (value box) para uma métrica numérica."""

    def __init__(self, label: str, value: str, unit: str = "",
                 accent: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("metric_card")
        self.setMinimumHeight(78)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(6)

        lbl = QLabel(label.upper())
        lbl.setWordWrap(True)
        lbl.setStyleSheet(
            f"color:{C['text2']}; font-size:10px; font-weight:800;"
            f"letter-spacing:1.2px; background:transparent;"
        )
        lay.addWidget(lbl)

        row = QHBoxLayout()
        row.setSpacing(6)

        color = accent or C["accent"]
        val = QLabel(value)
        val.setStyleSheet(
            f"color:{color}; font-size:23px; font-weight:800; background:transparent;"
        )
        row.addWidget(val)

        if unit:
            u = QLabel(unit)
            u.setWordWrap(True)
            u.setAlignment(Qt.AlignBottom)
            u.setStyleSheet(
                f"color:{C['text3']}; font-size:10px; font-weight:700;"
                f"padding-bottom:4px; background:transparent;"
            )
            row.addWidget(u)

        row.addStretch()
        lay.addLayout(row)


class ProbabilityBar(QFrame):
    """Barra de progresso linear para representar uma probabilidade."""

    def __init__(self, label: str, pct: float, extra: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("prob_bar")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(8)

        top = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"color:{C['text']}; font-size:12px; font-weight:700; background:transparent;"
        )
        top.addWidget(lbl)
        top.addStretch()

        pct_clamped = max(0.0, min(100.0, pct))
        color = C["cyan"] if pct_clamped < 70 else (C["gold"] if pct_clamped < 90 else C["red"])

        val = QLabel(f"{pct:.2f}%")
        val.setStyleSheet(
            f"color:{color}; font-size:14px; font-weight:800; background:transparent;"
        )
        top.addWidget(val)
        lay.addLayout(top)

        track = QFrame()
        track.setFixedHeight(10)
        track.setStyleSheet(f"background:{C['bg']}; border-radius:5px;")
        track_lay = QHBoxLayout(track)
        track_lay.setContentsMargins(0, 0, 0, 0)
        track_lay.setSpacing(0)

        fill_w = max(1, int(round(pct_clamped * 10)))
        rest_w = max(0, 1000 - fill_w)

        fill = QFrame()
        fill.setStyleSheet(f"background:{color}; border-radius:5px;")
        track_lay.addWidget(fill, fill_w)

        if rest_w:
            spacer = QFrame()
            spacer.setStyleSheet("background:transparent;")
            track_lay.addWidget(spacer, rest_w)

        lay.addWidget(track)

        if extra:
            ex = QLabel(extra)
            ex.setWordWrap(True)
            ex.setStyleSheet(f"color:{C['text3']}; font-size:10px; background:transparent;")
            lay.addWidget(ex)


class CircularGauge(QFrame):
    """Gauge circular (donut) — usado para destacar a taxa de utilização (ρ)."""

    def __init__(self, label: str, value: float, parent=None):
        super().__init__(parent)
        self.setObjectName("hero_card")
        self._value = max(0.0, min(1.0, value))

        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(20)

        self.canvas = _GaugeCanvas(self._value)
        self.canvas.setFixedSize(110, 110)
        lay.addWidget(self.canvas)

        texts = QVBoxLayout()
        texts.setSpacing(6)
        title = QLabel("UTILIZAÇÃO DO SISTEMA")
        title.setStyleSheet(
            f"color:{C['text2']}; font-size:10px; font-weight:800;"
            f"letter-spacing:1.6px; background:transparent;"
        )
        texts.addWidget(title)

        big = QLabel(f"{self._value*100:.2f}%")
        color = C["green"] if self._value < 0.7 else (C["gold"] if self._value < 0.9 else C["red"])
        big.setStyleSheet(
            f"color:{color}; font-size:30px; font-weight:800; background:transparent;"
        )
        texts.addWidget(big)

        sub = QLabel(label)
        sub.setWordWrap(True)
        sub.setStyleSheet(f"color:{C['text3']}; font-size:11px; background:transparent;")
        texts.addWidget(sub)

        texts.addStretch()
        lay.addLayout(texts, 1)


class _GaugeCanvas(QWidget):
    """Canvas auxiliar que desenha o arco do gauge circular."""

    def __init__(self, value: float, parent=None):
        super().__init__(parent)
        self._value = value

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(8, 8, -8, -8)

        pen_bg = QPen(QColor(C["border"]))
        pen_bg.setWidth(10)
        pen_bg.setCapStyle(Qt.RoundCap)
        painter.setPen(pen_bg)
        painter.drawArc(rect, 0, 360 * 16)

        color = C["green"] if self._value < 0.7 else (C["gold"] if self._value < 0.9 else C["red"])
        pen_fg = QPen(QColor(color))
        pen_fg.setWidth(10)
        pen_fg.setCapStyle(Qt.RoundCap)
        painter.setPen(pen_fg)

        span = int(360 * self._value * 16)
        painter.drawArc(rect, 90 * 16, -span)


class Banner(QFrame):
    """Faixa de aviso (erro / atenção / sucesso)."""

    def __init__(self, text: str, kind: str = "error", parent=None):
        super().__init__(parent)
        names = {"error": "banner_error", "warn": "banner_warn", "ok": "banner_ok"}
        colors = {"error": C["red"], "warn": C["yellow"], "ok": C["green"]}
        self.setObjectName(names.get(kind, "banner_error"))

        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)

        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setStyleSheet(
            f"color:{colors.get(kind, C['red'])}; font-size:12px; font-weight:700; background:transparent;"
        )
        lay.addWidget(lbl)


# ─── Dashboard de resultados ──────────────────────────────────────────────────

_LABEL_VALUE_RE = re.compile(
    r"^\s*([^=:\n]{1,48}?)\s*[=:]\s*"
    r"(-?\d+(?:[.,]\d+)?(?:[eE][-+]?\d+)?)\s*(.*)$"
)
_LABEL_VALUE_SPACED_RE = re.compile(
    r"^\s*(.{1,48}?)\s{2,}"
    r"(-?\d+(?:[.,]\d+)?(?:[eE][-+]?\d+)?)\s*(.*)$"
)
_PCT_RE = re.compile(r"\(?\s*(-?\d+(?:[.,]\d+)?)\s*%\s*\)?")
_HEADER_BAR_RE = re.compile(r"^[═─\-—\s]*$")
_RHO_RE = re.compile(r"(?i)\b(ρ|rho|utiliza)")


class ResultsDashboard(QWidget):
    """Painel de resultados em formato de dashboard: cartões de métricas,
    barras de probabilidade, gauge de utilização e notas/avisos."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._raw_text = ""

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(10)

        bar = QHBoxLayout()
        bar.setSpacing(6)
        title = make_label("RESULTADOS", "section_title")
        bar.addWidget(title)
        bar.addStretch()

        self.copy_btn = QPushButton("⎘  Copiar")
        self.copy_btn.setObjectName("primary")
        self.copy_btn.setFixedHeight(30)
        self.copy_btn.clicked.connect(self._copy)
        bar.addWidget(self.copy_btn)

        self.clear_btn = QPushButton("🗑  Limpar")
        self.clear_btn.setObjectName("danger")
        self.clear_btn.setFixedHeight(30)
        self.clear_btn.clicked.connect(self.clear)
        bar.addWidget(self.clear_btn)

        outer.addLayout(bar)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("background: transparent; border: none;")

        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.vlay = QVBoxLayout(self.container)
        self.vlay.setContentsMargins(4, 4, 4, 4)
        self.vlay.setSpacing(12)

        self.scroll.setWidget(self.container)
        outer.addWidget(self.scroll, 1)

        self.render()

    # ── API compatível com o OutputArea anterior ──────────────────────────
    def write(self, content: str):
        self._raw_text += content
        self.render()

    def set_text(self, content: str):
        self._raw_text = content
        self.render()

    def clear(self):
        self._raw_text = ""
        self.render()

    def _copy(self):
        txt = self._raw_text.strip()
        if txt:
            QApplication.clipboard().setText(txt)
            self.copy_btn.setText("✓  Copiado!")
            QTimer.singleShot(2000, lambda: self.copy_btn.setText("⎘  Copiar"))

    # ── Renderização ───────────────────────────────────────────────────────
    def _clear_layout(self):
        while self.vlay.count():
            item = self.vlay.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
            else:
                lay = item.layout()
                if lay is not None:
                    while lay.count():
                        sub = lay.takeAt(0)
                        sw = sub.widget()
                        if sw is not None:
                            sw.deleteLater()

    def render(self):
        self._clear_layout()

        text = self._raw_text
        if not text.strip():
            placeholder = QLabel("Os resultados aparecerão aqui após o cálculo.\n\nPreencha os parâmetros e pressione  ▶  CALCULAR.")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setWordWrap(True)
            placeholder.setStyleSheet(f"color:{C['text3']}; font-size:12px; padding:80px 20px;")
            self.vlay.addWidget(placeholder)
            self.vlay.addStretch()
            return

        lines = text.splitlines()

        # ── pré-varredura: gauge de utilização (ρ) em destaque ──────────
        hero_index = None
        for line in lines:
            stripped = line.strip()
            m = _LABEL_VALUE_RE.match(stripped) or _LABEL_VALUE_SPACED_RE.match(stripped)
            if m and _RHO_RE.search(m.group(1)):
                try:
                    raw_val = float(m.group(2).replace(",", "."))
                except ValueError:
                    continue
                if 0.0 <= raw_val <= 1.0:
                    self.vlay.addWidget(CircularGauge(m.group(1).strip(), raw_val))
                    hero_index = id(line)
                    break

        cards_buffer = []
        notes_buffer = []
        rho_used = hero_index is not None

        def flush_cards():
            if not cards_buffer:
                return
            grid = QGridLayout()
            grid.setSpacing(12)
            cols = 3
            for i, w in enumerate(cards_buffer):
                grid.addWidget(w, i // cols, i % cols)
            wrap = QWidget()
            wrap.setStyleSheet("background: transparent;")
            wrap.setLayout(grid)
            self.vlay.addWidget(wrap)
            cards_buffer.clear()

        def flush_notes():
            if not notes_buffer:
                return
            box = QFrame()
            box.setObjectName("notes_card")
            lay = QVBoxLayout(box)
            lay.setContentsMargins(16, 12, 16, 12)
            lbl = QLabel("\n".join(notes_buffer))
            lbl.setWordWrap(True)
            lbl.setStyleSheet(
                f"color:{C['text2']}; font-size:12px; "
                f"font-family:'JetBrains Mono','Consolas',monospace; background:transparent;"
            )
            lay.addWidget(lbl)
            self.vlay.addWidget(box)
            notes_buffer.clear()

        for raw_line in lines:
            line = raw_line.rstrip()
            stripped = line.strip()

            if not stripped or _HEADER_BAR_RE.match(stripped):
                continue

            # ── faixas de status ────────────────────────────────────────
            if stripped.startswith("✗"):
                flush_cards(); flush_notes()
                self.vlay.addWidget(Banner(stripped.lstrip("✗ ").strip(), "error"))
                continue
            if stripped.startswith("⚠"):
                flush_cards(); flush_notes()
                self.vlay.addWidget(Banner(stripped.lstrip("⚠ ").strip(), "warn"))
                continue
            if stripped.startswith("✓"):
                flush_cards(); flush_notes()
                self.vlay.addWidget(Banner(stripped.lstrip("✓ ").strip(), "ok"))
                continue

            # ── títulos de seção ─────────────────────────────────────────
            is_section = (
                stripped.startswith("──")
                or stripped.startswith("MODELO")
                or (stripped.isupper() and len(stripped) > 2)
            )
            if is_section:
                flush_cards(); flush_notes()
                title_txt = stripped.strip("─ ").strip()
                lbl = QLabel(title_txt)
                lbl.setStyleSheet(
                    f"color:{C['accent']}; font-size:13px; font-weight:800;"
                    f"letter-spacing:1.4px; padding-top:8px; background:transparent;"
                )
                self.vlay.addWidget(lbl)
                self.vlay.addWidget(divider())
                continue

            # ── tentativa de "label = valor (resto)" ──────────────────────
            m = _LABEL_VALUE_RE.match(stripped) or _LABEL_VALUE_SPACED_RE.match(stripped)
            if m and "=" not in m.group(3) and ":" not in m.group(3):
                label, value, rest = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()

                pct_m = _PCT_RE.search(rest)
                if pct_m:
                    try:
                        pct = float(pct_m.group(1).replace(",", "."))
                        flush_cards()
                        self.vlay.addWidget(ProbabilityBar(label, pct, f"valor exato: {value}"))
                        continue
                    except ValueError:
                        pass

                if _RHO_RE.search(label) and not rho_used:
                    try:
                        raw_val = float(value.replace(",", "."))
                        if 0.0 <= raw_val <= 1.0:
                            flush_cards()
                            self.vlay.addWidget(CircularGauge(label, raw_val))
                            rho_used = True
                            continue
                    except ValueError:
                        pass

                accent = C["accent"]
                if _RHO_RE.search(label):
                    accent = C["gold"]
                elif "p(" in label.lower() or label.lower().startswith("p"):
                    accent = C["cyan"]

                cards_buffer.append(MetricCard(label, value, rest, accent))
                continue

            # ── fallback: nota / texto livre ──────────────────────────────
            flush_cards()
            notes_buffer.append(stripped)

        flush_cards()
        flush_notes()
        self.vlay.addStretch()


# ─── Cabeçalho ────────────────────────────────────────────────────────────────

class Header(QWidget):
    tabRequested = Signal(int)

    def __init__(self, tab_names, parent=None):
        super().__init__(parent)
        self.setFixedHeight(92)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(32, 0, 32, 0)
        layout.setSpacing(24)

        # ── Lado esquerdo: ícone + textos ────────────────────────────
        left = QHBoxLayout()
        left.setSpacing(16)

        icon_lbl = QLabel("∑")
        icon_lbl.setFixedSize(46, 46)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            "stop:0 #1F6FEB, stop:1 #58A6FF);"
            "border-radius: 23px;"
            "color: white;"
            "font-size: 21px;"
            "font-weight: 900;"
        )
        left.addWidget(icon_lbl)

        texts = QVBoxLayout()
        texts.setSpacing(3)

        title = QLabel("TEORIA DAS FILAS")
        title.setStyleSheet(
            "color: #E6EDF3; font-size: 20px; font-weight: 800;"
            "letter-spacing: 1px; background: transparent;"
        )
        texts.addWidget(title)

        sub = QLabel("Calculadora de Desempenho  ·  Modelos Estocásticos")
        sub.setStyleSheet(
            "color: #8B949E; font-size: 11px; letter-spacing: 0.5px; background: transparent;"
        )
        texts.addWidget(sub)

        left.addLayout(texts)
        layout.addLayout(left)

        # ── Centro: pílulas de navegação ──────────────────────────────
        nav = QHBoxLayout()
        nav.setSpacing(8)
        nav.addStretch()

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        self.nav_buttons = []

        for i, name in enumerate(tab_names):
            btn = QPushButton(name.upper())
            btn.setObjectName("nav_pill")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            if i == 0:
                btn.setChecked(True)
            self.nav_group.addButton(btn, i)
            nav.addWidget(btn)
            self.nav_buttons.append(btn)

        nav.addStretch()
        layout.addLayout(nav, 1)

        self.nav_group.idClicked.connect(self.tabRequested.emit)

        # ── Lado direito: badge de versão ──────────────────────────────
        badge = QLabel("v3.0")
        badge.setStyleSheet(
            "background: #1A2230; color: #8B949E; border: 1px solid #26303F;"
            "border-radius: 10px; padding: 5px 14px; font-size: 10px; font-weight: 800;"
            "letter-spacing: 1px;"
        )
        layout.addWidget(badge, 0, Qt.AlignVCenter)

    def set_active(self, index: int):
        if 0 <= index < len(self.nav_buttons):
            self.nav_buttons[index].setChecked(True)

    def paintEvent(self, event):
        """Fundo com gradiente sutil + linha accent inferior."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        grad = QLinearGradient(0, 0, self.width(), 0)
        grad.setColorAt(0.0, QColor("#070A11"))
        grad.setColorAt(0.4, QColor("#0A0E14"))
        grad.setColorAt(1.0, QColor("#070A11"))
        painter.fillRect(self.rect(), grad)

        painter.setPen(QColor(C["border"]))
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)

        accent_grad = QLinearGradient(0, 0, self.width(), 0)
        accent_grad.setColorAt(0.0, QColor("#1F6FEB"))
        accent_grad.setColorAt(0.5, QColor("#58A6FF"))
        accent_grad.setColorAt(1.0, QColor("#BC8CFF"))
        painter.setPen(Qt.NoPen)
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

        hint = QLabel("Dashboard de Resultados em tempo real")
        hint.setStyleSheet(f"color: {C['text3']}; font-size: 10px;")
        layout.addWidget(hint)


# ─── Funções auxiliares de saída ──────────────────────────────────────────────

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


# ─── Painéis (entrada / saída) ────────────────────────────────────────────────

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


def _right_panel(output: "ResultsDashboard") -> QWidget:
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


def _calc_button() -> QPushButton:
    btn = QPushButton("▶   CALCULAR")
    btn.setObjectName("success")
    btn.setCursor(Qt.PointingHandCursor)
    return btn


# ── M/M/s ─────────────────────────────────────────────────────────────────────

class MmsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        form = QWidget()
        form_lay = QVBoxLayout(form)
        form_lay.setContentsMargins(0, 0, 0, 0)
        form_lay.setSpacing(20)

        grp = QGroupBox("PARÂMETROS  ·  M/M/s")
        grp_lay = QVBoxLayout(grp)
        grp_lay.setSpacing(14)

        grp_lay.addWidget(make_label("TAXAS DO SISTEMA", "sub_section"))
        grid1 = QGridLayout()
        grid1.setSpacing(14)
        self.lam = FieldEntry("Taxa de Chegada (λ)", "1.0", "clientes/h", icon="📈")
        self.mi  = FieldEntry("Taxa de Atendimento (μ)", "2.0", "clientes/h", icon="⚙️")
        grid1.addWidget(self.lam, 0, 0)
        grid1.addWidget(self.mi, 0, 1)
        grp_lay.addLayout(grid1)

        grp_lay.addWidget(divider())
        grp_lay.addWidget(make_label("CONFIGURAÇÃO DO CENÁRIO", "sub_section"))
        grid2 = QGridLayout()
        grid2.setSpacing(14)
        self.s = FieldEntry("Servidores (s)", "1", icon="🖥️")
        self.t = FieldEntry("Tempo t", "60", "min", icon="⏱️")
        self.n = FieldEntry("Clientes n  ·  P(N=n)", "5", icon="👥")
        grid2.addWidget(self.s, 0, 0)
        grid2.addWidget(self.t, 0, 1)
        grid2.addWidget(self.n, 0, 2)
        grp_lay.addLayout(grid2)

        btn = _calc_button()
        btn.clicked.connect(self._calc)
        grp_lay.addSpacing(6)
        grp_lay.addWidget(btn, alignment=Qt.AlignLeft)

        form_lay.addWidget(grp)

        self.output = ResultsDashboard()
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
            self.output.set_text("✗ Módulos de modelos não disponíveis.\n")
            return

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
        grp_lay.setSpacing(14)

        grp_lay.addWidget(make_label("TAXAS DO SISTEMA", "sub_section"))
        grid1 = QGridLayout()
        grid1.setSpacing(14)
        self.lam = FieldEntry("Taxa de Chegada (λ)", "8.0", "clientes/h", icon="📈")
        self.mi  = FieldEntry("Taxa de Atendimento (μ)", "10.0", "clientes/h", icon="⚙️")
        grid1.addWidget(self.lam, 0, 0)
        grid1.addWidget(self.mi, 0, 1)
        grp_lay.addLayout(grid1)

        grp_lay.addWidget(divider())
        grp_lay.addWidget(make_label("VARIABILIDADE DO SERVIÇO", "sub_section"))
        self.var = FieldEntry("Variância do Serviço (σ²)", "0.005", icon="📊")
        grp_lay.addWidget(self.var)

        btn = _calc_button()
        btn.clicked.connect(self._calc)
        grp_lay.addSpacing(6)
        grp_lay.addWidget(btn, alignment=Qt.AlignLeft)

        form_lay.addWidget(grp)

        self.output = ResultsDashboard()
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
            self.output.set_text("✗ Módulos não disponíveis.\n")
            return

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

        grp_lay.addWidget(make_label("TAXAS DE CHEGADA POR CLASSE", "sub_section"))
        lam_card = QFrame()
        lam_card.setObjectName("field_card")
        lam_lay = QHBoxLayout(lam_card)
        lam_lay.setContentsMargins(0, 0, 0, 0)
        self.lambdas = QLineEdit("1.5, 2.0, 0.5")
        self.lambdas.setObjectName("field_input")
        self.lambdas.setPlaceholderText("λ₁, λ₂, λ₃, …")
        lam_lay.addWidget(self.lambdas, 1)
        unit = QLabel("clientes/h")
        unit.setObjectName("unit_pill")
        lam_lay.addWidget(unit)
        grp_lay.addWidget(lam_card)

        grp_lay.addWidget(divider())
        grp_lay.addWidget(make_label("ATENDIMENTO E CAPACIDADE", "sub_section"))
        grid = QGridLayout()
        grid.setSpacing(14)
        self.mi = FieldEntry("Taxa de Atendimento (μ)", "4.0", "clientes/h", icon="⚙️")
        self.s  = FieldEntry("Servidores (s)", "2", icon="🖥️")
        grid.addWidget(self.mi, 0, 0)
        grid.addWidget(self.s, 0, 1)
        grp_lay.addLayout(grid)

        grp_lay.addWidget(divider())
        grp_lay.addWidget(make_label("TIPO DE DISCIPLINA", "sub_section"))
        type_row = QHBoxLayout()
        self.rg_preempt = QButtonGroup(self)
        self.rb_no  = QRadioButton("⏸  Sem Interrupção")
        self.rb_yes = QRadioButton("⏯  Com Interrupção")
        self.rb_no.setChecked(True)
        self.rg_preempt.addButton(self.rb_no, 0)
        self.rg_preempt.addButton(self.rb_yes, 1)
        type_row.addWidget(self.rb_no)
        type_row.addSpacing(20)
        type_row.addWidget(self.rb_yes)
        type_row.addStretch()
        grp_lay.addLayout(type_row)

        btn = _calc_button()
        btn.clicked.connect(self._calc)
        grp_lay.addSpacing(6)
        grp_lay.addWidget(btn, alignment=Qt.AlignLeft)

        form_lay.addWidget(grp)

        self.output = ResultsDashboard()
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
            self.output.set_text("✗ Módulos não disponíveis.\n")
            return

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
                    self.output.write(f"✗ {vals}\n")
                    return
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

        grp_lay.addWidget(make_label("TIPO DE MODELO", "sub_section"))
        type_row = QHBoxLayout()
        self.rg_type = QButtonGroup(self)
        self.rb_k = QRadioButton("📦  Capacidade Finita (K)")
        self.rb_n = QRadioButton("👥  População Finita (N)")
        self.rb_k.setChecked(True)
        self.rg_type.addButton(self.rb_k, 0)
        self.rg_type.addButton(self.rb_n, 1)
        type_row.addWidget(self.rb_k)
        type_row.addSpacing(20)
        type_row.addWidget(self.rb_n)
        type_row.addStretch()
        grp_lay.addLayout(type_row)

        grp_lay.addWidget(divider())

        grp_lay.addWidget(make_label("TAXAS DO SISTEMA", "sub_section"))
        grid1 = QGridLayout()
        grid1.setSpacing(14)
        self.lam = FieldEntry("Taxa de Chegada (λ)", "1.0", "clientes/h", icon="📈")
        self.mi  = FieldEntry("Taxa de Atendimento (μ)", "2.0", "clientes/h", icon="⚙️")
        grid1.addWidget(self.lam, 0, 0)
        grid1.addWidget(self.mi, 0, 1)
        grp_lay.addLayout(grid1)

        grp_lay.addWidget(make_label("CONFIGURAÇÃO DO CENÁRIO", "sub_section"))
        grid2 = QGridLayout()
        grid2.setSpacing(14)
        self.s     = FieldEntry("Servidores (s)", "1", icon="🖥️")
        self.limit = FieldEntry("Limite (K ou N)", "10", icon="🔢")
        grid2.addWidget(self.s, 0, 0)
        grid2.addWidget(self.limit, 0, 1)
        grp_lay.addLayout(grid2)

        btn = _calc_button()
        btn.clicked.connect(self._calc)
        grp_lay.addSpacing(6)
        grp_lay.addWidget(btn, alignment=Qt.AlignLeft)

        form_lay.addWidget(grp)

        self.output = ResultsDashboard()
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
            self.output.set_text("✗ Módulos não disponíveis.\n")
            return

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

        self.preview = QLabel("📥  Nenhum arquivo carregado\nAceita: PNG · JPG · BMP · PDF")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setFixedHeight(140)
        self.preview.setStyleSheet(
            f"background: {C['bg']}; border: 2px dashed {C['border2']}; border-radius: 10px;"
            f"color: {C['text3']}; font-size: 12px; font-weight: 600;"
        )
        grp_lay.addWidget(self.preview)

        btn_row = QHBoxLayout()
        b_img = QPushButton("🖼   Imagem")
        b_img.setObjectName("primary")
        b_img.clicked.connect(self._load_image)

        b_pdf = QPushButton("📄   PDF")
        b_pdf.setObjectName("primary")
        b_pdf.clicked.connect(self._load_pdf)

        btn_row.addWidget(b_img)
        btn_row.addSpacing(8)
        btn_row.addWidget(b_pdf)
        btn_row.addStretch()
        grp_lay.addLayout(btn_row)

        grp_lay.addWidget(divider())

        b_run = _calc_button()
        b_run.setText("🔍   PROCESSAR E RESOLVER")
        b_run.clicked.connect(self._process)
        grp_lay.addWidget(b_run, alignment=Qt.AlignLeft)

        form_lay.addWidget(grp)

        self.output = ResultsDashboard()
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
                f"background: {C['bg']}; border: 2px solid {C['green']}; border-radius: 10px;"
                f"color: {C['green']}; font-size: 12px; font-weight: 700;"
            )

    def _load_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Selecione PDF", "", "PDF (*.pdf);;Todos (*)")
        if path:
            self.current_file = path
            self.preview.setText(f"✓  {os.path.basename(path)}")
            self.preview.setStyleSheet(
                f"background: {C['bg']}; border: 2px solid {C['green']}; border-radius: 10px;"
                f"color: {C['green']}; font-size: 12px; font-weight: 700;"
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
            self.output.write("── TEXTO EXTRAÍDO ──\n")
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
            lines.append(f"  Lambda (λ) = {lam}")
            lines.append(f"  Mi (μ)     = {mi}")
            lines.append(f"  Servidores = {s}")
            lines.append(f"  Rho (ρ)    = {rho:.4f}   ({rho*100:.2f}%)")
            if rho >= 1:
                lines.append("⚠ Sistema instável (ρ ≥ 1)")
                return "\n".join(lines)
            if not MODELS_AVAILABLE:
                lines.append("✗ Modelos não disponíveis para cálculo completo.")
                return "\n".join(lines)
            try:
                modelo = Mm(lam=lam, mi=mi, s=s)
                res = _capture(modelo.resultado)
                lines.append(res)
            except Exception as e:
                lines.append(f"✗ Erro: {e}")
        else:
            lines.append("✗ Parâmetros insuficientes (precisa de λ e μ).")
            lines.append("  Texto extraído (prévia):")
            lines.append("  " + original[:600].replace("\n", "\n  "))
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
        info.setStyleSheet(f"color: {C['text2']}; font-size: 12px; line-height: 1.6;")
        info.setWordWrap(True)
        grp_lay.addWidget(info)

        btn = _calc_button()
        btn.setText("▶   RODAR TODOS OS EXERCÍCIOS")
        btn.clicked.connect(self._run)
        grp_lay.addWidget(btn, alignment=Qt.AlignLeft)

        form_lay.addWidget(grp)

        self.output = ResultsDashboard()
        sp = _make_splitter(_left_panel(form), _right_panel(self.output))
        root.addWidget(sp)

    def _run(self):
        if not MODELS_AVAILABLE:
            self.output.set_text("✗ Módulos não disponíveis.\n")
            return

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
    TAB_NAMES = ["M/M/s", "M/G/1", "Prioridades", "Filas Finitas", "OCR Solver", "Lista"]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Teoria das Filas")
        self.resize(1400, 960)
        self.setMinimumSize(1100, 780)
        self.setStyleSheet(STYLE)

        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = Header(self.TAB_NAMES)
        layout.addWidget(header)

        # Notebook
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        self.tabs.addTab(MmsTab(),       "M/M/s")
        self.tabs.addTab(Mg1Tab(),       "M/G/1")
        self.tabs.addTab(PriorityTab(),  "Prioridades")
        self.tabs.addTab(FiniteTab(),    "Filas Finitas")
        self.tabs.addTab(OCRTab(),       "OCR Solver")
        self.tabs.addTab(ExercisesTab(), "Lista")

        wrap = QWidget()
        wrap.setStyleSheet(f"background: {C['bg']};")
        wl = QVBoxLayout(wrap)
        wl.setContentsMargins(16, 12, 16, 12)
        wl.addWidget(self.tabs)

        layout.addWidget(wrap, 1)
        layout.addWidget(Footer())

        # ── Sincroniza pílulas do header com as abas ────────────────────
        header.tabRequested.connect(self.tabs.setCurrentIndex)
        self.tabs.currentChanged.connect(header.set_active)


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
