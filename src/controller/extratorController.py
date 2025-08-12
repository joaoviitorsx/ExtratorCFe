from src.service.extratorService import ExtratorService
from src.service.exportarXlsxService import ExportXlsxService
from src.service.exportarCsvService import ExportCsvService

class ExtratorController:
    def __init__(self):
        self.extrator_service = ExtratorService()
        self.export_service = ExportXlsxService()
        self.exportar_csv_service = ExportCsvService()
        self._resultado_processado = None

    def processarPasta(self, pasta_xml: str, progresso_callback=None) -> dict:
        try:
            print(f"Iniciando processamento da pasta: {pasta_xml}")
            self.extrator_service.limparCache()
            print("Cache limpo, iniciando processamento...")
            self._resultado_processado = self.extrator_service.processarPasta(pasta_xml, progresso_callback=progresso_callback)
            print("Processamento concluído, limpando cache...")
            self.extrator_service.limparCache()
            total_arquivos = sum(len(lista) for lista in self._resultado_processado.values())
            arquivos_erro = self._resultado_processado.get("fora_padrao", [])

            qtd_erros = len(arquivos_erro)
            qtd_validos = len(self._resultado_processado.get("venda_validada", [])) + \
                          len(self._resultado_processado.get("venda_presat", []))
            qtd_cancelados = len(self._resultado_processado.get("cancelamento_validado", [])) + \
                             len(self._resultado_processado.get("cancelamento_presat", []))

            return {
                "status": "sucesso",
                "mensagem": "Arquivos XML processados com sucesso.",
                "total": total_arquivos,
                "validos": qtd_validos,
                "cancelados": qtd_cancelados,
                "erros": qtd_erros,
                "lista_erros": arquivos_erro
            }

        except Exception as e:
            return {
                "status": "erro",
                "mensagem": f"Erro ao processar pasta: {str(e)}",
                "total": 0,
                "validos": 0,
                "cancelados": 0,
                "erros": 0,
                "lista_erros": []
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

            caminho_final = self.export_service.gerarPlanilha(self._resultado_processado, caminho_saida)

            total_arquivos = sum(len(lista) for lista in self._resultado_processado.values())
            arquivos_erro = self._resultado_processado.get("fora_padrao", [])

            qtd_erros = len(arquivos_erro)
            qtd_validos = len(self._resultado_processado.get("venda_validada", [])) + \
                          len(self._resultado_processado.get("venda_presat", []))
            qtd_cancelados = len(self._resultado_processado.get("cancelamento_validado", [])) + \
                             len(self._resultado_processado.get("cancelamento_presat", []))

            return {
                "status": "sucesso",
                "mensagem": f"Planilha salva em: {caminho_final}",
                "arquivo": caminho_final,
                "total": total_arquivos,
                "validos": qtd_validos,
                "cancelados": qtd_cancelados,
                "erros": qtd_erros,
                "lista_erros": arquivos_erro
            }

        except Exception as e:
            return {"status": "erro", "mensagem": f"Erro ao exportar a planilha: {str(e)}"}
        
    def exportarCsv(self, caminho_saida: str):
        try:
            if not self._resultado_processado:
                return {"status": "erro", "mensagem": "Nenhum processamento encontrado. Execute o processamento primeiro."}

            todosCfes = []
            for lista in self._resultado_processado.values():
                todosCfes.extend([cfe for cfe in lista if not isinstance(cfe, str)])

            if not todosCfes:
                return {"status": "erro", "mensagem": "Nenhum CF-e válido para exportar."}

            caminho_final = self.exportar_csv_service.gerarCsv(self._resultado_processado, caminho_saida)

            total_arquivos = sum(len(lista) for lista in self._resultado_processado.values())
            arquivos_erro = self._resultado_processado.get("fora_padrao", [])

            qtd_erros = len(arquivos_erro)
            qtd_validos = len(self._resultado_processado.get("venda_validada", [])) + \
                          len(self._resultado_processado.get("venda_presat", []))
            qtd_cancelados = len(self._resultado_processado.get("cancelamento_validado", [])) + \
                             len(self._resultado_processado.get("cancelamento_presat", []))

            return {
                "status": "sucesso",
                "mensagem": f"CSV salvo em: {caminho_final}",
                "arquivo": caminho_final,
                "total": total_arquivos,
                "validos": qtd_validos,
                "cancelados": qtd_cancelados,
                "erros": qtd_erros,
                "lista_erros": arquivos_erro
            }

        except Exception as e:
            return {"status": "erro", "mensagem": f"Erro ao exportar o CSV: {str(e)}"}