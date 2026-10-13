# SKA ECG Pathology

 [![arXiv](https://img.shields.io/badge/arXiv-2503.13942-b31b1b)](https://arxiv.org/abs/2503.13942)   [![arXiv](https://img.shields.io/badge/arXiv-2504.03214-b31b1b)](https://arxiv.org/abs/2504.03214)   [![Hugging Face](https://img.shields.io/badge/🤗%20Hugging%20Face-SKA-orange)](https://huggingface.co/quant-iota) [![Sponsor](https://img.shields.io/badge/Sponsor-quantiota-ea4aaa?logo=github-sponsors)](https://github.com/sponsors/quantiota)


**Structured Knowledge Accumulation (SKA) on pathological ECG**

This project applies the SKA real-time learner to pathological hearts, from the PhysioNet
[PTB Diagnostic ECG Database](https://physionet.org/content/ptbdb/1.0.0/).

The method is the one of
[SKA-ECG-Heart-Rate-Variability](https://github.com/quantiota/SKA-ECG-Heart-Rate-Variability):
the five waves of each heartbeat, the same input, the same learner, the same 3D cube.
Nothing is changed for pathology.

## A missing event

**First prototype (the results here).** Every beat sends its five events to the learner. A wave
that is not found in a beat (`present` = False) is still sent, with c = 0. If S is missing,
the learner reads ċ = 0 − c_R for "R→S" and ċ = c_T − 0 for "S→T": the two transitions keep
their names, but each one now joins a wave and nothing. Their transition probability P shifts:
lower for R→S, higher for S→T. The steps move within the band, not into a band of their own.
On a healthy heart, where the
waves are almost always present, the first prototype reads the beat as it is.

**Second prototype (next step).** A missing wave is removed from the stream. If S is
missing, the beat is P → Q → R → T → P, four events, and the transition is **R→T**:

**ċ = c_T − c_R**

Each transition then joins two waves that exist, and a new transition (R→T, P→R, …) is a
new band in the learner's space.

| | first prototype | second prototype |
|---|---|---|
| missing wave | sent, c = 0 | removed from the stream |
| beat with S missing | P→Q, Q→R, R→S, S→T, T→P | P→Q, Q→R, **R→T**, T→P |
| for | healthy hearts | pathological hearts |



## Cases

Lead II, 1000 Hz, the whole record (about 2 minutes), scale 25.

**Healthy controls**, the reference:

| record | PTB record | age |
|---|---|---|
| ptb185 | patient185/s0336lre | 22 |
| ptb236 | patient236/s0464_re | 25 |
| ptb242 | patient242/s0471_re | 28 |
| ptb105 | patient105/s0303lre | 32 |
| ptb279 | patient279/s0534_re | 35 |

**Myocardial infarction**, one woman aged 42 (acute inferior infarction), four records:

| record | PTB record | when |
|---|---|---|
| ptb049_s0173 | patient049/s0173lre | the day of the infarction |
| ptb049_s0178 | patient049/s0178lre | 4 days after |
| ptb049_s0186 | patient049/s0186lre | 11 days after |
| ptb049_s0314 | patient049/s0314lre | 14 months after |


## Repository

- [`ecg-data-validation/`](ecg-data-validation/): streams the PTB records into QuestDB (`ecg_patho_steps`)
- [`ska-ecg-engine/results/`](ska-ecg-engine/results/): the SKA output of each record (`ecg_patho_ska_results`)
- [`vr/`](vr/): the 3D cubes

The SKA real-time engine is proprietary and is not included in this repository.


## License

MIT. ECG data: from PhysioNet, under the license of the PTB Diagnostic ECG Database; cite the
database when you use it.
