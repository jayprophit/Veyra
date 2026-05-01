"""Quantum Sensor Applications"""
from typing import Dict

class QuantumApplications:
    """Use case economics"""
    
    def defense_applications(self) -> Dict:
        return {
            "gps_denied_navigation": {
                "market": "Military vehicles, submarines",
                "value": "Navigation without satellites",
                "contract_size": "10-100M"
            },
            "submarine_detection": {
                "technology": "Quantum gravimetry",
                "advantage": "Passive, undetectable",
                "market": "Anti-submarine warfare"
            }
        }
    
    def medical_applications(self) -> Dict:
        return {
            "meg_imaging": {
                "full_name": "Magnetoencephalography",
                "advantage": "Direct neural activity",
                "vs_fmri": "Better temporal resolution",
                "system_cost": 2e6
            },
            "cardiac_imaging": {
                "technology": "SQUID magnetometers",
                "application": "Fetal heart monitoring",
                "market": "High-risk pregnancies"
            }
        }
    
    def resource_exploration(self) -> Dict:
        return {
            "oil_gas": {
                "method": "Quantum gravimetry",
                "advantage": "Detects subsurface density",
                "survey_cost_reduction": 0.40
            },
            "minerals": {
                "method": "Diamond magnetometers",
                "application": "Subsurface mineral mapping",
                "accuracy_improvement": "10x over conventional"
            }
        }
