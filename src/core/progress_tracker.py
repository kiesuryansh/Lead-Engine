"""
Progress Tracking System for Lead Extraction

Tracks extraction progress in real-time and logs to SQLite database.
Provides hooks for live monitoring via dashboard.
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import json
from dataclasses import dataclass, asdict
import threading


@dataclass
class ExtractionJob:
    """Represents an extraction job"""
    job_id: str
    geography: str
    industry: str
    target_count: int
    status: str  # 'running', 'completed', 'failed'
    extracted_count: int
    started_at: str
    completed_at: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class ExtractionProgress:
    """Real-time progress update"""
    job_id: str
    geography: str
    industry: str
    current_count: int
    target_count: int
    percentage: float
    status: str
    current_company: Optional[str] = None
    timestamp: Optional[str] = None


class ProgressTracker:
    """
    Track extraction progress in real-time

    Stores progress in SQLite database for dashboard access
    """

    def __init__(self, db_path: str = "data/extraction_progress.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS extraction_jobs (
                job_id TEXT PRIMARY KEY,
                geography TEXT,
                industry TEXT,
                target_count INTEGER,
                extracted_count INTEGER,
                status TEXT,
                started_at TEXT,
                completed_at TEXT,
                error_message TEXT
            )
        """)

        # Progress updates table (for real-time tracking)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS progress_updates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT,
                geography TEXT,
                industry TEXT,
                current_count INTEGER,
                target_count INTEGER,
                percentage REAL,
                status TEXT,
                current_company TEXT,
                timestamp TEXT,
                FOREIGN KEY (job_id) REFERENCES extraction_jobs(job_id)
            )
        """)

        # Extracted leads summary
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT,
                geography TEXT,
                industry TEXT,
                company_name TEXT,
                company_country TEXT,
                extracted_at TEXT,
                FOREIGN KEY (job_id) REFERENCES extraction_jobs(job_id)
            )
        """)

        conn.commit()
        conn.close()

    def start_job(self, job: ExtractionJob) -> str:
        """Start tracking a new extraction job"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO extraction_jobs
                (job_id, geography, industry, target_count, extracted_count, status, started_at, completed_at, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job.job_id,
                job.geography,
                job.industry,
                job.target_count,
                job.extracted_count,
                job.status,
                job.started_at,
                job.completed_at,
                job.error_message
            ))

            conn.commit()
            conn.close()

            return job.job_id

    def update_progress(self, progress: ExtractionProgress):
        """Update extraction progress"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Add progress update
            cursor.execute("""
                INSERT INTO progress_updates
                (job_id, geography, industry, current_count, target_count, percentage, status, current_company, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                progress.job_id,
                progress.geography,
                progress.industry,
                progress.current_count,
                progress.target_count,
                progress.percentage,
                progress.status,
                progress.current_company,
                progress.timestamp or datetime.now().isoformat()
            ))

            # Update job extracted_count
            cursor.execute("""
                UPDATE extraction_jobs
                SET extracted_count = ?
                WHERE job_id = ?
            """, (progress.current_count, progress.job_id))

            conn.commit()
            conn.close()

    def complete_job(self, job_id: str, final_count: int, status: str = 'completed', error: Optional[str] = None):
        """Mark job as completed"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE extraction_jobs
                SET extracted_count = ?,
                    status = ?,
                    completed_at = ?,
                    error_message = ?
                WHERE job_id = ?
            """, (
                final_count,
                status,
                datetime.now().isoformat(),
                error,
                job_id
            ))

            conn.commit()
            conn.close()

    def add_lead_summary(self, job_id: str, geography: str, industry: str, company_name: str, company_country: str):
        """Add extracted lead to summary (for quick stats)"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO leads_summary
                (job_id, geography, industry, company_name, company_country, extracted_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                job_id,
                geography,
                industry,
                company_name,
                company_country,
                datetime.now().isoformat()
            ))

            conn.commit()
            conn.close()

    def get_active_jobs(self) -> List[Dict]:
        """Get all currently running jobs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT job_id, geography, industry, target_count, extracted_count, status, started_at
            FROM extraction_jobs
            WHERE status = 'running'
            ORDER BY started_at DESC
        """)

        jobs = []
        for row in cursor.fetchall():
            jobs.append({
                'job_id': row[0],
                'geography': row[1],
                'industry': row[2],
                'target_count': row[3],
                'extracted_count': row[4],
                'status': row[5],
                'started_at': row[6]
            })

        conn.close()
        return jobs

    def get_recent_jobs(self, limit: int = 10) -> List[Dict]:
        """Get recent extraction jobs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT job_id, geography, industry, target_count, extracted_count, status, started_at, completed_at
            FROM extraction_jobs
            ORDER BY started_at DESC
            LIMIT ?
        """, (limit,))

        jobs = []
        for row in cursor.fetchall():
            jobs.append({
                'job_id': row[0],
                'geography': row[1],
                'industry': row[2],
                'target_count': row[3],
                'extracted_count': row[4],
                'status': row[5],
                'started_at': row[6],
                'completed_at': row[7]
            })

        conn.close()
        return jobs

    def get_job_progress(self, job_id: str) -> Optional[Dict]:
        """Get current progress for a specific job"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT current_count, target_count, percentage, status, current_company, timestamp
            FROM progress_updates
            WHERE job_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """, (job_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'current_count': row[0],
                'target_count': row[1],
                'percentage': row[2],
                'status': row[3],
                'current_company': row[4],
                'timestamp': row[5]
            }
        return None

    def get_statistics(self) -> Dict:
        """Get overall extraction statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total jobs
        cursor.execute("SELECT COUNT(*) FROM extraction_jobs")
        total_jobs = cursor.fetchone()[0]

        # Completed jobs
        cursor.execute("SELECT COUNT(*) FROM extraction_jobs WHERE status = 'completed'")
        completed_jobs = cursor.fetchone()[0]

        # Total leads extracted
        cursor.execute("SELECT SUM(extracted_count) FROM extraction_jobs WHERE status = 'completed'")
        total_leads = cursor.fetchone()[0] or 0

        # By geography
        cursor.execute("""
            SELECT geography, SUM(extracted_count)
            FROM extraction_jobs
            WHERE status = 'completed'
            GROUP BY geography
        """)
        by_geography = {row[0]: row[1] for row in cursor.fetchall()}

        # By industry
        cursor.execute("""
            SELECT industry, SUM(extracted_count)
            FROM extraction_jobs
            WHERE status = 'completed'
            GROUP BY industry
        """)
        by_industry = {row[0]: row[1] for row in cursor.fetchall()}

        conn.close()

        return {
            'total_jobs': total_jobs,
            'completed_jobs': completed_jobs,
            'total_leads': total_leads,
            'by_geography': by_geography,
            'by_industry': by_industry
        }

    def get_recent_leads(self, limit: int = 50) -> List[Dict]:
        """Get recently extracted leads"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT geography, industry, company_name, company_country, extracted_at
            FROM leads_summary
            ORDER BY extracted_at DESC
            LIMIT ?
        """, (limit,))

        leads = []
        for row in cursor.fetchall():
            leads.append({
                'geography': row[0],
                'industry': row[1],
                'company_name': row[2],
                'company_country': row[3],
                'extracted_at': row[4]
            })

        conn.close()
        return leads


# Global tracker instance
_tracker = None

def get_tracker() -> ProgressTracker:
    """Get global progress tracker instance"""
    global _tracker
    if _tracker is None:
        _tracker = ProgressTracker()
    return _tracker


if __name__ == "__main__":
    # Test the tracker
    tracker = get_tracker()

    # Create test job
    job = ExtractionJob(
        job_id="test_job_1",
        geography="india",
        industry="fmcg",
        target_count=100,
        status="running",
        extracted_count=0,
        started_at=datetime.now().isoformat()
    )

    tracker.start_job(job)

    # Simulate progress
    for i in range(1, 11):
        progress = ExtractionProgress(
            job_id="test_job_1",
            geography="india",
            industry="fmcg",
            current_count=i * 10,
            target_count=100,
            percentage=(i * 10) / 100 * 100,
            status="running",
            current_company=f"Test Company {i}",
            timestamp=datetime.now().isoformat()
        )
        tracker.update_progress(progress)

    # Complete job
    tracker.complete_job("test_job_1", 100, "completed")

    # Get stats
    stats = tracker.get_statistics()
    print("\nStatistics:")
    print(json.dumps(stats, indent=2))

    print("\nTest complete! Database created at: data/extraction_progress.db")
