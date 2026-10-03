"""
Script de Migración de PINs a Cifrado Simétrico Fernet (Fase 3)
Proyecto: Control de Accesos FIUSAC / EMI

Este script es idempotente:
- Crea un respaldo preventivo de la base de datos antes de modificar nada.
- Recorre todos los usuarios en 'access_requests'.
- Si 'pin_acceso' ya está cifrado con Fernet, lo omite.
- Si 'pin_acceso' está en texto plano (ej. 4 dígitos), lo cifra con Fernet y guarda los cambios.
"""

import os
import shutil
from datetime import datetime
from database import SessionLocal, DB_FILE
import models
import crypto_utils

def crear_respaldo():
    if os.path.exists(DB_FILE):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{DB_FILE}.backup_pins_{timestamp}"
        shutil.copy2(DB_FILE, backup_path)
        print(f"📦 Respaldo preventivo creado exitosamente:\n   -> {backup_path}")
        return backup_path
    else:
        print(f"⚠️  No se encontró la base de datos en: {DB_FILE}")
        return None

def migrar_pins():
    print("=" * 60)
    print("🔐 INICIANDO MIGRACIÓN DE PINS A CIFRADO SIMÉTRICO (FERNET)")
    print("=" * 60)

    backup = crear_respaldo()
    if not backup:
        print("❌ Operación abortada: no se pudo crear el respaldo.")
        return

    db = SessionLocal()
    try:
        solicitudes = db.query(models.AccessRequest).all()
        total = len(solicitudes)
        migrados = 0
        ya_cifrados = 0
        sin_pin = 0

        print(f"\nAnalizando {total} registros en 'access_requests'...\n")

        for req in solicitudes:
            # Leemos directamente el valor crudo en la columna de la BD
            raw_pin = req._pin_acceso
            if not raw_pin:
                sin_pin += 1
                continue

            if crypto_utils.is_encrypted(raw_pin):
                ya_cifrados += 1
                print(f"   [OK - YA CIFRADO]  ID {req.id} ('{req.usuario}'): PIN ya protegido.")
            else:
                # El PIN está en texto plano -> lo asignamos a la property, que lo cifrará automáticamente
                pin_plano = str(raw_pin).strip()
                req.pin_acceso = pin_plano # El setter ejecuta encrypt_pin
                migrados += 1
                print(f"   [CIFRADO APLICADO] ID {req.id} ('{req.usuario}'): '{pin_plano}' -> {req._pin_acceso[:15]}...")

        db.commit()

        print("\n" + "=" * 60)
        print("📊 RESUMEN DE MIGRACIÓN DE PINS")
        print("=" * 60)
        print(f" Total registros evaluados: {total}")
        print(f" 🔐 PINs recién cifrados:    {migrados}")
        print(f" 🛡️  PINs ya cifrados:        {ya_cifrados}")
        print(f" ℹ️  Registros sin PIN:       {sin_pin}")
        print("=" * 60)
        print("🎉 ¡Migración de PINs completada con éxito!")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error durante la migración de PINs: {e}")
        print("🔄 Se aplicó rollback en la base de datos.")
    finally:
        db.close()

if __name__ == "__main__":
    migrar_pins()
