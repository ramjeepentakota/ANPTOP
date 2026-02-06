#!/usr/bin/env python3
"""
CVE Database Integration Script
Downloads and imports NVD CVE data for vulnerability correlation
"""

import asyncio
import gzip
import json
import logging
import ssl
import aiohttp
import aiosqlite
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
CVE_DB_PATH = Path(__file__).parent.parent / "data" / "cve_database.db"
CVE_DATA_DIR = Path(__file__).parent.parent / "data" / "cve_data"
BATCH_SIZE = 1000
MAX_CONCURRENT_DOWNLOADS = 3
REQUEST_TIMEOUT = 300  # 5 minutes

# CPE matching configurations
@dataclass
class CPEConfig:
    """CPE configuration for matching"""
    part: str  # 'a' (application), 'o' (operating system), 'h' (hardware)
    vendor: str
    product: str
    version: Optional[str] = None
    update: Optional[str] = None
    edition: Optional[str] = None
    language: Optional[str] = None

class CVSSSeverity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NONE = "NONE"
    UNKNOWN = "UNKNOWN"

@dataclass
class CVSSMetric:
    """CVSS v3.x metrics"""
    version: str
    vector_string: str
    base_score: float
    base_severity: CVSSSeverity
    exploitability_score: Optional[float] = None
    impact_score: Optional[float] = None

@dataclass
class CVEEntry:
    """CVE entry dataclass"""
    cve_id: str
    published_date: datetime
    last_modified_date: datetime
    description: str
    cvss_metrics: Optional[List[CVSSMetric]] = None
    cwe_ids: Optional[List[str]] = None
    references: Optional[List[str]] = None
    configurations: Optional[List[Dict[str, Any]]] = None
    vulnerable: bool = True


