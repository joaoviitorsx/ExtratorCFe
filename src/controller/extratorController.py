from src.service.extratorService import ExtratorService

class ExtratorController:
    def __init__(self):
        self.service = ExtratorService()

    def processar_pasta(self, pasta_path: str):
        try:
            resultados = self.service.ler_xmls(pasta_path)
            return {"status": "sucesso", "mensagem": f"{len(resultados)} arquivos processados.", "dados": resultados}
        except Exception as e:
            return {"status": "erro", "mensagem": str(e)}
