import logging
import fitz  # PyMuPDF
from app.core.exceptions import ValidationError

logger = logging.getLogger("app.services.document_parser")

class DocumentParserService:
    """
    Document Intelligence service extracting raw textual payloads from PDF files.
    """
    @staticmethod
    def extract_text_from_pdf(file_bytes: bytes) -> str:
        """
        Reads PDF binaries and returns aggregated clean text logs.
        """
        logger.info("DocumentParserService: initiating PDF text extraction.")
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            extracted_pages = []
            
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                if page_text:
                    extracted_pages.append(page_text)
                    
            doc.close()
            
            raw_text = "\n".join(extracted_pages).strip()
            if not raw_text:
                logger.warning("DocumentParserService: PDF text extraction yielded empty string.")
                raise ValidationError("The uploaded PDF document contains no readable text layout.")
                
            logger.info(f"DocumentParserService: extraction completed successfully. (len={len(raw_text)})")
            return raw_text
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"DocumentParserService: extraction failed with error: {e}", exc_info=True)
            raise ValidationError("Unable to read or parse the uploaded PDF file.")
        
    @staticmethod
    def clean_text_payload(text: str) -> str:
        """
        Filters duplicate spaces and standardizes character encodings.
        """
        lines = [line.strip() for line in text.splitlines()]
        clean_lines = [line for line in lines if line]
        return "\n".join(clean_lines)
