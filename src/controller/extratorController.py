from src.service.extratorService import ExtratorService
from src.service.exportarService import ExportService

class ExtratorController:
    def __init__(self):
        self.extrator_service = ExtratorService()
        self.export_service = ExportService()
        self._resultado_processado = None

    def processar_pasta(self, pasta_xml: str) -> dict:
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

    def exportar_planilha(self, caminho_planilha: str) -> dict:
        try:
            if self._resultado_processado is None:
                return {
                    "status": "erro",
                    "mensagem": "Nenhum processamento encontrado. Primeiro processe uma pasta."
                }

            caminho_final = self.export_service.gerarPlanilha(self._resultado_processado, caminho_planilha)
            return {
                "status": "sucesso",
                "mensagem": f"Planilha salva em: {caminho_final}",
                "arquivo": caminho_final
            }
        except Exception as e:
            return {
                "status": "erro",
                "mensagem": f"Erro ao exportar a planilha: {str(e)}"
            }
