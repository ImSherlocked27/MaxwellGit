# utils.py

import os
from collections import defaultdict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
    CSVLoader,
    UnstructuredExcelLoader
)
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema import Document
import json
import subprocess
import tempfile
from pathlib import Path
from agentic_doc.parse import parse
from dotenv import load_dotenv

def parse_pdf_document(pdf_path, result_save_dir=None):
    """
    Parse a PDF document using agentic_doc library.
    
    Args:
        pdf_path (str): Path to the PDF file to parse
        result_save_dir (str, optional): Directory to save results. 
                                       If None, creates a 'results' folder in the same directory as the PDF
    
    Returns:
        The result from the parse function
    """
    # Load environment variables
    load_dotenv()
    
    # Set default result directory if not provided
    if result_save_dir is None:
        pdf_dir = os.path.dirname(pdf_path)
        result_save_dir = os.path.join(pdf_dir, "results")
    
    # Parse the document
    result = parse(pdf_path, result_save_dir=result_save_dir)
    
    return result
# --- Document Conversion Utilities ---
def convert_word_to_pdf(word_file_path, output_dir=None):
    """
    Convert Word document to PDF using docx2pdf.
    
    Args:
        word_file_path (str): Path to the Word document
        output_dir (str, optional): Output directory for PDF. If None, uses same directory as input
    
    Returns:
        str: Path to the converted PDF file
    """
    try:
        from docx2pdf import convert
    except ImportError:
        raise ImportError("docx2pdf not found. Please install with: pip install docx2pdf")
    
    if output_dir is None:
        output_dir = os.path.dirname(word_file_path)
    
    try:
        # Generate output PDF filename
        word_filename = Path(word_file_path).stem
        pdf_path = os.path.join(output_dir, f"{word_filename}.pdf")
        
        # Convert using docx2pdf
        convert(word_file_path, pdf_path)
        
        if os.path.exists(pdf_path):
            return pdf_path
        else:
            raise Exception(f"PDF conversion completed but file not found at {pdf_path}")
            
    except Exception as e:
        raise Exception(f"Document conversion failed: {str(e)}")

def is_ocr_supported_format(file_extension):
    """Check if file format is supported by the OCR system."""
    ocr_supported = ['.pdf', '.png', '.jpg', '.jpeg']
    return file_extension.lower() in ocr_supported

def needs_conversion_for_ocr(file_extension):
    """Check if file needs conversion to be processed by OCR."""
    convertible_formats = ['.docx', '.doc']
    return file_extension.lower() in convertible_formats

# --- OCR Processing Functions ---
def process_ocr_json_result(json_result_path, source_filename):
    """
    Process OCR JSON result and extract chunks for RAG processing.
    
    Args:
        json_result_path (str): Path to the OCR JSON result file
        source_filename (str): Original filename for metadata
    
    Returns:
        list: List of LangChain Document objects created from OCR chunks
    """
    try:
        with open(json_result_path, 'r', encoding='utf-8') as f:
            ocr_data = json.load(f)
        
        chunks = ocr_data.get('chunks', [])
        documents = []
        
        # Filter chunks to exclude "figure" type and extract text
        for i, chunk in enumerate(chunks):
            chunk_type = chunk.get('chunk_type', '')
            
            # Skip figure chunks as requested
            if chunk_type.lower() == 'figure':
                continue
            
            text = chunk.get('text', '').strip()
            if not text:  # Skip empty chunks
                continue
            
            # Extract grounding information for metadata
            grounding = chunk.get('grounding', [])
            chunk_id = chunk.get('chunk_id', f'chunk_{i}')
            
            # Create metadata
            metadata = {
                'source_file': source_filename,
                'chunk_id': chunk_id,
                'chunk_type': chunk_type,
                'chunk_index': i,
                'ocr_processed': True
            }
            
            # Add page information if available
            if grounding:
                first_grounding = grounding[0]
                metadata['page'] = first_grounding.get('page', 0)
                
                # Add bounding box information
                box = first_grounding.get('box', {})
                if box:
                    metadata['bbox_left'] = box.get('l', 0)
                    metadata['bbox_top'] = box.get('t', 0)
                    metadata['bbox_right'] = box.get('r', 0)
                    metadata['bbox_bottom'] = box.get('b', 0)
            
            # Create LangChain Document
            doc = Document(
                page_content=text,
                metadata=metadata
            )
            documents.append(doc)
        
        print(f"Extracted {len(documents)} chunks from OCR result (filtered out figure chunks)")
        return documents
        
    except Exception as e:
        raise Exception(f"Error processing OCR JSON result: {str(e)}")

