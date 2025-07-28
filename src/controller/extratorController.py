from src.service.extratorService import ExtratorService
from src.service.exportarService import ExportService

class ExtratorController:
    def __init__(self):
        self.extrator_service = ExtratorService()
        self.export_service = ExportService()

    def processar(self, pasta_xml: str, caminho_planilha: str) -> dict:
        try:
            #Processa os arquivos XML e classifica
            resultado = self.extrator_service.processarPasta(pasta_xml)

            #Gera a planilha no local indicado
            caminho_final = self.export_service.gerarPlanilha(resultado, caminho_planilha)

            return {
                "status": "sucesso",
                "mensagem": f"Processamento concluído. Planilha salva em:\n{caminho_final}",
                "arquivo": caminho_final
            }

        except Exception as e:
            return {
                "status": "erro",
                "mensagem": f"Ocorreu um erro no processamento: {str(e)}"
            }
