from typing import List, Optional, Dict

class ItemModel:
    def __init__(
        self,
        nItem: str,
        cProd: Optional[str],
        cEAN: Optional[str],
        xProd: Optional[str],
        NCM: Optional[str],
        CFOP: Optional[str],
        uCom: Optional[str],
        qCom: Optional[float],
        vUnCom: Optional[float],
        vProd: Optional[float],
        indRegra: Optional[str],
        cBarra: Optional[str] = None,
        cBarraTrib: Optional[str] = None,
        uTrib: Optional[str] = None,
        qTrib: Optional[float] = None,
        vUnTrib: Optional[float] = None,
        vDesc: Optional[float] = None,
        vOutro: Optional[float] = None,
        impostos: Optional[Dict[str, Dict]] = None,
        infAdProd: Optional[str] = None,
        obsFiscoDet: Optional[List[Dict[str, str]]] = None
    ):
        self.nItem = nItem
        self.cProd = cProd
        self.cEAN = cEAN
        self.xProd = xProd
        self.NCM = NCM
        self.CFOP = CFOP
        self.uCom = uCom
        self.qCom = qCom
        self.vUnCom = vUnCom
        self.vProd = vProd
        self.indRegra = indRegra
        self.cBarra = cBarra
        self.cBarraTrib = cBarraTrib
        self.uTrib = uTrib
        self.qTrib = qTrib
        self.vUnTrib = vUnTrib
        self.vDesc = vDesc
        self.vOutro = vOutro
        self.impostos = impostos or {}
        self.infAdProd = infAdProd                
        self.obsFiscoDet = obsFiscoDet or []


class CFeModel:
    def __init__(
        self,
        chave: str,
        versaoDadosEnt: Optional[str],
        ide: Dict[str, Optional[str]],
        emitente: Dict[str, Optional[str]],
        destinatario: Dict[str, Optional[str]],
        entrega: Optional[Dict[str, Optional[str]]] = None,
        itens: List[ItemModel] = None,
        totais: Dict[str, Optional[float]] = None,
        pagamentos: List[Dict[str, Optional[str]]] = None,
        infAdic: Dict[str, Optional[str]] = None,
        assinaturaQRCODE: Optional[str] = None,
        status: str = ""
    ):
        self.chave = chave
        self.versaoDadosEnt = versaoDadosEnt
        self.ide = ide
        self.emitente = emitente
        self.destinatario = destinatario
        self.entrega = entrega or {}
        self.itens = itens or []
        self.totais = totais or {}
        self.pagamentos = pagamentos or []
        self.infAdic = infAdic or {}
        self.assinaturaQRCODE = assinaturaQRCODE
        self.status = status
