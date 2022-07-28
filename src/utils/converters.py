import os

import pandas as pd
import win32com.client
from docx import Document
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
    path_doc_abs = os.path.abspath(path_doc)
    path_docx_abs = os.path.abspath(path_docx)
    if converter == "word":
        word = win32com.client.gencache.EnsureDispatch("Word.Application")
        doc = word.Documents.Open(path_doc_abs)
        doc.Activate()
        word.ActiveDocument.SaveAs(
            path_docx_abs, FileFormat=constants.wdFormatXMLDocument
        )
        doc.Close(False)
    else:
        raise AttributeError(f"The converter {converter} is not supported now.")


def docx_to_pandas(path_docx: str, table_num: int, header_num: int = 1) -> pd.DataFrame:
    """Convert tables from docx file into pandas dataframe.

    Args:
        path_docx: Path to docx file.
        table_num: Sequential table number for the conversion (from 1).
        header_num: Number of header rows in the table.

    Returns:
        Dataframe with data loaded from the table.
    """
    # Load docx file
    document = Document(path_docx)

    # Find necessary table
    table = document.tables[table_num - 1]

    # Load data from the table
    data = [[cell.text for cell in row.cells] for row in table.rows]

    # Convert data into dataframe
    cols = (
        pd.Index(data[0])
        if header_num == 1
        else pd.MultiIndex.from_arrays(data[0:header_num])
    )
    return pd.DataFrame(data[header_num:], columns=cols)
