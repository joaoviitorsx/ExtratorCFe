import os
import time
import xlsxwriter
from src.models.cfeModel import CFeModel

class ExportXlsxService:
    def __init__(self):
        self._headers_cache = None
        
    @property
    def _headers(self):
        if self._headers_cache is None:
            self._headers_cache = self._montarHeaders()
        return self._headers_cache

    def gerarPlanilha(self, cfes_dict: dict, caminho_saida: str) -> str:
        if not caminho_saida.lower().endswith(".xlsx"):
            caminho_saida += ".xlsx"

        os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
        wb = xlsxwriter.Workbook(caminho_saida, {'constant_memory': True})

        vendas_data = self._prepararDadosVendas(cfes_dict)
        cancelados_data = self._prepararDadosCancelados(cfes_dict)
        fora_padrao_data = self._prepararDadosForaPadrao(cfes_dict)

        if vendas_data:
            self._escreverAba(wb, "Vendas", vendas_data)
        if cancelados_data:
            self._escreverAba(wb, "Cancelados", cancelados_data)
        if fora_padrao_data:
            self._escreverAbaForaPadrao(wb, fora_padrao_data)

        wb.close()
        return caminho_saida

    def _prepararDadosVendas(self, cfes_dict):
        vendas = cfes_dict.get("venda_validada", []) + cfes_dict.get("venda_presat", [])
        return self._processarCfes(vendas) if vendas else None

    def _prepararDadosCancelados(self, cfes_dict):
        cancelados = cfes_dict.get("cancelamento_validado", []) + cfes_dict.get("cancelamento_presat", [])
        return self._processarCfes(cancelados) if cancelados else None

    def _prepararDadosForaPadrao(self, cfes_dict):
        fora_padrao = cfes_dict.get("fora_padrao", [])
        return [[arquivo, "Arquivo inválido ou não é um XML de CF-e"] for arquivo in fora_padrao] if fora_padrao else None

    def _processarCfes(self, lista_cfe):
        todas_linhas = []
        
        for cfe in lista_cfe:
            dados_base = self._extrairDadosBase(cfe)
            for item in cfe.itens:
                linha = self._criarLinhaItem(dados_base, item)
                todas_linhas.append(linha)

        return todas_linhas

    def _extrairDadosBase(self, cfe: CFeModel):
        ide = cfe.ide or {}
        emit = cfe.emitente or {}
        dest = cfe.destinatario or {}
        totais = cfe.totais or {}
        pagamentos = cfe.pagamentos or []
        infAdic = cfe.infAdic or {}

        obsFisco = "-"
        if cfe.obsFisco:
            obsFisco = " | ".join(f"{o.get('xCampo', '')}: {o.get('xTexto', '')}" for o in cfe.obsFisco)

        forma_pagamento = "-"
        valor_pago = "-"
        if pagamentos:
            forma_pagamento = " | ".join(p.get('cMP', '-') for p in pagamentos)
            valor_pago = " | ".join(p.get('vMP', '-') for p in pagamentos)

        troco = totais.get("vTroco", "-")

        return (
            (cfe.chave, cfe.versao, cfe.versaoDadosEnt, cfe.versaoSB,
             ide.get("cUF", "-"), ide.get("cNF", "-"), ide.get("mod", "-"),
             ide.get("nserieSAT", "-"), ide.get("nCFe", "-"),
             ide.get("dEmi", "-"), ide.get("hEmi", "-"), ide.get("cDV", "-"),
             ide.get("tpAmb", "-"), ide.get("CNPJ", "-"),
             ide.get("signAC", "-"), cfe.assinaturaQRCODE, ide.get("numeroCaixa", "-")),
            (emit.get("CNPJ", "-"), emit.get("xNome", "-"), emit.get("xFant", "-"),
             emit.get("enderEmit", {}).get("xLgr", "-"), emit.get("enderEmit", {}).get("nro", "-"),
             emit.get("enderEmit", {}).get("xCpl", "-"), emit.get("enderEmit", {}).get("xBairro", "-"),
             emit.get("enderEmit", {}).get("xMun", "-"), emit.get("enderEmit", {}).get("CEP", "-"),
             emit.get("IE", "-"), emit.get("cRegTrib", "-"), emit.get("indRatISSQN", "-")),
            (dest.get("CPF", dest.get("CNPJ", "-")), dest.get("xNome", "-")),
            (totais.get("ICMSTot", {}).get("vICMS", "-"),
             totais.get("ICMSTot", {}).get("vProd", "-"),
             totais.get("ICMSTot", {}).get("vDesc", "-"),
             totais.get("ICMSTot", {}).get("vPIS", "-"),
             totais.get("ICMSTot", {}).get("vCOFINS", "-"),
             totais.get("vCFe", "-"), totais.get("vCFeLei12741", "-")),
            (forma_pagamento, valor_pago, troco),
            (obsFisco, infAdic.get("infCpl", "-"))
        )

    def _criarLinhaItem(self, dados_base, item):
        impostos = item.impostos or {}
        icms = self._extrairImposto(impostos, "ICMS")
        pis = self._extrairImposto(impostos, "PIS")
        cofins = self._extrairImposto(impostos, "COFINS")

        item_dados = (
            item.cProd, item.xProd, item.cEAN, item.NCM, item.CEST,
            item.CFOP, item.uCom, item.qCom, item.vUnCom, item.vProd,
            item.vDesc, item.vOutro, item.indRegra, item.vItem12741
        )

        imposto_dados = (
            icms.get("Orig", "-"), icms.get("CST", "-"), icms.get("pICMS", "-"), icms.get("vICMS", "-"),
            pis.get("CST", "-"), pis.get("vBC", "-"), pis.get("pPIS", "-"), pis.get("vPIS", "-"),
            cofins.get("CST", "-"), cofins.get("vBC", "-"), cofins.get("pCOFINS", "-"), cofins.get("vCOFINS", "-")
        )

        return dados_base[0] + dados_base[1] + dados_base[2] + item_dados + imposto_dados + dados_base[3] + dados_base[4] + dados_base[5]

    def _extrairImposto(self, impostos: dict, tipo: str) -> dict:
        if not impostos or tipo not in impostos:
            return {}

        bloco = impostos[tipo]
        if isinstance(bloco, dict):
            return next((dados for dados in bloco.values() if isinstance(dados, dict)), {})
        
        return {}

    def _escreverAba(self, wb, nome_aba: str, dados_linhas: list):
        ws = wb.add_worksheet(nome_aba)
        ws.write_row(0, 0, self._headers)

        for row, linha in enumerate(dados_linhas, start=1):
            ws.write_row(row, 0, linha)

    def _escreverAbaForaPadrao(self, wb, dados_linhas: list):
        ws = wb.add_worksheet("Fora do Padrão")
        headers = ["Arquivo", "Motivo"]
        ws.write_row(0, 0, headers)

        for row, linha in enumerate(dados_linhas, start=1):
            ws.write_row(row, 0, linha)

    def _montarHeaders(self):
        return (
            "Chave", "Versão CF-e", "Versão Dados Ent", "Versão SAT",
            "Código UF", "Código Numérico", "Modelo", "Nº Série SAT", "Nº CF-e",
            "Data Emissão", "Hora Emissão", "Dígito Verificador", "Tipo Ambiente",
            "CNPJ Software House", "Assinatura AC", "Assinatura QR Code", "Número do Caixa",
            "CNPJ Emitente", "Nome Social", "Nome Fantasia",
            "Logradouro Emitente", "Número Emitente", "Complemento Emitente",
            "Bairro Emitente", "Município Emitente", "CEP Emitente",
            "IE Emitente", "Regime Tributário", "Indicador ISSQN",
            "CPF/CNPJ Destinatário", "Nome Destinatário",
            "Código Produto", "Descrição Produto", "EAN", "NCM", "CEST", "CFOP",
            "Unidade", "Quantidade", "V. Unitário", "V. Total", "Desconto", "Outros", "Regra",
            "Valor Tributos Lei 12741", "ICMS Origem", "ICMS CST", "ICMS Alíquota", "ICMS Valor",
            "PIS CST", "PIS Base", "PIS Alíquota", "PIS Valor",
            "COFINS CST", "COFINS Base", "COFINS Alíquota", "COFINS Valor",
            "Total ICMS", "Total Produtos", "Total Desconto", "Total PIS", "Total COFINS",
            "Total CF-e", "Total Tributos Lei 12741",
            "Forma Pagamento", "Valor Pago", "Troco",
            "Observações do Fisco", "Informações Complementares"
        )

    def montarHeaders(self):
        return list(self._headers)

    def extrairImposto(self, impostos: dict, tipo: str) -> dict:
        return self._extrairImposto(impostos, tipo)