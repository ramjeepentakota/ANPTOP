#!/usr/bin/env python3
"""
ANPTOP Backup and Recovery Script
Backs up PostgreSQL, Redis, and evidence files
"""

import os
import sys
import json
import gzip
import shutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
BACKUP_DIR = Path(os.environ.get('BACKUP_DIR', '/backups'))
POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = int(os.environ.get('POSTGRES_PORT', 5432))
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'anptop')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'anptop_secret')
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'anptop')
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
EVIDENCE_DIR = Path(os.environ.get('EVIDENCE_DIR', '/data/evidence'))
RETENTION_DAYS = int(os.environ.get('BACKUP_RETENTION_DAYS', 30))

# AWS S3 Configuration (optional)
S3_BUCKET = os.environ.get('S3_BACKUP_BUCKET', '')
S3_PREFIX = os.environ.get('S3_BACKUP_PREFIX', 'anptop/backups')


class BackupManager:
    """Manages backup and recovery operations"""
    
    def __init__(self):
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    def get_timestamp(self) -> str:
        """Get current timestamp for backup files"""
        return datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    
    def get_backup_filename(self, backup_type: str) -> str:
        """Generate backup filename"""
        timestamp = self.get_timestamp()
        return f"anptop_{backup_type}_{timestamp}.sql.gz"
    
    # =========================================================================
    # PostgreSQL Backup/Recovery
    # =========================================================================
    
    def backup_postgres(self) -> Path:
        """Create PostgreSQL backup"""
        backup_file = BACKUP_DIR / self.get_backup_filename('postgres')
        
        env = os.environ.copy()
        env['PGPASSWORD'] = POSTGRES_PASSWORD
        
        cmd = [
            'pg_dump',
            '-h', POSTGRES_HOST,
            '-p', str(POSTGRES_PORT),
            '-U', POSTGRES_USER,
            '-d', POSTGRES_DB,
            '-F', 'c',  # Custom format for compression
            '-Z', '9',   # Compression level
            '-f', str(backup_file)
        ]
        
        try:
            logger.info(f"Starting PostgreSQL backup to {backup_file}")
            subprocess.run(
                cmd,
                env=env,
                check=True,
                capture_output=True
            )
            logger.info(f"PostgreSQL backup completed: {backup_file}")
            return backup_file
        except subprocess.CalledProcessError as e:
            logger.error(f"PostgreSQL backup failed: {e}")
            raise
    
    def restore_postgres(self, backup_file: Path):
        """Restore PostgreSQL from backup"""
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_file}")
        
        env = os.environ.copy()
        env['PGPASSWORD'] = POSTGRES_PASSWORD
        
        # Drop and recreate database (use with caution!)
        drop_cmd = [
            'psql',
            '-h', POSTGRES_HOST,
            '-p', str(POSTGRES_PORT),
            '-U', POSTGRES_USER,
            '-d', 'postgres',
            '-c', f'DROP DATABASE IF EXISTS {POSTGRES_DB}_restore'
        ]
        
        restore_cmd = [
            'pg_restore',
            '-h', POSTGRES_HOST,
            '-p', str(POSTGRES_PORT),
            '-U', POSTGRES_USER,
            '-d', f'{POSTGRES_DB}_restore',
            '-c',  # Clean (drop) objects before recreating
            str(backup_file)
        ]
        
        try:
            logger.info(f"Starting PostgreSQL restore from {backup_file}")
            subprocess.run(drop_cmd, env=env, check=True, capture_output=True)
            subprocess.run(restore_cmd, env=env, check=True, capture_output=True)
            logger.info("PostgreSQL restore completed")
        except subprocess.CalledProcessError as e:
            logger.error(f"PostgreSQL restore failed: {e}")
            raise
    
    # =========================================================================
    # Redis Backup/Recovery
    # =========================================================================
    
    def backup_redis(self) -> Path:
        """Create Redis backup"""
        backup_file = BACKUP_DIR / self.get_backup_filename('redis')
        
        try:
            import redis
            r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
            
            # BGSAVE triggers background save
            r.bgsave()
            
            # Wait for save to complete
            while r.lastsave() == r.lastsave():
                import time
                time.sleep(0.1)
            
            # Copy the RDB file
            rdb_source = Path('/data/appendonly.aof') if Path('/data/appendonly.aof').exists() else None
            
            # For AOF persistence
            if rdb_source:
                shutil.copy(rdb_source, backup_file)
            else:
                # Get all keys and save as JSON
                keys = r.keys('*')
                data = {}
                for key in keys:
                    key_type = r.type(key)
                    if key_type == 'string':
                        data[key] = r.get(key)
                    elif key_type == 'hash':
                        data[key] = r.hgetall(key)
                    elif key_type == 'list':
                        data[key] = r.lrange(key, 0, -1)
                    elif key_type == 'set':
                        data[key] = list(r.smembers(key))
                    elif key_type == 'zset':
                        data[key] = r.zrange(key, 0, -1, withscores=True)
                
                with gzip.open(backup_file, 'wt') as f:
                    json.dump(data, f)
            
            logger.info(f"Redis backup completed: {backup_file}")
            return backup_file
        
        except Exception as e:
            logger.error(f"Redis backup failed: {e}")
            raise
    
    def restore_redis(self, backup_file: Path):
        """Restore Redis from backup"""
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_file}")
        
        try:
            import redis
            r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
            
            # Clear existing data
            r.flushall()
            
            # Load from JSON backup
            with gzip.open(backup_file, 'rt') as f:
                data = json.load(f)
            
            for key, value in data.items():
                key_type = r.type(key)
                if isinstance(value, dict):
                    r.hset(key, mapping=value)
                elif isinstance(value, list):
                    # Check if it's a sorted set (contains tuples with scores)
                    if value and isinstance(value[0], (list, tuple)):
                        r.zadd(key, dict(value))
                    else:
                        r.rpush(key, *value)
                elif isinstance(value, set):
                    r.sadd(key, *value)
                else:
                    r.set(key, value)
            
            logger.info("Redis restore completed")
        
        except Exception as e:
            logger.error(f"Redis restore failed: {e}")
            raise
    
    # =========================================================================
    # Evidence Files Backup/Recovery
    # =========================================================================
    
    def backup_evidence(self) -> Path:
        """Create evidence files backup"""
        backup_file = BACKUP_DIR / self.get_backup_filename('evidence')
        
        if not EVIDENCE_DIR.exists():
            logger.warning(f"Evidence directory not found: {EVIDENCE_DIR}")
            return None
        
        try:
            logger.info(f"Starting evidence backup to {backup_file}")
            
            # Create tar.gz archive
            shutil.make_archive(
                str(backup_file).replace('.tar.gz', ''),
                'gzip',
                root_dir=EVIDENCE_DIR.parent,
                base_dir=EVIDENCE_DIR.name
            )
            
            logger.info(f"Evidence backup completed: {backup_file}")
            return backup_file
        
        except Exception as e:
            logger.error(f"Evidence backup failed: {e}")
            raise
    
    def restore_evidence(self, backup_file: Path):
        """Restore evidence files from backup"""
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_file}")
        
        try:
            logger.info(f"Starting evidence restore from {backup_file}")
            
            # Clear existing evidence
            if EVIDENCE_DIR.exists():
                shutil.rmtree(EVIDENCE_DIR)
            EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
            
            # Extract backup
            shutil.unpack_archive(str(backup_file), str(EVIDENCE_DIR))
            
            logger.info("Evidence restore completed")
        
        except Exception as e:
            logger.error(f"Evidence restore failed: {e}")
            raise
    
    # =========================================================================
    # Full Backup/Recovery
    # =========================================================================
    
    def full_backup(self) -> Dict[str, Path]:
        """Create full system backup"""
        backup_manifest = {
            'timestamp': self.get_timestamp(),
            'version': '1.0',
            'components': {}
        }
        
        try:
            # Backup PostgreSQL
            backup_manifest['components']['postgres'] = str(self.backup_postgres())
            
            # Backup Redis
            backup_manifest['components']['redis'] = str(self.backup_redis())
            
            # Backup Evidence
            evidence_backup = self.backup_evidence()
            if evidence_backup:
                backup_manifest['components']['evidence'] = str(evidence_backup)
            
            # Save manifest
            manifest_file = BACKUP_DIR / f"anptop_manifest_{self.get_timestamp()}.json"
            with open(manifest_file, 'w') as f:
                json.dump(backup_manifest, f, indent=2)
            
            backup_manifest['manifest_file'] = str(manifest_file)
            
            logger.info("Full backup completed successfully")
            return backup_manifest
        
        except Exception as e:
            logger.error(f"Full backup failed: {e}")
            raise
    
    def full_restore(self, manifest_file: Path):
        """Restore full system from manifest"""
        with open(manifest_file, 'r') as f:
            manifest = json.load(f)
        
        try:
            # Restore components in order
            if 'postgres' in manifest['components']:
                self.restore_postgres(Path(manifest['components']['postgres']))
            
            if 'redis' in manifest['components']:
                self.restore_redis(Path(manifest['components']['redis']))
            
            if 'evidence' in manifest['components']:
                self.restore_evidence(Path(manifest['components']['evidence']))
            
            logger.info("Full restore completed successfully")
        
        except Exception as e:
            logger.error(f"Full restore failed: {e}")
            raise
    
    # =========================================================================
    # Maintenance
    # =========================================================================
    
    def cleanup_old_backups(self):
        """Remove backups older than retention period"""
        cutoff_date = datetime.utcnow() - timedelta(days=RETENTION_DAYS)
        
        removed = 0
        for backup_file in BACKUP_DIR.glob('anptop_*'):
            if backup_file.stat().st_mtime < cutoff_date.timestamp():
                backup_file.unlink()
                removed += 1
                logger.info(f"Removed old backup: {backup_file}")
        
        logger.info(f"Cleaned up {removed} old backup files")
        return removed
    
    def list_backups(self) -> Dict[str, Any]:
        """List all available backups"""
        backups = {
            'postgres': [],
            'redis': [],
            'evidence': [],
            'manifests': []
        }
        
        for backup_file in sorted(BACKUP_DIR.glob('anptop_*')):
            if backup_file.suffix == '.gz':
                backup_type = backup_file.name.split('_')[1]
                if backup_type in backups:
                    backups[backup_type].append({
                        'file': str(backup_file),
                        'size_mb': round(backup_file.stat().st_size / (1024 * 1024), 2),
                        'created': datetime.fromtimestamp(
                            backup_file.stat().st_mtime
                        ).isoformat()
                    })
            elif backup_file.suffix == '.json':
                backups['manifests'].append({
                    'file': str(backup_file),
                    'created': datetime.fromtimestamp(
                        backup_file.stat().st_mtime
                    ).isoformat()
                })
        
        return backups
    
    def verify_backup(self, backup_file: Path) -> bool:
        """Verify backup integrity"""
        if not backup_file.exists():
            return False
        
        try:
            if backup_file.suffix == '.gz':
                # Test gzip integrity
                with gzip.open(backup_file, 'rt') as f:
                    f.read(1024)
            
            logger.info(f"Backup verified: {backup_file}")
            return True
        
        except Exception as e:
            logger.error(f"Backup verification failed: {e}")
            return False


