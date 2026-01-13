# Backwards-compatible wrapper for the old module name
# Import from the new module and emit a deprecation warning so downstream
# code continues to work but is guided to migrate to the new name.
import warnings
from pdf_converter import PDFConverter

warnings.warn(
    "Importing from 'pdf_converterr' is deprecated; please use 'pdf_converter' instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["PDFConverter"]
