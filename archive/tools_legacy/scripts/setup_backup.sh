#!/bin/bash
# ================================================================
# Setup automated backups for Veyra
# Run this once to configure nightly backups
# ================================================================

set -e

echo "🏦 Veyra Backup Setup"
echo "================================="
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_SCRIPT="$SCRIPT_DIR/backup.sh"

# Check if backup script exists
if [ ! -f "$BACKUP_SCRIPT" ]; then
    echo "❌ Backup script not found at $BACKUP_SCRIPT"
    exit 1
fi

# Make backup script executable
chmod +x "$BACKUP_SCRIPT"
echo "✅ Backup script is executable"

# Check for .env file
ENV_FILE="$(dirname "$SCRIPT_DIR")/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "⚠️  .env file not found at $ENV_FILE"
    echo "   Creating template .env file..."
    
    cat > "$ENV_FILE" << 'EOF'
# Veyra Environment Configuration

# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=finmaster
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis
REDIS_PASSWORD=your_redis_password

# Backup Configuration
BACKUP_PASSPHRASE=your_secure_backup_passphrase_min_16_chars

# Optional: Cloud Storage
# RCLONE_REMOTE=gdrive:Backups
# Or: RCLONE_REMOTE=s3:mybucket/backups
EOF

    echo "✅ Created template .env file"
    echo "⚠️  Please edit .env and set your secure passwords"
    echo ""
fi

# Prompt for backup passphrase if not set
if ! grep -q "BACKUP_PASSPHRASE=" "$ENV_FILE" 2>/dev/null || grep -q "BACKUP_PASSPHRASE=your_secure" "$ENV_FILE" 2>/dev/null; then
    echo "🔐 Setting up backup encryption passphrase..."
    echo "   This will be used to encrypt your backups."
    echo "   Minimum 16 characters recommended."
    echo ""
    
    read -sp "Enter backup passphrase: " PASSPHRASE
    echo ""
    
    if [ ${#PASSPHRASE} -lt 8 ]; then
        echo "❌ Passphrase too short (minimum 8 characters)"
        exit 1
    fi
    
    # Update .env file
    if grep -q "BACKUP_PASSPHRASE=" "$ENV_FILE" 2>/dev/null; then
        # Update existing
        sed -i "s/BACKUP_PASSPHRASE=.*/BACKUP_PASSPHRASE=$PASSPHRASE/" "$ENV_FILE" 2>/dev/null || \
        sed -i.bak "s/BACKUP_PASSPHRASE=.*/BACKUP_PASSPHRASE=$PASSPHRASE/" "$ENV_FILE"
    else
        # Add new
        echo "BACKUP_PASSPHRASE=$PASSPHRASE" >> "$ENV_FILE"
    fi
    
    echo "✅ Backup passphrase configured"
fi

# Test backup directory
echo ""
echo "📁 Testing backup directory..."
BACKUP_DIR="$HOME/veyra-backups"
mkdir -p "$BACKUP_DIR"

if [ -d "$BACKUP_DIR" ]; then
    echo "✅ Backup directory: $BACKUP_DIR"
    df -h "$BACKUP_DIR" | tail -1
else
    echo "❌ Failed to create backup directory"
    exit 1
fi

# Test backup script
echo ""
echo "🧪 Testing backup script..."
if "$BACKUP_SCRIPT" --dry-run 2>/dev/null; then
    echo "✅ Backup script test passed"
else
    echo "⚠️  Backup script test had issues (this is normal if PostgreSQL isn't running)"
fi

# Offer to setup cron job
echo ""
echo "⏰ Automated Backup Schedule"
echo "==========================="
echo "Would you like to schedule automatic nightly backups at 2:00 AM?"
read -p "Setup cron job? (y/n): " SETUP_CRON

if [[ $SETUP_CRON =~ ^[Yy]$ ]]; then
    # Check if cron job already exists
    if crontab -l 2>/dev/null | grep -q "$BACKUP_SCRIPT"; then
        echo "⚠️  Backup cron job already exists"
        echo "   Current crontab entry:"
        crontab -l | grep "$BACKUP_SCRIPT"
    else
        # Add cron job
        (crontab -l 2>/dev/null; echo "0 2 * * * $BACKUP_SCRIPT >> $HOME/veyra-backups/cron.log 2>&1") | crontab -
        echo "✅ Cron job added: 0 2 * * * (daily at 2:00 AM)"
    fi
    
    echo ""
    echo "📋 Current crontab entries:"
    crontab -l | grep -E "(veyra|backup)" || echo "   (no entries yet)"
else
    echo "ℹ️  Skipping cron setup"
    echo "   To manually run backups: $BACKUP_SCRIPT"
fi

# Cloud backup info
echo ""
echo "☁️  Cloud Backup (Optional)"
echo "=========================="
echo "To enable cloud backups, install and configure rclone:"
echo ""
echo "1. Install rclone:"
echo "   curl https://rclone.org/install.sh | sudo bash"
echo ""
echo "2. Configure rclone:"
echo "   rclone config"
echo ""
echo "3. Add to .env:"
echo "   RCLONE_REMOTE=gdrive:Backups"
echo "   or"
echo "   RCLONE_REMOTE=s3:mybucket/backups"
echo ""

# Summary
echo ""
echo "🎉 Backup Setup Complete!"
echo "========================"
echo ""
echo "Backup Location: $BACKUP_DIR"
echo "Backup Script:   $BACKUP_SCRIPT"
echo "Schedule:        $(crontab -l 2>/dev/null | grep "$BACKUP_SCRIPT" | awk '{print $1, $2}' || echo 'Not scheduled')"
echo ""
echo "Manual backup command:"
echo "  $BACKUP_SCRIPT"
echo ""
echo "View backup log:"
echo "  tail -f $BACKUP_DIR/backup.log"
echo ""
echo "To restore from backup, see instructions in:"
echo "  $BACKUP_DIR/backup.log"
echo ""
