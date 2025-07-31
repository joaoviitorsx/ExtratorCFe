from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

@dataclass
class ItemModel:
    nItem: str
    cProd: str
    cEAN: str
    xProd: str
    NCM: str
    CEST: str                
    CFOP: str
    uCom: str
    qCom: Optional[float]
    vUnCom: Optional[float]
    vProd: Optional[float]
    indRegra: str
    vItem: Optional[float]           
    vDesc: Optional[float]            
    vOutro: Optional[float]           
    impostos: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    vItem12741: Optional[str] = "-"    

    def toDict(self) -> Dict[str, Any]:
        return {
            "nItem": self.nItem,
            "cProd": self.cProd,
            "cEAN": self.cEAN,
            "xProd": self.xProd,
            "NCM": self.NCM,
            "CEST": self.CEST,      
            "CFOP": self.CFOP,
            "uCom": self.uCom,
            "qCom": self.qCom,
            "vUnCom": self.vUnCom,
            "vProd": self.vProd,
            "indRegra": self.indRegra,
            "vItem": self.vItem,
            "vDesc": self.vDesc,
            "vOutro": self.vOutro,
            "impostos": self.impostos,
            "vItem12741": self.vItem12741
        }

@dataclass
class CFeModel:
    chave: str
    versao: str
    versaoDadosEnt: str
    versaoSB: str

    ide: Dict[str, Any]
    emitente: Dict[str, Any]
    destinatario: Dict[str, Any]
    itens: List[ItemModel] = field(default_factory=list)
    totais: Dict[str, Any] = field(default_factory=dict)
    pagamentos: List[Dict[str, Any]] = field(default_factory=list)
    infAdic: Dict[str, Any] = field(default_factory=dict)
    obsFisco: List[Dict[str, str]] = field(default_factory=list)
    assinaturaQRCODE: str = "-"
    status: str = "venda_validada"

    def toDict(self) -> Dict[str, Any]:
        return {
            "chave": self.chave,
            "versao": self.versao,
            "versaoDadosEnt": self.versaoDadosEnt,
            "versaoSB": self.versaoSB,
            "ide": self.ide,
            "emitente": self.emitente,
            "destinatario": self.destinatario,
            "itens": [item.toDict() for item in self.itens],
            "totais": self.totais,
            "pagamentos": self.pagamentos,
            "infAdic": self.infAdic,
            "obsFisco": self.obsFisco,
            "assinaturaQRCODE": self.assinaturaQRCODE,
            "status": self.status
        }
