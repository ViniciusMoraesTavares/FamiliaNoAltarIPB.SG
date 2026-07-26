import math

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPageLayout, QPageSize, QPen
from PySide6.QtPrintSupport import QPrintDialog, QPrinter, QPrintPreviewWidget
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.icon import get_app_icon


class NumerosImpressaoDialog(QDialog):
    def __init__(self, numeros, parent=None):
        super().__init__(parent)
        self.numeros = [int(n) for n in numeros]
        self.printer = QPrinter(QPrinter.HighResolution)
        self.printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        self.printer.setPageOrientation(QPageLayout.Orientation.Portrait)
        self._init_ui()
        self._aplicar_configuracoes()
        self._atualizar_resumo()
        self.preview.updatePreview()

    def _init_ui(self):
        self.setWindowTitle("Imprimir Números Não Sorteados")
        self.setModal(True)
        self.resize(1180, 820)
        try:
            icon = get_app_icon()
            if not icon.isNull():
                self.setWindowIcon(icon)
        except Exception:
            pass

        self.setStyleSheet("""
            QDialog {
                background-color: #F5F7F6;
            }
            QFrame#sidebar {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 18px;
            }
            QFrame#previewCard {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 18px;
            }
            QLabel#title {
                color: #1F2937;
                font-size: 24px;
                font-weight: 800;
            }
            QLabel#subtitle {
                color: #6B7280;
                font-size: 13px;
            }
            QLabel#sectionTitle {
                color: #374151;
                font-size: 13px;
                font-weight: 700;
            }
            QLabel#infoValue {
                color: #2c4b23;
                font-size: 14px;
                font-weight: 700;
            }
            QComboBox {
                min-height: 40px;
                padding: 0 12px;
                border: 1px solid #D1D5DB;
                border-radius: 10px;
                background-color: #FFFFFF;
                color: #111827;
                font-size: 14px;
            }
            QComboBox:hover {
                border-color: #9CA3AF;
            }
            QPushButton#primary {
                min-height: 42px;
                padding: 0 16px;
                background-color: #2c4b23;
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 700;
            }
            QPushButton#primary:hover {
                background-color: #243f1d;
            }
            QPushButton#secondary {
                min-height: 42px;
                padding: 0 16px;
                background-color: #FFFFFF;
                color: #374151;
                border: 1px solid #D1D5DB;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton#secondary:hover {
                background-color: #F9FAFB;
            }
            QLabel#badge {
                color: #2c4b23;
                background-color: #EDF5EA;
                border: 1px solid #D4E4CF;
                border-radius: 10px;
                padding: 8px 10px;
                font-size: 12px;
                font-weight: 700;
            }
        """)

        root = QHBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(320)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)
        sidebar_layout.setSpacing(16)

        title = QLabel("Impressão dos números")
        title.setObjectName("title")
        subtitle = QLabel(
            "Gera folhas com os números das famílias ainda não sorteadas, "
            "com espaçamento apropriado para recorte."
        )
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)
        sidebar_layout.addWidget(title)
        sidebar_layout.addWidget(subtitle)

        self.badge = QLabel("")
        self.badge.setObjectName("badge")
        self.badge.setWordWrap(True)
        sidebar_layout.addWidget(self.badge)

        self.formato_combo = self._criar_combo(
            "Formato da folha",
            [
                ("A4", QPageSize.PageSizeId.A4),
                ("Carta", QPageSize.PageSizeId.Letter),
            ],
            sidebar_layout,
        )
        self.orientacao_combo = self._criar_combo(
            "Orientação",
            [
                ("Retrato", QPageLayout.Orientation.Portrait),
                ("Paisagem", QPageLayout.Orientation.Landscape),
            ],
            sidebar_layout,
        )
        self.margem_combo = self._criar_combo(
            "Margem da folha",
            [
                ("Pequena", 8),
                ("Média", 10),
                ("Ampla", 12),
            ],
            sidebar_layout,
        )
        self.espacamento_combo = self._criar_combo(
            "Espaçamento para corte",
            [
                ("Médio", 8),
                ("Confortável", 10),
                ("Amplo", 12),
            ],
            sidebar_layout,
        )

        info_card = QFrame()
        info_card.setStyleSheet(
            "QFrame { background-color: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 14px; }"
        )
        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(14, 14, 14, 14)
        info_layout.setSpacing(8)
        info_title = QLabel("Resumo da impressão")
        info_title.setObjectName("sectionTitle")
        self.info_total = QLabel("")
        self.info_total.setObjectName("infoValue")
        self.info_grade = QLabel("")
        self.info_grade.setObjectName("infoValue")
        self.info_folhas = QLabel("")
        self.info_folhas.setObjectName("infoValue")
        info_layout.addWidget(info_title)
        info_layout.addWidget(self.info_total)
        info_layout.addWidget(self.info_grade)
        info_layout.addWidget(self.info_folhas)
        sidebar_layout.addWidget(info_card)

        sidebar_layout.addStretch(1)

        actions = QHBoxLayout()
        actions.setSpacing(10)
        btn_fechar = QPushButton("Fechar")
        btn_fechar.setObjectName("secondary")
        btn_fechar.clicked.connect(self.close)
        btn_imprimir = QPushButton("Imprimir")
        btn_imprimir.setObjectName("primary")
        btn_imprimir.clicked.connect(self._imprimir)
        actions.addWidget(btn_fechar)
        actions.addWidget(btn_imprimir)
        sidebar_layout.addLayout(actions)

        preview_card = QFrame()
        preview_card.setObjectName("previewCard")
        preview_layout = QVBoxLayout(preview_card)
        preview_layout.setContentsMargins(18, 18, 18, 18)
        preview_layout.setSpacing(12)
        preview_title = QLabel("Visualização")
        preview_title.setObjectName("sectionTitle")
        preview_layout.addWidget(preview_title)

        self.preview = QPrintPreviewWidget(self.printer, preview_card)
        self.preview.paintRequested.connect(self._renderizar_paginas)
        preview_layout.addWidget(self.preview, 1)

        root.addWidget(sidebar)
        root.addWidget(preview_card, 1)

        for combo in (
            self.formato_combo,
            self.orientacao_combo,
            self.margem_combo,
            self.espacamento_combo,
        ):
            combo.currentIndexChanged.connect(self._ao_mudar_configuracao)

    def _criar_combo(self, titulo, itens, layout_pai):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        label = QLabel(titulo)
        label.setObjectName("sectionTitle")
        combo = QComboBox()
        for texto, valor in itens:
            combo.addItem(texto, valor)
        layout.addWidget(label)
        layout.addWidget(combo)
        layout_pai.addWidget(container)
        return combo

    def _ao_mudar_configuracao(self):
        self._aplicar_configuracoes()
        self._atualizar_resumo()
        self.preview.updatePreview()

    def _aplicar_configuracoes(self):
        page_size = self.formato_combo.currentData()
        orientacao = self.orientacao_combo.currentData()
        self.printer.setPageSize(QPageSize(page_size))
        self.printer.setPageOrientation(orientacao)

    def _mm_para_px(self, printer, mm):
        return int((printer.resolution() * mm) / 25.4)

    def _layout_grade(self, printer):
        page_rect = printer.pageRect(QPrinter.Unit.DevicePixel)
        margem = self._mm_para_px(printer, int(self.margem_combo.currentData()))
        espacamento = self._mm_para_px(printer, int(self.espacamento_combo.currentData()))
        usable = page_rect.adjusted(margem, margem, -margem, -margem)

        min_largura = self._mm_para_px(printer, 42)
        min_altura = self._mm_para_px(printer, 34)

        largura = max(usable.width(), min_largura)
        altura = max(usable.height(), min_altura)

        colunas = max(1, (largura + espacamento) // max(min_largura + espacamento, 1))
        linhas = max(1, (altura + espacamento) // max(min_altura + espacamento, 1))

        cell_w = (usable.width() - ((colunas - 1) * espacamento)) / max(colunas, 1)
        cell_h = (usable.height() - ((linhas - 1) * espacamento)) / max(linhas, 1)

        return {
            "page_rect": page_rect,
            "usable_rect": usable,
            "margem": margem,
            "espacamento": espacamento,
            "colunas": int(colunas),
            "linhas": int(linhas),
            "cell_w": float(cell_w),
            "cell_h": float(cell_h),
            "por_folha": max(1, int(colunas) * int(linhas)),
        }

    def _atualizar_resumo(self):
        layout = self._layout_grade(self.printer)
        total = len(self.numeros)
        folhas = max(1, math.ceil(total / layout["por_folha"])) if total else 0
        self.badge.setText(f"{total} números prontos para impressão")
        self.info_total.setText(f"Total de números: {total}")
        self.info_grade.setText(
            f"Grade por folha: {layout['colunas']} colunas x {layout['linhas']} linhas"
        )
        self.info_folhas.setText(f"Folhas estimadas: {folhas}")

    def _renderizar_paginas(self, printer):
        painter = QPainter(printer)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            layout = self._layout_grade(printer)
            por_folha = layout["por_folha"]
            folhas = math.ceil(len(self.numeros) / por_folha) if self.numeros else 0

            for indice_folha in range(folhas):
                if indice_folha:
                    printer.newPage()

                inicio = indice_folha * por_folha
                fim = inicio + por_folha
                numeros_folha = self.numeros[inicio:fim]

                for indice, numero in enumerate(numeros_folha):
                    linha = indice // layout["colunas"]
                    coluna = indice % layout["colunas"]

                    x = layout["usable_rect"].x() + coluna * (layout["cell_w"] + layout["espacamento"])
                    y = layout["usable_rect"].y() + linha * (layout["cell_h"] + layout["espacamento"])
                    rect = QRectF(x, y, layout["cell_w"], layout["cell_h"])

                    pen = QPen(QColor("#9CA3AF"))
                    pen.setWidth(1)
                    pen.setStyle(Qt.PenStyle.DashLine)
                    painter.setPen(pen)
                    painter.drawRoundedRect(rect, 8, 8)

                    font = QFont("Segoe UI", 10)
                    font.setBold(True)
                    font.setPixelSize(max(34, int(min(layout["cell_h"] * 0.42, layout["cell_w"] * 0.55))))
                    painter.setFont(font)
                    painter.setPen(QColor("#000000"))
                    painter.drawText(rect, Qt.AlignCenter, str(numero))
        finally:
            painter.end()

    def _imprimir(self):
        dialog = QPrintDialog(self.printer, self)
        dialog.setWindowTitle("Imprimir números das famílias")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._renderizar_paginas(self.printer)
