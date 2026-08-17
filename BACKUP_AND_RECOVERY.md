# Política de Backup e Recuperação de Desastres (DRP) — LHCRM Pro

## 1. Estratégia de Backup

Para garantir continuidade de negócios e RPO (Recovery Point Objective) inferior a 1 hora com RTO (Recovery Time Objective) inferior a 30 minutos:

1. **Backups Automáticos Contínuos (PITR - Point in Time Recovery):**
   - No Supabase / PostgreSQL gerenciado, habilitar retenção diária de WAL (Write-Ahead Logging) por 7 a 30 dias.
2. **Backups Lógicos Diários (`pg_dump`):**
   - Script automatizado diário gerando dump compactado e criptografado com chave AES-256 e upload para bucket seguro (AWS S3 ou Cloudflare R2).

---

## 2. Script de Backup Lógico Automatizado

```bash
#!/bin/bash
set -e

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="/backups/lhcrm_db_${TIMESTAMP}.sql.gz"

echo "Iniciando backup do banco de dados..."
pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" --no-owner --clean | gzip > "$BACKUP_FILE"

echo "Backup concluído com sucesso: $BACKUP_FILE"

# Upload para armazenamento em nuvem com retenção de 30 dias
# aws s3 cp "$BACKUP_FILE" s3://lhcrm-backups/
```

---

## 3. Procedimento de Restauração de Emergência

Para restaurar um backup em um banco de dados novo:

```bash
# 1. Descompactar e restaurar
gunzip -c /backups/lhcrm_db_YYYYMMDD_HHMMSS.sql.gz | psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME"

# 2. Executar migrações para garantir paridade com a versão da aplicação
alembic upgrade head

# 3. Validar integridade dos dados e contadores
python -m app.cli check-health
```
