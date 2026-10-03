"""
Script de Migración de Contraseñas a Bcrypt (Fase 2)
Proyecto: Control de Accesos FIUSAC / EMI

Este script es idempotente:
- Crea un respaldo preventivo de la base de datos antes de modificar nada.
- Recorre todos los usuarios de 'access_requests'.
- Si la contraseña ya es un hash de Bcrypt ($2b$ o $2a$), la omite.
- Si la contraseña está en texto plano, la hashea de forma segura con Bcrypt.
"""

import os
import shutil
from datetime import datetime
from database import SessionLocal
import models
import auth

DB_PATH = os.path.join(os.path.dirname(__file__), "accesos_EMI.db")

def crear_respaldo():
    if os.path.exists(DB_PATH):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{DB_PATH}.backup_{timestamp}"
        shutil.copy2(DB_PATH, backup_path)
        print(f"📦 Respaldo preventivo creado exitosamente:\n   -> {backup_path}")
        return backup_path
    else:
        print(f"⚠️  No se encontró la base de datos en: {DB_PATH}")
        return None

def migrar_contrasenas():
    print("=" * 60)
    print("🔒 INICIANDO MIGRACIÓN DE CONTRASEÑAS A BCRYPT")
    print("=" * 60)
    
    # 1. Crear copia de seguridad
    backup = crear_respaldo()
    if not backup:
        print("❌ Operación abortada: no se pudo crear el respaldo.")
        return

    db = SessionLocal()
    try:
        # 2. Consultar todos los registros de usuarios
        usuarios = db.query(models.AccessRequest).all()
        total_usuarios = len(usuarios)
        migrados = 0
        ya_protegidos = 0
        sin_password = 0

        print(f"\nAnalizando {total_usuarios} registros de usuarios en 'access_requests'...\n")

        for u in usuarios:
            pwd = u.password
            if not pwd:
                sin_password += 1
                continue
            
            # Verificar si ya es un hash de Bcrypt
            if pwd.startswith(("$2b$", "$2a$")) and len(pwd) == 60:
                ya_protegidos += 1
                print(f"   [OK - YA PROTEGIDO] Usuario ID {u.id} ('{u.usuario}'): Hash Bcrypt válido.")
            else:
                # Está en texto plano -> lo hasheamos
                hash_nuevo = auth.get_password_hash(pwd)
                u.password = hash_nuevo
                migrados += 1
                print(f"   [MIGRADO A BCRYPT]  Usuario ID {u.id} ('{u.usuario}'): '{pwd}' -> {hash_nuevo[:12]}...")

        # 3. Verificar también la tabla admins
        admins = db.query(models.Admin).all()
        admins_migrados = 0
        for adm in admins:
            if adm.hashed_password and not adm.hashed_password.startswith(("$2b$", "$2a$")):
                adm.hashed_password = auth.get_password_hash(adm.hashed_password)
                admins_migrados += 1
                print(f"   [MIGRADO ADMIN] Admin ID {adm.id} ('{adm.username}') migrado a Bcrypt.")

        # Guardar cambios
        db.commit()

        print("\n" + "=" * 60)
        print("📊 RESUMEN DE LA MIGRACIÓN")
        print("=" * 60)
        print(f" Total usuarios evaluados:     {total_usuarios}")
        print(f" ✅ Nuevos usuarios migrados:  {migrados}")
        print(f" 🛡️  Usuarios ya protegidos:    {ya_protegidos}")
        if sin_password > 0:
            print(f" ℹ️  Usuarios sin contraseña:    {sin_password}")
        if admins_migrados > 0:
            print(f" 👤 Admins migrados:           {admins_migrados}")
        print("=" * 60)
        print("🎉 ¡Migración completada con éxito!")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error durante la migración: {e}")
        print("🔄 Se aplicó rollback en la base de datos.")
    finally:
        db.close()

if __name__ == "__main__":
    migrar_contrasenas()
