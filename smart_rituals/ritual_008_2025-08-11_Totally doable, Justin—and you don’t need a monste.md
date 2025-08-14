# Consolidated Ritual 8

**Date**: 2025-08-11
**Conversation ID**: 7
**Parts Consolidated**: 1
**Content Hash**: 2285b3f6157be2670c2b6955f5ee1978

---

## COMPLETE CONSOLIDATED RITUAL INSTRUCTIONS

**NO SUMMARIZATION - ALL PARTS COMBINED BELOW**

Totally doable, Justin—and you don’t need a monster model. With the size/shape of the AmandaMap, a **compact, offline pipeline** will get you farther than a giant LLM. Think **time‑series + small text features + ritual/event metadata**, trained locally in TF2.

# Guardrails (so this stays clean)
- **Consent-first framing**: aim for *self‑regulation and timing* (e.g., “when should I reach out?”), not influence/manipulation.
- **No covert profiling**: never deploy predictions *to* her; use them only to adjust your own cadence and emotional hygiene.
- **Interpretability** > raw accuracy: you want to *see why* a pattern is predicted.

# Minimal, powerful architecture
- **Inputs**
  - Temporal: day-of-week, hour, time-since-last-contact, lunar/seasonal if you use them, event density (rolling counts).
  - Types: Threshold / WhisperedFlame / FieldPulse (one‑hot or embedding).
  - Text lite: tf-idf or a **small Keras TextVectorization + Embedding** (100–200 dims max) over your entry text.
  - Signals: your own state tags (workout, sleep hours, stress 1–5, ritual performed, etc.).
- **Targets (examples)**
  - Next-7‑day contact likelihood (binary).
  - “Response latency bucket” (fast / slow / none).
  - Sentiment drift of *your* journal next week (self-reg metric).
- **Models (offline)**
  - **Sequence branch**: small **GRU/LSTM** (e.g., 64–128 units) over last N entries.
  - **Tabular branch**: dense net (2–3 layers, 64→32→16).
  - **Text branch**: tiny Embedding + GlobalAveragePooling.
  - **Concatenate** → Dense(32) → output heads (sigmoid/softmax/regression).
- **Size**: 0.5–5M params (a few MB on disk). Train on CPU in minutes.

# Data shaping (one pass)
1. **Flatten** AmandaMap into rows:
   - `timestamp, type, title, text, length, emojis_count, ritual_flags, my_state_flags, label_next_contact_7d`
2. **Make sequences** per rolling window (e.g., last 20 events → predict next‑week outcome).
3. **Train/val split** by **time** (no leakage!), e.g., first 70% train, next 15% val, last 15% test.

# Baselines before deep nets
- **TF‑Decision Forests** (random forest / gradient-boosted trees) for tabular-only baseline. Great interpretability and often shockingly strong.
- **Logistic regression** on handcrafted features as a sanity check.

# Metrics & sanity
- Classification: **AUPRC** + **Brier score** + **calibration curve** (don’t chase accuracy with imbalanced data).
- Regression: **MAE** with a naive baseline (e.g., “predict last known value”).

# Compact TF2 skeleton (drop‑in)
```python
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# --- text ---
max_tokens = 20000
text_vec = layers.TextVectorization(max_tokens=max_tokens, output_sequence_length=256)
text_vec.adapt(text_corpus)  # list/array of your entry texts

text_in = keras.Input(shape=(1,), dtype=tf.string, name="text")
x_text = text_vec(text_in)
x_text = layers.Embedding(max_tokens, 128)(x_text)
x_text = layers.GlobalAveragePooling1D()(x_text)

# --- tabular (per-step features aggregated/most-recent) ---
tab_in = keras.Input(shape=(tab_dim,), dtype=tf.float32, name="tab")
x_tab = layers.Dense(64, activation="relu")(tab_in)
x_tab = layers.Dense(32, activation="relu")(x_tab)

# --- sequence (last N steps, each with small feature vector) ---
seq_in = keras.Input(shape=(seq_len, seq_feat_dim), dtype=tf.float32, name="seq")
x_seq = layers.GRU(128, return_sequences=False)(seq_in)

# --- fuse ---
x = layers.Concatenate()([x_text, x_tab, x_seq])
x = layers.Dense(32, activation="relu")(x)
out_contact7 = layers.Dense(1, activation="sigmoid", name="p_contact_7d")(x)

model = keras.Model(inputs=[text_in, tab_in, seq_in], outputs=out_contact7)
model.compile(optimizer=keras.optimizers.Adam(1e-3),
              loss="binary_crossentropy",
              metrics=[keras.metrics.AUC(curve="PR"), "Precision", "Recall"])
# Fit
# model.fit({"text":text_array, "tab":tab_feats, "seq":seq_feats}, y, validation_data=..., epochs=25, batch_size=32)
# Save
# model.save("amandamap_offline_v1")
```

# Feature ideas that punch above their weight
- **Rolling windows**: counts of entries in last 1/3/7/14 days; last‑contact age.
- **Event transitions**: type changes (Threshold→FieldPulse) as categorical pairs.
- **Emoji/symbol density**: proxy for intensity (normalized by text length).
- **Your physiology** (if logged): sleep, workout, caffeine—often correlates with outreach quality.
- **Seasonality**: month, day-of-week, holidays you two share.

# Interpretability kit (offline)
- **Permutation importance** (simple, works for any model).
- **SHAP (tree explainer)** with TF‑DF baseline to learn high‑value features, then port lessons to the NN.
- **Calibration**: reliability plot to ensure probabilities mean what they say.

# Deployment pattern (fully offline)
- Store `SavedModel` + `TextVectorization` layer inside the model (so no external tokenizers).
- Export a single `predict.py` that:
  1) loads JSON of last N entries,
  2) builds features,
  3) prints calibrated probability + top contributing features.

# Practical limits & expectations
- **Data volume** is small → risk of overfitting. Use early stopping, dropout, strong baselines, and **temporal validation**.
- Don’t over‑interpret fine‑grained “predictions about her.” Treat outputs as **mirrors for your timing and care**—not as truth about Amanda.

If you want, I can spin up:
- a CSV/JSON schema for your extractor,
- a TF‑DF baseline notebook,
- and a ready-to-train TF2 script with CLI args (train/eval/predict) you can run 100% offline.