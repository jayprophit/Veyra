#!/bin/bash
# SSL Certificate Automation Script
# Supports: Let's Encrypt (Free), Cloudflare Origin, Self-signed (dev)

set -e

DOMAIN=${1:-"localhost"}
EMAIL=${2:-"admin@localhost"}
MODE=${3:-"letsencrypt"}  # Options: letsencrypt, cloudflare, selfsigned

LOG_FILE="/var/log/ssl_automation.log"
CERT_DIR="/etc/letsencrypt/live/$DOMAIN"

echo "========================================"
echo "SSL Certificate Automation"
echo "Domain: $DOMAIN"
echo "Mode: $MODE"
echo "========================================"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

install_certbot() {
    log "Installing Certbot..."
    if command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y certbot python3-certbot-nginx
    elif command -v yum &> /dev/null; then
        sudo yum install -y certbot python3-certbot-nginx
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y certbot python3-certbot-nginx
    else
        log "ERROR: Package manager not supported"
        exit 1
    fi
}

setup_letsencrypt() {
    log "Setting up Let's Encrypt certificate..."
    
    # Check if certbot is installed
    if ! command -v certbot &> /dev/null; then
        install_certbot
    fi
    
    # Request certificate
    sudo certbot certonly --standalone \
        -d $DOMAIN \
        --agree-tos \
        --non-interactive \
        --email $EMAIL \
        --preferred-challenges http
    
    if [ $? -eq 0 ]; then
        log "Certificate obtained successfully!"
        
        # Setup auto-renewal
        setup_renewal
        
        # Display certificate info
        display_cert_info
    else
        log "ERROR: Failed to obtain certificate"
        exit 1
    fi
}

setup_cloudflare() {
    log "Setting up Cloudflare Origin certificate..."
    
    echo ""
    echo "Instructions for Cloudflare SSL:"
    echo "1. Log in to Cloudflare dashboard"
    echo "2. Select your domain: $DOMAIN"
    echo "3. Go to SSL/TLS > Origin Server"
    echo "4. Click 'Create Certificate'"
    echo "5. Choose 'Let Cloudflare generate a private key and a CSR'"
    echo "6. Save the certificate and key to:"
    echo "   - /etc/ssl/certs/cloudflare_origin.pem"
    echo "   - /etc/ssl/private/cloudflare_origin.key"
    echo ""
    echo "Benefits:"
    echo "- Free unlimited SSL"
    echo "- 15-year validity"
    echo "- Full encryption between Cloudflare and origin"
}

setup_selfsigned() {
    log "Creating self-signed certificate for development..."
    
    CERT_PATH="./ssl/dev"
    mkdir -p $CERT_PATH
    
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout $CERT_PATH/private.key \
        -out $CERT_PATH/certificate.crt \
        -subj "/C=US/ST=State/L=City/O=Veyra/CN=$DOMAIN"
    
    log "Self-signed certificate created at $CERT_PATH"
    log "Valid for 365 days"
}

setup_renewal() {
    log "Setting up auto-renewal..."
    
    # Test renewal
    sudo certbot renew --dry-run
    
    # Add to crontab if not exists
    if ! sudo crontab -l | grep -q "certbot renew"; then
        (sudo crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet --deploy-hook 'systemctl reload nginx'") | sudo crontab -
        log "Auto-renewal cron job added (runs daily at 3 AM)"
    fi
}

display_cert_info() {
    echo ""
    echo "========================================"
    echo "Certificate Information"
    echo "========================================"
    
    if [ -f "$CERT_DIR/fullchain.pem" ]; then
        openssl x509 -in $CERT_DIR/fullchain.pem -noout -text | grep -E "Subject:|Issuer:|Not Before|Not After"
    fi
    
    echo ""
    echo "Certificate files:"
    echo "  - Certificate: $CERT_DIR/fullchain.pem"
    echo "  - Private Key: $CERT_DIR/privkey.pem"
    echo "  - Chain: $CERT_DIR/chain.pem"
    echo ""
    echo "Next renewal check:"
    certbot certificates
}

case $MODE in
    letsencrypt)
        setup_letsencrypt
        ;;
    cloudflare)
        setup_cloudflare
        ;;
    selfsigned)
        setup_selfsigned
        ;;
    *)
        echo "Usage: $0 <domain> <email> <mode>"
        echo "Modes: letsencrypt, cloudflare, selfsigned"
        exit 1
        ;;
esac

echo ""
echo "SSL setup complete!"
