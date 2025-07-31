import os
from collections import defaultdict
from src.service.cfeParse import parseCfe
from concurrent.futures import ThreadPoolExecutor, as_completed

class ExtratorService:
    def __init__(self, max_workers=8, batch_size=500):
        self.max_workers = max_workers
        self.batch_size = batch_size

    def _processarArquivos(self, caminho_completo):
        if not caminho_completo.lower().endswith(".xml"):
            return ("fora_padrao", os.path.basename(caminho_completo))

        cfe = parseCfe(caminho_completo)
        if cfe is None or getattr(cfe, "status", None) == "fora_padrao":
            return ("fora_padrao", os.path.basename(caminho_completo))

        return (cfe.status, cfe)

    def chunker(self, seq, size):
        for pos in range(0, len(seq), size):
            yield seq[pos:pos + size]

    def processarPasta(self, pasta_path: str, progresso_callback=None):
        resultado = defaultdict(list)
        arquivos = [
            entry.path for entry in os.scandir(pasta_path)
            if entry.is_file()
        ]
        total = len(arquivos)
        processados = 0

        for lote in self.chunker(arquivos, self.batch_size):
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {executor.submit(self._processarArquivos, arquivo): arquivo for arquivo in lote}
                for future in as_completed(futures):
                    status, dado = future.result()
                    resultado[status].append(dado)
            processados += len(lote)
            if progresso_callback:
                progresso_callback(processados, total)

        return dict(resultado)