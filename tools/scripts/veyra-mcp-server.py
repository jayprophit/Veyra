#!/usr/bin/env python3
"""
Veyra MCP Server - Model Context Protocol Integration
Provides programmatic access to Docker and Kubernetes operations
"""

import json
import subprocess
import os
import sys
from typing import Dict, Any, List

class VeyraDockerMCP:
    """MCP Server for Docker/K8s operations"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.docker_compose_file = os.path.join(project_root, "docker-compose.yml")
    
    def run_command(self, cmd: str, cwd: str = None) -> Dict[str, Any]:
        """Execute shell command and return result"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                cwd=cwd or self.project_root,
                timeout=300
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout.strip(),
                "error": result.stderr.strip(),
                "code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timeout",
                "code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "code": -1
            }
    
    def docker_build(self, tag: str = "latest", nocache: bool = False) -> Dict:
        """Build Docker image"""
        cmd = f"docker build -t veyra:{tag}"
        if nocache:
            cmd += " --no-cache"
        cmd += " -f infrastructure/docker/web.Dockerfile ."
        return self.run_command(cmd)
    
    def docker_compose_up(self, build: bool = False, detached: bool = True, profile: str = "") -> Dict:
        """Start Docker Compose"""
        cmd = "docker compose up"
        if build:
            cmd += " --build"
        if detached:
            cmd += " -d"
        if profile:
            cmd += f" --profile {profile}"
        return self.run_command(cmd)
    
    def docker_compose_down(self, remove_volumes: bool = False) -> Dict:
        """Stop Docker Compose"""
        cmd = "docker compose down"
        if remove_volumes:
            cmd += " -v"
        return self.run_command(cmd)
    
    def docker_ps(self, all: bool = False) -> Dict:
        """List containers"""
        cmd = "docker ps"
        if all:
            cmd += " -a"
        cmd += ' --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'
        return self.run_command(cmd)
    
    def docker_logs(self, container: str, follow: bool = False, tail: int = 50) -> Dict:
        """Get container logs"""
        cmd = f"docker logs --tail {tail}"
        if follow:
            cmd += " -f"
        cmd += f" {container}"
        return self.run_command(cmd)
    
    def kubernetes_deploy(self, namespace: str = "default", watch: bool = False) -> Dict:
        """Deploy to Kubernetes"""
        cmd = f"kubectl apply -k infrastructure/kubernetes/ -n {namespace}"
        result = self.run_command(cmd)
        
        if result["success"] and watch:
            watch_cmd = f"kubectl get pods -n {namespace} -w"
            self.run_command(watch_cmd)
        
        return result
    
    def kubernetes_logs(self, pod: str, namespace: str = "default", follow: bool = False) -> Dict:
        """Get Kubernetes pod logs"""
        cmd = f"kubectl logs {pod} -n {namespace}"
        if follow:
            cmd += " -f"
        return self.run_command(cmd)
    
    def health_check(self, verbose: bool = False) -> Dict:
        """Full health check"""
        checks = {
            "docker": self.run_command("docker --version")["success"],
            "docker_compose": self.run_command("docker compose version")["success"],
            "kubectl": self.run_command("kubectl version --client")["success"],
            "python": self.run_command("python --version")["success"],
            "containers": self._check_containers(),
            "volumes": self._check_volumes(),
            "networks": self._check_networks()
        }
        
        if verbose:
            checks["details"] = {
                "docker_info": self.run_command("docker info")["output"],
                "docker_stats": self.run_command("docker stats --no-stream")["output"],
                "compose_ps": self.run_command("docker compose ps")["output"]
            }
        
        return {
            "success": all(v for k, v in checks.items() if k != "details"),
            "checks": checks
        }
    
    def system_resources(self) -> Dict:
        """Check system resources"""
        return {
            "docker_df": json.loads(self.run_command("docker system df --format json")["output"] or "{}"),
            "docker_stats": self.run_command("docker stats --no-stream --format json")["output"],
            "disk_usage": self.run_command("docker system df")["output"]
        }
    
    def _check_containers(self) -> bool:
        """Check if containers are running"""
        result = self.run_command("docker compose ps --format json")
        return result["success"]
    
    def _check_volumes(self) -> int:
        """Count Docker volumes"""
        result = self.run_command("docker volume ls --format json")
        try:
            volumes = json.loads(result["output"] or "[]")
            return len(volumes)
        except:
            return 0
    
    def _check_networks(self) -> int:
        """Count Docker networks"""
        result = self.run_command("docker network ls --format json")
        try:
            networks = json.loads(result["output"] or "[]")
            return len(networks)
        except:
            return 0

# MCP Tool Handler
def handle_tool_call(tool_name: str, parameters: Dict[str, Any]) -> str:
    """Handle MCP tool calls"""
    mcp = VeyraDockerMCP()
    
    try:
        if tool_name == "docker_build":
            result = mcp.docker_build(
                tag=parameters.get("tag", "latest"),
                nocache=parameters.get("nocache", False)
            )
        elif tool_name == "docker_compose_up":
            result = mcp.docker_compose_up(
                build=parameters.get("build", False),
                detached=parameters.get("detached", True),
                profile=parameters.get("profile", "")
            )
        elif tool_name == "docker_compose_down":
            result = mcp.docker_compose_down(
                remove_volumes=parameters.get("remove_volumes", False)
            )
        elif tool_name == "docker_ps":
            result = mcp.docker_ps(all=parameters.get("all", False))
        elif tool_name == "docker_logs":
            result = mcp.docker_logs(
                container=parameters["container"],
                follow=parameters.get("follow", False),
                tail=parameters.get("tail", 50)
            )
        elif tool_name == "kubernetes_deploy":
            result = mcp.kubernetes_deploy(
                namespace=parameters.get("namespace", "default"),
                watch=parameters.get("watch", False)
            )
        elif tool_name == "kubernetes_logs":
            result = mcp.kubernetes_logs(
                pod=parameters["pod"],
                namespace=parameters.get("namespace", "default"),
                follow=parameters.get("follow", False)
            )
        elif tool_name == "health_check":
            result = mcp.health_check(verbose=parameters.get("verbose", False))
        elif tool_name == "system_resources":
            result = mcp.system_resources()
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
        
        return json.dumps(result, indent=2)
    
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    # For testing
    if len(sys.argv) > 1:
        tool = sys.argv[1]
        params = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
        print(handle_tool_call(tool, params))
    else:
        # Start MCP server
        mcp = VeyraDockerMCP()
        print(json.dumps(mcp.health_check(verbose=True), indent=2))