def process_document_with_ocr(file_path, source_filename, temp_dir="./temp_files"):
    """
    Process a document using the OCR system and return LangChain Documents.
    
    Args:
        file_path (str): Path to the file to process
        source_filename (str): Original filename for metadata
        temp_dir (str): Temporary directory for processing
    
    Returns:
        list: List of LangChain Document objects
    """
   
    file_extension = os.path.splitext(file_path)[1].lower()
    
    # Ensure temp directory exists
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # Check if file needs conversion for OCR
        if needs_conversion_for_ocr(file_extension):
            print(f"Converting {source_filename} to PDF for OCR processing...")
            pdf_path = convert_word_to_pdf(file_path, temp_dir)
            file_to_process = pdf_path
        elif is_ocr_supported_format(file_extension):
            file_to_process = file_path
        else:
            raise Exception(f"File format {file_extension} is not supported for OCR processing")
        
        # Process with OCR
        print(f"Processing {source_filename} with OCR...")
        result = parse_pdf_document(file_to_process, result_save_dir=temp_dir)
        
        # The OCR function should save a JSON file, find it
        result_files = [f for f in os.listdir(temp_dir) if f.endswith('.json')]
        if not result_files:
            raise Exception("OCR processing did not generate expected JSON result")
        
        # Use the most recent JSON file (in case there are multiple)
        json_file = sorted(result_files, key=lambda x: os.path.getmtime(os.path.join(temp_dir, x)))[-1]
        json_path = os.path.join(temp_dir, json_file)
        
        # Process the JSON result to extract documents
        documents = process_ocr_json_result(json_path, source_filename)
        
        return documents
        
    except Exception as e:
        print(f"Error processing {source_filename} with OCR: {str(e)}")
        raise

# --- 1. Document Loading ---
def load_documents(uploaded_files):
    """Loads text from uploaded files into LangChain Document objects using file-specific loaders."""
    docs = []
    temp_dir = "./temp_uploaded_files"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    for file in uploaded_files:
        temp_path = os.path.join(temp_dir, file.name)
        with open(temp_path, "wb") as f:
            f.write(file.getvalue())
        
        # Choose loader based on file extension
        file_extension = os.path.splitext(file.name)[1].lower()
        
        try:
            if file_extension == '.pdf':
                loader = PyPDFLoader(temp_path)
            elif file_extension == '.txt':
                loader = TextLoader(temp_path, encoding='utf-8')
            elif file_extension in ['.docx', '.doc']:
                loader = Docx2txtLoader(temp_path)
            elif file_extension == '.csv':
                loader = CSVLoader(temp_path)
            elif file_extension in ['.xlsx', '.xls']:
                loader = UnstructuredExcelLoader(temp_path)
            else:
                # Fallback to UnstructuredFileLoader for unknown types
                from langchain_community.document_loaders import UnstructuredFileLoader
                loader = UnstructuredFileLoader(temp_path)
            
            # Add source filename to metadata for each document
            loaded_docs = loader.load()
            for doc in loaded_docs:
                doc.metadata['source_file'] = file.name
            docs.extend(loaded_docs)
            
        except Exception as e:
            print(f"Error loading {file.name}: {str(e)}")
            # Optionally try fallback loader for unsupported files
            try:
                from langchain_community.document_loaders import UnstructuredFileLoader
                loader = UnstructuredFileLoader(temp_path)
                loaded_docs = loader.load()
                for doc in loaded_docs:
                    doc.metadata['source_file'] = file.name
                docs.extend(loaded_docs)
                print(f"Successfully loaded {file.name} using fallback UnstructuredFileLoader")
            except Exception as fallback_error:
                print(f"Fallback also failed for {file.name}: {str(fallback_error)}")
    
    return docs

