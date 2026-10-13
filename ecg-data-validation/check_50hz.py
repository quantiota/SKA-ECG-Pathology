"""50 Hz rule: mains amplitude (48-52 Hz band) of the streamed lead, whole record, below 0.1 mV.

    python check_50hz.py          # every record of records.txt
Same rule as for the Autonomic Aging women.
"""
import numpy as np

from config import ECG_CONFIG as C
from ptb_chain import PTBRecord, read_records

for path, rid in read_records(C['records']):
    r = PTBRecord(C['data_dir'], path, rid, C['channel'])
    x = r.value()
    X = np.fft.rfft(x - x.mean())
    f = np.fft.rfftfreq(len(x), 1 / r.fs)
    band = (f >= 48) & (f <= 52)
    y = np.fft.irfft(np.where(band, X, 0), len(x))          # the 48-52 Hz part of the signal
    amp = np.sqrt(2) * y.std()                               # amplitude of an equivalent sine
    print(f"{rid}  {path}  50 Hz amplitude {amp:.2f} mV   {'OK' if amp < 0.1 else 'EXCLUDE'}")
