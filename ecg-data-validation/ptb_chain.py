"""PTB record reader — the data source for the pathology stream.

Turns PTB WFDB records (header + 16-bit binary) into a sequence of samples, one
per millisecond, for a single fixed lead:

    sample k  =  the ECG at t = k ms
    value     =  (adc - baseline) / gain     in mV, from the record header

The 12 standard leads are in the .dat file, the 3 Frank leads in the .xyz file.
Records are emitted one after another, each whole. Raw values only: no
filtering, no beat detection, no scaling.
"""
from __future__ import annotations

import pathlib

import numpy as np


def read_header(path):
    """PTB .hea -> fs, n, the signals (file, gain, baseline, name) and the
    '# key: value' comments (age, sex, Reason for admission, ...)."""
    text = pathlib.Path(path).read_text().splitlines()
    lines = [l for l in text if l.strip() and not l.startswith('#')]
    _, nsig, fs, n = lines[0].split()[:4]
    signals = []
    for l in lines[1:1 + int(nsig)]:
        f = l.split()
        g = f[2].split('/')[0]
        gain, base = (float(g.split('(')[0]), float(g.split('(')[1].rstrip(')'))) \
            if '(' in g else (float(g), 0.0)
        signals.append({'file': f[0], 'fmt': f[1], 'gain': gain, 'baseline': base,
                        'name': f[-1]})
    info = {}
    for l in text:
        if l.startswith('#') and ':' in l:
            k, v = l[1:].split(':', 1)
            info[k.strip()] = v.strip()
    return {'nsig': int(nsig), 'fs': float(fs), 'n': int(n), 'signals': signals,
            'info': info}


def read_records(path):
    """records.txt -> [(PTB path, record_id)], in order ('#' lines ignored)."""
    out = []
    for l in pathlib.Path(path).read_text().splitlines():
        if l.strip() and not l.startswith('#'):
            f = l.split()
            out.append((f[0], f[1]))
    return out


class PTBRecord:
    """One record, one lead, whole."""

    def __init__(self, data_dir, path, record_id, channel):
        self.record_id = record_id
        hdr = read_header(pathlib.Path(data_dir) / f'{path}.hea')
        names = [s['name'] for s in hdr['signals']]
        if channel not in names:
            raise SystemExit(f'record {record_id} has no channel {channel!r}; has {names}')
        sig = hdr['signals'][names.index(channel)]
        if sig['fmt'] != '16':
            raise SystemExit(f'record {record_id}: format {sig["fmt"]} not supported')
        self.fs, self.gain, self.baseline = hdr['fs'], sig['gain'], sig['baseline']
        self.info = hdr['info']
        self.age = self.info.get('age', 'unknown')

        same = [s['name'] for s in hdr['signals'] if s['file'] == sig['file']]
        raw = np.fromfile((pathlib.Path(data_dir) / path).parent / sig['file'], dtype='<i2')
        if raw.size != hdr['n'] * len(same):
            raise SystemExit(f'record {record_id}: header says {hdr["n"]:,} samples, '
                             f'file holds {raw.size // len(same):,}')
        self.adc = raw.reshape(-1, len(same))[:, same.index(channel)].astype(np.int64)

    @property
    def n(self):
        return int(self.adc.size)

    def value(self):
        """The samples in mV."""
        return (self.adc - self.baseline) / self.gain


class PTBChain:
    """Walks the listed records and yields one event per sample."""

    def __init__(self, data_dir, records, channel, max_steps=None):
        self.records = [PTBRecord(data_dir, p, rid, channel) for p, rid in records]
        self.max_steps = max_steps

    @property
    def total_steps(self):
        return sum(r.n for r in self.records)

    def events(self):
        step = 0
        for rec in self.records:
            v = rec.value()
            for k in range(rec.n):
                if self.max_steps is not None and step >= self.max_steps:
                    return
                yield {'step': step, 'record_id': rec.record_id, 'age_band': rec.age,
                       'sample_index': k, 'record_length': rec.n,
                       'adc': int(rec.adc[k]), 'value': float(v[k])}
                step += 1


if __name__ == '__main__':
    from config import ECG_CONFIG as C
    for p, rid in read_records(C['records']):
        r = PTBRecord(C['data_dir'], p, rid, C['channel'])
        v = r.value()
        print(f'{rid}  {p}  age {r.age}  {r.info.get("sex", "?")}  '
              f'{r.info.get("Reason for admission", "?")}  '
              f'{r.n:,} samples ({r.n / r.fs:.0f} s)  {v.min():+.3f} .. {v.max():+.3f} mV')
