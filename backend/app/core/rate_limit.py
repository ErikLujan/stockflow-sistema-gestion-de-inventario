"""
Módulo de limitación de tasa (Rate Limiting).
Proporciona la instancia principal de slowapi para proteger los endpoints
contra ataques de denegación de servicio (DoS) y fuerza bruta.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)