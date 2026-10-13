"""Simulated real-time PTB ECG stream into QuestDB — raw parameters only.

The PTB records were sampled at 1000 Hz, so the stream runs at the same rate.
Samples are emitted in packets paced against the wall clock, and each row is
stamped on a FIXED GRID anchored at the run's start time:

    timestamp(k) = t_start + k / rate_hz

These are ASSIGNED timestamps, not observations.

Records are streamed one after another, in the order of records.txt, each whole,
on the same lead. They are APPENDED to ecg_patho_steps: a record already in the
table is refused, so each case is streamed once and stays separable by record_id.
age_band holds the patient's age from the PTB header.

No returns, no entropy, no learning. Raw values only.
"""
import argparse
import logging
import os
import signal
import socket
import time
import traceback

import psycopg2

from config import QDB_CONFIG, ILP_CONFIG, ECG_CONFIG, LOG_CONFIG
from ptb_chain import PTBChain, read_records

os.makedirs('logs', exist_ok=True)
logging.basicConfig(level=getattr(logging, LOG_CONFIG['level']),
                    format=LOG_CONFIG['format'],
                    filename=LOG_CONFIG['file'], filemode='a')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter(LOG_CONFIG['format']))
logging.getLogger('').addHandler(console)

TABLE = ECG_CONFIG['table']

CREATE_SQL = f"""
CREATE TABLE IF NOT EXISTS {TABLE} (
    record_id SYMBOL,
    age_band SYMBOL,
    channel SYMBOL,
    step_index LONG,
    sample_index LONG,
    adc LONG,
    value DOUBLE,
    rate_hz DOUBLE,
    record_length LONG,
    total_steps LONG,
    timestamp TIMESTAMP
) TIMESTAMP(timestamp) PARTITION BY DAY;
"""


def ilp_escape(v: str) -> str:
    """Escape an ILP tag value: spaces, commas and equals must be backslashed."""
    return str(v).replace("\\", "\\\\").replace(" ", "\\ ").replace(",", "\\,").replace("=", "\\=")


def prepare_table(record_ids):
    """Create the table if absent. Never drops. Refuses records already present."""
    conn = psycopg2.connect(**QDB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute(CREATE_SQL)
            conn.commit()
            cur.execute(f"SELECT DISTINCT record_id FROM {TABLE};")
            present = {r[0] for r in cur.fetchall()}
    finally:
        conn.close()
    dup = [r for r in record_ids if r in present]
    if dup:
        raise SystemExit(f"already in {TABLE}: {dup}. Remove them from records.txt.")
    logging.info(f"{TABLE} ready ({len(present)} records already in it)")


def send_packet(sock, lines):
    """Ship one packet over ILP. Raises on failure: a dropped packet is a gap."""
    try:
        sock.sendall("".join(lines).encode())
    except Exception as e:
        logging.error(f"Error sending ECG packet over ILP: {e}")
        logging.error(traceback.format_exc())
        raise


def run_stream(data_dir, records, channel, rate_hz, packet_steps, max_steps):
    """Emit the records in packets, paced against the wall clock, over ILP."""
    chain = PTBChain(data_dir, records, channel, max_steps=max_steps)
    total_steps = chain.total_steps
    n_emit = total_steps if max_steps is None else min(max_steps, total_steps)
    dt = 1.0 / rate_hz
    logging.info(f"Streaming {len(records)} records | lead {channel} | "
                 f"{total_steps:,} samples | {rate_hz:,.0f} Hz | packets of {packet_steps:,}")
    logging.info(f"Emitting {n_emit:,} samples -> projected duration "
                 f"{n_emit / rate_hz / 60:.2f} min")

    ch = ilp_escape(channel)
    sock = socket.create_connection((ILP_CONFIG["host"], ILP_CONFIG["port"]), timeout=30)
    t_start = time.time()
    t0_ns = int(t_start * 1e9)

    lines, count, packets, current = [], 0, 0, None
    try:
        for e in chain.events():
            if e['record_id'] != current:
                current = e['record_id']
                logging.info(f"Record {current} (age {e['age_band']})")
            ts_ns = t0_ns + round(count * 1e9 / rate_hz)
            lines.append(
                f"{TABLE},record_id={ilp_escape(e['record_id'])},"
                f"age_band={ilp_escape(e['age_band'])},channel={ch} "
                f"step_index={e['step']}i,sample_index={e['sample_index']}i,"
                f"adc={e['adc']}i,value={e['value']:.6f},"
                f"rate_hz={rate_hz},record_length={e['record_length']}i,"
                f"total_steps={total_steps}i {ts_ns}\n")
            count += 1

            if len(lines) >= packet_steps:
                lag = (t_start + count * dt) - time.time()
                if lag > 0:
                    time.sleep(lag)
                send_packet(sock, lines)
                lines = []
                packets += 1
                if packets % 60 == 0:
                    el = time.time() - t_start
                    logging.info(f"Collected {count:,} raw ECG samples  "
                                 f"({count/el:,.0f} samples/s, {el:.0f}s elapsed)")
    finally:
        if lines:
            try:
                send_packet(sock, lines)
                logging.info(f"Flushed final partial packet ({len(lines)} samples)")
            except Exception:
                logging.error("Final packet could not be flushed")
        sock.close()

    elapsed = time.time() - t_start
    logging.info(f"Done: {count:,} samples in {elapsed:.1f}s ({count/elapsed:,.0f} samples/s)")
    return count


def shutdown(signum, frame):
    """Raise, so the stream's finally-block flushes the partial packet."""
    logging.info(f"Received shutdown signal: {signum}")
    raise KeyboardInterrupt


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--rate", type=float, default=ECG_CONFIG["rate_hz"],
                   help="emission rate in Hz (1000 = the native rate)")
    p.add_argument("--packet", type=int, default=ECG_CONFIG["packet_steps"])
    p.add_argument("--max-steps", type=int, default=ECG_CONFIG["max_steps"])
    p.add_argument("--records", nargs="+",
                   help="record_ids of records.txt to stream (default: all)")
    a = p.parse_args()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    records = read_records(ECG_CONFIG["records"])
    if a.records:
        unknown = set(a.records) - {rid for _, rid in records}
        if unknown:
            raise SystemExit(f"not in records.txt: {sorted(unknown)}")
        records = [(p, rid) for p, rid in records if rid in a.records]
    if not records:
        raise SystemExit("records.txt lists no record")
    prepare_table([rid for _, rid in records])
    run_stream(ECG_CONFIG["data_dir"], records, ECG_CONFIG["channel"],
               a.rate, a.packet, a.max_steps)
