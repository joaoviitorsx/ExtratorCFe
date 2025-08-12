from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass(slots=True, eq=False)
class ItemModel:
    nItem: str
    cProd: str
    cEAN: str = "-"
    xProd: str = "-"
    NCM: str = "-"
    CEST: str = "-"
    CFOP: str = "-"
    uCom: str = "-"
    indRegra: str = "-"
    qCom: str = "-"
    vUnCom: str = "-"
    vProd: str = "-"
    vItem: str = "-"
    vDesc: str = "-"
    vOutro: str = "-"
    vItem12741: str = "-"
    impostos: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.impostos is None:
            self.impostos = {}

@dataclass(slots=True, eq=False)
class CFeModel:
    chave: str
    versao: str = "-"
    versaoDadosEnt: str = "-"
    versaoSB: str = "-"
    assinaturaQRCODE: str = "-"
    status: str = "venda_validada"
    ide: Dict[str, Any] = None
    emitente: Dict[str, Any] = None
    destinatario: Dict[str, Any] = None
    totais: Dict[str, Any] = None
    infAdic: Dict[str, Any] = None
    itens: List[ItemModel] = None
    pagamentos: List[Dict[str, Any]] = None
    obsFisco: List[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.ide is None:
            self.ide = {}
        if self.emitente is None:
            self.emitente = {}
        if self.destinatario is None:
            self.destinatario = {}
        if self.totais is None:
            self.totais = {}
        if self.infAdic is None:
            self.infAdic = {}
        if self.itens is None:
            self.itens = []
        if self.pagamentos is None:
            self.pagamentos = []
        if self.obsFisco is None:
            self.obsFisco = []
    
    def getTotalItens(self) -> int:
        return len(self.itens)
    
    def getValorTotal(self) -> str:
        return self.totais.get("vCFe", "-")
    
    def getCnpjEmitente(self) -> str:
        return self.emitente.get("CNPJ", "-")
    
    def getNomeEmitente(self) -> str:
        return self.emitente.get("xNome", "-")
    
    def getCpfCnpjDestinario(self) -> str:
        return self.destinatario.get("CPF", self.destinatario.get("CNPJ", "-"))
    
    def getDataEmissao(self) -> str:
        return self.ide.get("dEmi", "-")
    
    def getHoraEmissao(self) -> str:
        return self.ide.get("hEmi", "-")
    
    def isCancelamento(self) -> bool:
        return "cancelamento" in self.status.lower()
    
    def isVenda(self) -> bool:
        return "venda" in self.status.lower()
    
    def getNumeroCfe(self) -> str:
        return self.ide.get("nCFe", "-")
    
    def getSerieSat(self) -> str:
        return self.ide.get("nserieSAT", "-")
    
    def toBasicDict(self) -> Dict[str, Any]:
        return {
            "chave": self.chave,
            "status": self.status,
            "total_itens": len(self.itens),
            "valor_total": self.getValorTotal(),
            "emitente": self.getNomeEmitente(),
            "data_emissao": self.getDataEmissao(),
            "numero_cfe": self.getNumeroCfe()
        }