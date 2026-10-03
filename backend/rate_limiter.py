"""
Módulo de Rate Limiting y Control de Fuerza Bruta (Fase 5)
Proyecto: Control de Accesos FIUSAC / EMI

Protege los endpoints críticos (teclado de cerradura, logins) limitando
el número de intentos fallidos consecutivos a 5. Tras 5 fallos, aplica
un bloqueo temporal de 60 segundos por IP/identificador.
"""

import time
from typing import Tuple, Dict

MAX_ATTEMPTS = 5
BLOCK_DURATION_SECONDS = 60

class RateLimiter:
    def __init__(self, max_attempts: int = MAX_ATTEMPTS, block_duration: int = BLOCK_DURATION_SECONDS):
        self.max_attempts = max_attempts
        self.block_duration = block_duration
        # Estructura: { key: { "attempts": int, "blocked_until": float, "last_attempt": float } }
        self._records: Dict[str, dict] = {}

    def _cleanup_if_expired(self, key: str) -> None:
        """Limpia registros viejos si ya expiró el tiempo de bloqueo o inactividad."""
        record = self._records.get(key)
        if not record:
            return
        now = time.time()
        # Si el bloqueo ya expiró hace más de la duración del bloqueo, resetear
        if record.get("blocked_until") and now >= record["blocked_until"]:
            del self._records[key]
        elif now - record.get("last_attempt", 0) > (self.block_duration * 2):
            del self._records[key]

    def check_is_blocked(self, key: str) -> Tuple[bool, int]:
        """
        Comprueba si la clave está actualmente bloqueada.
        Retorna: (está_bloqueado: bool, segundos_restantes: int)
        """
        self._cleanup_if_expired(key)
        record = self._records.get(key)
        if not record:
            return False, 0

        blocked_until = record.get("blocked_until")
        if blocked_until:
            now = time.time()
            if now < blocked_until:
                remaining = int(blocked_until - now) + 1
                return True, remaining
            else:
                # El bloqueo acaba de terminar
                del self._records[key]
                return False, 0

        return False, 0

    def record_failure(self, key: str) -> Tuple[bool, int, int]:
        """
        Registra un intento fallido.
        Retorna: (ha_sido_bloqueado: bool, intentos_restantes: int, segundos_bloqueo: int)
        """
        now = time.time()
        record = self._records.get(key, {"attempts": 0, "blocked_until": None, "last_attempt": now})
        record["attempts"] += 1
        record["last_attempt"] = now

        if record["attempts"] >= self.max_attempts:
            record["blocked_until"] = now + self.block_duration
            self._records[key] = record
            return True, 0, self.block_duration

        self._records[key] = record
        remaining_attempts = self.max_attempts - record["attempts"]
        return False, remaining_attempts, 0

    def reset(self, key: str) -> None:
        """Reinicia el contador tras una autenticación exitosa."""
        if key in self._records:
            del self._records[key]

# Instancia global del limitador
limiter = RateLimiter(max_attempts=5, block_duration=60)
