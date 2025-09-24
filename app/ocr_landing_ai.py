from agentic_doc.parse import parse
from dotenv import load_dotenv
import os

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

