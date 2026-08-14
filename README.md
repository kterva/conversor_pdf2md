# 📄 Conversor de PDF a Markdown (.md) - Desktop App

Una aplicación de escritorio nativa en **Python + PyQt6** moderna, rápida y privada para convertir documentos **PDF a formato Markdown (`.md`)** con soporte para selección múltiple en lote, conservación de imágenes y vista previa renderizada en tiempo real.

---

## ✨ Características Principal

- 📄 **Conversión Inteligente de PDF a Markdown:**
  - Extrae títulos (`#`, `##`, `###`), viñetas, tablas, negritas, cursivas y bloques de código.
  - Opción de incluir marcadores de separación de página (`---`).
- 🖼️ **Extracción y Conservación de Imágenes:**
  - Guarda automáticamente las imágenes incrustadas del PDF en una carpeta dedicada `nombre_images/` e inserta los enlaces de imagen relacionales en el archivo `.md`.
- 📚 **Modo Lote Múltiple / Un solo archivo:**
  - **1 solo archivo:** Muestra la interfaz dividida (*Split-View*) con editor editable a la izquierda y vista previa renderizada HTML a la derecha.
  - **Múltiples archivos:** Muestra un **listado/tabla interactiva** con el estado de conversión en tiempo real de cada archivo.
- 🧠 **Memoria Persistente de Carpetas (`QSettings`):**
  - Recuerda automáticamente la última carpeta utilizada al abrir o guardar archivos.
- 📝 **Editor y Visor Integrado de Markdown:**
  - Puedes abrir cualquier archivo `.md` existente para editarlo o visualizarlo.
- 🔒 **100% Local y Privado:**
  - Tus archivos no se envían a ningún servidor externo.

---

## 🛠️ Requisitos e Instalación

### Requisitos
- **Python 3.10+**
- Linux / macOS / Windows

### Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/kterva/conversor_pdf2md.git
   cd conversor_pdf2md
   ```

2. Crea el entorno virtual e instala las dependencias:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

---

## 🚀 Uso

Ejecuta el launcher script:
```bash
./run.sh
```

O ejecuta el punto de entrada directamente:
```bash
venv/bin/python main.py
```

---

## 📁 Estructura del Proyecto

```
conversor_pdf2md/
├── converter_engine.py   # Motor de conversión PDF -> Markdown e imágenes
├── gui.py                # Interfaz gráfica PyQt6 (Drag & Drop, Split View, Tabla en lote)
├── main.py               # Punto de entrada ejecutable
├── test_converter.py     # Pruebas unitarias automatizadas del motor
├── requirements.txt      # Dependencias del proyecto
└── run.sh                # Script de lanzamiento para Linux/macOS
```

---

## 📄 Licencia

MIT License.
