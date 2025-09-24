# Maxwell-RAG

Una aplicación de generación aumentada por recuperación (RAG) con modelos de IA.

## Descripción

Maxwell-RAG es una aplicación Streamlit que permite a los usuarios crear y utilizar vectorstores para la generación aumentada por recuperación (RAG) con diferentes modelos de IA. Esta aplicación facilita subir documentos, procesarlos y consultarlos mediante chat utilizando OpenAI, Google Generative AI o HuggingFace.

## Características

- **Creación de Vectorstores**: Sube documentos (PDF, TXT, CSV, DOCX) para crear índices vectoriales.
- **Múltiples Proveedores de IA**: Soporte para OpenAI, Google Generative AI y HuggingFace.
- **Opciones de Retriever**: Configura diferentes tipos de retrievers:
  - Vectorstore backed retriever
  - Contextual compression
  - Cohere reranker
- **Interfaz Chat**: Interactúa con tus documentos a través de una interfaz de chat natural.
- **Soporte Multilingüe**: Respuestas en diferentes idiomas.

## Estructura del Proyecto

```
Maxwell-RAG/
│
├── app/                          # Código principal de la aplicación
│   ├── core/                     # Funcionalidad principal
│   │   ├── document_processing.py # Procesamiento de documentos
│   │   ├── retrieval.py          # Configuración de retrievers
│   │   └── vectorstore.py        # Creación y gestión de vectorstores
│   │
│   ├── services/                 # Servicios de la aplicación
│   │   ├── chat_service.py       # Servicios de chat y conversación
│   │   └── llm_service.py        # Configuración de modelos de lenguaje
│   │
│   ├── ui/                       # Componentes de la interfaz de usuario
│   │   ├── styles.py             # Estilos CSS
│   │   └── views.py              # Vistas de la aplicación
│   │
│   ├── utils/                    # Utilidades
│   │   └── helpers.py            # Funciones auxiliares
│   │
│   └── main.py                   # Punto de entrada principal
│
├── data/                         # Directorio de datos
│   ├── tmp/                      # Archivos temporales
│   └── vector_stores/            # Vectorstores almacenados
│
├── README.md                     # Este archivo
└── RAG_app copy.py               # Archivo original de referencia
```

## Requisitos

- Python 3.8+
- Streamlit
- LangChain
- Chromadb
- Dependencias para proveedores de LLM (OpenAI, Google Generative AI, HuggingFace)

## Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/tu-usuario/Maxwell-RAG.git
cd Maxwell-RAG
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecuta la aplicación:
```bash
streamlit run app/main.py
```

## Uso

1. **Pantalla de Bienvenida**:
   - Elige entre "Abrir un vectorstore guardado" o "Crear un nuevo vectorstore".

2. **Crear Vectorstore**:
   - Selecciona un proveedor de IA y proporciona tu API key.
   - Configura el tipo de retriever y los parámetros del modelo.
   - Sube los documentos y asigna un nombre al vectorstore.
   - Haz clic en "Crear Vectorbase".

3. **Chat con Vectorstore**:
   - Selecciona un vectorstore existente de la barra lateral.
   - Comienza a hacer preguntas en el chat.
   - Las respuestas se generarán basadas en el contenido de los documentos.

## Licencia

[Incluir información de licencia]

## Contacto

[Incluir información de contacto] 