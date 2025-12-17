"""
Cache de sincronización para evitar llamadas excesivas a Google Sheets API.
Mantiene un timestamp de la última sincronización y solo permite sync si pasó suficiente tiempo.
Thread-safe usando threading.Lock.
"""
import time
import threading

# Variable global para cache de sincronización con lock para thread-safety
_LAST_SYNC_TIME = None
_SYNC_LOCK = threading.Lock()
SYNC_CACHE_SECONDS = 60  # 1 minuto de cache

def should_sync():
    """
    Devuelve True si pasó suficiente tiempo desde la última sync.
    Thread-safe.
    """
    with _SYNC_LOCK:
        if _LAST_SYNC_TIME is None:
            return True
        
        elapsed = time.time() - _LAST_SYNC_TIME
        return elapsed > SYNC_CACHE_SECONDS

def mark_synced():
    """
    Marca que se realizó una sincronización.
    Thread-safe.
    """
    global _LAST_SYNC_TIME
    with _SYNC_LOCK:
        _LAST_SYNC_TIME = time.time()

def force_sync():
    """
    Fuerza que la próxima llamada sincronice (resetea el cache).
    Thread-safe.
    """
    global _LAST_SYNC_TIME
    with _SYNC_LOCK:
        _LAST_SYNC_TIME = None

def get_cache_age():
    """
    Devuelve cuántos segundos pasaron desde la última sincronización.
    Retorna None si nunca se sincronizó.
    Thread-safe.
    """
    with _SYNC_LOCK:
        if _LAST_SYNC_TIME is None:
            return None
        return time.time() - _LAST_SYNC_TIME
