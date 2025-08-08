"""
Sistema de log para debug do Sheets2Anki.
Salva todas as mensagens de debug em arquivo para análise posterior.
"""

import os
import time
from datetime import datetime

class DebugLogger:
    def __init__(self, log_file="debug_note_type_ids.log"):
        self.log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), log_file)
        self.enabled = True
        
    def log(self, message, prefix="DEBUG"):
        """
        Registra uma mensagem de debug tanto no console quanto no arquivo.
        
        Args:
            message (str): Mensagem para registrar
            prefix (str): Prefixo da mensagem (ex: "NOTE_TYPE_IDS", "SYNC")
        """
        if not self.enabled:
            return
            
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Com milissegundos
        formatted_message = f"[{timestamp}] [{prefix}] {message}"
        
        # Imprimir no console (para aparecer no Anki)
        print(formatted_message)
        
        # Salvar no arquivo
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(formatted_message + "\n")
                f.flush()  # Forçar escrita imediata
        except Exception as e:
            print(f"[DEBUG_LOGGER] Erro ao escrever log: {e}")
    
    def clear_log(self):
        """Limpa o arquivo de log."""
        try:
            with open(self.log_path, "w", encoding="utf-8") as f:
                f.write(f"=== LOG INICIADO EM {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        except Exception as e:
            print(f"[DEBUG_LOGGER] Erro ao limpar log: {e}")
    
    def get_log_path(self):
        """Retorna o caminho completo do arquivo de log."""
        return self.log_path

# Instância global do logger
debug_logger = DebugLogger()

def log_debug(message, prefix="DEBUG"):
    """Função conveniente para logging."""
    debug_logger.log(message, prefix)

def clear_debug_log():
    """Função conveniente para limpar o log."""
    debug_logger.clear_log()

def get_debug_log_path():
    """Função conveniente para obter o caminho do log."""
    return debug_logger.get_log_path()
