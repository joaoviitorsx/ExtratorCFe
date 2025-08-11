import os
import time
from collections import defaultdict
from src.service.cfeParse import parseCfe
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from multiprocessing import cpu_count

class ExtratorService:
    def __init__(self, max_workers=None, batch_size=650):
        self.max_workers = max_workers or min(cpu_count() * 2, 20)
        self.batch_size = batch_size

    def processarPasta(self, pasta_path: str, progresso_callback=None, usar_multiprocessing=False):
        tempo_inicio = time.time()
        if progresso_callback:
            progresso_callback(0, 1)

        arquivos = self.listarArquivos(pasta_path)
        if not arquivos:
            if progresso_callback:
                progresso_callback(0, 1)
            return {}

        total = len(arquivos)
        if progresso_callback:
            progresso_callback(0, total)

        if usar_multiprocessing and total > 10000:
            resultado = self.processoMulti(arquivos, total, progresso_callback)
        else:
            resultado = self.processoThreads(arquivos, total, progresso_callback)

        if progresso_callback:
            progresso_callback(total, total)

        return dict(resultado)

    def listarArquivos(self, pasta_path: str):
        arquivos = []
        try:
            with os.scandir(pasta_path) as entries:
                for entry in entries:
                    if entry.is_file() and entry.name.lower().endswith('.xml'):
                        arquivos.append(entry.path)
        except OSError:
            return []
        return arquivos

    def processarArquivos(self, lote_arquivos):
        resultado_local = defaultdict(list)
        
        for arquivo in lote_arquivos:
            try:
                if not arquivo.lower().endswith('.xml'):
                    resultado_local["fora_padrao"].append(os.path.basename(arquivo))
                    continue
                    
                cfe = parseCfe(arquivo)
                if cfe is None:
                    resultado_local["fora_padrao"].append(os.path.basename(arquivo))
                    continue
                    
                status = getattr(cfe, "status", "fora_padrao")
                if status == "fora_padrao":
                    resultado_local["fora_padrao"].append(os.path.basename(arquivo))
                else:
                    resultado_local[status].append(cfe)
            except Exception:
                resultado_local["fora_padrao"].append(os.path.basename(arquivo))

        return dict(resultado_local)

    def processoThreads(self, arquivos, total, progresso_callback):
        resultado = defaultdict(list)
        processados = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Processar em lotes
            for i in range(0, total, self.batch_size):
                lote = arquivos[i:i + self.batch_size]
                future = executor.submit(self.processarArquivos, lote)
                
                try:
                    resultado_lote = future.result()
                    for status, dados in resultado_lote.items():
                        resultado[status].extend(dados)
                    
                    processados += len(lote)
                    if progresso_callback:
                        progresso_callback(processados, total)
                except Exception:
                    pass

        return resultado

    def processoMulti(self, arquivos, total, progresso_callback):
        resultado = defaultdict(list)
        processados = 0
        max_processes = min(cpu_count(), 8)

        with ProcessPoolExecutor(max_workers=max_processes) as executor:
            # Processar em lotes
            for i in range(0, total, self.batch_size):
                lote = arquivos[i:i + self.batch_size]
                future = executor.submit(processoGlobal, lote)
                
                try:
                    resultado_lote = future.result()
                    for status, dados in resultado_lote.items():
                        resultado[status].extend(dados)
                    
                    processados += len(lote)
                    if progresso_callback:
                        progresso_callback(processados, total)
                except Exception:
                    pass

        return resultado

def processoGlobal(lote_arquivos):
    from collections import defaultdict
    from src.service.cfeParse import parseCfe
    import os

    resultado_local = defaultdict(list)

    for arquivo in lote_arquivos:
        try:
            if not arquivo.lower().endswith('.xml'):
                resultado_local["fora_padrao"].append(os.path.basename(arquivo))
                continue

            cfe = parseCfe(arquivo)
            if cfe is None:
                resultado_local["fora_padrao"].append(os.path.basename(arquivo))
                continue

            status = getattr(cfe, "status", "fora_padrao")
            if status == "fora_padrao":
                resultado_local["fora_padrao"].append(os.path.basename(arquivo))
            else:
                resultado_local[status].append(cfe)

        except Exception:
            resultado_local["fora_padrao"].append(os.path.basename(arquivo))

    return dict(resultado_local)