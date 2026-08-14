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
        """High-fidelity PDF to Markdown converter with layout & math cleaning."""
        try:
            from markitdown import MarkItDown
            md = MarkItDown()
            res = md.convert(file_path)
            md_text = res.text_content
        except ImportError:
            md_text = ""

        doc = fitz.open(file_path)
        base_name = os.path.splitext(os.path.basename(file_path))[0]

        if extract_images and image_output_dir:
            try:
                os.makedirs(image_output_dir, exist_ok=True)
            except Exception:
                extract_images = False

        md_pages = []
        img_counter = 1
        sup_neg = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')

        use_fallback = not bool(md_text.strip())

        for page_num in range(len(doc)):
            page = doc[page_num]
            cleaned_lines = []

            if use_fallback:
                raw_text = page.get_text("text")
                if not raw_text.strip() or len(raw_text.strip()) < 4:
                    continue

                lines = [line.strip() for line in raw_text.split('\n')]
                for line in lines:
                    if not line:
                        if cleaned_lines and cleaned_lines[-1] != '':
                            cleaned_lines.append('')
                        continue
                    
                    line = re.sub(r'([A-Za-z])\s*', r'$\\vec{\1}$', line)
                    line = re.sub(r'\s*([A-Za-z])', r'$\\vec{\1}$', line)
                    line = re.sub(r'^\s*\s*$', '', line)
                    if not line.strip(): continue

                    line = re.sub(r'(\d+(?:[.,]\d+)?)\s*[xX*×]\s*10\s*[-−–]\s*(\d+)', lambda m: f'{m.group(1)} × 10⁻' + m.group(2).translate(sup_neg), line)
                    line = re.sub(r'(\d+(?:[.,]\d+)?)\s*[xX*×]\s*10\s*(\d{1,3})\b', lambda m: f'{m.group(1)} × 10' + m.group(2).translate(sup_neg), line)
                    line = re.sub(r'([a-zA-Z])2\b', r'\1²', line)
                    line = re.sub(r'([a-zA-Z])3\b', r'\1³', line)
                    line = re.sub(r'', r'⇒', line)
                    line = re.sub(r'', r'•', line)
                    line = re.sub(r'', r'α', line)
                    line = re.sub(r'', r'β', line)
                    line = re.sub(r'', r'Δ', line)
                    
                    if len(line) < 60 and line.isupper() and not line.endswith('.'):
                        if not line.startswith('#'):
                            line = f"## {line.title()}"
                            
                    line = re.sub(r'[ \t]{4,}', '   ', line)
                    cleaned_lines.append(line)

            # Image Extraction with Background Filters
            if extract_images and image_output_dir and os.path.exists(image_output_dir):
                images_in_page = page.get_images(full=True)
                for img_info in images_in_page:
                    xref = img_info[0]
                    try:
                        base_img = doc.extract_image(xref)
                        w = base_img.get('width', 0)
                        h = base_img.get('height', 0)
                        
                        if w < 50 or h < 50: continue
                        if w > 0 and h > 0:
                            if w/h > 4.5 or h/w > 4.5: continue
                        if base_img.get('colorspace') == 1 and base_img.get('bpc') == 1: continue

                        img_ext = base_img['ext']
                        img_name = f'{base_name}_img_p{page_num+1}_{img_counter}.{img_ext}'
                        img_path = os.path.join(image_output_dir, img_name)
                        with open(img_path, 'wb') as f:
                            f.write(base_img['image'])
                        
                        rel_img = os.path.join(os.path.basename(image_output_dir), img_name)
                        cleaned_lines.append(f'\n![Imagen P{page_num+1} {img_counter}]({rel_img})\n')
                        img_counter += 1
                    except Exception:
                        pass

            if use_fallback:
                page_md = '\n'.join(cleaned_lines)
                page_md = re.sub(r'\n{3,}', '\n\n', page_md).strip()
                if page_md:
                    md_pages.append(page_md)
            elif cleaned_lines:
                md_pages.append('\n'.join(cleaned_lines))

        doc.close()
        
        if not use_fallback:
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
            if md_pages:
                final_text += '\n\n### Imágenes Extraídas\n\n' + '\n'.join(md_pages)
            return final_text
        else:
            separator = '\n\n---\n\n' if include_page_breaks else '\n\n'
            return separator.join(md_pages)

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
