# SKA learning on pathological ECG — results

**What the SKA learner does with the five waves of the heartbeat, in healthy and pathological hearts.**

This folder holds the **results** of the SKA engine: the learner's output for every step.
The engine code is not published. The method, the input and the learner's 3D space are the
ones of [SKA-ECG-Heart-Rate-Variability](https://github.com/quantiota/SKA-ECG-Heart-Rate-Variability/tree/main/ska-ecg-engine),
unchanged.

The records come from the PhysioNet
[PTB Diagnostic ECG Database](https://physionet.org/content/ptbdb/1.0.0/), lead II, 1000 Hz,
the whole record (about 2 minutes). Cosine input, scale 25. One run per record: all its steps,
five per beat.

## Healthy controls

| age | record | cube |
|---|---|---|
| 22 | ptb185 | [`ska_ecg_ptb185_scale25_vr.html`](../vr/ska_ecg_ptb185_scale25_vr.html) |
| 25 | ptb236 | [`ska_ecg_ptb236_scale25_vr.html`](../vr/ska_ecg_ptb236_scale25_vr.html) |
| 28 | ptb242 | [`ska_ecg_ptb242_scale25_vr.html`](../vr/ska_ecg_ptb242_scale25_vr.html) |
| 32 | ptb105 | [`ska_ecg_ptb105_scale25_vr.html`](../vr/ska_ecg_ptb105_scale25_vr.html) |
| 35 | ptb279 | [`ska_ecg_ptb279_scale25_vr.html`](../vr/ska_ecg_ptb279_scale25_vr.html) |

## Myocardial infarction

One woman aged 42, acute inferior infarction, four records.

| when | record | cube |
|---|---|---|
| the day of the infarction | ptb049_s0173 | [`ska_ecg_ptb049_s0173_scale25_vr.html`](../vr/ska_ecg_ptb049_s0173_scale25_vr.html) |
| 4 days after | ptb049_s0178 | [`ska_ecg_ptb049_s0178_scale25_vr.html`](../vr/ska_ecg_ptb049_s0178_scale25_vr.html) |
| 11 days after | ptb049_s0186 | [`ska_ecg_ptb049_s0186_scale25_vr.html`](../vr/ska_ecg_ptb049_s0186_scale25_vr.html) |
| 14 months after | ptb049_s0314 | [`ska_ecg_ptb049_s0314_scale25_vr.html`](../vr/ska_ecg_ptb049_s0314_scale25_vr.html) |

## Files

```
build_ecg_vr.py              fills the cube template with one run (record, scale)
ska_ecg_vr_template.html     the cube (Three.js), placeholders __DATA__ and __DESCRIPTION__
results/
└── <record>/
    └── ska_<record>_runs.csv    one row per step
```

The cubes are in [`../vr/`](../vr/). To rebuild one:

```bash
python build_ecg_vr.py ska_ecg_vr_template.html results/ptb185/ska_ptb185_runs.csv 25 "female, 22, Healthy control" ../vr/ska_ecg_ptb185_scale25_vr.html
```

## Data — `results/<record>/ska_<record>_runs.csv`

The same columns as in SKA-ECG-Heart-Rate-Variability, stored in QuestDB in `ecg_patho_ska_results`.

| column | meaning |
|---|---|
| `record_id`, `input`, `scale` | the run |
| `event`, `transition` | the wave (P, Q, R, S, T) and the transition into it |
| `event_index`, `k`, `peak` | step n = 5k + j, beat k, sample index of the wave's peak |
| `value_cos`, `value_sin` | Re c_n, Im c_n (mV); 0 when the wave is absent |
| `value_return` | u_n = Re ċ_n (mV) |
| `x_input` | x_n, what the learner reads |
| `rr` | time from the beat's P peak to the next beat's P peak (ms) |
| `knowledge` | z = ‖Z‖ |
| `decision`, `decision_norm` | the learner's last decision D and ‖D‖ |
| `entropy` | H |
| `delta_t` | time since the previous wave (s) |
| `cosine_similarity`, `delta_h_over_delta_d`, `frobenius_norm`, `matrix_size` | learner diagnostics |
| `P`, `zdot`, `zdot_back` | **computed at export**: P = exp(−\|ΔH/H\|) from `entropy`; ż from `knowledge` and `delta_t`, central (`zdot`) and backward (`zdot_back`) difference |
| `timestamp` | the wave's time in the recording |
