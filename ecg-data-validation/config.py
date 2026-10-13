"""Configuration for the PTB ECG stream."""
import os

# QuestDB ILP (line protocol) — ingestion path, 9009
ILP_CONFIG = {
    'host': os.getenv('QDB_ILP_HOST', os.getenv('QDB_PG_HOST', 'localhost')),
    'port': int(os.getenv('QDB_ILP_PORT', '9009')),
}

# QuestDB pg-wire — queries and DDL, 8812
QDB_CONFIG = {
    'dbname': os.getenv('QDB_PG_NAME', 'qdb'),
    'user': os.getenv('QDB_PG_USER', 'admin'),
    'password': os.getenv('QDB_PG_PASSWORD', 'quest'),
    'host': os.getenv('QDB_PG_HOST', 'localhost'),
    'port': os.getenv('QDB_PG_PORT', '8812'),
}

# ECG Stream Configuration
ECG_CONFIG = {
    'table': 'ecg_patho_steps',
    'data_dir': os.getenv('ECG_DATA', 'data'),
    'records': 'records.txt',        # PTB record paths and IDs, in order
    'dataset': 'ptbdb/1.0.0',
    'channel': 'ii',                 # one fixed lead for every record
    # PTB records were sampled at 1000 Hz and last about 2 minutes; each is
    # streamed whole, at the native rate: 1 sample = 1 ms.
    'rate_hz': 1000.0,
    'packet_steps': 1000,            # one packet per second
    'max_steps': None,               # None = every record, whole length
}

# Logging Configuration
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s %(levelname)s %(message)s',
    'file': 'logs/ecg_validation.log',
}
