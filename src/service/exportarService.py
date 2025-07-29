import os
import pandas as pd
from typing import List
from src.models.cfeModel import CFeModel

class ExportService:
    def __init__(self):
        pass

    def gerarPlanilha(self, cfes: List[CFeModel], caminho_saida: str) -> str:
        headers = [
            # 📌 Bloco geral (infCFe / ide)
            "Chave", "Versão CF-e", "Versão Dados Ent", "Versão SAT",
            "Código UF", "Código Numérico", "Modelo", "Nº Série SAT", "Nº CF-e",
            "Data Emissão", "Hora Emissão", "Dígito Verificador", "Tipo Ambiente",
            "CNPJ Software House", "Assinatura AC", "Assinatura QR Code", "Número do Caixa",

            # 📌 Emitente
            "CNPJ Emitente", "Nome Social", "Nome Fantasia",
            "Logradouro Emitente", "Número Emitente", "Complemento Emitente",
            "Bairro Emitente", "Município Emitente", "CEP Emitente",
            "IE Emitente", "Regime Tributário", "Indicador ISSQN",

            # 📌 Destinatário
            "CPF/CNPJ Destinatário", "Nome Destinatário",

            # 📌 Produtos (cada linha vai repetir os dados do CF-e para cada produto)
            "Código Produto", "Descrição Produto", "EAN", "NCM", "CEST", "CFOP",
            "Unidade", "Quantidade", "V. Unitário", "V. Total", "Desconto", "Outros",
            "Regra",

            # 📌 Impostos por item
            "Valor Tributos Lei 12741", 
            "ICMS Origem", "ICMS CST", "ICMS Alíquota", "ICMS Valor",
            "PIS CST", "PIS Base", "PIS Alíquota", "PIS Valor",
            "COFINS CST", "COFINS Base", "COFINS Alíquota", "COFINS Valor",

            # 📌 Totais
            "Total ICMS", "Total Produtos", "Total Desconto", "Total PIS", "Total COFINS",
            "Total CF-e", "Total Tributos Lei 12741",

            # 📌 Pagamento
            "Forma Pagamento", "Valor Pago", "Troco",

            # 📌 Informações adicionais
            "Observações do Fisco", "Informações Complementares"
        ]

        linhas = []

        for cfe in cfes:
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
                    # CF-e (Cabeçalho)
                    cfe.chave, cfe.versao, cfe.versaoDadosEnt, cfe.versaoSB,
                    ide.get("cUF", "-"), ide.get("cNF", "-"), ide.get("mod", "-"),
                    ide.get("nserieSAT", "-"), ide.get("nCFe", "-"),
                    ide.get("dEmi", "-"), ide.get("hEmi", "-"), ide.get("cDV", "-"),
                    ide.get("tpAmb", "-"), ide.get("CNPJ", "-"),
                    ide.get("signAC", "-"), cfe.assinaturaQRCODE, ide.get("numeroCaixa", "-"),

                    # Emitente
                    emit.get("CNPJ", "-"), emit.get("xNome", "-"), emit.get("xFant", "-"),
                    emit.get("enderEmit", {}).get("xLgr", "-"), emit.get("enderEmit", {}).get("nro", "-"),
                    emit.get("enderEmit", {}).get("xCpl", "-"), emit.get("enderEmit", {}).get("xBairro", "-"),
                    emit.get("enderEmit", {}).get("xMun", "-"), emit.get("enderEmit", {}).get("CEP", "-"),
                    emit.get("IE", "-"), emit.get("cRegTrib", "-"), emit.get("indRatISSQN", "-"),

                    # Destinatário
                    dest.get("CPF", dest.get("CNPJ", "-")), dest.get("xNome", "-"),

                    # Produto
                    item.cProd, item.xProd, item.cEAN, item.NCM, item.CEST,
                    item.CFOP, item.uCom, item.qCom, item.vUnCom, item.vProd,
                    item.vDesc, item.vOutro, item.indRegra,

                    # Impostos
                    item.vItem12741,
                    icms_data.get("Orig", "-"), icms_data.get("CST", "-"),
                    icms_data.get("pICMS", "-"), icms_data.get("vICMS", "-"),
                    pis_data.get("CST", "-"), pis_data.get("vBC", "-"),
                    pis_data.get("pPIS", "-"), pis_data.get("vPIS", "-"),
                    cofins_data.get("CST", "-"), cofins_data.get("vBC", "-"),
                    cofins_data.get("pCOFINS", "-"), cofins_data.get("vCOFINS", "-"),

                    # Totais
                    totais.get("ICMSTot", {}).get("vICMS", "-"),
                    totais.get("ICMSTot", {}).get("vProd", "-"),
                    totais.get("ICMSTot", {}).get("vDesc", "-"),
                    totais.get("ICMSTot", {}).get("vPIS", "-"),
                    totais.get("ICMSTot", {}).get("vCOFINS", "-"),
                    totais.get("vCFe", "-"),
                    totais.get("vCFeLei12741", "-"),

                    # Pagamento
                    forma_pagamento, valor_pago, troco,

                    # Informações adicionais
                    obsFisco,
                    infAdic.get("infCpl", "-")
                ]
                linhas.append(linha)

        df = pd.DataFrame(linhas, columns=headers)

        if not caminho_saida.lower().endswith(".xlsx"):
            caminho_saida += ".xlsx"
        os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
        df.to_excel(caminho_saida, index=False)

        return caminho_saida

    def extrairImposto(self, impostos: dict, tipo: str) -> dict:
        if tipo not in impostos:
            return {}
        bloco = impostos[tipo]
        if isinstance(bloco, dict):
            for chave, dados in bloco.items():
                if isinstance(dados, dict):
                    return dados
        return {}
