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

    chave = inf.get('Id', '')
    versao = inf.get('versaoDadosEnt')

    #ide
    ide_dict = {}
    ide = inf.find('ide')
    if ide is not None:
        for elem in ide.iterchildren():
            ide_dict[elem.tag] = elem.text

    #emit
    emit_dict = {}
    emit = inf.find('emit')
    if emit is not None:
        for elem in emit.iterchildren():
            emit_dict[elem.tag] = elem.text

    #dest
    dest_dict = {}
    dest = inf.find('dest')
    if dest is not None:
        for elem in dest.iterchildren():
            dest_dict[elem.tag] = elem.text

    #entrega
    entrega_dict = {}
    entrega = inf.find('entrega')
    if entrega is not None:
        for elem in entrega.iterchildren():
            entrega_dict[elem.tag] = elem.text

    #det
    itens = []
    for det in inf.findall('det'):
        prod = det.find('prod')

        # Captura impostos do item
        impostos = {}
        imp = det.find('imposto')
        if imp is not None:
            for imp_tag in imp.iterchildren():
                impostos[imp_tag.tag] = {c.tag: c.text for c in imp_tag.iterchildren()}

        itens.append(ItemModel(
            nItem=det.get('nItem'),
            cProd=prod.findtext('cProd'),
            cEAN=prod.findtext('cEAN'),
            xProd=prod.findtext('xProd'),
            NCM=prod.findtext('NCM'),
            CFOP=prod.findtext('CFOP'),
            uCom=prod.findtext('uCom'),
            qCom=converte(prod.findtext('qCom')),
            vUnCom=converte(prod.findtext('vUnCom')),
            vProd=converte(prod.findtext('vProd')),
            indRegra=prod.findtext('indRegra'),
            cBarra=prod.findtext('cBarra'),
            cBarraTrib=prod.findtext('cBarraTrib'),
            uTrib=prod.findtext('uTrib'),
            qTrib=converte(prod.findtext('qTrib')),
            vUnTrib=converte(prod.findtext('vUnTrib')),
            vDesc=converte(prod.findtext('vDesc')),
            vOutro=converte(prod.findtext('vOutro')),
            impostos=impostos
        ))

    # totais
    totais = {}
    total = inf.find('total')
    if total is not None:
        for elem in total.iterchildren():
            totais[elem.tag] = converte(elem.text)

    # pagamentos
    pagamentos = []
    pgto = inf.find('pgto')
    if pgto is not None:
        for mp in pgto.findall('MP'):
            pagamentos.append({
                'cMP': mp.findtext('cMP'),
                'vMP': mp.findtext('vMP'),
                'cAdmC': mp.findtext('cAdmC')
            })

    #informacoes adicionais
    infAdic = {}
    infadic_tag = inf.find('infAdic')
    if infadic_tag is not None:
        for elem in infadic_tag.iterchildren():
            infAdic[elem.tag] = elem.text

    assinatura = root.findtext('.//assinaturaQRCODE')

    # STATUS DO ARQUIVO
    if is_cancel:
        status = 'cancelamento_validado' if assinatura else 'cancelamento_presat'
    else:
        status = 'venda_validada' if assinatura else 'venda_presat'

    return CFeModel(
        chave=chave,
        versaoDadosEnt=versao,
        ide=ide_dict,
        emitente=emit_dict,
        destinatario=dest_dict,
        itens=itens,
        totais=totais,
        pagamentos=pagamentos,
        infAdic=infAdic,
        assinaturaQRCODE=assinatura,
        status=status
    )
