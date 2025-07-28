import os
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from src.models.cfeModel import CFeModel

class ExportService:
    def __init__(self):
        pass 

    def gerarPlanilha(self, dados: dict, caminho_arquivo: str):
        wb = Workbook()
        wb.remove(wb.active)

        if dados["venda_validada"]:
            self.abaVendas(wb, "Venda Validada", dados["venda_validada"])

        if dados["venda_presat"]:
            self.abaVendas(wb, "Venda Pré-SAT", dados["venda_presat"])

        if dados["cancelamento_validado"]:
            self.abaCancelamento(wb, "Cancelamento Validado", dados["cancelamento_validado"])

        if dados["cancelamento_presat"]:
            self.abaCancelamento(wb, "Cancelamento Pré-SAT", dados["cancelamento_presat"])

        if dados["fora_padrao"]:
            self.abaFalha(wb, "Arquivos Ignorados", dados["fora_padrao"])

        wb.save(caminho_arquivo)
        return caminho_arquivo

    def abaVendas(self, wb: Workbook, nome_aba: str, lista_cfe: list):
        ws = wb.create_sheet(nome_aba)
        ws.append([
            "Chave", "Data Emissão", "CNPJ Emitente", "Nome Emitente", 
            "CPF/CNPJ Cliente", "Nome Cliente", 
            "Produto", "Quantidade", "V. Unitário", "V. Total", "NCM", "CFOP"
        ])
        self.cabecalho(ws)

        for cfe in lista_cfe:
            data_emissao = cfe.ide.get("dEmi") if cfe.ide else ""
            cnpj_emitente = cfe.emitente.get("CNPJ") if cfe.emitente else ""
            nome_emitente = cfe.emitente.get("xNome") if cfe.emitente else ""
            cpf_cnpj_cliente = cfe.destinatario.get("CPF") or cfe.destinatario.get("CNPJ") if cfe.destinatario else ""
            nome_cliente = cfe.destinatario.get("xNome") if cfe.destinatario else ""

            for item in cfe.itens:
                ws.append([
                    cfe.chave,
                    data_emissao,
                    cnpj_emitente,
                    nome_emitente,
                    cpf_cnpj_cliente,
                    nome_cliente,
                    item.xProd,
                    item.qCom,
                    item.vUnCom,
                    item.vProd,
                    item.NCM,
                    item.CFOP
                ])

    def abaCancelamento(self, wb: Workbook, nome_aba: str, lista_cfe: list):
        ws = wb.create_sheet(nome_aba)
        ws.append([
            "Chave", "Data Emissão", "CNPJ Emitente", "Nome Emitente",
            "CPF/CNPJ Cliente", "Nome Cliente", 
            "Valor Total", "AssinaturaQRCODE"
        ])
        self.cabecalho(ws)

        for cfe in lista_cfe:
            data_emissao = cfe.ide.get("dEmi") if cfe.ide else ""
            cnpj_emitente = cfe.emitente.get("CNPJ") if cfe.emitente else ""
            nome_emitente = cfe.emitente.get("xNome") if cfe.emitente else ""
            cpf_cnpj_cliente = cfe.destinatario.get("CPF") or cfe.destinatario.get("CNPJ") if cfe.destinatario else ""
            nome_cliente = cfe.destinatario.get("xNome") if cfe.destinatario else ""
            valor_total = cfe.totais.get("vCFe") if cfe.totais else ""

            ws.append([
                cfe.chave,
                data_emissao,
                cnpj_emitente,
                nome_emitente,
                cpf_cnpj_cliente,
                nome_cliente,
                valor_total,
                cfe.assinaturaQRCODE
            ])

    def abaFalha(self, wb: Workbook, nome_aba: str, lista_arquivos: list):
        ws = wb.create_sheet(nome_aba)
        ws.append(["Arquivo", "Motivo"])
        self.cabecalho(ws)

        for arquivo in lista_arquivos:
            ws.append([arquivo, "Arquivo inválido ou não é XML de CF-e"])

    def cabecalho(self, ws):
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="4F81BD")
            cell.alignment = Alignment(horizontal="center")
