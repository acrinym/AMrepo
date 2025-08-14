# Consolidated Ritual 199

**Date**: 2025-06-08
**Conversation ID**: 287
**Parts Consolidated**: 1
**Content Hash**: c86c99636d8b82ba2edfb928ea4d11f3

---

## COMPLETE CONSOLIDATED RITUAL INSTRUCTIONS

**NO SUMMARIZATION - ALL PARTS COMBINED BELOW**

YES, Justin—this is **exactly** the kind of tech ritual I live for. 😎🔥

You’re right: **modding Epic Games versions is a pain**, and **DecimaWorkshop** isn’t a full tool—just a loose collection of files for unpacking assets, not a mod manager. So let’s go deeper.

---

## 🔧 GOAL: **Cross-Launcher Save Game Switcher**  
Let’s outline a custom tool that can *backup*, *convert (if possible)*, and *sync* saves between the Steam and Epic versions of **Death Stranding: Director’s Cut**.

### ⚠️ Problem:
- Steam and Epic save files are stored in **different directories**, and possibly use **different encryption/formatting**.
- The game does **not natively support cross-launcher saves.**
- But… with the right tools and rituals, we *can* build a translator/wrapper.

---

## ⚙️ Tool Plan: `DSSaveSwitch`

### 🔥 Phase 1: Setup & Detection

1. **Auto-detect install paths:**
   - Steam: `C:\Program Files (x86)\Steam\steamapps\common\Death Stranding Director's Cut`
   - Epic: `C:\Program Files\Epic Games\DeathStrandingDC`
   - Custom paths allowed via config or GUI.

2. **Detect save folders:**
   - Steam: `%USERPROFILE%\Documents\KojimaProductions\DeathStranding`
   - Epic: Likely `%LOCALAPPDATA%` or `%USERPROFILE%\Saved Games\Epic\DeathStrandingDC`
   - We'll scan for `.sav` or similar.

---

### 🧠 Phase 2: Save Game Handling

1. **Backup manager**
   - Timestamped copies of both Steam and Epic saves before any overwrite.
   - GUI toggle to switch between "active" platform.

2. **Conversion attempt (Optional Advanced)**
   - Try analyzing format differences (we’ll hex the files side-by-side).
   - Might require decompressing / de-obfuscating saves (unknown if keys are used).
   - If successful, re-encode and copy to other platform’s save dir.
   - If not possible: log warning + allow one-way mirroring (for testing).

---

### 🖥️ GUI Features (Qt or Tkinter):

- Launcher path setup (manual or auto-detect)
- Save file viewer (timestamps, file size, current level or status)
- “Switch Save to [Epic|Steam]” button
- “Backup All Saves” button
- Mod-safe toggle (prevent overwriting modded files)

---

## 🔒 Risks

- If saves are **platform-encrypted**, this won’t work without decryption keys.
- If saves are **bound to user IDs**, we’d need a patch or workaround.
- But if they’re just **JSON or binary blobs**, we can parse and translate.

---

## 🛠️ Let's Begin

Would you like this as:
- 💻 **Python script** (easier to edit, GUI w/ Tkinter)
- 🖥️ **Qt GUI app** (more polished, maybe for broader use)
- 🧪 **Command-line CLI** (power user, minimal interface)

Also: do you want this to *auto-detect mods* (like DXVK, reshade, etc) and alert if present?

---

We can call this tool:

> 🔄 `StrandLink` – Because it bridges the strands between platforms. 💀👶🌈  
Or just `DSSaveSwitch`, if you want something low-key.

Ready to build? I’ll write the skeleton in the format you want.