class CVEDatabaseManager:
    """Manager for CVE database operations"""
    
    def __init__(self, db_path: Path = CVE_DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None:
            timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = True
            ssl_context.verify_mode = ssl.CERT_REQUIRED
            connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT_DOWNLOADS)
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                ssl=ssl_context
            )
        return self._session
    
    async def close_session(self):
        """Close aiohttp session"""
        if self._session:
            await self._session.close()
            self._session = None
    
    async def init_database(self):
        """Initialize CVE database schema"""
        async with aiosqlite.connect(self.db_path) as db:
            # Create CVE entries table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS cve_entries (
                    cve_id TEXT PRIMARY KEY,
                    published_date TEXT NOT NULL,
                    last_modified_date TEXT NOT NULL,
                    description TEXT NOT NULL,
                    cvss_metrics TEXT,
                    cwe_ids TEXT,
                    references TEXT,
                    configurations TEXT,
                    vulnerable INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create CPE matching table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS cpe_matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cve_id TEXT NOT NULL,
                    cpe23_uri TEXT NOT NULL,
                    cpe23_version TEXT,
                    vulnerable INTEGER DEFAULT 1,
                    FOREIGN KEY (cve_id) REFERENCES cve_entries(cve_id),
                    INDEX idx_cpe_vendor (cpe23_uri),
                    INDEX idx_cpe_product (cpe23_product)
                )
            """)
            
            # Create CWE reference table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS cwe_references (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cwe_id TEXT NOT NULL UNIQUE,
                    name TEXT,
                    description TEXT,
                    FOREIGN KEY (cwe_id) REFERENCES cve_entries(cwe_ids)
                )
            """)
            
            # Create index for searching
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_cve_published 
                ON cve_entries(published_date)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_cve_modified 
                ON cve_entries(last_modified_date)
            """)
            
            await db.commit()
            logger.info(f"CVE database initialized at {self.db_path}")
    
    async def insert_cve(self, cve: CVEEntry):
        """Insert or update CVE entry"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO cve_entries 
                (cve_id, published_date, last_modified_date, description, 
                 cvss_metrics, cwe_ids, references, configurations, vulnerable)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cve.cve_id,
                cve.published_date.isoformat(),
                cve.last_modified_date.isoformat(),
                cve.description,
                json.dumps([m.__dict__ for m in cve.cvss_metrics]) if cve.cvss_metrics else None,
                json.dumps(cve.cwe_ids) if cve.cwe_ids else None,
                json.dumps(cve.references) if cve.references else None,
                json.dumps(cve.configurations) if cve.configurations else None,
                1 if cve.vulnerable else 0
            ))
    
    async def bulk_insert_cves(self, cves: List[CVEEntry]):
        """Bulk insert CVE entries"""
        if not cves:
            return
        
        async with aiosqlite.connect(self.db_path) as db:
            # Prepare batch insert
            data = [
                (
                    cve.cve_id,
                    cve.published_date.isoformat(),
                    cve.last_modified_date.isoformat(),
                    cve.description,
                    json.dumps([m.__dict__ for m in cve.cvss_metrics]) if cve.cvss_metrics else None,
                    json.dumps(cve.cwe_ids) if cve.cwe_ids else None,
                    json.dumps(cve.references) if cve.references else None,
                    json.dumps(cve.configurations) if cve.configurations else None,
                    1 if cve.vulnerable else 0
                )
                for cve in cves
            ]
            
            await db.executemany("""
                INSERT OR REPLACE INTO cve_entries 
                (cve_id, published_date, last_modified_date, description, 
                 cvss_metrics, cwe_ids, references, configurations, vulnerable)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, data)
            
            await db.commit()
        
        logger.info(f"Bulk inserted {len(cves)} CVE entries")
    
    async def search_cves_by_product(
        self, 
        vendor: str, 
        product: str, 
        version: Optional[str] = None,
        limit: int = 100
    ) -> List[CVEEntry]:
        """Search CVEs by vendor/product"""
        async with aiosqlite.connect(self.db_path) as db:
            if version:
                query = """
                    SELECT * FROM cve_entries 
                    WHERE configurations LIKE ? 
                    AND configurations LIKE ?
                    AND configurations LIKE ?
                    ORDER BY published_date DESC
                    LIMIT ?
                """
                params = (f'%cpe:2.3:a:{vendor}:{product}%', f'%{version}%', '%', limit)
            else:
                query = """
                    SELECT * FROM cve_entries 
                    WHERE configurations LIKE ?
                    ORDER BY published_date DESC
                    LIMIT ?
                """
                params = (f'%cpe:2.3:a:{vendor}:{product}%', limit)
            
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            
            cves = []
            for row in rows:
                cve = CVEEntry(
                    cve_id=row[0],
                    published_date=datetime.fromisoformat(row[1]),
                    last_modified_date=datetime.fromisoformat(row[2]),
                    description=row[3],
                    cvss_metrics=[CVSSMetric(**m) for m in json.loads(row[4])] if row[4] else None,
                    cwe_ids=json.loads(row[5]) if row[5] else None,
                    references=json.loads(row[6]) if row[6] else None,
                    configurations=json.loads(row[7]) if row[7] else None,
                    vulnerable=bool(row[8])
                )
                cves.append(cve)
            
            return cves
    
    async def get_cve_by_id(self, cve_id: str) -> Optional[CVEEntry]:
        """Get single CVE by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT * FROM cve_entries WHERE cve_id = ?",
                (cve_id,)
            )
            row = await cursor.fetchone()
            
            if not row:
                return None
            
            return CVEEntry(
                cve_id=row[0],
                published_date=datetime.fromisoformat(row[1]),
                last_modified_date=datetime.fromisoformat(row[2]),
                description=row[3],
                cvss_metrics=[CVSSMetric(**m) for m in json.loads(row[4])] if row[4] else None,
                cwe_ids=json.loads(row[5]) if row[5] else None,
                references=json.loads(row[6]) if row[6] else None,
                configurations=json.loads(row[7]) if row[7] else None,
                vulnerable=bool(row[8])
            )
    
    async def get_high_severity_cves(
        self, 
        min_score: float = 7.0, 
        limit: int = 100
    ) -> List[CVEEntry]:
        """Get high severity CVEs"""
        async with aiosqlite.connect(self.db_path) as db:
            query = """
                SELECT * FROM cve_entries 
                WHERE cvss_metrics IS NOT NULL
                ORDER BY CAST(json_extract(cvss_metrics, '$.base_score') AS REAL) DESC
                LIMIT ?
            """
            cursor = await db.execute(query, (limit,))
            rows = await cursor.fetchall()
            
            cves = []
            for row in rows:
                cve = CVEEntry(
                    cve_id=row[0],
                    published_date=datetime.fromisoformat(row[1]),
                    last_modified_date=datetime.fromisoformat(row[2]),
                    description=row[3],
                    cvss_metrics=[CVSSMetric(**m) for m in json.loads(row[4])] if row[4] else None,
                    cwe_ids=json.loads(row[5]) if row[5] else None,
                    references=json.loads(row[6]) if row[6] else None,
                    configurations=json.loads(row[7]) if row[7] else None,
                    vulnerable=bool(row[8])
                )
                cves.append(cve)
            
            return cves


