import os
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from src.models.cfeModel import CFeModel

class ExportService:
    def __init__(self):
        pass

    def gerarPlanilha(self, cfes_dict: dict, caminho_saida: str) -> str:
        wb = Workbook()
        wb.remove(wb.active)

        if cfes_dict.get("venda_validada") or cfes_dict.get("venda_presat"):
            self.abaCompleta(
                wb,
                "Vendas",
                cfes_dict.get("venda_validada", []) + cfes_dict.get("venda_presat", [])
            )

        if cfes_dict.get("cancelamento_validado") or cfes_dict.get("cancelamento_presat"):
            self.abaCompleta(
                wb,
                "Cancelados",
                cfes_dict.get("cancelamento_validado", []) + cfes_dict.get("cancelamento_presat", [])
            )

        if cfes_dict.get("fora_padrao"):
            self.foraPadrao(wb, "Fora do Padrão", cfes_dict["fora_padrao"])

        if not caminho_saida.lower().endswith(".xlsx"):
            caminho_saida += ".xlsx"

        os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
        wb.save(caminho_saida)

        return caminho_saida

    def abaCompleta(self, wb: Workbook, nome_aba: str, lista_cfe: list):
        ws = wb.create_sheet(nome_aba)

        headers = [
            "Chave", "Versão CF-e", "Versão Dados Ent", "Versão SAT",
            "Código UF", "Código Numérico", "Modelo", "Nº Série SAT", "Nº CF-e",
            "Data Emissão", "Hora Emissão", "Dígito Verificador", "Tipo Ambiente",
            "CNPJ Software House", "Assinatura AC", "Assinatura QR Code", "Número do Caixa",

            # Emitente
            "CNPJ Emitente", "Nome Social", "Nome Fantasia",
            "Logradouro Emitente", "Número Emitente", "Complemento Emitente",
            "Bairro Emitente", "Município Emitente", "CEP Emitente",
            "IE Emitente", "Regime Tributário", "Indicador ISSQN",

            # Destinatário
            "CPF/CNPJ Destinatário", "Nome Destinatário",

            # Produtos
            "Código Produto", "Descrição Produto", "EAN", "NCM", "CEST", "CFOP",
            "Unidade", "Quantidade", "V. Unitário", "V. Total", "Desconto", "Outros",
            "Regra",

            # Impostos por item
            "Valor Tributos Lei 12741", 
            "ICMS Origem", "ICMS CST", "ICMS Alíquota", "ICMS Valor",
            "PIS CST", "PIS Base", "PIS Alíquota", "PIS Valor",
            "COFINS CST", "COFINS Base", "COFINS Alíquota", "COFINS Valor",

            # Totais
            "Total ICMS", "Total Produtos", "Total Desconto", "Total PIS", "Total COFINS",
            "Total CF-e", "Total Tributos Lei 12741",

            # Pagamento
            "Forma Pagamento", "Valor Pago", "Troco",

            # Informações adicionais
            "Observações do Fisco", "Informações Complementares"
        ]
        ws.append(headers)
        self.cabecalho(ws, headers)

        for cfe in lista_cfe:
            ide = cfe.ide
            emit = cfe.emitente
            dest = cfe.destinatario
            totais = cfe.totais
            pagamentos = cfe.pagamentos
            infAdic = cfe.infAdic
            obsFisco = " | ".join([f"{o.get('xCampo', '')}: {o.get('xTexto', '')}" for o in cfe.obsFisco]) if cfe.obsFisco else "-"

            forma_pagamento = " | ".join([p.get('cMP', '-') for p in pagamentos]) if pagamentos else "-"
            valor_pago = " | ".join([p.get('vMP', '-') for p in pagamentos]) if pagamentos else "-"
            troco = "-"
            if hasattr(cfe, "pagamentos") and cfe.pagamentos:
                troco = cfe.totais.get("vTroco", "-") if "vTroco" in cfe.totais else "-"
            if troco == "-" and cfe.pagamentos:
                troco = cfe.pagamentos[0].get("vTroco", "-") if "vTroco" in cfe.pagamentos[0] else "-"

            for item in cfe.itens:
                impostos = item.impostos
                icms_data = self.extrairImposto(impostos, "ICMS")
                pis_data = self.extrairImposto(impostos, "PIS")
                cofins_data = self.extrairImposto(impostos, "COFINS")

                linha = [
                    cfe.chave, cfe.versao, cfe.versaoDadosEnt, cfe.versaoSB,
                    ide.get("cUF", "-"), ide.get("cNF", "-"), ide.get("mod", "-"),
                    ide.get("nserieSAT", "-"), ide.get("nCFe", "-"),
                    ide.get("dEmi", "-"), ide.get("hEmi", "-"), ide.get("cDV", "-"),
                    ide.get("tpAmb", "-"), ide.get("CNPJ", "-"),
                    ide.get("signAC", "-"), cfe.assinaturaQRCODE, ide.get("numeroCaixa", "-"),

                    emit.get("CNPJ", "-"), emit.get("xNome", "-"), emit.get("xFant", "-"),
                    emit.get("enderEmit", {}).get("xLgr", "-"), emit.get("enderEmit", {}).get("nro", "-"),
                    emit.get("enderEmit", {}).get("xCpl", "-"), emit.get("enderEmit", {}).get("xBairro", "-"),
                    emit.get("enderEmit", {}).get("xMun", "-"), emit.get("enderEmit", {}).get("CEP", "-"),
                    emit.get("IE", "-"), emit.get("cRegTrib", "-"), emit.get("indRatISSQN", "-"),

                    dest.get("CPF", dest.get("CNPJ", "-")), dest.get("xNome", "-"),

                    item.cProd, item.xProd, item.cEAN, item.NCM, item.CEST,
                    item.CFOP, item.uCom, item.qCom, item.vUnCom, item.vProd,
                    item.vDesc, item.vOutro, item.indRegra,

                    item.vItem12741,
                    icms_data.get("Orig", "-"), icms_data.get("CST", "-"),
                    icms_data.get("pICMS", "-"), icms_data.get("vICMS", "-"),
                    pis_data.get("CST", "-"), pis_data.get("vBC", "-"),
                    pis_data.get("pPIS", "-"), pis_data.get("vPIS", "-"),
                    cofins_data.get("CST", "-"), cofins_data.get("vBC", "-"),
                    cofins_data.get("pCOFINS", "-"), cofins_data.get("vCOFINS", "-"),

                    totais.get("ICMSTot", {}).get("vICMS", "-"),
                    totais.get("ICMSTot", {}).get("vProd", "-"),
                    totais.get("ICMSTot", {}).get("vDesc", "-"),
                    totais.get("ICMSTot", {}).get("vPIS", "-"),
                    totais.get("ICMSTot", {}).get("vCOFINS", "-"),
                    totais.get("vCFe", "-"),
                    totais.get("vCFeLei12741", "-"),

                    forma_pagamento, valor_pago, troco,
                    obsFisco,
                    infAdic.get("infCpl", "-")
                ]
                ws.append(linha)

    def foraPadrao(self, wb: Workbook, nome_aba: str, lista_arquivos: list):
        ws = wb.create_sheet(nome_aba)
        headers = ["Arquivo", "Motivo"]
        ws.append(headers)
        self.cabecalho(ws, headers)
        for arquivo in lista_arquivos:
            ws.append([arquivo, "Arquivo inválido ou não é um XML de CF-e"])

    def cabecalho(self, ws, headers):
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="4F81BD")
            cell.alignment = Alignment(horizontal="center")
        for i, header in enumerate(headers, 1):
            col_letter = ws.cell(row=1, column=i).column_letter
            ws.column_dimensions[col_letter].width = max(len(header) + 2, 12)

    def extrairImposto(self, impostos: dict, tipo: str) -> dict:
        if tipo not in impostos:
            return {}
        bloco = impostos[tipo]
        if isinstance(bloco, dict):
            for chave, dados in bloco.items():
                if isinstance(dados, dict):
                    return dados
        return {}