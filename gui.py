"""
GUI Module for PDF to Markdown Converter Desktop Application
Built with PyQt6, featuring Multi-File Batch Selection, Drag & Drop, Image Preservation, and Split-View Live Preview.
"""

import sys
import os
from typing import Optional, List, Dict
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QMimeData, QSettings
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QSplitter, QPlainTextEdit,
    QTextBrowser, QCheckBox, QFrame, QStatusBar, QMessageBox,
    QProgressBar, QStackedWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)
from PyQt6.QtGui import QFont, QIcon, QColor, QDragEnterEvent, QDropEvent, QClipboard

import markdown
from converter_engine import PDFToMarkdownConverter

# Modern Dark Theme Stylesheet (QSS)
DARK_STYLE_SHEET = """
QMainWindow {
    background-color: #0F172A;
}

QWidget {
    color: #F8FAFC;
    font-family: 'Segoe UI', Inter, Roboto, sans-serif;
    font-size: 13px;
}

/* Header */
#HeaderFrame {
    background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
    border-bottom: 1px solid #334155;
    padding: 16px;
}

#AppTitle {
    font-size: 20px;
    font-weight: 700;
    color: #F8FAFC;
}

#AppSubtitle {
    font-size: 12px;
    color: #94A3B8;
}

/* Drop Zone */
#DropZone {
    background-color: #1E293B;
    border: 2px dashed #475569;
    border-radius: 12px;
    padding: 20px;
    min-height: 90px;
}

#DropZone[dragHover="true"] {
    background-color: #2D3748;
    border-color: #6366F1;
}

#DropZone[hasFile="true"] {
    background-color: #0F172A;
    border: 2px solid #10B981;
}

#DropZoneTitle {
    font-size: 15px;
    font-weight: 600;
    color: #E2E8F0;
}

#DropZoneHint {
    font-size: 12px;
    color: #94A3B8;
}

/* Control Toolbar */
#ControlFrame {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 10px;
}

QPushButton {
    background-color: #334155;
    color: #F8FAFC;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 8px 14px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #475569;
    border-color: #64748B;
}

QPushButton:pressed {
    background-color: #1E293B;
}

QPushButton#PrimaryBtn {
    background-color: #6366F1;
    color: #FFFFFF;
    border: none;
}

QPushButton#PrimaryBtn:hover {
    background-color: #4F46E5;
}

QPushButton#PrimaryBtn:disabled {
    background-color: #333878;
    color: #64748B;
}

QPushButton#SuccessBtn {
    background-color: #10B981;
    color: #FFFFFF;
    border: none;
}

QPushButton#SuccessBtn:hover {
    background-color: #059669;
}

QCheckBox {
    color: #CBD5E1;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #64748B;
    background-color: #0F172A;
}

QCheckBox::indicator:checked {
    background-color: #6366F1;
    border-color: #6366F1;
}

/* Table Widget for Batch View */
QTableWidget {
    background-color: #020617;
    border: 1px solid #334155;
    border-radius: 8px;
    gridline-color: #1E293B;
    color: #E2E8F0;
}

QTableWidget::item {
    padding: 8px;
}

QHeaderView::section {
    background-color: #1E293B;
    color: #F8FAFC;
    padding: 8px;
    font-weight: 600;
    border: none;
    border-bottom: 2px solid #334155;
}

/* Editors and Splitter */
QSplitter::handle {
    background-color: #334155;
    width: 3px;
    margin: 2px;
}

QSplitter::handle:hover {
    background-color: #6366F1;
}

QPlainTextEdit, QTextBrowser {
    background-color: #020617;
    color: #E2E8F0;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 12px;
    font-family: 'JetBrains Mono', 'Consolas', 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.5;
}

QPlainTextEdit:focus, QTextBrowser:focus {
    border-color: #6366F1;
}

QStatusBar {
    background-color: #0F172A;
    border-top: 1px solid #334155;
    color: #94A3B8;
}

QProgressBar {
    border: 1px solid #334155;
    border-radius: 4px;
    text-align: center;
    background-color: #0F172A;
    color: #F8FAFC;
    max-height: 14px;
}

QProgressBar::chunk {
    background-color: #6366F1;
    border-radius: 3px;
}
"""