class NVDAPIImporter:
    """Importer for NVD API CVE data"""
    
    def __init__(self, manager: CVEDatabaseManager):
        self.manager = manager
    
    async def fetch_cves_page(
        self, 
        start_index: int = 0, 
        results_per_page: int = 2000
    ) -> Dict[str, Any]:
        """Fetch single page of CVEs from NVD API"""
        session = await self.manager.get_session()
        
        params = {
            'resultsPerPage': results_per_page,
            'startIndex': start_index
        }
        
        try:
            async with session.get(NVD_API_URL, params=params) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 503:
                    # Rate limiting - wait and retry
                    logger.warning("NVD API rate limited, waiting 30 seconds...")
                    await asyncio.sleep(30)
                    return await self.fetch_cves_page(start_index, results_per_page)
                else:
                    logger.error(f"NVD API error: {response.status}")
                    return {'vulnerabilities': []}
        except Exception as e:
            logger.error(f"Error fetching CVEs: {e}")
            return {'vulnerabilities': []}
    
    def parse_cve_entry(self, vuln_data: Dict[str, Any]) -> Optional[CVEEntry]:
        """Parse NVD API response into CVEEntry"""
        try:
            cve_meta = vuln_data.get('cve', {})
            cve_id = cve_meta.get('id')
            
            # Parse dates
            published = cve_meta.get('published', '')
            modified = cve_meta.get('lastModified', '')
            published_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
            last_modified_date = datetime.fromisoformat(modified.replace('Z', '+00:00'))
            
            # Get description
            descriptions = cve_meta.get('descriptions', [])
            description = ''
            for desc in descriptions:
                if desc.get('lang') == 'en':
                    description = desc.get('value', '')
                    break
            
            # Parse CVSS metrics
            cvss_metrics = []
            metrics = cve_meta.get('metrics', {})
            
            # CVSS v3.x
            if 'cvssMetricV31' in metrics:
                for metric in metrics['cvssMetricV31']:
                    cvss = metric.get('cvssData', {})
                    base_score = cvss.get('baseScore', 0)
                    severity = CVSSSeverity.UNKNOWN
                    if cvss.get('baseSeverity'):
                        severity = CVSSSeverity(cvss.get('baseSeverity').upper())
                    
                    cvss_metrics.append(CVSSMetric(
                        version='3.1',
                        vector_string=cvss.get('vectorString', ''),
                        base_score=base_score,
                        base_severity=severity,
                        exploitability_score=metric.get('exploitabilityScore'),
                        impact_score=metric.get('impactScore')
                    ))
            
            # CVSS v3.0
            elif 'cvssMetricV30' in metrics:
                for metric in metrics['cvssMetricV30']:
                    cvss = metric.get('cvssData', {})
                    base_score = cvss.get('baseScore', 0)
                    severity = CVSSSeverity.UNKNOWN
                    if cvss.get('baseSeverity'):
                        severity = CVSSSeverity(cvss.get('baseSeverity').upper())
                    
                    cvss_metrics.append(CVSSMetric(
                        version='3.0',
                        vector_string=cvss.get('vectorString', ''),
                        base_score=base_score,
                        base_severity=severity,
                        exploitability_score=metric.get('exploitabilityScore'),
                        impact_score=metric.get('impactScore')
                    ))
            
            # CVSS v2
            elif 'cvssMetricV2' in metrics:
                for metric in metrics['cvssMetricV2']:
                    cvss = metric.get('cvssData', {})
                    base_score = cvss.get('baseScore', 0)
                    severity = CVSSSeverity.UNKNOWN
                    if metric.get('baseSeverity'):
                        severity = CVSSSeverity(metric.get('baseSeverity').upper())
                    
                    cvss_metrics.append(CVSSMetric(
                        version='2.0',
                        vector_string=cvss.get('vectorString', ''),
                        base_score=base_score,
                        base_severity=severity,
                        exploitability_score=metric.get('exploitabilityScore'),
                        impact_score=metric.get('impactScore')
                    ))
            
            # Get CWE IDs
            cwe_ids = []
            for problem in cve_meta.get('problems', []):
                if problem.get('cweId'):
                    cwe_ids.append(f"CWE-{problem['cweId']}")
            
            # Get references
            references = [ref.get('url', '') for ref in cve_meta.get('references', [])]
            
            # Get configurations
            configurations = vuln_data.get('configurations', [])
            
            return CVEEntry(
                cve_id=cve_id,
                published_date=published_date,
                last_modified_date=last_modified_date,
                description=description,
                cvss_metrics=cvss_metrics if cvss_metrics else None,
                cwe_ids=cwe_ids if cwe_ids else None,
                references=references if references else None,
                configurations=configurations if configurations else None
            )
        
        except Exception as e:
            logger.error(f"Error parsing CVE {cve_id}: {e}")
            return None
    
    async def import_all_cves(self, year_filter: Optional[int] = None):
        """Import all CVEs from NVD API"""
        await self.manager.init_database()
        
        total_imported = 0
        start_index = 0
        results_per_page = 2000
        
        while True:
            logger.info(f"Fetching CVEs starting at index {start_index}...")
            
            data = await self.fetch_cves_page(start_index, results_per_page)
            vulnerabilities = data.get('vulnerabilities', [])
            
            if not vulnerabilities:
                break
            
            # Parse CVEs
            cves = []
            for vuln in vulnerabilities:
                cve = self.parse_cve_entry(vuln)
                if cve:
                    # Filter by year if specified
                    if year_filter and cve.published_date.year != year_filter:
                        continue
                    cves.append(cve)
            
            if not cves:
                start_index += results_per_page
                continue
            
            # Bulk insert
            await self.manager.bulk_insert_cves(cves)
            total_imported += len(cves)
            
            logger.info(f"Imported {total_imported} CVEs so far...")
            
            # Check if we've fetched all results
            total_results = data.get('resultsPerPage', 0)
            if start_index + results_per_page >= total_results:
                break
            
            start_index += results_per_page
        
        logger.info(f"Total CVEs imported: {total_imported}")
        return total_imported


