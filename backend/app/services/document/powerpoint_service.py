from zipfile import ZipFile
import xml.etree.ElementTree as ET


class PowerPointService:
    """Service for reading PowerPoint presentations."""

    def extract_text(self, file_path: str) -> str:
        with ZipFile(file_path) as presentation:
            slide_names = [
                name
                for name in presentation.namelist()
                if name.startswith("ppt/slides/slide") and name.endswith(".xml")
            ]

            slides = []

            for slide_name in slide_names:
                root = ET.fromstring(presentation.read(slide_name))
                texts = [
                    node.text
                    for node in root.findall(".//{*}t")
                    if node.text
                ]

                if texts:
                    slides.append("\n".join(texts))

        return "\n\n".join(slides)
