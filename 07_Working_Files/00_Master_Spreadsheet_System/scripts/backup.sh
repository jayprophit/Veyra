#!/bin/bash
# ================================================================
# Financial Master — Automated Encrypted Backup Script
# Merged from FinOS
# Runs nightly at 02:00 via cron
# Schedule: crontab -e → 0 2 * * * /path/to/backup.sh
# ================================================================

set -e

FINOS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$HOME/financial-master-backups"
LOG_FILE="$BACKUP_DIR/backup.log"

mkdir -p "$BACKUP_DIR"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"; }

log "🏦 Starting Financial Master backup..."

# ── Load environment ────────────────────────────────────────────
if [ -f "$FINOS_DIR/.env" ]; then
    set -a && source "$FINOS_DIR/.env" && set +a
fi

if [ -z "$BACKUP_PASSPHRASE" ]; then
    log "⚠️  BACKUP_PASSPHRASE not set — using default (INSECURE - set in .env)"
    BACKUP_PASSPHRASE="financial-master-default"
fi

# ── PostgreSQL dump ─────────────────────────────────────────────
log "Dumping PostgreSQL..."

# Check if using Docker or local PostgreSQL
if command -v docker &> /dev/null && docker ps | grep -q postgres; then
    # Docker PostgreSQL
    docker exec postgres pg_dump \
        -U "${POSTGRES_USER:-postgres}" \
        "${POSTGRES_DB:-finmaster}" \
        | gzip \
        | openssl enc -aes-256-cbc -pbkdf2 -salt \
            -pass pass:"$BACKUP_PASSPHRASE" \
            -out "$BACKUP_DIR/postgres-$DATE.sql.gz.enc"
else
    # Local PostgreSQL
    pg_dump \
        -U "${POSTGRES_USER:-postgres}" \
        -h "${POSTGRES_HOST:-localhost}" \
        -p "${POSTGRES_PORT:-5432}" \
        "${POSTGRES_DB:-finmaster}" \
        | gzip \
        | openssl enc -aes-256-cbc -pbkdf2 -salt \
            -pass pass:"$BACKUP_PASSPHRASE" \
            -out "$BACKUP_DIR/postgres-$DATE.sql.gz.enc" 2>/dev/null || {
                log "❌ PostgreSQL dump failed - check connection settings"
                exit 1
            }
fi

log "✅ PostgreSQL dump complete: postgres-$DATE.sql.gz.enc"

# ── Redis backup (if applicable) ────────────────────────────────
if command -v redis-cli &> /dev/null; then
    log "Dumping Redis..."
    redis-cli BGSAVE 2>/dev/null || true
    # Wait for BGSAVE to complete
    sleep 5
    log "✅ Redis dump initiated"
fi

# ── Full stack backup ────────────────────────────────────────────
log "Creating full stack archive..."
tar -czf - \
    --exclude "$FINOS_DIR/node_modules" \
    --exclude "$FINOS_DIR/__pycache__" \
    --exclude "$FINOS_DIR/*.pyc" \
    --exclude "$FINOS_DIR/.git" \
    --exclude "$FINOS_DIR/.pytest_cache" \
    --exclude "$FINOS_DIR/dashboard/node_modules" \
    --exclude "$FINOS_DIR/dashboard/build" \
    --exclude "$FINOS_DIR/dashboard/dist" \
    "$FINOS_DIR" \
    | openssl enc -aes-256-cbc -pbkdf2 -salt \
        -pass pass:"$BACKUP_PASSPHRASE" \
        -out "$BACKUP_DIR/finmaster-full-$DATE.tar.gz.enc"

log "✅ Full archive complete: finmaster-full-$DATE.tar.gz.enc"

# ── Upload to remote (if rclone configured) ─────────────────────
if command -v rclone &> /dev/null && [ -n "$RCLONE_REMOTE" ]; then
    log "Uploading to $RCLONE_REMOTE..."
    
    # Create dated folder
    rclone mkdir "$RCLONE_REMOTE/finmaster-backups/$DATE" 2>/dev/null || true
    
    # Upload backups
    rclone copy "$BACKUP_DIR/postgres-$DATE.sql.gz.enc" "$RCLONE_REMOTE/finmaster-backups/$DATE/"
    rclone copy "$BACKUP_DIR/finmaster-full-$DATE.tar.gz.enc" "$RCLONE_REMOTE/finmaster-backups/$DATE/"
    
    log "✅ Remote upload complete"
else
    log "ℹ️  rclone not configured — backup stored locally only"
    log "   To enable cloud backup:"
    log "   1. Install rclone: https://rclone.org/install/"
    log "   2. Configure: rclone config"
    log "   3. Set RCLONE_REMOTE in .env (e.g., RCLONE_REMOTE=gdrive:Backups)"
fi

# ── Cleanup old local backups (keep 30 days) ────────────────────
find "$BACKUP_DIR" -name "*.enc" -mtime +30 -delete 2>/dev/null || true
log "✅ Old backups cleaned up (30+ days)"

# ── Summary ─────────────────────────────────────────────────────
BACKUP_SIZE=$(du -h "$BACKUP_DIR" | tail -1 | cut -f1)
log "🎉 Backup complete! Total backup dir size: $BACKUP_SIZE"
log "   Location: $BACKUP_DIR"
log "   Files:"
ls -lh "$BACKUP_DIR"/*$DATE* 2>/dev/null | while read line; do
    log "     $line"
done

# ── Restore instructions ─────────────────────────────────────────
cat >> "$LOG_FILE" << 'RESTORE'

================================================================
RESTORE INSTRUCTIONS
================================================================

# Restore PostgreSQL from backup:
openssl enc -d -aes-256-cbc -pbkdf2 -in postgres-DATE.sql.gz.enc \
    -pass pass:YOUR_PASSPHRASE | gunzip | \
    psql -U postgres -d finmaster

# Or with Docker:
openssl enc -d -aes-256-cbc -pbkdf2 -in postgres-DATE.sql.gz.enc \
    -pass pass:YOUR_PASSPHRASE | gunzip | \
    docker exec -i postgres psql -U postgres -d finmaster

# Restore full stack:
openssl enc -d -aes-256-cbc -pbkdf2 -in finmaster-full-DATE.tar.gz.enc \
    -pass pass:YOUR_PASSPHRASE | tar -xzf - -C /

================================================================

RESTORE
