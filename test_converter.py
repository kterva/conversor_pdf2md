"""
Unit & Integration Test Script for PDFToMarkdownConverter
Generates a sample PDF file and tests markdown extraction.
"""

import os
import sys
import pymupdf as fitz  # PyMuPDF
from converter_engine import PDFToMarkdownConverter


def create_sample_pdf(pdf_path: str):
    """Creates a sample PDF document for testing conversion."""
    doc = fitz.open()
    
    # Page 1
    page1 = doc.new_page()
    p1_text = """Guía de Inicio Rápido: Conversor PDF a Markdown

1. Introducción
Este es un documento de prueba en formato PDF diseñado para verificar el motor de conversión a Markdown (.md).

2. Características Principales
- Detección de títulos y subtítulos
- Formato de listas con viñetas
- Extracción de bloques de texto y párrafos
- Separación elegante de páginas mediante el símbolo ---

Código de Ejemplo en Python:
def saludar(nombre):
    print(f"Hola {nombre}")
"""
    page1.insert_text((50, 50), p1_text, fontsize=12)

    # Page 2
    page2 = doc.new_page()
    p2_text = """3. Especificaciones Técnicas

- Soporte de múltiples plataformas (Linux, macOS, Windows)
- Motor gráfico nativo con PyQt6
- Exportación instantánea a archivo .md

Conclusión
La conversión se realiza de forma local y segura en tu equipo.
"""
    page2.insert_text((50, 50), p2_text, fontsize=12)

    doc.save(pdf_path)
    doc.close()
    print(f"[TEST] PDF de prueba creado exitosamente en: {pdf_path}")


def run_test():
    """Runs automated test on PDFToMarkdownConverter."""
    sample_pdf = "/home/leo/.gemini/antigravity/scratch/pdf-to-md-desktop/test_sample.pdf"
    create_sample_pdf(sample_pdf)

    converter = PDFToMarkdownConverter()
    
    # Test file info
    info = converter.get_file_info(sample_pdf)
    print(f"[TEST] Info del archivo: {info}")
    assert info["page_count"] == 2, f"Se esperaban 2 páginas, pero se obtuvieron {info['page_count']}"

    # Test conversion
    md_result, meta = converter.convert_to_markdown(sample_pdf, include_page_breaks=True)
    print("\n--- CONTENIDO MARKDOWN EXTRAÍDO ---")
    print(md_result)
    print("-----------------------------------\n")

    assert len(md_result) > 50, "El resultado de la conversión está vacío o es demasiado corto"
    assert "Guía de Inicio Rápido" in md_result, "No se encontró el título principal en el Markdown"
    
    print("[SUCCESS] ¡Todas las pruebas automáticas del motor pasaron con éxito!")

    # Clean up test pdf
    if os.path.exists(sample_pdf):
        os.remove(sample_pdf)


if __name__ == "__main__":
    run_test()
