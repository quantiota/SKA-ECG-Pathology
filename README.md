# SKA ECG Pathology

 [![arXiv](https://img.shields.io/badge/arXiv-2503.13942-b31b1b)](https://arxiv.org/abs/2503.13942)   [![arXiv](https://img.shields.io/badge/arXiv-2504.03214-b31b1b)](https://arxiv.org/abs/2504.03214)   [![Hugging Face](https://img.shields.io/badge/🤗%20Hugging%20Face-SKA-orange)](https://huggingface.co/quant-iota) [![Sponsor](https://img.shields.io/badge/Sponsor-quantiota-ea4aaa?logo=github-sponsors)](https://github.com/sponsors/quantiota)


**Structured Knowledge Accumulation (SKA) on pathological ECG**

This project applies the SKA real-time learner to pathological hearts, from the PhysioNet
[PTB Diagnostic ECG Database](https://physionet.org/content/ptbdb/1.0.0/).

The method is the one of
[SKA-ECG-Heart-Rate-Variability](https://github.com/quantiota/SKA-ECG-Heart-Rate-Variability):
the five waves of each heartbeat, the same input, the same learner, the same 3D cube.

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

**Myocardial infarction**: patients with their first ECG on the day of the infarction (day 0),
and the following ECGs. Records `ptb<patient>_<PTB record>`, e.g. `ptb049_s0173`.

Women:

| patient | age | infarction | PTB records | days after the infarction |
|---|---|---|---|---|
| 049 | 42 | inferior | s0173, s0178, s0186, s0314 | 0, 4, 11, 444 |
| 051 | 55 | antero-septal | s0179, s0181, s0187, s0213 | 0, 4, 10, 112 |
| 085 | 56 | posterior | s0296, s0297, s0298, s0345 | 0, 5, 11, 145 |
| 098 | 63 | inferior | s0386, s0389, s0398, s0409 | 0, 5, 23, 30 |
| 046 | 64 | antero-septal | s0156, s0161, s0168, s0184 | 0, 2, 12, 37 |
| 086 | 66 | infero-lateral | s0316 | 0 |
| 100 | 72 | inferior | s0399, s0401, s0407 | 0, 3, 7 |
| 091 | 78 | antero-septal | s0353, s0357, s0361, s0408 | 0, 4, 11, 78 |

Men:

| patient | age | infarction | PTB records | days after the infarction |
|---|---|---|---|---|
| 035 | 40 | inferior | s0110, s0119, s0145 | 0, 5, 63 |
| 054 | 47 | infero-lateral | s0192, s0195, s0197 | 0, 3, 10 |
| 032 | 49 | antero-septal | s0102, s0106, s0115, s0165 | 0, 4, 11, 98 |
| 065 | 52 | infero-postero-lateral | s0221, s0226, s0229, s0282 | 0, 5, 7, 194 |
| 099 | 52 | antero-lateral | s0387, s0388, s0397, s0419 | 0, 4, 22, 91 |
| 088 | 54 | inferior | s0339, s0352, s0413 | 0, 7, 92 |
| 084 | 55 | antero-septal | s0281, s0288, s0289, s0313 | 0, 6, 7, 127 |
| 077 | 65 | inferior | s0251, s0254, s0258, s0285 | 0, 5, 9, 43 |
| 082 | 65 | antero-septal | s0267, s0271, s0279, s0320 | 0, 3, 8, 142 |
| 087 | 66 | infero-postero-lateral | s0321, s0326, s0330 | 0, 4, 9 |
| 078 | 68 | inferior | s0255, s0259, s0262, s0317 | 0, 2, 9, 167 |
| 097 | 68 | anterior | s0380, s0382, s0384, s0394 | 0, 3, 10, 34 |
| 023 | 69 | inferior | s0080, s0081, s0085, s0103 | 0, 2, 11, 31 |


## Repository

- [`ecg-data-validation/`](ecg-data-validation/): streams the PTB records into QuestDB (`ecg_patho_steps`)
- [`ska-ecg-engine/results/`](ska-ecg-engine/results/): the SKA output of each record (`ecg_patho_ska_results`)
- [`vr/`](vr/): the 3D cubes

The SKA real-time engine is proprietary and is not included in this repository.


## License

MIT. ECG data: from PhysioNet, under the license of the PTB Diagnostic ECG Database; cite the
database when you use it.