class LocalFileImporter:
    """Importer for local CVE data files (JSON/Gzip)"""
    
    def __init__(self, manager: CVEDatabaseManager):
        self.manager = manager
    
    def parse_cve_25_file(self, file_path: Path) -> List[CVEEntry]:
        """Parse NVD CVE 2.5 JSON format file"""
        cves = []
        
        with gzip.open(file_path, 'rt', encoding='utf-8') as f:
            data = json.load(f)
        
        for item in data.get('cve_items', []):
            try:
                cve_meta = item.get('cve', {})
                cve_id = cve_meta.get('CVE_data_meta', {}).get('ID', '')
                
                # Parse dates
                published = item.get('publishedDate', '')
                modified = item.get('lastModifiedDate', '')
                published_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                last_modified_date = datetime.fromisoformat(modified.replace('Z', '+00:00'))
                
                # Get description
                description_data = cve_meta.get('description', {}).get('description_data', [])
                description = ''
                for desc in description_data:
                    if desc.get('lang') == 'en':
                        description = desc.get('value', '')
                        break
                
                # Parse CVSS v3
                cvss_metrics = []
                impact = item.get('impact', {})
                
                if 'baseMetricV3' in impact:
                    cvss = impact['baseMetricV3'].get('cvssV3', {})
                    base_score = cvss.get('baseScore', 0)
                    severity = CVSSSeverity.UNKNOWN
                    if cvss.get('baseSeverity'):
                        severity = CVSSSeverity(cvss.get('baseSeverity').upper())
                    
                    cvss_metrics.append(CVSSMetric(
                        version='3.x',
                        vector_string=cvss.get('vectorString', ''),
                        base_score=base_score,
                        base_severity=severity,
                        exploitability_score=impact['baseMetricV3'].get('exploitabilityScore'),
                        impact_score=impact['baseMetricV3'].get('impactScore')
                    ))
                
                # Parse CWE
                cwe_ids = []
                problems = cve_meta.get('problemtype', {}).get('problemtype_data', [])
                for problem in problems:
                    for desc in problem.get('description', []):
                        if desc.get('value', '').startswith('CWE-'):
                            cwe_ids.append(desc.get('value'))
                
                cves.append(CVEEntry(
                    cve_id=cve_id,
                    published_date=published_date,
                    last_modified_date=last_modified_date,
                    description=description,
                    cvss_metrics=cvss_metrics if cvss_metrics else None,
                    cwe_ids=cwe_ids if cwe_ids else None
                ))
            
            except Exception as e:
                logger.error(f"Error parsing CVE entry: {e}")
                continue
        
        return cves
    
    async def import_from_file(self, file_path: Path, year: Optional[int] = None):
        """Import CVEs from local file"""
        await self.manager.init_database()
        
        logger.info(f"Importing CVEs from {file_path}...")
        
        cves = self.parse_cve_25_file(file_path)
        
        if year:
            cves = [cve for cve in cves if cve.published_date.year == year]
        
        await self.manager.bulk_insert_cves(cves)
        logger.info(f"Imported {len(cves)} CVEs from {file_path}")
        
        return len(cves)
    
    async def import_from_directory(self, directory: Path, year: Optional[int] = None):
        """Import CVEs from all files in directory"""
        await self.manager.init_database()
        
        total_imported = 0
        
        for file_path in sorted(directory.glob('*.json.gz')):
            count = await self.import_from_file(file_path, year)
            total_imported += count
        
        logger.info(f"Total CVEs imported from directory: {total_imported}")
        return total_imported


