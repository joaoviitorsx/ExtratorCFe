from lxml import etree
from typing import Optional
from src.utils.converter import converte
from src.models.cfeModel import CFeModel, ItemModel

def parseCfe(file_path: str) -> Optional[CFeModel]:
    try:
        tree = etree.parse(file_path)
        root = tree.getroot()
    except Exception:
        return None

    tag = root.tag.lower()
    is_cancel = tag.endswith('cfecanc')

    inf = root.find('.//infCFe')
    if inf is None:
        return None

    chave = inf.get('Id', '-') or '-'
    versao = inf.get('versao', '-') or '-'
    versao_dados_ent = inf.get('versaoDadosEnt', '-') or '-'
    versao_sb = inf.get('versaoSB', '-') or '-'

    ide_dict = {}
    ide = inf.find('ide')
    if ide is not None:
        for elem in ide.iterchildren():
            ide_dict[elem.tag] = elem.text if elem.text else "-"
    if "dEmi" in ide_dict and ide_dict["dEmi"] not in ("-", None):
        d = ide_dict["dEmi"]
        ide_dict["dEmi"] = f"{d[0:4]}-{d[4:6]}-{d[6:8]}"
    if "hEmi" in ide_dict and ide_dict["hEmi"] not in ("-", None):
        h = ide_dict["hEmi"]
        ide_dict["hEmi"] = f"{h[0:2]}:{h[2:4]}:{h[4:6]}"

    emit_dict = {}
    emit = inf.find('emit')
    if emit is not None:
        for elem in emit.iterchildren():
            if elem.tag != "enderEmit":
                emit_dict[elem.tag] = elem.text if elem.text else "-"
            else:
                ender_dict = {}
                for end_elem in elem.iterchildren():
                    ender_dict[end_elem.tag] = end_elem.text if end_elem.text else "-"
                emit_dict["enderEmit"] = ender_dict
    else:
        emit_dict = {"CNPJ": "-", "xNome": "-", "xFant": "-", "IE": "-", "cRegTrib": "-", "indRatISSQN": "-", "enderEmit": {}}

    dest_dict = {}
    dest = inf.find('dest')
    if dest is not None:
        for elem in dest.iterchildren():
            dest_dict[elem.tag] = elem.text if elem.text else "-"
    else:
        dest_dict = {"CNPJ": "-", "CPF": "-", "xNome": "-"}

    entrega_dict = {}
    entrega = inf.find('entrega')
    if entrega is not None:
        for elem in entrega.iterchildren():
            entrega_dict[elem.tag] = elem.text if elem.text else "-"
    else:
        entrega_dict = {"xLgr": "-", "nro": "-", "xCpl": "-", "xBairro": "-", "xMun": "-", "UF": "-"}

    itens = []
    for det in inf.findall('det'):
        prod = det.find('prod')
        item_dados = {
            "nItem": det.get('nItem', '-') or "-",
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
        impostos = {}
        imp = det.find('imposto')
        if imp is not None:
            for imp_tag in imp.iterchildren():
                impostos[imp_tag.tag] = {}
                for c in imp_tag.iterchildren():
                    impostos[imp_tag.tag][c.tag] = c.text if c.text else "-"

        tribItem = imp.findtext('vItem12741', "-") if imp is not None else "-"

        itens.append(ItemModel(
            nItem=item_dados["nItem"],
            cProd=item_dados["cProd"],
            cEAN=item_dados["cEAN"],
            xProd=item_dados["xProd"],
            NCM=item_dados["NCM"],
            CFOP=item_dados["CFOP"],
            CEST=item_dados["CEST"],
            uCom=item_dados["uCom"],
            qCom=item_dados["qCom"],
            vUnCom=item_dados["vUnCom"],
            vProd=item_dados["vProd"],
            indRegra=item_dados["indRegra"],
            vItem=item_dados["vItem"],
            vDesc=item_dados["vDesc"],
            vOutro=item_dados["vOutro"],
            impostos=impostos,
            vItem12741=tribItem
        ))

    totais = {}
    total = inf.find('total')
    if total is not None:
        for elem in total.iterchildren():
            if len(elem) == 0:
                totais[elem.tag] = converte(elem.text)
            else:
                totais[elem.tag] = {}
                for child in elem.iterchildren():
                    totais[elem.tag][child.tag] = converte(child.text)
    else:
        totais = {"vCFe": "-", "vCFeLei12741": "-"}

    pagamentos = []
    troco = "-"
    pgto = inf.find('pgto')
    if pgto is not None:
        for mp in pgto.findall('MP'):
            pagamentos.append({
                'cMP': mp.findtext('cMP', "-"),
                'vMP': mp.findtext('vMP', "-"),
                'cAdmC': mp.findtext('cAdmC', "-")
            })
        troco = pgto.findtext('vTroco', "-")

    infAdic = {}
    infadic_tag = inf.find('infAdic')
    if infadic_tag is not None:
        for elem in infadic_tag.iterchildren():
            infAdic[elem.tag] = elem.text if elem.text else "-"
    else:
        infAdic = {"infCpl": "-"}

    obsFisco = []
    for obs in inf.findall('obsFisco'):
        obsFisco.append({
            "xCampo": obs.get("xCampo", "-"),
            "xTexto": obs.findtext("xTexto", "-")
        })

    assinatura = root.findtext('.//assinaturaQRCODE', "-")

    tem_emit = inf.find('emit') is not None
    tem_itens = len(inf.findall('det')) > 0
    tem_total = inf.find('total') is not None

    if not (tem_emit and tem_itens and tem_total):
        status = 'fora_padrao'
    else:
        if is_cancel:
            status = 'cancelamento_validado' if assinatura != "-" else 'cancelamento_presat'
        else:
            status = 'venda_validada' if assinatura != "-" else 'venda_presat'

    return CFeModel(
        chave=chave,
        versao=versao,
        versaoDadosEnt=versao_dados_ent,
        versaoSB=versao_sb,
        ide=ide_dict,
        emitente=emit_dict,
        destinatario=dest_dict,
        itens=itens,
        totais=totais,
        pagamentos=pagamentos,
        infAdic=infAdic,
        obsFisco=obsFisco,
        assinaturaQRCODE=assinatura,
        status=status
    )
