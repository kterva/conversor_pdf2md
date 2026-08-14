"""
Converter Engine Module
Handles PDF extraction to Markdown (.md), text file formatting, and image preservation.
"""

import os
from typing import Dict, Any, Tuple, Optional
import pymupdf as fitz  # PyMuPDF


class PDFToMarkdownConverter:
    """Engine for converting PDF and text files into Markdown format with image extraction."""

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
        Converts input file (PDF, TXT, etc.) into Markdown string.
        Optionally extracts embedded images into image_output_dir.
        Returns (markdown_content, metadata).
        """
        info = self.get_file_info(file_path)
        ext = info["extension"]

        if ext == ".pdf":
            md_content = self._convert_pdf(
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

    def _convert_pdf(
        self,
        file_path: str,
        include_page_breaks: bool,
        extract_images: bool,
        image_output_dir: Optional[str]
    ) -> str:
        """Converts PDF file to Markdown with image extraction support."""
        try:
            import pymupdf4llm
            kwargs = {
                "page_chunks": True,
                "write_images": extract_images,
            }
            if extract_images and image_output_dir:
                os.makedirs(image_output_dir, exist_ok=True)
                kwargs["image_path"] = image_output_dir

            page_chunks = pymupdf4llm.to_markdown(file_path, **kwargs)
            
            md_pages = []
            for chunk in page_chunks:
                text = chunk.get("text", "").strip()
                if text:
                    md_pages.append(text)

            separator = "\n\n---\n\n" if include_page_breaks else "\n\n"
            return separator.join(md_pages)
        except Exception as e:
            # Fallback method
            return self._convert_pdf_fallback(file_path, include_page_breaks, extract_images, image_output_dir)

    def _convert_pdf_fallback(
        self,
        file_path: str,
        include_page_breaks: bool,
        extract_images: bool,
        image_output_dir: Optional[str]
    ) -> str:
        """Fallback method parsing PDF text & images directly with PyMuPDF."""
        doc = fitz.open(file_path)
        pages_md = []
        img_counter = 1

        if extract_images and image_output_dir:
            os.makedirs(image_output_dir, exist_ok=True)

        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("blocks")
            page_lines = []

            for b in blocks:
                text = b[4].strip()
                if not text:
                    continue

                lines = text.split("\n")
                first_line = lines[0].strip()
                
                if len(first_line) < 60 and not first_line.endswith("."):
                    if page_num == 0 and len(page_lines) == 0:
                        page_lines.append(f"# {first_line}")
                        if len(lines) > 1:
                            page_lines.append("\n".join(lines[1:]))
                        continue

                page_lines.append(text)

            # Extract page images if enabled
            if extract_images and image_output_dir:
                images_in_page = page.get_images(full=True)
                for img_info in images_in_page:
                    xref = img_info[0]
                    try:
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        img_filename = f"image_p{page_num+1}_{img_counter}.{image_ext}"
                        img_save_path = os.path.join(image_output_dir, img_filename)
                        
                        with open(img_save_path, "wb") as f_img:
                            f_img.write(image_bytes)

                        rel_path = os.path.relpath(img_save_path, start=os.path.dirname(image_output_dir))
                        page_lines.append(f"\n![Imagen P{page_num+1}]({rel_path})\n")
                        img_counter += 1
                    except Exception:
                        pass

            pages_md.append("\n\n".join(page_lines))

        doc.close()
        separator = "\n\n---\n\n" if include_page_breaks else "\n\n"
        return separator.join(pages_md)

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
        """Normalizes multiple consecutive newlines."""
        import re
        return re.sub(r"\n{3,}", "\n\n", text).strip()

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Returns human-readable file size."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