# Rendered HTML CSS inside QTextBrowser
RENDERED_HTML_STYLE = """
<style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #E2E8F0;
        background-color: #020617;
        line-height: 1.6;
        padding: 10px;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #F8FAFC;
        margin-top: 1.2em;
        margin-bottom: 0.5em;
        font-weight: 700;
        border-bottom: 1px solid #334155;
        padding-bottom: 0.3em;
    }
    h1 { font-size: 1.8em; color: #818CF8; }
    h2 { font-size: 1.4em; color: #A5B4FC; }
    h3 { font-size: 1.2em; color: #C7D2FE; }
    p { margin-bottom: 1em; }
    a { color: #38BDF8; text-decoration: none; }
    img {
        max-width: 100%;
        height: auto;
        border-radius: 8px;
        border: 1px solid #334155;
        margin: 12px 0;
    }
    code {
        font-family: 'Consolas', 'Courier New', monospace;
        background-color: #1E293B;
        color: #F472B6;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.9em;
    }
    pre {
        background-color: #0F172A;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 12px;
        overflow-x: auto;
    }
    pre code {
        background-color: transparent;
        color: #E2E8F0;
        padding: 0;
    }
    blockquote {
        border-left: 4px solid #6366F1;
        margin: 0;
        padding-left: 12px;
        color: #94A3B8;
        font-style: italic;
    }
    ul, ol { padding-left: 20px; margin-bottom: 1em; }
    li { margin-bottom: 0.3em; }
    hr {
        border: none;
        border-top: 2px dashed #475569;
        margin: 2em 0;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        margin-bottom: 1em;
    }
    th, td {
        border: 1px solid #334155;
        padding: 8px 12px;
        text-align: left;
    }
    th {
        background-color: #1E293B;
        color: #F8FAFC;
    }
</style>
"""


class SingleConversionWorker(QThread):
    """Worker thread to run single PDF conversion."""
    finished_signal = pyqtSignal(str, dict)
    error_signal = pyqtSignal(str)

    def __init__(self, file_path: str, include_page_breaks: bool, extract_images: bool):
        super().__init__()
        self.file_path = file_path
        self.include_page_breaks = include_page_breaks
        self.extract_images = extract_images
        self.converter = PDFToMarkdownConverter()

    def run(self):
        try:
            base_dir = os.path.dirname(self.file_path)
            base_name = os.path.splitext(os.path.basename(self.file_path))[0]
            img_dir = os.path.join(base_dir, f"{base_name}_images") if self.extract_images else None

            md_text, meta = self.converter.convert_to_markdown(
                self.file_path,
                include_page_breaks=self.include_page_breaks,
                extract_images=self.extract_images,
                image_output_dir=img_dir
            )
            self.finished_signal.emit(md_text, meta)
        except Exception as e:
            self.error_signal.emit(str(e))


class BatchConversionWorker(QThread):
    """Worker thread for batch processing multiple PDF files."""
    file_started = pyqtSignal(int, str)
    file_finished = pyqtSignal(int, str, str)  # index, status, output_path
    batch_completed = pyqtSignal(int, int)  # successful, total

    def __init__(self, file_paths: List[str], output_dir: str, include_page_breaks: bool, extract_images: bool):
        super().__init__()
        self.file_paths = file_paths
        self.output_dir = output_dir
        self.include_page_breaks = include_page_breaks
        self.extract_images = extract_images
        self.converter = PDFToMarkdownConverter()

    def run(self):
        successful = 0
        total = len(self.file_paths)

        for index, file_path in enumerate(self.file_paths):
            self.file_started.emit(index, os.path.basename(file_path))
            try:
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                out_md_path = os.path.join(self.output_dir, f"{base_name}.md")
                img_dir = os.path.join(self.output_dir, f"{base_name}_images") if self.extract_images else None

                md_text, meta = self.converter.convert_to_markdown(
                    file_path,
                    include_page_breaks=self.include_page_breaks,
                    extract_images=self.extract_images,
                    image_output_dir=img_dir
                )

                with open(out_md_path, "w", encoding="utf-8") as f:
                    f.write(md_text)

                successful += 1
                self.file_finished.emit(index, "✅ Completado", out_md_path)
            except Exception as e:
                self.file_finished.emit(index, f"❌ Error: {str(e)[:40]}", "")

        self.batch_completed.emit(successful, total)


