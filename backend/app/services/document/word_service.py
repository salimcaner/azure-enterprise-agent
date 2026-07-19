from zipfile import ZipFile
import xml.etree.ElementTree as ET


class WordService:
    """Service for reading Word documents."""

    def extract_text(self, file_path: str) -> str:
        with ZipFile(file_path) as document:
            xml_content = document.read("word/document.xml")

        root = ET.fromstring(xml_content)
        namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

        paragraphs = []

        for paragraph in root.findall(".//w:p", namespace):
            texts = [
                node.text
                for node in paragraph.findall(".//w:t", namespace)
                if node.text
            ]

            if texts:
                paragraphs.append("".join(texts))

        return "\n".join(paragraphs)