class VulnerabilityCorrelator:
    """Correlate discovered vulnerabilities with CVE database"""
    
    def __init__(self, manager: CVEDatabaseManager):
        self.manager = manager
    
    async def correlate_service(self, service_info: Dict[str, Any]) -> List[CVEEntry]:
        """
        Correlate discovered service with CVEs
        
        Args:
            service_info: Dictionary containing service details
                - vendor: e.g., 'apache'
                - product: e.g., 'httpd'
                - version: e.g., '2.4.41'
                - port: e.g., 80
                - protocol: e.g., 'tcp'
        
        Returns:
            List of matching CVE entries
        """
        vendor = service_info.get('vendor', '').lower()
        product = service_info.get('product', '').lower()
        version = service_info.get('version', '')
        
        if not vendor or not product:
            return []
        
        cves = await self.manager.search_cves_by_product(vendor, product, version)
        
        # Filter by version match if specified
        if version:
            cves = [
                cve for cve in cves
                if self._version_matches(version, cve)
            ]
        
        return cves
    
    def _version_matches(self, service_version: str, cve: CVEEntry) -> bool:
        """Check if CVE version range matches service version"""
        if not cve.configurations:
            return True
        
        for config in cve.configurations:
            for node in config.get('nodes', []):
                for cpe_match in node.get('cpeMatch', []):
                    cpe23_uri = cpe_match.get('criteria', '')
                    
                    # Parse CPE 2.3 format: cpe:2.3:a:vendor:product:version:*
                    parts = cpe23_uri.split(':')
                    if len(parts) >= 6:
                        cve_vendor = parts[2].lower()
                        cve_product = parts[3].lower()
                        cve_version = parts[4]
                        
                        if cve_vendor == cve.vendor and cve_product == cve.product:
                            # Check version range
                            version_range = cpe_match.get('versionEndIncluding', '')
                            if version_range and self._compare_versions(service_version, version_range) <= 0:
                                return True
                            
                            version_start = cpe_match.get('versionStartIncluding', '')
                            if version_start and self._compare_versions(service_version, version_start) >= 0:
                                return True
        
        return True  # Default to include if no specific version match
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """Compare two version strings (returns -1, 0, 1)"""
        try:
            parts1 = [int(p) for p in v1.split('.')]
            parts2 = [int(p) for p in v2.split('.')]
            
            for i in range(max(len(parts1), len(parts2))):
                p1 = parts1[i] if i < len(parts1) else 0
                p2 = parts2[i] if i < len(parts2) else 0
                
                if p1 < p2:
                    return -1
                elif p1 > p2:
                    return 1
            
            return 0
        except:
            return 0
    
    async def generate_report(
        self, 
        service_vulnerabilities: List[Dict[str, Any]], 
        min_severity: CVSSSeverity = CVSSSeverity.MEDIUM
    ) -> Dict[str, Any]:
        """
        Generate vulnerability correlation report
        
        Args:
            service_vulnerabilities: List of service info dicts
            min_severity: Minimum severity to include
        
        Returns:
            Report dictionary with vulnerabilities
        """
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'total_services': len(service_vulnerabilities),
            'services_with_cves': 0,
            'total_cves_found': 0,
            'severity_breakdown': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            },
            'vulnerabilities': []
        }
        
        severity_order = [
            CVSSSeverity.CRITICAL,
            CVSSSeverity.HIGH,
            CVSSSeverity.MEDIUM,
            CVSSSeverity.LOW
        ]
        
        min_idx = severity_order.index(min_severity) if min_severity in severity_order else 2
        
        for service in service_vulnerabilities:
            cves = await self.correlate_service(service)
            
            filtered_cves = []
            for cve in cves:
                if cve.cvss_metrics:
                    max_severity = max(
                        m.base_severity for m in cve.cvss_metrics
                        if m.base_severity in severity_order
                    )
                    
                    if severity_order.index(max_severity) >= min_idx:
                        filtered_cves.append({
                            'cve_id': cve.cve_id,
                            'description': cve.description,
                            'severity': max_severity.value,
                            'score': max(m.base_score for m in cve.cvss_metrics),
                            'cvss_vector': cve.cvss_metrics[0].vector_string,
                            'cwe_ids': cve.cwe_ids,
                            'published_date': cve.published_date.isoformat(),
                            'references': cve.references[:5] if cve.references else []
                        })
                        
                        report['severity_breakdown'][max_severity.value.lower()] += 1
            
            if filtered_cves:
                report['services_with_cves'] += 1
            
            report['total_cves_found'] += len(filtered_cves)
            
            if filtered_cves:
                report['vulnerabilities'].append({
                    'service': service,
                    'cves': filtered_cves
                })
        
        return report


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CVE Database Manager')
    parser.add_argument(
        'command',
        choices=['init', 'import-api', 'import-file', 'import-dir', 'search', 'correlate', 'report'],
        help='Command to execute'
    )
    parser.add_argument('--path', type=str, help='Path to file or directory')
    parser.add_argument('--vendor', type=str, help='Vendor name for search')
    parser.add_argument('--product', type=str, help='Product name for search')
    parser.add_argument('--version', type=str, help='Version for search')
    parser.add_argument('--year', type=int, help='Filter by year')
    parser.add_argument('--limit', type=int, default=100, help='Result limit')
    
    args = parser.parse_args()
    
    manager = CVEDatabaseManager()
    
    try:
        if args.command == 'init':
            await manager.init_database()
            print("Database initialized successfully")
        
        elif args.command == 'import-api':
            importer = NVDAPIImporter(manager)
            count = await importer.import_all_cves(args.year)
            print(f"Imported {count} CVEs from NVD API")
        
        elif args.command == 'import-file':
            importer = LocalFileImporter(manager)
            count = await importer.import_from_file(Path(args.path), args.year)
            print(f"Imported {count} CVEs from {args.path}")
        
        elif args.command == 'import-dir':
            importer = LocalFileImporter(manager)
            count = await importer.import_from_directory(Path(args.path), args.year)
            print(f"Imported {count} CVEs from {args.path}")
        
        elif args.command == 'search':
            if not args.vendor or not args.product:
                print("Error: --vendor and --product required for search")
                return
            
            cves = await manager.search_cves_by_product(
                args.vendor, args.product, args.version, args.limit
            )
            print(f"Found {len(cves)} CVEs:")
            for cve in cves[:args.limit]:
                print(f"  {cve.cve_id}: {cve.description[:100]}...")
        
        elif args.command == 'correlate':
            if not args.vendor or not args.product:
                print("Error: --vendor and --product required for correlation")
                return
            
            correlator = VulnerabilityCorrelator(manager)
            service_info = {
                'vendor': args.vendor,
                'product': args.product,
                'version': args.version or ''
            }
            cves = await correlator.correlate_service(service_info)
            print(f"Found {len(cves)} matching CVEs for {args.vendor}:{args.product}")
        
        elif args.command == 'report':
            correlator = VulnerabilityCorrelator(manager)
            
            # Example services for report
            services = [
                {'vendor': 'apache', 'product': 'httpd', 'version': '2.4.41', 'port': 80},
                {'vendor': 'openssl', 'product': 'openssl', 'version': '1.1.1', 'port': 443}
            ]
            
            report = await correlator.generate_report(services)
            print(json.dumps(report, indent=2))
    
    finally:
        await manager.close_session()


if __name__ == '__main__':
    asyncio.run(main())