class DropZoneWidget(QFrame):
    """Custom Drag and Drop Frame Widget supporting multiple files."""
    files_dropped_signal = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DropZone")
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(4)

        self.icon_label = QLabel("📥", self)
        self.icon_label.setStyleSheet("font-size: 28px;")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title_label = QLabel("Arrastra tus archivos PDF aquí (Soporta selección múltiple)", self)
        self.title_label.setObjectName("DropZoneTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.hint_label = QLabel("o haz clic para seleccionar uno o varios archivos de tu equipo", self)
        self.hint_label.setObjectName("DropZoneHint")
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.title_label)
        layout.addWidget(self.hint_label)

        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            initial_dir = ""
            main_win = self.window()
            if main_win and hasattr(main_win, "get_last_directory"):
                initial_dir = main_win.get_last_directory("pdf")
            files, _ = QFileDialog.getOpenFileNames(
                self,
                "Seleccionar archivo(s)",
                initial_dir,
                "Archivos soportados (*.pdf *.txt *.md *.json *.py *.csv *.log *.html);;PDF (*.pdf);;Todos (*.*)"
            )
            if files:
                self.files_dropped_signal.emit(files)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setProperty("dragHover", True)
            self.style().unpolish(self)
            self.style().polish(self)

    def dragLeaveEvent(self, event):
        self.setProperty("dragHover", False)
        self.style().unpolish(self)
        self.style().polish(self)

    def dropEvent(self, event: QDropEvent):
        self.setProperty("dragHover", False)
        urls = event.mimeData().urls()
        if urls:
            file_paths = [u.toLocalFile() for u in urls if os.path.exists(u.toLocalFile())]
            if file_paths:
                self.files_dropped_signal.emit(file_paths)
        self.style().unpolish(self)
        self.style().polish(self)

    def update_single_file_info(self, file_name: str, file_size: str, page_count: int):
        self.setProperty("hasFile", True)
        self.style().unpolish(self)
        self.style().polish(self)
        self.icon_label.setText("📄")
        self.title_label.setText(f"Archivo adjuntado: {file_name}")
        self.hint_label.setText(f"Tamaño: {file_size} | Páginas: {page_count} (Clic para cambiar)")

    def update_batch_info(self, file_count: int):
        self.setProperty("hasFile", True)
        self.style().unpolish(self)
        self.style().polish(self)
        self.icon_label.setText("📚")
        self.title_label.setText(f"Modo Lote Activo: {file_count} archivos seleccionados")
        self.hint_label.setText("Verás el listado de archivos en la tabla a continuación. Haz clic en 'Convertir Todos'")

    def reset_zone(self):
        self.setProperty("hasFile", False)
        self.style().unpolish(self)
        self.style().polish(self)
        self.icon_label.setText("📥")
        self.title_label.setText("Arrastra tus archivos PDF aquí (Soporta selección múltiple)")
        self.hint_label.setText("o haz clic para seleccionar uno o varios archivos de tu equipo")


