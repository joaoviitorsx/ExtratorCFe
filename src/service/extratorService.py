import os
import xml.etree.ElementTree as ET

class ExtratorService:
    def ler_xmls(self, pasta_path: str):
        cfe_list = []

        for arquivo in os.listdir(pasta_path):
            if arquivo.lower().endswith(".xml"):
                file_path = os.path.join(pasta_path, arquivo)
                cfe_info = self._processar_xml(file_path)
                if cfe_info:
                    cfe_list.append(cfe_info)

        return cfe_list

    def _processar_xml(self, file_path: str):
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            chave = root.attrib.get("Id", "SEM CHAVE")

            return {
                "arquivo": os.path.basename(file_path),
                "chave": chave
            }
        except Exception as e:
            print(f"Erro ao processar {file_path}: {e}")
            return None
