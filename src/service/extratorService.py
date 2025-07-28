import os
from src.service.cfeParse import parseCfe

class ExtratorService:
    def __init__(self):
        pass

    def processarPasta(self, pasta_path: str):
        resultado = {
            "venda_validada": [],
            "venda_presat": [],
            "cancelamento_validado": [],
            "cancelamento_presat": [],
            "fora_padrao": []
        }

        for arquivo in os.listdir(pasta_path):
            caminho_completo = os.path.join(pasta_path, arquivo)

            if not os.path.isfile(caminho_completo):
                continue

            if not arquivo.lower().endswith(".xml"):
                resultado["fora_padrao"].append(arquivo)
                continue

            cfe = parseCfe(caminho_completo)

            if cfe is None:
                resultado["fora_padrao"].append(arquivo)
                continue

            if cfe.status == "venda_validada":
                resultado["venda_validada"].append(cfe)
            elif cfe.status == "venda_presat":
                resultado["venda_presat"].append(cfe)
            elif cfe.status == "cancelamento_validado":
                resultado["cancelamento_validado"].append(cfe)
            elif cfe.status == "cancelamento_presat":
                resultado["cancelamento_presat"].append(cfe)
            else:
                resultado["fora_padrao"].append(arquivo)

        return resultado

    def processarArquivo(self, arquivo_path: str):
        if not arquivo_path.lower().endswith(".xml"):
            return {"fora_padrao": [os.path.basename(arquivo_path)]}

        cfe = parseCfe(arquivo_path)

        if cfe is None:
            return {"fora_padrao": [os.path.basename(arquivo_path)]}

        return {cfe.status: [cfe]}