async def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ANPTOP Backup Manager')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Backup commands
    backup_parser = subparsers.add_parser('backup', help='Create backups')
    backup_parser.add_argument(
        '--type',
        choices=['postgres', 'redis', 'evidence', 'full'],
        default='full',
        help='Backup type'
    )
    
    # Restore commands
    restore_parser = subparsers.add_parser('restore', help='Restore from backup')
    restore_parser.add_argument(
        'file',
        type=Path,
        help='Backup file or manifest'
    )
    
    # Maintenance commands
    subparsers.add_parser('cleanup', help='Remove old backups')
    subparsers.add_parser('list', help='List available backups')
    
    args = parser.parse_args()
    
    manager = BackupManager()
    
    if args.command == 'backup':
        if args.type == 'postgres':
            path = manager.backup_postgres()
            print(f"PostgreSQL backup: {path}")
        elif args.type == 'redis':
            path = manager.backup_redis()
            print(f"Redis backup: {path}")
        elif args.type == 'evidence':
            path = manager.backup_evidence()
            if path:
                print(f"Evidence backup: {path}")
        elif args.type == 'full':
            result = manager.full_backup()
            print(f"Full backup completed: {result['manifest_file']}")
    
    elif args.command == 'restore':
        if str(args.file).endswith('_manifest_'):
            manager.full_restore(args.file)
            print("Full restore completed")
        else:
            # Determine type and restore
            if 'postgres' in str(args.file):
                manager.restore_postgres(args.file)
            elif 'redis' in str(args.file):
                manager.restore_redis(args.file)
            elif 'evidence' in str(args.file):
                manager.restore_evidence(args.file)
            print("Restore completed")
    
    elif args.command == 'cleanup':
        removed = manager.cleanup_old_backups()
        print(f"Removed {removed} old backups")
    
    elif args.command == 'list':
        backups = manager.list_backups()
        print(json.dumps(backups, indent=2))
    
    else:
        parser.print_help()


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
