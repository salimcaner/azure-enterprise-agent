from zipfile import ZipFile
import xml.etree.ElementTree as ET


class ExcelService:
    """Service for reading Excel workbooks."""

    def extract_text(self, file_path: str) -> str:
        with ZipFile(file_path) as workbook:
            shared_strings = self._read_shared_strings(workbook)
            worksheet_names = [
                name
                for name in workbook.namelist()
                if name.startswith("xl/worksheets/sheet") and name.endswith(".xml")
            ]

            rows = []

            for worksheet_name in worksheet_names:
                root = ET.fromstring(workbook.read(worksheet_name))

                for row in root.findall(".//{*}row"):
                    values = [
                        self._cell_value(cell, shared_strings)
                        for cell in row.findall("{*}c")
                    ]
                    values = [value for value in values if value]

                    if values:
                        rows.append(" ".join(values))

        return "\n".join(rows)

    def _read_shared_strings(self, workbook: ZipFile) -> list[str]:
        if "xl/sharedStrings.xml" not in workbook.namelist():
            return []

        root = ET.fromstring(workbook.read("xl/sharedStrings.xml"))
        shared_strings = []

        for item in root.findall(".//{*}si"):
            texts = [
                node.text
                for node in item.findall(".//{*}t")
                if node.text
            ]
            shared_strings.append("".join(texts))

        return shared_strings

    def _cell_value(self, cell: ET.Element, shared_strings: list[str]) -> str:
        value = cell.find("{*}v")

        if value is None or value.text is None:
            return ""

        if cell.attrib.get("t") == "s":
            index = int(value.text)
            return shared_strings[index] if index < len(shared_strings) else ""

        return value.text
