# Veyra Directory Organization Plan

## Current Issues
- Many Python files scattered in root directory
- Multiple duplicate deployment guides and scripts
- Temporary fix files need cleanup
- Documentation files not properly organized
- Configuration files mixed with other files

## Target Directory Structure
```
Veyra/
├── README.md                    # Main documentation
├── LICENSE                      # License file
├── .gitignore                   # Git ignore file
├── .env.example                 # Environment template
├── src/                         # Source code
│   ├── backend/                  # Backend application
│   └── frontend/                 # Frontend application
├── docs/                        # Documentation
│   ├── guides/                   # User guides
│   ├── api/                      # API documentation
│   └── deployment/                # Deployment guides
├── scripts/                      # Utility and deployment scripts
│   ├── deployment/                # Deployment scripts
│   ├── setup/                    # Setup scripts
│   └── maintenance/               # Maintenance scripts
├── config/                       # Configuration files
│   ├── development/               # Dev configs
│   ├── staging/                   # Staging configs
│   └── production/                # Production configs
├── tests/                        # Test files
├── deployment/                   # Deployment configurations
│   ├── docker/                   # Docker files
│   ├── k8s/                      # Kubernetes files
│   └── cloud/                    # Cloud-specific configs
└── tools/                        # Development tools
    └── audit/                     # Audit tools
```

## Files to Move
### Python Scripts (move to scripts/)
- analyze_endpoints.py
- deploy_*.py
- fix_*.py
- run_*.py
- setup_*.py
- verify_*.py
- ZERO_COST_SETUP_SCRIPTS*.py

### Documentation (move to docs/)
- *_GUIDE.md
- *_REPORT.md
- *_ANALYSIS.md
- README.md (keep in root)

### Configuration (move to config/)
- docker-compose*.yml
- .env.example (keep in root)
- render.yaml
- wrangler.toml

### Temporary Files (delete)
- *.backup
- fix_*.py
- comprehensive_audit.log
- test_report.json
- production_report.json

## Cleanup Actions
1. Create proper directory structure
2. Move files to appropriate locations
3. Remove duplicates and temporary files
4. Update references in files
5. Clean up root directory
