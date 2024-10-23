#!/usr/bin/env python
"""
This script is used to automatically backup and delete backups from Sonarr/Radarr.
It runs forever and triggers a new backup every BACKUP_INTERVAL seconds.
It will command Sonarr/Radarr to create a new backup, unzip it, run tarsnapper on it and delete the backup afterwards.

Environment variables:
    - ARR_API_KEY:          API key for Sonarr/Radarr
    - ARR_URL:              URL of Sonarr/Radarr
    - ARR_CONFIG_DIR:       Directory where Sonarr/Radarr stores backups (default: /config)
    - TARSNAPPER_CONFIG:    Path to tarsnapper config file (default: /config/tarsnapper.yaml)
    - BACKUP_INTERVAL:      Interval in seconds between backups (default: 86400)
    - ARR_TMP_DIR:          Directory to store temporary files (default: /tmp/arr-backup)
    - LOG_LEVEL:            Log level (default: INFO)
    - LOG_FORMAT:           Log format (default: '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
"""

import os
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import logging
import json
import requests
import subprocess
import time
import typing
import zipfile

ARR_API_KEY = os.getenv('ARR_API_KEY')
ARR_URL = os.getenv('ARR_URL')
ARR_CONFIG_DIR = os.getenv('ARR_CONFIG_DIR', '/config')

TARSNAPPER_CONFIG = os.getenv('TARSNAPPER_CONFIG', '/config/tarsnapper.yaml')

BACKUP_INTERVAL = os.getenv('BACKUP_INTERVAL', 86400)
TMP_DIR = os.getenv('ARR_TMP_DIR', '/tmp/arr-backup')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


@dataclass
class Backup:
    id: int
    name: str
    time: datetime


class Arr:
    def __init__(self):
        self.session = requests.session()
        pass

    def send_request(self, req: requests.Request) -> requests.Response:
        # Add API key to request
        req.headers['X-API-KEY'] = ARR_API_KEY
        p_req = req.prepare()

        req = self.session.send(p_req)
        if req.status_code != 200 and req.status_code != 201:
            raise RuntimeError(f'Failed to send request: {req.status_code}')

        return req

    def get_backups(self) -> list[dict[str, typing.Any]]:
        logger.debug('Getting backups from %s', ARR_URL)
        req = requests.Request('GET', f'{ARR_URL}/api/v3/system/backup')
        res = self.send_request(req)
        return res.json()

    def get_latest_backup(self) -> Backup:
        backups = self.get_backups()
        try:
            latest = max(filter(lambda x: x['type'] == 'manual', backups),
                         key=lambda x: datetime.fromisoformat(x['time']))
            return Backup(latest['id'], latest['name'], datetime.fromisoformat(latest['time']))
        except ValueError:
            raise RuntimeError('No manual backups found')

    def delete_backup(self, id: int):
        logger.debug(f'Deleting backup {id}')
        req = requests.Request('DELETE', f'{ARR_URL}/api/v3/system/backup/{id}')
        self.send_request(req)

    def trigger_backup(self):
        logger.debug('Triggering new backup')
        req = requests.Request('POST', f'{ARR_URL}/api/v3/command')
        req.data = json.dumps({"name": "Backup"})
        req.headers['Content-Type'] = 'application/json'
        self.send_request(req)

    def get_backup(self):
        backup = None
        try:
            backup = self.get_latest_backup()
            logger.info(f'Latest backup: {backup.name} ({backup.time})')

            if (datetime.now(timezone.utc) - backup.time).total_seconds() > BACKUP_INTERVAL / 2:
                logger.info('Backup is too old, triggering new backup')
                self.trigger_backup()
        except RuntimeError as e:
            if 'No manual backups found' not in str(e):
                raise e
            logger.info('No manual backups found, triggering new backup')
            self.trigger_backup()

        # Wait for backup to finish
        while backup is None or (datetime.now(timezone.utc) - backup.time).total_seconds() > BACKUP_INTERVAL / 2:
            logger.info('Waiting for backup to finish')
            time.sleep(5)
            backup = self.get_latest_backup()

        return backup


def copy_backup(name: str) -> str:
    path = f'{ARR_CONFIG_DIR}/Backups/manual/{name}'
    dst_path = TMP_DIR
    logger.info(f'Copying backup {path} to {dst_path}')

    # Create directory in tmpdir to unzip backup into
    os.makedirs(dst_path, exist_ok=True)

    # Unzip backup
    try:
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(dst_path)
    except FileNotFoundError:
        shutil.rmtree(dst_path)
        raise

    return dst_path


def tarsnap_fsck():
    logger.info('Running tarsnap --fsck')
    child = subprocess.Popen(
        ['tarsnap', '--fsck'],
    )
    ret = child.wait()
    if ret != 0:
        raise RuntimeError(f'tarsnap --fsck failed with exit code {ret}')


def setup_tarsnap():
    # Check if tarsnapper is installed
    try:
        subprocess.run(['tarsnapper', '--version'])
    except FileNotFoundError:
        raise RuntimeError('tarsnapper is not installed')

    # Check if tarsnap is installed
    try:
        subprocess.run(['tarsnap', '--version'])
    except FileNotFoundError:
        raise RuntimeError('tarsnap is not installed')

    # Check if tarsnapper config file exists
    if not os.path.exists(TARSNAPPER_CONFIG):
        raise RuntimeError(f'TARSNAPPER_CONFIG {TARSNAPPER_CONFIG} does not exist')

    # Run tarsnap --fsck
    tarsnap_fsck()


def tarsnapper():
    # Run tarsnap --fsck
    tarsnap_fsck()

    # Run tarsnapper
    logger.info('Running tarsnapper')

    child = subprocess.Popen(
        ['tarsnapper', '--config', TARSNAPPER_CONFIG, '-v', 'make'],
    )

    ret = child.wait()
    if ret != 0:
        raise RuntimeError(f'tarsnapper failed with exit code {ret}')


def inner_main():
    arr = Arr()

    # Get latest backup
    backup = arr.get_backup()

    # Copy backup locally
    backup_path = copy_backup(backup.name)
    logger.info(f'Backup copied to {backup_path}')

    # Run tarsnapper
    tarsnapper()

    # Delete backup
    # shutil.rmtree(backup_path)
    for filename in os.listdir(backup_path):
        file_path = os.path.join(backup_path, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    arr.delete_backup(backup.id)
    logger.info(f'Backup deleted')


def main():
    # Check if all required environment variables are set
    if not ARR_API_KEY:
        raise RuntimeError('ARR_API_KEY is not set')
    if not ARR_URL:
        raise RuntimeError('ARR_URL is not set')

    # Setup logging
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)

    setup_tarsnap()

    while True:
        try:
            logger.info('Starting backup process')
            inner_main()
        except Exception as e:
            logger.error(f'An error occurred', exc_info=e)

        logger.info("Next backup at %s", datetime.now() + timedelta(seconds=BACKUP_INTERVAL))
        time.sleep(BACKUP_INTERVAL)


if __name__ == '__main__':
    main()