# --- 2. Intelligent Chunking ---
def get_chunking_strategy(doc_type="General"):
    """
    Unified chunking strategy for all document types to optimize Spanish content.
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=500,
        add_start_index=True
    )

def split_documents(docs, doc_type="General"):
    """Splits documents using the selected strategy."""
    splitter = get_chunking_strategy(doc_type)
    return splitter.split_documents(docs)

# --- 3. Document-Level Summary Generation ---
def create_document_summary(document_content, source_file, config):
    """
    Creates a comprehensive summary for an entire document that will be used as metadata
    for all chunks from that document. This summary focuses on key information for retrieval.
    """
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable not set.")

    enrichment_llm = ChatOpenAI(model=config.get("gpt_model", "gpt-5-mini"), temperature=0)
    
    # Use configurable prompts from config, with fallback defaults
    document_summary_template = config.get("document_summary_prompt", """Analiza el siguiente documento completo y crea un resumen estructurado en español que incluya:

1. RESUMEN GENERAL: Una descripción concisa del contenido y propósito del documento
2. PERSONAS MENCIONADAS: Nombres de personas, autores, firmantes, o individuos relevantes
3. NÚMEROS DE IDENTIFICACIÓN: DNI, NIE, números de expediente, códigos, referencias, etc.
4. FECHAS IMPORTANTES: Fechas de emisión, vencimiento, eventos mencionados
5. ENTIDADES Y ORGANIZACIONES: Empresas, instituciones, departamentos mencionados
6. CONCEPTOS CLAVE: Términos técnicos, productos, servicios, o temas principales
7. DATOS FINANCIEROS: Montos, precios, presupuestos, si aplica
8. UBICACIONES: Direcciones, ciudades, países mencionados

Documento: {source_file}
Contenido:
---
{document_content}
---

