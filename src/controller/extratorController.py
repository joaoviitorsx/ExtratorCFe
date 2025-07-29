from src.service.extratorService import ExtratorService
from src.service.exportarService import ExportService

class ExtratorController:
    def __init__(self):
        self.extrator_service = ExtratorService()
        self.export_service = ExportService()
        self._resultado_processado = None

    def processarPasta(self, pasta_xml: str) -> dict:
        try:
            self._resultado_processado = self.extrator_service.processarPasta(pasta_xml)
            return {
                "status": "sucesso",
                "mensagem": "Arquivos XML processados com sucesso."
            }
        except Exception as e:
            return {
                "status": "erro",
                "mensagem": f"Erro ao processar pasta: {str(e)}"
            }

    def exportarPlanilha(self, caminho_saida: str):
        try:
            if not self._resultado_processado:
                return {"status": "erro", "mensagem": "Nenhum processamento encontrado. Execute o processamento primeiro."}

            todosCfes = []
            for lista in self._resultado_processado.values():
                todosCfes.extend([cfe for cfe in lista if not isinstance(cfe, str)])

            if not todosCfes:
                return {"status": "erro", "mensagem": "Nenhum CF-e válido para exportar."}

            caminho_final = self.export_service.gerarPlanilha(todosCfes, caminho_saida)

            return {
                "status": "sucesso",
                "mensagem": f"Planilha salva em: {caminho_final}",
                "arquivo": caminho_final
            }

        except Exception as e:
            return {"status": "erro", "mensagem": f"Erro ao exportar a planilha: {str(e)}"}

