"""
Converter Engine Module
Handles PDF extraction to Markdown (.md), text formatting, scientific notation cleanup, and image preservation.
"""

import os
import re
from typing import Dict, Any, Tuple, Optional
import pymupdf as fitz  # PyMuPDF


class PDFToMarkdownConverter:
    """Engine for converting PDF and text files into clean, beautiful Markdown with math & image support."""

    def __init__(self):
        pass

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Extract basic file metadata (size, extension, page count if PDF)."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_size = os.path.getsize(file_path)
        ext = os.path.splitext(file_path)[1].lower()
        info = {
            "path": file_path,
            "filename": os.path.basename(file_path),
            "size_bytes": file_size,
            "size_human": self._format_size(file_size),
            "extension": ext,
            "page_count": 1,
            "title": os.path.basename(file_path),
            "author": "Unknown",
        }

        if ext == ".pdf":
            try:
                doc = fitz.open(file_path)
                info["page_count"] = len(doc)
                metadata = doc.metadata or {}
                if metadata.get("title"):
                    info["title"] = metadata.get("title")
                if metadata.get("author"):
                    info["author"] = metadata.get("author")
                doc.close()
            except Exception as e:
                info["error"] = str(e)

        return info

    def convert_to_markdown(
        self,
        file_path: str,
        include_page_breaks: bool = True,
        clean_extra_newlines: bool = True,
        extract_images: bool = True,
        image_output_dir: Optional[str] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Converts input file (PDF, TXT, etc.) into clean Markdown string.
        Extracts embedded images and cleans scientific/mathematical notation.
        """
        info = self.get_file_info(file_path)
        ext = info["extension"]

        if ext == ".pdf":
            md_content = self._convert_pdf_enhanced(
                file_path,
                include_page_breaks=include_page_breaks,
                extract_images=extract_images,
                image_output_dir=image_output_dir
            )
        elif ext in [".txt", ".log", ".json", ".csv", ".html", ".py", ".md", ".js", ".css"]:
            md_content = self._convert_text_file(file_path, ext)
        else:
            md_content = self._convert_text_file(file_path, ext)

        if clean_extra_newlines:
            md_content = self._clean_newlines(md_content)

        return md_content, info

    def _convert_pdf_enhanced(
        self,
        file_path: str,
        include_page_breaks: bool,
        extract_images: bool,
        image_output_dir: Optional[str]
    ) -> str:
        """High-fidelity PDF to Markdown converter using PyMuPDF4LLM with bundled Tessdata."""
        import pymupdf4llm
        import os

        # Point Tesseract to local tessdata bundled with the app
        base_dir = os.path.dirname(os.path.abspath(__file__))
        tessdata_path = os.path.join(base_dir, "tessdata")
        os.environ["TESSDATA_PREFIX"] = tessdata_path

        if extract_images and image_output_dir:
            try:
                os.makedirs(image_output_dir, exist_ok=True)
                md_text = pymupdf4llm.to_markdown(
                    file_path, 
                    write_images=True, 
                    image_path=image_output_dir,
                    image_format="png"
                )
                # Reemplazar rutas absolutas por relativas para visibilidad en Obsidian/MarkText
                abs_dir = os.path.abspath(image_output_dir)
                rel_dir = os.path.basename(abs_dir)
                md_text = md_text.replace(f"({abs_dir}/", f"({rel_dir}/")
            except Exception:
                md_text = pymupdf4llm.to_markdown(file_path)
        else:
            md_text = pymupdf4llm.to_markdown(file_path)

        # Apply scientific notation and math cleanup
        sup_neg = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')
        lines = md_text.split('\n')
        cleaned_md_text = []
        for line in lines:
            line = re.sub(r'([A-Za-z])\s*', r'$\\vec{\1}$', line)
            line = re.sub(r'\s*([A-Za-z])', r'$\\vec{\1}$', line)
            line = re.sub(r'^\s*\s*$', '', line)
            line = re.sub(r'(\d+(?:[.,]\d+)?)\s*[xX*×]\s*10\s*[-−–]\s*(\d+)', lambda m: f'{m.group(1)} × 10⁻' + m.group(2).translate(sup_neg), line)
            line = re.sub(r'(\d+(?:[.,]\d+)?)\s*[xX*×]\s*10\s*(\d{1,3})\b', lambda m: f'{m.group(1)} × 10' + m.group(2).translate(sup_neg), line)
            line = re.sub(r'([a-zA-Z])2\b', r'\1²', line)
            line = re.sub(r'([a-zA-Z])3\b', r'\1³', line)
            line = re.sub(r'', r'⇒', line)
            line = re.sub(r'', r'•', line)
            line = re.sub(r'', r'α', line)
            line = re.sub(r'', r'β', line)
            line = re.sub(r'', r'Δ', line)
            cleaned_md_text.append(line)

        final_text = '\n'.join(cleaned_md_text)
        
        # Mover las imágenes al final del documento
        if extract_images and image_output_dir:
            image_tags = re.findall(r'!\[.*?\]\(.*?\)', final_text)
            if image_tags:
                # Eliminar las imágenes del texto principal
                final_text = re.sub(r'!\[.*?\]\(.*?\)\n*', '', final_text)
                final_text += '\n\n### Imágenes del Documento\n\n' + '\n\n'.join(image_tags)
        
        if not include_page_breaks:
            final_text = re.sub(r'\n---\n', '\n', final_text)

        return final_text

    def _convert_text_file(self, file_path: str, ext: str) -> str:
        """Reads non-PDF files and formats as Markdown."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception as e:
            return f"> **Error al leer archivo:** {str(e)}"

        if ext == ".md":
            return content

        if ext in [".py", ".json", ".js", ".css", ".html", ".csv", ".log"]:
            lang = ext.replace(".", "")
            filename = os.path.basename(file_path)
            return f"# {filename}\n\n```{lang}\n{content}\n```"

        filename = os.path.basename(file_path)
        return f"# {filename}\n\n{content}"

    def _clean_newlines(self, text: str) -> str:
        """Normalizes multiple consecutive newlines and extra spaces."""
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Returns human-readable file size."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