class MainWindow(QMainWindow):
    """Main Application Window with Single & Multi-File Batch Modes."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF to Markdown Converter (.md)")
        self.resize(1150, 780)

        self.settings = QSettings("Antigravity", "PDFToMarkdownConverter")
        self.selected_files: List[str] = []
        self.current_markdown: str = ""
        self.single_worker: Optional[SingleConversionWorker] = None
        self.batch_worker: Optional[BatchConversionWorker] = None

        self._init_ui()

    def get_last_directory(self, category: str = "general") -> str:
        key = f"last_{category}_dir"
        default_dir = os.path.expanduser("~")
        val = self.settings.value(key, None)
        if not val:
            val = self.settings.value("last_general_dir", default_dir)
        val_str = str(val)
        return val_str if os.path.isdir(val_str) else default_dir

    def set_last_directory(self, path: str, category: str = "general"):
        if not path:
            return
        dir_path = path if os.path.isdir(path) else os.path.dirname(path)
        if os.path.isdir(dir_path):
            self.settings.setValue(f"last_{category}_dir", dir_path)
            self.settings.setValue("last_general_dir", dir_path)

    def _init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # 1. Header
        header_frame = QFrame()
        header_frame.setObjectName("HeaderFrame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_box = QVBoxLayout()
        app_title = QLabel("📄 Conversor de PDF a Markdown (.md) - Un Archivo o Múltiples")
        app_title.setObjectName("AppTitle")
        app_sub = QLabel("Convierte archivos individuales con vista previa en vivo o múltiples PDF en lote con conservación de imágenes")
        app_sub.setObjectName("AppSubtitle")
        title_box.addWidget(app_title)
        title_box.addWidget(app_sub)

        header_layout.addLayout(title_box)
        header_layout.addStretch()

        main_layout.addWidget(header_frame)

        # 2. Drag & Drop Zone
        self.drop_zone = DropZoneWidget(self)
        self.drop_zone.files_dropped_signal.connect(self.on_files_selected)
        main_layout.addWidget(self.drop_zone)

        # 3. Control Toolbar
        control_frame = QFrame()
        control_frame.setObjectName("ControlFrame")
        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(8, 6, 8, 6)

        self.btn_select = QPushButton("📂 Seleccionar Archivo(s)")
        self.btn_select.clicked.connect(self.open_files_dialog)

        self.btn_open_md = QPushButton("📝 Abrir .md")
        self.btn_open_md.clicked.connect(self.open_md_file_dialog)

        self.btn_convert = QPushButton("⚡ Convertir a .md", objectName="PrimaryBtn")
        self.btn_convert.clicked.connect(self.start_conversion)
        self.btn_convert.setEnabled(False)

        saved_chk_page = self.settings.value("include_page_breaks", True, type=bool)
        self.chk_page_breaks = QCheckBox("Marcadores (---)")
        self.chk_page_breaks.setChecked(saved_chk_page)
        self.chk_page_breaks.stateChanged.connect(lambda s: self.settings.setValue("include_page_breaks", bool(s)))

        saved_chk_img = self.settings.value("extract_images", True, type=bool)
        self.chk_extract_images = QCheckBox("🖼️ Extraer Imágenes")
        self.chk_extract_images.setChecked(saved_chk_img)
        self.chk_extract_images.stateChanged.connect(lambda s: self.settings.setValue("extract_images", bool(s)))

        self.btn_copy = QPushButton("📋 Copiar Markdown")
        self.btn_copy.clicked.connect(self.copy_markdown)
        self.btn_copy.setEnabled(False)

        self.btn_save = QPushButton("💾 Guardar .md", objectName="SuccessBtn")
        self.btn_save.clicked.connect(self.save_markdown_file)
        self.btn_save.setEnabled(False)

        self.btn_clear = QPushButton("🗑️ Limpiar")
        self.btn_clear.clicked.connect(self.clear_all)

        control_layout.addWidget(self.btn_select)
        control_layout.addWidget(self.btn_open_md)
        control_layout.addWidget(self.btn_convert)
        control_layout.addWidget(self.chk_page_breaks)
        control_layout.addWidget(self.chk_extract_images)
        control_layout.addStretch()
        control_layout.addWidget(self.btn_copy)
        control_layout.addWidget(self.btn_save)
        control_layout.addWidget(self.btn_clear)

        main_layout.addWidget(control_frame)

        # 4. Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # 5. Stacked Widget (Mode 0: Single Split View | Mode 1: Multi-File Batch Table View)
        self.view_stack = QStackedWidget()

        # View 0: Single File Splitter View
        self.splitter_view = QSplitter(Qt.Orientation.Horizontal)

        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        lbl_editor = QLabel("✏️ Código Fuente Markdown (Editable):")
        lbl_editor.setStyleSheet("font-weight: 600; color: #CBD5E1;")
        self.text_editor = QPlainTextEdit()
        self.text_editor.setPlaceholderText("El texto en formato Markdown aparecerá aquí...")
        self.text_editor.textChanged.connect(self.on_markdown_edited)
        editor_layout.addWidget(lbl_editor)
        editor_layout.addWidget(self.text_editor)

        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        lbl_preview = QLabel("👁️ Vista Previa Renderizada (HTML + Imágenes):")
        lbl_preview.setStyleSheet("font-weight: 600; color: #CBD5E1;")
        self.preview_browser = QTextBrowser()
        preview_layout.addWidget(lbl_preview)
        preview_layout.addWidget(self.preview_browser)

        self.splitter_view.addWidget(editor_container)
        self.splitter_view.addWidget(preview_container)
        self.splitter_view.setSizes([575, 575])

        # View 1: Multi-File Batch Table View
        self.batch_table_widget = QWidget()
        batch_layout = QVBoxLayout(self.batch_table_widget)
        batch_layout.setContentsMargins(0, 0, 0, 0)

        lbl_batch_header = QLabel("📚 Listado de Archivos para Conversión en Lote:")
        lbl_batch_header.setStyleSheet("font-weight: 600; font-size: 14px; color: #CBD5E1;")

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["📄 Archivo", "📏 Tamaño", "📑 Páginas", "📊 Estado", "📁 Salida"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        batch_layout.addWidget(lbl_batch_header)
        batch_layout.addWidget(self.table)

        self.view_stack.addWidget(self.splitter_view)      # Index 0
        self.view_stack.addWidget(self.batch_table_widget) # Index 1

        main_layout.addWidget(self.view_stack, stretch=1)

        # 6. Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo. Selecciona o arrastra uno o varios archivos PDF para comenzar.")

    def open_files_dialog(self):
        initial_dir = self.get_last_directory("pdf")
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleccionar archivo(s) PDF o Documento(s)",
            initial_dir,
            "Archivos soportados (*.pdf *.txt *.md *.json *.py *.csv *.log *.html);;PDF (*.pdf);;Todos (*.*)"
        )
        if files:
            self.on_files_selected(files)

    def open_md_file_dialog(self):
        initial_dir = self.get_last_directory("md")
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir archivo Markdown (.md)",
            initial_dir,
            "Archivos Markdown (*.md *.markdown *.txt);;Todos (*.*)"
        )
        if file_path:
            self.on_files_selected([file_path])

    def on_files_selected(self, files: List[str]):
        if not files:
            return

        self.selected_files = files
        first_file = files[0]
        self.set_last_directory(first_file, "pdf" if first_file.lower().endswith(".pdf") else "md")

        converter = PDFToMarkdownConverter()

        if len(files) == 1:
            # Mode 0: Single File View
            self.view_stack.setCurrentIndex(0)
            self.btn_copy.setVisible(True)
            self.btn_save.setVisible(True)

            try:
                info = converter.get_file_info(first_file)
                self.drop_zone.update_single_file_info(
                    info["filename"],
                    info["size_human"],
                    info["page_count"]
                )
                self.btn_convert.setText("⚡ Convertir a .md")
                self.btn_convert.setEnabled(True)
                self.status_bar.showMessage(f"Archivo listo: {info['filename']} ({info['size_human']}). Haz clic en 'Convertir'")
                self.start_conversion()
            except Exception as e:
                QMessageBox.critical(self, "Error de Archivo", f"No se pudo analizar el archivo:\n{str(e)}")
        else:
            # Mode 1: Multi-File Batch Table View
            self.view_stack.setCurrentIndex(1)
            self.btn_copy.setVisible(False)
            self.btn_save.setVisible(False)

            self.drop_zone.update_batch_info(len(files))
            self.btn_convert.setText(f"⚡ Convertir ({len(files)} Archivos)")
            self.btn_convert.setEnabled(True)

            # Populate table
            self.table.setRowCount(len(files))
            for i, fpath in enumerate(files):
                fname = os.path.basename(fpath)
                try:
                    info = converter.get_file_info(fpath)
                    fsize = info["size_human"]
                    pages = str(info["page_count"])
                except Exception:
                    fsize = "Error"
                    pages = "-"

                self.table.setItem(i, 0, QTableWidgetItem(f"📄 {fname}"))
                self.table.setItem(i, 1, QTableWidgetItem(fsize))
                self.table.setItem(i, 2, QTableWidgetItem(pages))
                self.table.setItem(i, 3, QTableWidgetItem("⏳ Pendiente"))
                self.table.setItem(i, 4, QTableWidgetItem(os.path.dirname(fpath)))

            self.status_bar.showMessage(f"Modo Lote: {len(files)} archivos cargados en la lista. Haz clic en 'Convertir ({len(files)} Archivos)'")

    def start_conversion(self):
        if not self.selected_files:
            return

        extract_imgs = self.chk_extract_images.isChecked()
        page_breaks = self.chk_page_breaks.isChecked()

        if len(self.selected_files) == 1:
            # Single file conversion
            file_path = self.selected_files[0]
            self.btn_convert.setEnabled(False)
            self.progress_bar.setRange(0, 0)  # indeterminate
            self.progress_bar.setVisible(True)
            self.status_bar.showMessage("Procesando y convirtiendo archivo a Markdown...")

            self.single_worker = SingleConversionWorker(
                file_path,
                include_page_breaks=page_breaks,
                extract_images=extract_imgs
            )
            self.single_worker.finished_signal.connect(self.on_single_success)
            self.single_worker.error_signal.connect(self.on_single_error)
            self.single_worker.start()
        else:
            # Multi-file batch conversion
            output_dir = QFileDialog.getExistingDirectory(
                self,
                "Seleccionar Carpeta de Destino para Guardar los Archivos .md",
                self.get_last_directory("save")
            )
            if not output_dir:
                return

            self.set_last_directory(output_dir, "save")
            self.btn_convert.setEnabled(False)
            self.progress_bar.setRange(0, len(self.selected_files))
            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(True)
            self.status_bar.showMessage(f"Iniciando conversión en lote de {len(self.selected_files)} archivos...")

            self.batch_worker = BatchConversionWorker(
                self.selected_files,
                output_dir,
                include_page_breaks=page_breaks,
                extract_images=extract_imgs
            )
            self.batch_worker.file_started.connect(self.on_batch_file_started)
            self.batch_worker.file_finished.connect(self.on_batch_file_finished)
            self.batch_worker.batch_completed.connect(self.on_batch_completed)
            self.batch_worker.start()

    def on_single_success(self, md_text: str, meta: dict):
        self.progress_bar.setVisible(False)
        self.btn_convert.setEnabled(True)
        self.current_markdown = md_text

        self.text_editor.blockSignals(True)
        self.text_editor.setPlainText(md_text)
        self.text_editor.blockSignals(False)

        self.render_html_preview(md_text)

        self.btn_copy.setEnabled(True)
        self.btn_save.setEnabled(True)

        lines = md_text.count("\n") + 1
        chars = len(md_text)
        self.status_bar.showMessage(
            f"✅ Conversión completada. {lines} líneas | {chars} caracteres extraídos."
        )

    def on_single_error(self, err_msg: str):
        self.progress_bar.setVisible(False)
        self.btn_convert.setEnabled(True)
        QMessageBox.critical(self, "Error de Conversión", f"Ocurrió un error al convertir:\n{err_msg}")
        self.status_bar.showMessage("Error durante la conversión.")

    def on_batch_file_started(self, index: int, filename: str):
        self.table.setItem(index, 3, QTableWidgetItem("⚡ Convirtiendo..."))
        self.status_bar.showMessage(f"Convirtiendo [{index+1}/{len(self.selected_files)}]: {filename}")

    def on_batch_file_finished(self, index: int, status: str, out_path: str):
        self.table.setItem(index, 3, QTableWidgetItem(status))
        if out_path:
            self.table.setItem(index, 4, QTableWidgetItem(out_path))
        self.progress_bar.setValue(index + 1)

    def on_batch_completed(self, successful: int, total: int):
        self.progress_bar.setVisible(False)
        self.btn_convert.setEnabled(True)
        QMessageBox.information(
            self,
            "Conversión en Lote Completada",
            f"Se han convertido exitosamente {successful} de {total} archivos en formato Markdown (.md)."
        )
        self.status_bar.showMessage(f"🎉 Conversión en lote completada: {successful}/{total} archivos guardados con éxito.")

    def on_markdown_edited(self):
        if self.view_stack.currentIndex() == 0:
            md_text = self.text_editor.toPlainText()
            self.current_markdown = md_text
            self.render_html_preview(md_text)
            enabled = len(md_text.strip()) > 0
            self.btn_copy.setEnabled(enabled)
            self.btn_save.setEnabled(enabled)

    def render_html_preview(self, md_text: str):
        try:
            html_body = markdown.markdown(
                md_text,
                extensions=['extra', 'codehilite', 'tables', 'fenced_code', 'toc']
            )
            full_html = f"{RENDERED_HTML_STYLE}\n<body>{html_body}</body>"
            self.preview_browser.setHtml(full_html)
        except Exception as e:
            self.preview_browser.setPlainText(f"Error al renderizar vista previa: {str(e)}")

    def copy_markdown(self):
        if not self.current_markdown:
            return
        clipboard = QApplication.clipboard()
        clipboard.setText(self.current_markdown)
        self.status_bar.showMessage("📋 ¡Markdown copiado exitosamente al portapapeles!")

    def save_markdown_file(self):
        if not self.current_markdown:
            return

        default_name = "documento.md"
        if self.selected_files:
            base = os.path.splitext(os.path.basename(self.selected_files[0]))[0]
            default_name = f"{base}.md"

        last_save_dir = self.get_last_directory("save")
        initial_path = os.path.join(last_save_dir, default_name)

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar archivo Markdown",
            initial_path,
            "Archivo Markdown (*.md);;Texto (*.txt)"
        )

        if save_path:
            try:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(self.current_markdown)
                self.set_last_directory(save_path, "save")
                QMessageBox.information(
                    self,
                    "Archivo Guardado",
                    f"El archivo Markdown ha sido guardado en:\n{save_path}"
                )
                self.status_bar.showMessage(f"💾 Archivo guardado en: {save_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error al guardar", f"No se pudo guardar el archivo:\n{str(e)}")

    def clear_all(self):
        self.selected_files = []
        self.current_markdown = ""
        self.drop_zone.reset_zone()
        self.text_editor.clear()
        self.preview_browser.clear()
        self.table.setRowCount(0)
        self.view_stack.setCurrentIndex(0)
        self.btn_convert.setText("⚡ Convertir a .md")
        self.btn_convert.setEnabled(False)
        self.btn_copy.setEnabled(False)
        self.btn_save.setEnabled(False)
        self.btn_copy.setVisible(True)
        self.btn_save.setVisible(True)
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Listo. Selecciona o arrastra uno o varios archivos PDF para comenzar.")


def run_app():
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE_SHEET)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_app()
