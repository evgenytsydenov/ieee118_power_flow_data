import win32com.client
from win32com.client import constants


def doc_to_docx(path_doc: str, path_docx: str, converter: str = "word") -> None:
    """Convert doc-file into docx-file.

    Currently, only the "word" converter is supported.
    However, it is possible to add other converters:
     - LibreOffice-based (see, https://github.com/unoconv/unoserver)
     - Cloud-based (see, https://products.aspose.com/words/python-net/)

    Args:
        path_doc: Path to doc file.
        path_docx: Path to docx file.
        converter: Application used for conversion.
    """
    if converter == "word":
        word = win32com.client.gencache.EnsureDispatch("Word.Application")
        doc = word.Documents.Open(path_doc)
        doc.Activate()
        word.ActiveDocument.SaveAs(path_docx, FileFormat=constants.wdFormatXMLDocument)
        doc.Close(False)
    else:
        raise AttributeError(f"The converter {converter} is not supported now.")
