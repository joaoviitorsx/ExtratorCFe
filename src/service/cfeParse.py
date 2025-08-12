from __future__ import annotations

from lxml import etree
from typing import Optional, Dict, Any, List, Tuple
import threading

from src.utils.converter import converte as _conv
from src.models.cfeModel import CFeModel, ItemModel

# Reutilização de parser por thread (reduz custo de criação e objetos temporários)
_thread_locals = threading.local()

def _get_parser() -> etree.XMLParser:
    p = getattr(_thread_locals, "parser", None)
    if p is None:
        _thread_locals.parser = etree.XMLParser(
            resolve_entities=False,   # evita expansão de entidades
            remove_blank_text=True,   # menos nós/whitespace
            recover=True,             # tenta continuar em XMLs imperfeitos
            huge_tree=True,           # evita checks caros em nós grandes
        )
        p = _thread_locals.parser
    return p

def _parse_bytes(file_path: str) -> Optional[etree._Element]:
    """Lê o arquivo em bytes e parseia com parser reutilizável da thread."""
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        # fromstring é mais leve que etree.parse(file) + getroot()
        return etree.fromstring(data, parser=_get_parser())
    except Exception:
        return None


class CFeParser:
    @staticmethod
    def parse(file_path: str) -> Optional[CFeModel]:
        root = _parse_bytes(file_path)
        if root is None:
            return None

        is_cancel = root.tag.lower().endswith('cfecanc')
        # busca direta reduz sobrecarga
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
        # acessos diretos são mais baratos que dicionários intermediários
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
        d: Dict[str, str] = {}
        for e in list(ide):
            d[e.tag] = e.text or "-"
        CFeParser._formatar_data(d, "dEmi")
        CFeParser._formatar_hora(d, "hEmi")
        return d

    @staticmethod
    def _formatar_data(data_dict: Dict[str, str], campo: str) -> None:
        v = data_dict.get(campo)
        if v and v != "-" and len(v) == 8:
            data_dict[campo] = f"{v[0:4]}-{v[4:6]}-{v[6:8]}"

    @staticmethod
    def _formatar_hora(data_dict: Dict[str, str], campo: str) -> None:
        v = data_dict.get(campo)
        if v and v != "-" and len(v) == 6:
            data_dict[campo] = f"{v[0:2]}:{v[2:4]}:{v[4:6]}"

    @staticmethod
    def _extrair_emitente(inf_element) -> Dict[str, Any]:
        emit = inf_element.find('emit')
        if emit is None:
            return CFeParser._get_emitente_padrao()

        emit_dict: Dict[str, Any] = {}
        for elem in list(emit):
            if elem.tag != "enderEmit":
                emit_dict[elem.tag] = elem.text or "-"
            else:
                emit_dict["enderEmit"] = CFeParser._extrair_endereco(elem)
        return emit_dict

    @staticmethod
    def _extrair_endereco(endereco_element) -> Dict[str, str]:
        out: Dict[str, str] = {}
        for e in list(endereco_element):
            out[e.tag] = e.text or "-"
        return out

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
        out: Dict[str, str] = {}
        for e in list(dest):
            out[e.tag] = e.text or "-"
        return out

    @staticmethod
    def _extrair_entrega(inf_element) -> Dict[str, str]:
        entrega = inf_element.find('entrega')
        if entrega is None:
            return {"xLgr": "-", "nro": "-", "xCpl": "-", "xBairro": "-", "xMun": "-", "UF": "-"}
        out: Dict[str, str] = {}
        for e in list(entrega):
            out[e.tag] = e.text or "-"
        return out

    @staticmethod
    def _extrair_itens(inf_element) -> List[ItemModel]:
        itens: List[ItemModel] = []
        for det in inf_element.findall('det'):
            item = CFeParser._processar_item(det)
            if item:
                itens.append(item)
        return itens

    @staticmethod
    def _processar_item(det_element) -> Optional[ItemModel]:
        prod = det_element.find('prod')
        if prod is None:
            return None

        ftxt = prod.findtext  # local binding diminui overhead de lookups
        item_data = {
            "nItem": det_element.get('nItem') or "-",
            "cProd": ftxt('cProd', "-"),
            "cEAN": ftxt('cEAN', "-"),
            "xProd": ftxt('xProd', "-"),
            "NCM":  ftxt('NCM', "-"),
            "CEST": ftxt('CEST', "-"),
            "CFOP": ftxt('CFOP', "-"),
            "uCom": ftxt('uCom', "-"),
            "qCom": _conv(ftxt('qCom')),
            "vUnCom": _conv(ftxt('vUnCom')),
            "vProd": _conv(ftxt('vProd')),
            "indRegra": ftxt('indRegra', "-"),
            "vItem": _conv(ftxt('vItem')),
            "vDesc": _conv(ftxt('vDesc')),
            "vOutro": _conv(ftxt('vOutro')),
            "cBarra": ftxt('cBarra', "-"),
            "cBarraTrib": ftxt('cBarraTrib', "-"),
            "uTrib": ftxt('uTrib', "-"),
            "qTrib": _conv(ftxt('qTrib')),
            "vUnTrib": _conv(ftxt('vUnTrib')),
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
            CEST=item_data.get("CEST", "-"),
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
        imp = det_element.find('imposto')
        if imp is None:
            return {}
        out: Dict[str, Dict[str, str]] = {}
        for bloco in list(imp):  # ICMS, PIS, COFINS, etc
            inner: Dict[str, str] = {}
            for child in list(bloco):
                inner[child.tag] = child.text or "-"
            out[bloco.tag] = inner
        return out

    @staticmethod
    def _extrair_trib_item(det_element) -> str:
        imp = det_element.find('imposto')
        return imp.findtext('vItem12741', "-") if imp is not None else "-"

    @staticmethod
    def _extrair_totais(inf_element) -> Dict[str, Any]:
        total = inf_element.find('total')
        if total is None:
            return {"vCFe": "-", "vCFeLei12741": "-"}
        totais: Dict[str, Any] = {}
        for elem in list(total):
            if len(elem) == 0:
                totais[elem.tag] = _conv(elem.text)
            else:
                inner = {}
                for child in list(elem):
                    inner[child.tag] = _conv(child.text)
                totais[elem.tag] = inner
        return totais

    @staticmethod
    def _extrair_pagamentos(inf_element) -> tuple[List[Dict[str, str]], str]:
        pgto = inf_element.find('pgto')
        if pgto is None:
            return [], "-"
        pagamentos = []
        for mp in pgto.findall('MP'):
            pagamentos.append({
                'cMP': mp.findtext('cMP', "-"),
                'vMP': mp.findtext('vMP', "-"),
                'cAdmC': mp.findtext('cAdmC', "-")
            })
        troco = pgto.findtext('vTroco', "-")
        return pagamentos, troco

    @staticmethod
    def _extrair_info_adicional(inf_element) -> Dict[str, str]:
        inf_adic = inf_element.find('infAdic')
        if inf_adic is None:
            return {"infCpl": "-"}
        out: Dict[str, str] = {}
        for e in list(inf_adic):
            out[e.tag] = e.text or "-"
        return out

    @staticmethod
    def _extrair_obs_fisco(inf_element) -> List[Dict[str, str]]:
        out: List[Dict[str, str]] = []
        for obs in inf_element.findall('obsFisco'):
            out.append({
                "xCampo": obs.get("xCampo", "-"),
                "xTexto": obs.findtext("xTexto", "-")
            })
        return out

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
