# 💳 SEPA Request-to-Pay – Prototipo Full Stack

Prototipo *full stack* desarrollado para un TFG que **emula el ciclo completo del servicio SEPA Request-to-Pay (SRTP)**, demostrando cómo supera las limitaciones del SEPA Direct Debit en pagos digitales.

## 🛠 Tecnologías
- **Backend:** Python 3.12 · Flask · Flask-SocketIO · SQLAlchemy · SQLite  
- **Frontend:** HTML5 · CSS3 · JavaScript  
- **Docs:** Memoria en LaTeX · Pruebas automatizadas con Postman

## 🚀 Funcionalidades clave
- Creación, validación y enrutado de solicitudes RTP  
- Decisión del pagador (aceptar/rechazar) con notificaciones en tiempo real  
- Registro seguro y trazable de cambios de estado mediante hashes SHA-256  
- Arquitectura modular: Gateway REST · Service RTP · Notification Hub

## 📂 Estructura
- backend/ # API REST y lógica de negocio
- frontend/ # Interfaz web para simular actores RTP
- MemoriaTFG/ # Documentación y memoria en LaTeX
  
## 🎯 Objetivo
Validar **SRTP** como alternativa ágil, segura y trazable al SDD, proporcionando una base flexible para futuras integraciones y escenarios de producción.
