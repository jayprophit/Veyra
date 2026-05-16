#!/usr/bin/env python3
"""
Veyra Docker Health Check & Diagnostic Tool
Provides comprehensive system diagnostics and automation
"""

import subprocess
import json
import sys
import time
from pathlib import Path

class VeyraDocker:
    def __init__(self):
        self.containers = [
            'veyra-web',
            'veyra-api',
            'veyra-postgres',
            'veyra-redis',
            'veyra-qdrant',
            'veyra-adminer'
        ]
    
    def run_cmd(self, cmd):
        """Execute shell command"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout.strip(), result.returncode
        except Exception as e:
            return str(e), 1
    
    def check_docker(self):
        """Verify Docker installation"""
        print("🔍 Checking Docker installation...")
        output, code = self.run_cmd('docker --version')
        if code == 0:
            print(f"✅ {output}")
            return True
        print("❌ Docker not installed")
        return False
    
    def check_compose(self):
        """Verify Docker Compose"""
        print("🔍 Checking Docker Compose...")
        output, code = self.run_cmd('docker compose version')
        if code == 0:
            print(f"✅ {output}")
            return True
        print("❌ Docker Compose not installed")
        return False
    
    def check_containers(self):
        """Check running containers"""
        print("\n📦 Container Status:")
        output, _ = self.run_cmd('docker compose ps --format "table {{.Names}}\\t{{.Status}}"')
        if output:
            print(output)
        else:
            print("❌ No containers running")
    
    def check_volumes(self):
        """Check Docker volumes"""
        print("\n💾 Docker Volumes:")
        output, _ = self.run_cmd('docker volume ls --format "table {{.Name}}\\t{{.Driver}}"')
        if output:
            print(output)
    
    def check_networks(self):
        """Check Docker networks"""
        print("\n🌐 Docker Networks:")
        output, _ = self.run_cmd('docker network ls --format "table {{.Name}}\\t{{.Driver}}"')
        if output:
            print(output)
    
    def check_resources(self):
        """Check system resources"""
        print("\n📊 System Resource Usage:")
        output, _ = self.run_cmd('docker stats --no-stream --format "table {{.Container}}\\t{{.CPUPerc}}\\t{{.MemUsage}}"')
        if output:
            print(output)
    
    def check_logs(self, container='veyra-web', lines=20):
        """View container logs"""
        print(f"\n📋 Logs from {container} (last {lines} lines):")
        output, _ = self.run_cmd(f'docker compose logs --tail {lines} {container}')
        if output:
            print(output)
    
    def prune(self, force=False):
        """Clean up unused Docker resources"""
        print("\n🧹 Pruning Docker resources...")
        cmd = 'docker system prune -f'
        if force:
            cmd += ' -a'
        output, code = self.run_cmd(cmd)
        if code == 0:
            print(f"✅ {output}")
        else:
            print(f"❌ {output}")
    
    def full_health_check(self):
        """Complete system health check"""
        print("🏥 FULL HEALTH CHECK")
        print("=" * 50)
        
        if not self.check_docker():
            return False
        
        if not self.check_compose():
            return False
        
        self.check_containers()
        self.check_volumes()
        self.check_networks()
        self.check_resources()
        
        print("\n✅ Health check complete")
        return True

if __name__ == '__main__':
    veyra = VeyraDocker()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == 'health':
            veyra.full_health_check()
        elif cmd == 'logs':
            container = sys.argv[2] if len(sys.argv) > 2 else 'veyra-web'
            veyra.check_logs(container)
        elif cmd == 'prune':
            veyra.prune(force=True)
        elif cmd == 'status':
            veyra.check_containers()
        else:
            print(f"Unknown command: {cmd}")
    else:
        veyra.full_health_check()
