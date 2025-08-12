import os
import time
from collections import defaultdict
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import cpu_count
from typing import List, Dict, Optional, Callable
import gc
import psutil

class ExtratorService:
    def __init__(self, max_workers=None, batch_size=150):
        available_memory = psutil.virtual_memory().available / (1024**3)
        cpu_cores = cpu_count()
        
        if available_memory < 4:
            self.max_workers = min(cpu_cores, 4)
            self.batch_size = 15
        elif available_memory < 6:
            self.max_workers = min(cpu_cores * 2, 8)
            self.batch_size = 20
        else:
            self.max_workers = max_workers or min(cpu_cores * 2, 12)
            self.batch_size = batch_size
            
        print(f"Configuração: {self.max_workers} workers, lotes de {self.batch_size}")
        self._cache_parse = {}

    def processarPasta(self, pasta_path: str, progresso_callback=None) -> Dict:
        tempo_inicio = time.time()
        
        if progresso_callback:
            progresso_callback(0, 1)

        arquivos = self._listarArquivos(pasta_path)
        if not arquivos:
            if progresso_callback:
                progresso_callback(0, 1)
            return {}

        total = len(arquivos)
        print(f"Encontrados {total} arquivos XML para processamento")
        
        if progresso_callback:
            progresso_callback(0, total)

        resultado = self._processoThreads(arquivos, total, progresso_callback)

        tempo_total = time.time() - tempo_inicio
        print(f"Processamento concluído em {tempo_total:.2f}s ({total/tempo_total:.1f} arquivos/s)")
        
        if progresso_callback:
            progresso_callback(total, total)

        return dict(resultado)

    def _listarArquivos(self, pasta_path: str) -> List[str]:
        try:
            pasta = Path(pasta_path)
            if not pasta.exists() or not pasta.is_dir():
                return []
            
            arquivos = []
            for arquivo in pasta.iterdir():
                if arquivo.is_file() and arquivo.suffix.lower() == '.xml':
                    arquivos.append(str(arquivo))
            
            print(f"Debug: Encontrados {len(arquivos)} arquivos XML")
            return arquivos
            
        except Exception as e:
            print(f"Erro ao listar arquivos: {e}")
            return []

    def _processoThreads(self, arquivos: List[str], total: int, progresso_callback=None) -> defaultdict:
        resultado = defaultdict(list)
        processados = 0
        
        print(f"Configurando {self.max_workers} workers para processamento...")
        
        lotes = [arquivos[i:i + self.batch_size] for i in range(0, len(arquivos), self.batch_size)]
        
        print(f"Divididos em {len(lotes)} lotes de até {self.batch_size} arquivos cada")
        
        with ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="CFe") as executor:
            print("Submetendo lotes para processamento...")
            
            future_to_lote = {}
            for i, lote in enumerate(lotes):
                future = executor.submit(self._processarLote, lote)
                future_to_lote[future] = lote
                
                if (i + 1) % 10 == 0:
                    print(f"Submetidos {i + 1}/{len(lotes)} lotes...")
                    if progresso_callback:
                        progresso_callback(min(i, total // 20), total)
            
            print(f"Todos os {len(lotes)} lotes submetidos. Aguardando processamento...")
            
            time.sleep(0.1)
            
            lotes_completados = 0
            for future in as_completed(future_to_lote):
                try:
                    resultado_lote = future.result(timeout=45)
                    
                    for status, dados in resultado_lote.items():
                        resultado[status].extend(dados)
                    
                    processados += len(future_to_lote[future])
                    lotes_completados += 1
                    
                    if lotes_completados % 5 == 0:
                        print(f"Completados {lotes_completados}/{len(lotes)} lotes ({processados}/{total} arquivos)")
                    
                    if progresso_callback:
                        progresso_callback(processados, total)
                        
                except Exception as e:
                    lote_com_erro = future_to_lote[future]
                    print(f"Erro no lote {lotes_completados + 1}: {e}")
                    for arquivo in lote_com_erro:
                        resultado["fora_padrao"].append(os.path.basename(arquivo))
                    
                    processados += len(lote_com_erro)
                    lotes_completados += 1
                    
                    if progresso_callback:
                        progresso_callback(processados, total)

        return resultado

    def _processarLote(self, lote_arquivos: List[str]) -> Dict:
        resultado_local = defaultdict(list)
        
        for arquivo in lote_arquivos:
            try:
                if not arquivo.lower().endswith('.xml'):
                    resultado_local["fora_padrao"].append(os.path.basename(arquivo))
                    continue
                
                try:
                    stat = os.stat(arquivo)
                    if stat.st_size == 0:
                        resultado_local["fora_padrao"].append(os.path.basename(arquivo))
                        continue
                except (OSError, FileNotFoundError):
                    resultado_local["fora_padrao"].append(os.path.basename(arquivo))
                    continue
                
                cfe = self._parseCfe(arquivo)
                if cfe is None:
                    resultado_local["fora_padrao"].append(os.path.basename(arquivo))
                    continue
                
                status = getattr(cfe, "status", "fora_padrao")
                if status == "fora_padrao":
                    resultado_local["fora_padrao"].append(os.path.basename(arquivo))
                else:
                    resultado_local[status].append(cfe)
                    
            except Exception as e:
                resultado_local["fora_padrao"].append(os.path.basename(arquivo))
        
        return dict(resultado_local)

    def _parseCfe(self, arquivo: str):
        try:
            from src.service.cfeParse import parseCfe
            
            if arquivo in self._cache_parse:
                return self._cache_parse[arquivo]
            
            cfe = parseCfe(arquivo)
            
            if cfe and len(self._cache_parse) < 200:
                self._cache_parse[arquivo] = cfe
                
            return cfe
            
        except Exception:
            return None

    def limparCache(self):
        self._cache_parse.clear()
        gc.collect()

    def listarArquivos(self, pasta_path: str) -> List[str]:
        return self._listarArquivos(pasta_path)

    def processarArquivos(self, lote_arquivos: List[str]) -> Dict:
        return self._processarLote(lote_arquivos)