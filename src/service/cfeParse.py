from lxml import etree
from typing import Optional, Dict, Any, List
from src.utils.converter import converte
from src.models.cfeModel import CFeModel, ItemModel

class CFeParser:
    @staticmethod
    def parse(file_path: str) -> Optional[CFeModel]:
        try:
            tree = etree.parse(file_path)
            root = tree.getroot()
        except Exception:
            return None

        is_cancel = root.tag.lower().endswith('cfecanc')
        inf = root.find('.//infCFe')
        if inf is None:
            return None

        chave_info = CFeParser._extrair_chave_info(inf)
        ide_data = CFeParser._extrair_ide(inf)
        emit_data = CFeParser._extrair_emitente(inf)
        dest_data = CFeParser._extrair_destinatario(inf)
        entrega_data = CFeParser._extrair_entrega(inf)
        itens = CFeParser._extrair_itens(inf)
        totais = CFeParser._extrair_totais(inf)
        pagamentos, troco = CFeParser._extrair_pagamentos(inf)
        inf_adic = CFeParser._extrair_info_adicional(inf)
        obs_fisco = CFeParser._extrair_obs_fisco(inf)
        assinatura = root.findtext('.//assinaturaQRCODE', "-")
        status = CFeParser._determinar_status(inf, is_cancel, assinatura)

        return CFeModel(
            chave=chave_info['chave'],
            versao=chave_info['versao'],
            versaoDadosEnt=chave_info['versao_dados_ent'],
            versaoSB=chave_info['versao_sb'],
            ide=ide_data,
            emitente=emit_data,
            destinatario=dest_data,
            itens=itens,
            totais=totais,
            pagamentos=pagamentos,
            infAdic=inf_adic,
            obsFisco=obs_fisco,
            assinaturaQRCODE=assinatura,
            status=status
        )

    @staticmethod
    def _extrair_chave_info(inf_element) -> Dict[str, str]:
        return {
            'chave': inf_element.get('Id', '-'),
            'versao': inf_element.get('versao', '-'),
            'versao_dados_ent': inf_element.get('versaoDadosEnt', '-'),
            'versao_sb': inf_element.get('versaoSB', '-')
        }

    @staticmethod
    def _extrair_ide(inf_element) -> Dict[str, str]:
        ide = inf_element.find('ide')
        if ide is None:
            return {}

        ide_dict = {elem.tag: elem.text or "-" for elem in ide.iterchildren()}
        CFeParser._formatar_data(ide_dict, "dEmi")
        CFeParser._formatar_hora(ide_dict, "hEmi")
        return ide_dict

    @staticmethod
    def _formatar_data(data_dict: Dict[str, str], campo: str) -> None:
        if campo in data_dict and data_dict[campo] not in ("-", None):
            data = data_dict[campo]
            if len(data) == 8:
                data_dict[campo] = f"{data[0:4]}-{data[4:6]}-{data[6:8]}"

    @staticmethod
    def _formatar_hora(data_dict: Dict[str, str], campo: str) -> None:
        if campo in data_dict and data_dict[campo] not in ("-", None):
            hora = data_dict[campo]
            if len(hora) == 6:
                data_dict[campo] = f"{hora[0:2]}:{hora[2:4]}:{hora[4:6]}"

    @staticmethod
    def _extrair_emitente(inf_element) -> Dict[str, Any]:
        emit = inf_element.find('emit')
        if emit is None:
            return CFeParser._get_emitente_padrao()

        emit_dict = {}
        for elem in emit.iterchildren():
            if elem.tag != "enderEmit":
                emit_dict[elem.tag] = elem.text or "-"
            else:
                emit_dict["enderEmit"] = CFeParser._extrair_endereco(elem)
        return emit_dict

    @staticmethod
    def _extrair_endereco(endereco_element) -> Dict[str, str]:
        return {elem.tag: elem.text or "-" for elem in endereco_element.iterchildren()}

    @staticmethod
    def _get_emitente_padrao() -> Dict[str, Any]:
        return {
            "CNPJ": "-", 
            "xNome": "-", 
            "xFant": "-", 
            "IE": "-", 
            "cRegTrib": "-", 
            "indRatISSQN": "-", 
            "enderEmit": {}
        }

    @staticmethod
    def _extrair_destinatario(inf_element) -> Dict[str, str]:
        dest = inf_element.find('dest')
        if dest is None:
            return {"CNPJ": "-", "CPF": "-", "xNome": "-"}
        return {elem.tag: elem.text or "-" for elem in dest.iterchildren()}

    @staticmethod
    def _extrair_entrega(inf_element) -> Dict[str, str]:
        entrega = inf_element.find('entrega')
        if entrega is None:
            return {"xLgr": "-", "nro": "-", "xCpl": "-", "xBairro": "-", "xMun": "-", "UF": "-"}
        return {elem.tag: elem.text or "-" for elem in entrega.iterchildren()}

    @staticmethod
    def _extrair_itens(inf_element) -> List[ItemModel]:
        return [CFeParser._processar_item(det) for det in inf_element.findall('det') if CFeParser._processar_item(det)]

    @staticmethod
    def _processar_item(det_element) -> Optional[ItemModel]:
        prod = det_element.find('prod')
        if prod is None:
            return None

        item_data = {
            "nItem": det_element.get('nItem', '-') or "-",
            "cProd": prod.findtext('cProd', "-"),
            "cEAN": prod.findtext('cEAN', "-"),
            "xProd": prod.findtext('xProd', "-"),
            "NCM": prod.findtext('NCM', "-"),
            "CEST": prod.findtext('CEST', "-"),
            "CFOP": prod.findtext('CFOP', "-"),
            "uCom": prod.findtext('uCom', "-"),
            "qCom": converte(prod.findtext('qCom')),
            "vUnCom": converte(prod.findtext('vUnCom')),
            "vProd": converte(prod.findtext('vProd')),
            "indRegra": prod.findtext('indRegra', "-"),
            "vItem": converte(prod.findtext('vItem')),
            "vDesc": converte(prod.findtext('vDesc')),
            "vOutro": converte(prod.findtext('vOutro')),
            "cBarra": prod.findtext('cBarra', "-"),
            "cBarraTrib": prod.findtext('cBarraTrib', "-"),
            "uTrib": prod.findtext('uTrib', "-"),
            "qTrib": converte(prod.findtext('qTrib')),
            "vUnTrib": converte(prod.findtext('vUnTrib'))
        }

        impostos = CFeParser._extrair_impostos(det_element)
        trib_item = CFeParser._extrair_trib_item(det_element)

        return ItemModel(
            nItem=item_data["nItem"],
            cProd=item_data["cProd"],
            cEAN=item_data["cEAN"],
            xProd=item_data["xProd"],
            NCM=item_data["NCM"],
            CFOP=item_data["CFOP"],
            CEST=item_data["CEST"],
            uCom=item_data["uCom"],
            qCom=item_data["qCom"],
            vUnCom=item_data["vUnCom"],
            vProd=item_data["vProd"],
            indRegra=item_data["indRegra"],
            vItem=item_data["vItem"],
            vDesc=item_data["vDesc"],
            vOutro=item_data["vOutro"],
            impostos=impostos,
            vItem12741=trib_item
        )

    @staticmethod
    def _extrair_impostos(det_element) -> Dict[str, Dict[str, str]]:
        impostos = {}
        imp = det_element.find('imposto')
        if imp is not None:
            for imp_tag in imp.iterchildren():
                impostos[imp_tag.tag] = {child.tag: child.text or "-" for child in imp_tag.iterchildren()}
        return impostos

    @staticmethod
    def _extrair_trib_item(det_element) -> str:
        imp = det_element.find('imposto')
        return imp.findtext('vItem12741', "-") if imp is not None else "-"

    @staticmethod
    def _extrair_totais(inf_element) -> Dict[str, Any]:
        total = inf_element.find('total')
        if total is None:
            return {"vCFe": "-", "vCFeLei12741": "-"}
        totais = {}
        for elem in total.iterchildren():
            if len(elem) == 0:
                totais[elem.tag] = converte(elem.text)
            else:
                totais[elem.tag] = {child.tag: converte(child.text) for child in elem.iterchildren()}
        return totais

    @staticmethod
    def _extrair_pagamentos(inf_element) -> tuple[List[Dict[str, str]], str]:
        pgto = inf_element.find('pgto')
        if pgto is None:
            return [], "-"
        pagamentos = [{
            'cMP': mp.findtext('cMP', "-"),
            'vMP': mp.findtext('vMP', "-"),
            'cAdmC': mp.findtext('cAdmC', "-")
        } for mp in pgto.findall('MP')]
        troco = pgto.findtext('vTroco', "-")
        return pagamentos, troco

    @staticmethod
    def _extrair_info_adicional(inf_element) -> Dict[str, str]:
        inf_adic = inf_element.find('infAdic')
        if inf_adic is None:
            return {"infCpl": "-"}
        return {elem.tag: elem.text or "-" for elem in inf_adic.iterchildren()}

    @staticmethod
    def _extrair_obs_fisco(inf_element) -> List[Dict[str, str]]:
        return [{
            "xCampo": obs.get("xCampo", "-"),
            "xTexto": obs.findtext("xTexto", "-")
        } for obs in inf_element.findall('obsFisco')]

    @staticmethod
    def _determinar_status(inf_element, is_cancel: bool, assinatura: str) -> str:
        tem_emit = inf_element.find('emit') is not None
        tem_itens = len(inf_element.findall('det')) > 0
        tem_total = inf_element.find('total') is not None
        if not (tem_emit and tem_itens and tem_total):
            return 'fora_padrao'
        if is_cancel:
            return 'cancelamento_validado' if assinatura != "-" else 'cancelamento_presat'
        return 'venda_validada' if assinatura != "-" else 'venda_presat'


def parseCfe(file_path: str) -> Optional[CFeModel]:
    return CFeParser.parse(file_path)
