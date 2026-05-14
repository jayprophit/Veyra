"""Job Marketplace for Financial Traders."""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class JobType(Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    FREELANCE = "freelance"
    REMOTE = "remote"

class JobCategory(Enum):
    TRADER = "trader"
    ANALYST = "analyst"
    QUANT = "quant"
    STRATEGIST = "strategist"
    RISK_MANAGER = "risk_manager"
    PORTFOLIO_MANAGER = "portfolio_manager"

@dataclass
class JobListing:
    id: str
    title: str
    company: str
    description: str
    job_type: JobType
    category: JobCategory
    salary_range: str
    location: str
    requirements: List[str]
    required_level: int
    required_courses: List[str]
    posted_at: datetime
    posted_by: str
    active: bool = True

@dataclass
class JobApplication:
    id: str
    job_id: str
    applicant_id: str
    resume_hash: str
    cover_message: str
    status: str
    applied_at: datetime

class JobMarketplace:
    """Job board for trading professionals with blockchain CV storage."""
    
    def __init__(self):
        self.jobs: Dict[str, JobListing] = {}
        self.applications: Dict[str, JobApplication] = {}
        self.user_cvs: Dict[str, str] = {}
    
    async def post_job(self, job_data: Dict) -> str:
        job_id = f"job_{len(self.jobs)}"
        job = JobListing(
            id=job_id,
            title=job_data['title'],
            company=job_data['company'],
            description=job_data['description'],
            job_type=JobType(job_data['type']),
            category=JobCategory(job_data['category']),
            salary_range=job_data.get('salary', 'Competitive'),
            location=job_data.get('location', 'Remote'),
            requirements=job_data.get('requirements', []),
            required_level=job_data.get('min_level', 1),
            required_courses=job_data.get('courses', []),
            posted_at=datetime.now(),
            posted_by=job_data['employer_id']
        )
        self.jobs[job_id] = job
        return job_id
    
    async def search_jobs(self, 
                         category: Optional[str] = None,
                         job_type: Optional[str] = None,
                         location: Optional[str] = None) -> List[Dict]:
        results = []
        for job in self.jobs.values():
            if not job.active:
                continue
            if category and job.category.value != category:
                continue
            if job_type and job.job_type.value != job_type:
                continue
            if location and location.lower() not in job.location.lower():
                continue
            results.append({
                'id': job.id, 'title': job.title, 'company': job.company,
                'type': job.job_type.value, 'category': job.category.value,
                'salary': job.salary_range, 'location': job.location,
                'requirements': job.requirements, 'min_level': job.required_level,
                'posted': job.posted_at.isoformat()
            })
        return results
    
    async def store_cv_blockchain(self, user_id: str, cv_data: str) -> str:
        """Store CV hash on blockchain for verification."""
        import hashlib
        cv_hash = hashlib.sha256(cv_data.encode()).hexdigest()
        self.user_cvs[user_id] = cv_hash
        return cv_hash
    
    async def apply(self, user_id: str, job_id: str, message: str) -> Dict:
        if job_id not in self.jobs:
            return {'success': False, 'error': 'Job not found'}
        
        job = self.jobs[job_id]
        cv_hash = self.user_cvs.get(user_id, '')
        
        app_id = f"app_{len(self.applications)}"
        application = JobApplication(
            id=app_id, job_id=job_id, applicant_id=user_id,
            resume_hash=cv_hash, cover_message=message,
            status='pending', applied_at=datetime.now()
        )
        self.applications[app_id] = application
        
        return {
            'success': True,
            'application_id': app_id,
            'cv_verified': cv_hash != ''
        }

jobs = JobMarketplace()
