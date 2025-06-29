
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import android.content
import android.graphics
import android.graphics.pdf
import android.print_
import typing



class PrintedPdfDocument(android.graphics.pdf.PdfDocument):
    def __init__(self, context: android.content.Context, printAttributes: android.print_.PrintAttributes): ...
    def getPageContentRect(self) -> android.graphics.Rect: ...
    def getPageHeight(self) -> int: ...
    def getPageWidth(self) -> int: ...
    @typing.overload
    def startPage(self, pageInfo: android.graphics.pdf.PdfDocument.PageInfo) -> android.graphics.pdf.PdfDocument.Page: ...
    @typing.overload
    def startPage(self, int: int) -> android.graphics.pdf.PdfDocument.Page: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("android.print_.pdf")``.

    PrintedPdfDocument: typing.Type[PrintedPdfDocument]
