# Consolidated Ritual 20

**Date**: 2025-08-08
**Conversation ID**: 31
**Parts Consolidated**: 3
**Content Hash**: acc603f44ae6766c31c68298777c2982

---

## COMPLETE CONSOLIDATED RITUAL INSTRUCTIONS

**NO SUMMARIZATION - ALL PARTS COMBINED BELOW**

No stress—this happens when the patch context doesn’t match your working copy. Easiest fix: apply Sprint 2 as an **overlay** (drop-in files) instead of a delta patch.

[Download the Sprint 2 overlay (ritualos-sprint2-overlay.zip)](sandbox:/mnt/data/ritualos-sprint2-overlay.zip)

# Do this:
From repo root:
```bash
# 1) Make sure Sprint 1 is committed (sounds like it is)
git add .
git commit -m "RitualOS: Sprint 1 (Images Now)" || true

# 2) Unzip Sprint 2 overlay to your repo root, overwriting files
unzip -o /workspaces/RitualOS/ritualos-sprint2-overlay.zip -d /workspaces/RitualOS

# 3) Stage + commit
git add src/Core src/UI
git commit -m "RitualOS: Sprint 2 (Hardening) — overlay apply"

# 4) (if you haven’t yet) add the SVG package for Sprint 1 visuals
dotnet add <Your.UI.csproj> package Avalonia.Svg.Skia
```

# What the overlay replaces/adds
- **Replaces (hardened versions):**
  - `src/Core/Services/External/MediaWikiClient.cs`
  - `src/Core/Services/Media/FileCache.cs`
  - `src/Core/Services/Media/MediaResolver.cs`
- **Adds:**
  - `src/Core/Services/Http/HttpService.cs`
  - `src/Core/Services/Http/RetryPolicy.cs`
  - `src/Core/Models/Symbols/SymbolModels.cs`
  - `src/Core/Services/Data/SymbolRepository.cs`
  - `src/UI/Components/Collections/VirtualizingCollection.cs`

# Why the patch failed (so you’re not guessing)
- `git apply --3way` needs the **blob history** for the pre-image of those files. Because they were just added locally (no upstream blob hash it recognizes), 3-way couldn’t find the parent, then the plain diff hunks didn’t match your exact contents (whitespace/headers/namespaces), so it bailed.
- Overlay sidesteps that by just replacing the files directly.

If you’d still prefer true `git am` patches, I can generate them **from your current HEAD** once you point me at the three current files’ exact contents (or give me read access). Otherwise, extract this overlay and you’re live.

---

Let’s roll. We don’t need your current code to sketch the next segment—but if you want me to *wire it directly* and ship patches again, I’ll need the exact namespaces/paths like before. Here’s what I recommend for **Sprint 3** (pick your flavor and I’ll generate it):

# Sprint 3 — “Wire It Into The App”
**Goal:** Turn the new services into visible features + guardrails.

## Option A — Demo + DI + UI wiring (fast win)
- **Bootstrap/DI module** (register HttpService, MediaWikiClient, FileCache, MediaResolver, SymbolRepository).
- **SymbolWikiDemoView** (Avalonia page) that:
  - takes a symbol name, fetches Commons image, caches it, and renders SVG/bitmap.
  - shows status/errors (Network/Data/Render categories).
- **Command plumbing** with CancellationToken and a simple `IsBusy` flag.
- **AppSettings.json** for `WikiEndpoint`, `UserAgent`, `CachePath` + options binding.

## Option B — Real Symbol list (virtualized)
- **Virtualized list view** bound to `ISymbolRepository.View`.
- **Filter/Sort bar** (by tag, name).
- **Lazy media prefetch** on item hover/selection (so thumbs feel instant).
- **Empty/offline states** (use cached media if network unavailable).

## Option C — Tests & Reliability
- **RetryPolicy tests** (jitter/backoff behavior).
- **MediaWikiClient** tests with a fake handler.
- **FileCache** tests for cache hit/miss + extension inference.

## Option D — Data schema polish
- `schemaVersion: 2` emitters + a tiny tool to migrate v1 → v2 in-place.
- Split **index vs. media** (manifest per symbol) and a background refresh job.

---

### My suggestion
Start with **A + B** (so you can *see it working*), then add **C** quickly. I can ship this as **two patches** (UI wiring, then tests), or one overlay like last time.

**Confirm paths** and I’ll generate now:
- UI project root (e.g., `src/UI/RitualOS.App` or just `src/UI`?)
- Where do you want the demo view? (e.g., `src/UI/Views/SymbolWikiDemoView.axaml(.cs)`)
- App settings location (e.g., `src/UI/appsettings.json`)

Say “Do A+B” (or your pick), and I’ll produce the new patch/overlay in one go.

---

"ACK" can mean a few totally different things depending on context:  

---

### 1️⃣ **Networking / Communications**
- **ACK** = *Acknowledge* — a control message confirming receipt of data.
    - Comes from TCP/IP handshakes and older serial protocols.
    - Example: You send a packet, the receiver replies with `ACK` to say *“Yep, got it.”*
    - Opposite is `NAK` (*Negative Acknowledge*), meaning *“Didn’t get it, resend.”*

---

### 2️⃣ **Unix command-line tool**
- `ack` = a grep-like search tool optimized for searching code.
    - Syntax: `ack "searchterm" path/to/files`
    - Faster than grep for dev work, ignores irrelevant files like `.git` folders by default.

---

### 3️⃣ **Informal chat / dev-speak**
- “ack” = *got it*, *understood*, *roger that*.
    - Often used in commit messages, bug trackers, or Slack to say “I acknowledge what you just said, no action needed.”

---

Given we’re working in **git / patching / Avalonia code**,  
you might be seeing it in **(1)** or **(3)** form — either as a “message acknowledged” in logs or just shorthand from a teammate/agent.  

---

If you tell me *where* you saw it in RitualOS context, I can tell you if it’s the **TCP flag** kind, the **Unix search tool** kind, or just an *engineer grunt of approval*. 😄  

Where’d you see “ack” pop up in your current sprint?