Responde en formato estructurado y conciso, enfocándote en información que sea útil para búsquedas y recuperación de información.""")
    
    short_summary_template = config.get("short_summary_prompt", "Resume en español el siguiente documento en 2-3 oraciones concisas, manteniendo términos clave y nombres importantes:\n\nDocumento: {source_file}\n\n---\n\n{document_content}")
    
    # Create prompt templates from the configurable strings
    document_summary_prompt = ChatPromptTemplate.from_template(document_summary_template)
    short_summary_prompt = ChatPromptTemplate.from_template(short_summary_template)

    document_summary_chain = document_summary_prompt | enrichment_llm | StrOutputParser()
    short_summary_chain = short_summary_prompt | enrichment_llm | StrOutputParser()
    
    document_summary = document_summary_chain.invoke({
        "document_content": document_content,
        "source_file": source_file
    })
    
    short_summary = short_summary_chain.invoke({
        "document_content": document_content,
        "source_file": source_file
    })
    
    return {
        "document_summary": document_summary,
        "summary": short_summary  # For backward compatibility
    }

# --- 4. Optimized Document-Level Enrichment ---
def enrich_chunks_with_document_summaries(chunks, config):
    """
    Groups chunks by source document and creates one comprehensive summary per document.
    This summary is then applied to all chunks from that document, significantly reducing
    LLM calls while providing rich metadata for retrieval.
    """
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable not set.")

    # Group chunks by source document
    chunks_by_document = defaultdict(list)
    for chunk in chunks:
        source_file = chunk.metadata.get('source_file', 'unknown_source')
        chunks_by_document[source_file].append(chunk)
    
    enriched_chunks = []
    document_summaries = {}
    
    # Process each document once
    for source_file, doc_chunks in chunks_by_document.items():
        print(f"Creating summary for document: {source_file} ({len(doc_chunks)} chunks)")
        
        # Combine all chunk content from this document for comprehensive analysis
        document_content = "\n\n".join([chunk.page_content for chunk in doc_chunks])
        
        # Truncate if too long (to avoid token limits)
        max_content_length = 40000  # Adjusted for GPT-4o-mini context window
        if len(document_content) > max_content_length:
            document_content = document_content[:max_content_length] + "\n\n[CONTENIDO TRUNCADO...]"
        
        # Create comprehensive document summary
        summary_data = create_document_summary(document_content, source_file, config)
        document_summaries[source_file] = summary_data
        
        # Apply the same summary to all chunks from this document
        for chunk in doc_chunks:
            chunk.metadata['document_summary'] = summary_data['document_summary']
            chunk.metadata['summary'] = summary_data['summary']  # Backward compatibility
            chunk.metadata['source_file'] = source_file
            enriched_chunks.append(chunk)
    
    print(f"Document summarization complete. Created {len(document_summaries)} document summaries for {len(enriched_chunks)} chunks.")
    return enriched_chunks

# --- 5. Legacy function for backward compatibility (now calls optimized version) ---
def enrich_chunks_with_llm(chunks, config):
    """
    Legacy function name kept for backward compatibility.
    Now calls the optimized document-level enrichment function.
    """
    return enrich_chunks_with_document_summaries(chunks, config)

# --- 6. Central Processing and Indexing Function ---
def process_and_index_documents(uploaded_files, collection_name, doc_type, config, chroma_path):
    """
    The main workflow function to process and index documents.
    Returns the number of chunks processed and a list of the chunks themselves.
    Note: ChromaDB will handle all persistence - no more pickle files needed.
    """
    # Step 1: Load
    docs = load_documents(uploaded_files)
    if not docs:
        raise ValueError("Could not extract text from the uploaded files.")

    # Step 2: Split
    chunks = split_documents(docs, doc_type)
    
    # Step 3: Enrich with document-level summaries (optimized approach)
    enriched_chunks = enrich_chunks_with_document_summaries(chunks, config)

    # Note: No more pickle file saving - ChromaDB will handle all storage
    print(f"Document processing complete. {len(enriched_chunks)} enriched chunks ready for ChromaDB storage.")
    
    return enriched_chunks, len(enriched_chunks)

# --- 7. OCR-based Document Processing Functions ---
def load_documents_with_ocr(uploaded_files, use_ocr=True):
    """
    Load documents using OCR when possible, fallback to traditional loaders.
    
    Args:
        uploaded_files: List of uploaded files from Streamlit
        use_ocr (bool): Whether to use OCR for supported file types
    
    Returns:
        list: List of LangChain Document objects
    """
    docs = []
    temp_dir = "./temp_uploaded_files"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    for file in uploaded_files:
        temp_path = os.path.join(temp_dir, file.name)
        with open(temp_path, "wb") as f:
            f.write(file.getvalue())
        
        file_extension = os.path.splitext(file.name)[1].lower()
        
        try:
            # Determine if we should use OCR for this file
            should_use_ocr = (
                use_ocr and 
                (is_ocr_supported_format(file_extension) or needs_conversion_for_ocr(file_extension))
            )
            
            if should_use_ocr:
                print(f"Processing {file.name} with OCR...")
                ocr_docs = process_document_with_ocr(temp_path, file.name, temp_dir)
                docs.extend(ocr_docs)
            else:
                print(f"Processing {file.name} with traditional loader...")
                # Use traditional loading method
                if file_extension == '.pdf':
                    loader = PyPDFLoader(temp_path)
                elif file_extension == '.txt':
                    loader = TextLoader(temp_path, encoding='utf-8')
                elif file_extension in ['.docx', '.doc']:
                    loader = Docx2txtLoader(temp_path)
                elif file_extension == '.csv':
                    loader = CSVLoader(temp_path)
                elif file_extension in ['.xlsx', '.xls']:
                    loader = UnstructuredExcelLoader(temp_path)
                else:
                    from langchain_community.document_loaders import UnstructuredFileLoader
                    loader = UnstructuredFileLoader(temp_path)
                
                loaded_docs = loader.load()
                for doc in loaded_docs:
                    doc.metadata['source_file'] = file.name
                    doc.metadata['ocr_processed'] = False
                docs.extend(loaded_docs)
                
        except Exception as e:
            print(f"Error processing {file.name}: {str(e)}")
            # Try fallback to traditional loading
            try:
                print(f"Attempting fallback loading for {file.name}...")
                from langchain_community.document_loaders import UnstructuredFileLoader
                loader = UnstructuredFileLoader(temp_path)
                loaded_docs = loader.load()
                for doc in loaded_docs:
                    doc.metadata['source_file'] = file.name
                    doc.metadata['ocr_processed'] = False
                docs.extend(loaded_docs)
                print(f"Successfully loaded {file.name} using fallback loader")
            except Exception as fallback_error:
                print(f"All loading methods failed for {file.name}: {str(fallback_error)}")
    
    return docs

def process_ocr_chunks_for_rag(ocr_documents, config):
    """
    Process OCR-generated documents for RAG workflow.
    Since OCR already provides chunks, we skip traditional chunking and go directly to enrichment.
    
    Args:
        ocr_documents: List of LangChain Documents from OCR processing
        config: Configuration dictionary
    
    Returns:
        list: Enriched chunks ready for embedding
    """
    # OCR documents are already chunked, so we can skip the splitting step
    # and go directly to enrichment
    print(f"Processing {len(ocr_documents)} OCR chunks for RAG workflow...")
    
    # Apply document-level enrichment
    enriched_chunks = enrich_chunks_with_document_summaries(ocr_documents, config)
    
    return enriched_chunks

def process_and_index_documents_with_ocr(uploaded_files, collection_name, doc_type, config, chroma_path, use_ocr=True):
    """
    Enhanced main workflow function that uses OCR when possible.
    
    Args:
        uploaded_files: List of uploaded files from Streamlit
        collection_name: Name of the ChromaDB collection
        doc_type: Document type for chunking strategy (used only for non-OCR files)
        config: Configuration dictionary
        chroma_path: Path to ChromaDB storage
        use_ocr (bool): Whether to use OCR for supported file types
    
    Returns:
        tuple: (enriched_chunks, num_chunks)
    """
    # Step 1: Load documents (with OCR when possible)
    docs = load_documents_with_ocr(uploaded_files, use_ocr=use_ocr)
    if not docs:
        raise ValueError("Could not extract text from the uploaded files.")
    
    # Step 2: Separate OCR and non-OCR documents
    ocr_docs = [doc for doc in docs if doc.metadata.get('ocr_processed', False)]
    traditional_docs = [doc for doc in docs if not doc.metadata.get('ocr_processed', False)]
    
    enriched_chunks = []
    
    # Step 3a: Process OCR documents (already chunked)
    if ocr_docs:
        print(f"Processing {len(ocr_docs)} OCR-generated chunks...")
        ocr_enriched = process_ocr_chunks_for_rag(ocr_docs, config)
        enriched_chunks.extend(ocr_enriched)
    
    # Step 3b: Process traditional documents (need chunking)
    if traditional_docs:
        print(f"Processing {len(traditional_docs)} documents with traditional chunking...")
        traditional_chunks = split_documents(traditional_docs, doc_type)
        traditional_enriched = enrich_chunks_with_document_summaries(traditional_chunks, config)
        enriched_chunks.extend(traditional_enriched)
    
    print(f"Document processing complete. {len(enriched_chunks)} enriched chunks ready for ChromaDB storage.")
    print(f"  - OCR processed: {len(ocr_docs)} chunks")
    print(f"  - Traditional processed: {len(traditional_docs)} documents -> {len(enriched_chunks) - len(ocr_docs)} chunks")
    
    return enriched_chunks, len(enriched_chunks)