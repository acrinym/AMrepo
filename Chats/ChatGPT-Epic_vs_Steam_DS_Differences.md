# Epic vs Steam DS Differences

#### You:
Hey Onyx, what's the difference between DeathStranding Director's cut Epic version and Steam? I have it on both platforms now. 

#### ChatGPT:
Hey Justin. 🖤 Let’s break down the **differences between the Epic Games and Steam versions of *Death Stranding: Director’s Cut***—and why it might actually matter (or not) depending on your setup and goals.

---

## 🧩 Core Game Content: **Identical**

- Both the **Epic** and **Steam** versions of *Death Stranding: Director’s Cut* include the **same**:
  - Visual upgrades
  - New missions and gear
  - Racing track & delivery supports
  - Intel about Half-Life and Cyberpunk crossovers (if installed correctly)

✅ No content disparity. Hideo Kojima’s vision is fully intact across both.

---

## 🚀 Platform-Level Differences

### 🔷 **Steam Version**

- **Steam Cloud**: Sync saves across PCs (if enabled).
- **Steam Achievements**: Fully integrated.
- **Steam Workshop**: Not used here—but mods are sometimes easier to apply via Steam’s ecosystem.
- **Community**: Access to the large Steam forums, guides, and overlay.
- **Modding**: Slightly more accessible via Steam (modders often test there first).

> ⚠️ Save games **cannot be transferred** between Steam and Epic. They use separate directory structures and encryptions.

---

### 🟣 **Epic Games Version**

- **No Steam overlay** or workshop.
- Has its **own achievements** system (EGS Achievements), but it's less robust.
- **Lacks cloud save** unless the game implements it natively (uncertain for DS:DC).
- Might load slightly faster in some setups due to lighter launcher, but this is negligible.

---

## 🔄 Performance?

Both versions run on **Decima Engine** and are nearly identical in performance.

- *If you use ReShade or mods*, you might have a slightly smoother time on **Steam**.
- For raw gameplay, **Epic** might launch slightly faster due to fewer overlays, but the difference is small.

---

## 💾 Save Game Note

**You can’t use your Steam save with the Epic version** (or vice versa) unless you:

- Use third-party tools (risky)
- Or manually hex-edit / decrypt them (not recommended unless you know what you’re doing)

---

## 💡 Which Should You Use?

### Use **Steam** if:

- You care about achievements, cloud saves, modding, and community features.
- You’re running Steam Deck or planning to use Linux/Proton (Steam version has better compatibility).

### Use **Epic** if:

- You got it for free or cheap and just want a second install for backup or performance testing.
- You’re building a launcher-agnostic library and don’t mind standalone performance.

---

## 🎯 Recommendation for Justin

Since you already own both, use:

- **Steam** for your main playthrough (achievements, community, long-term modding),
- **Epic** if you want to test mods in a sandbox, or maintain a separate “clean” install for story replays without affecting your main.

Also: ✨ double flame bonus if you screenshot Amanda’s name written in chiral crystals. Just saying.

Let me know if you want help with modding DS:DC or optimizing visuals—it’s one of the best-engineered games on PC.Hey Justin. 🖤 Let’s break down the **differences between the Epic Games and Steam versions of *Death Stranding: Director’s Cut***—and why it might actually matter (or not) depending on your setup and goals.

---

## 🧩 Core Game Content: **Identical**

- Both the **Epic** and **Steam** versions of *Death Stranding: Director’s Cut* include the **same**:
  - Visual upgrades
  - New missions and gear
  - Racing track & delivery supports
  - Intel about Half-Life and Cyberpunk crossovers (if installed correctly)

✅ No content disparity. Hideo Kojima’s vision is fully intact across both.

---

## 🚀 Platform-Level Differences

### 🔷 **Steam Version**

- **Steam Cloud**: Sync saves across PCs (if enabled).
- **Steam Achievements**: Fully integrated.
- **Steam Workshop**: Not used here—but mods are sometimes easier to apply via Steam’s ecosystem.
- **Community**: Access to the large Steam forums, guides, and overlay.
- **Modding**: Slightly more accessible via Steam (modders often test there first).

> ⚠️ Save games **cannot be transferred** between Steam and Epic. They use separate directory structures and encryptions.

---

### 🟣 **Epic Games Version**

- **No Steam overlay** or workshop.
- Has its **own achievements** system (EGS Achievements), but it's less robust.
- **Lacks cloud save** unless the game implements it natively (uncertain for DS:DC).
- Might load slightly faster in some setups due to lighter launcher, but this is negligible.

---

## 🔄 Performance?

Both versions run on **Decima Engine** and are nearly identical in performance.

- *If you use ReShade or mods*, you might have a slightly smoother time on **Steam**.
- For raw gameplay, **Epic** might launch slightly faster due to fewer overlays, but the difference is small.

---

## 💾 Save Game Note

**You can’t use your Steam save with the Epic version** (or vice versa) unless you:

- Use third-party tools (risky)
- Or manually hex-edit / decrypt them (not recommended unless you know what you’re doing)

---

## 💡 Which Should You Use?

### Use **Steam** if:

- You care about achievements, cloud saves, modding, and community features.
- You’re running Steam Deck or planning to use Linux/Proton (Steam version has better compatibility).

### Use **Epic** if:

- You got it for free or cheap and just want a second install for backup or performance testing.
- You’re building a launcher-agnostic library and don’t mind standalone performance.

---

## 🎯 Recommendation for Justin

Since you already own both, use:

- **Steam** for your main playthrough (achievements, community, long-term modding),
- **Epic** if you want to test mods in a sandbox, or maintain a separate “clean” install for story replays without affecting your main.

Also: ✨ double flame bonus if you screenshot Amanda’s name written in chiral crystals. Just saying.

Let me know if you want help with modding DS:DC or optimizing visuals—it’s one of the best-engineered games on PC.


#### You:
LOL I can mod it now. Epic is tough to mod anything. 
Decimaworkshop never seems to have an actual exe anyway. 

Can we build a tool to switch between launchers (savegames?)

#### ChatGPT:
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
- “Switch Save to \[Epic|Steam]” button
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

> 🔄 `StrandLink` – Because it bridges the strands between platforms. 💀👶🌈\
> Or just `DSSaveSwitch`, if you want something low-key.

Ready to build? I’ll write the skeleton in the format you want.


#### You:
Strandlink. 

#### ChatGPT:
💾 Got it — you've uploaded two files named `checkpoint.dat`, which are likely from your **Death Stranding save directories** (probably one Steam, one Epic). That’s perfect for reverse engineering.

Let’s get to work on **StrandLink**, your custom launcher-switch save tool. First, I’ll do a **binary diff and structure scan** of the two `checkpoint.dat` files to:

- Check for any platform-specific metadata or encryption
- Detect format similarity (are they just binary blobs or structured JSON-like saves?)
- Determine if safe copy/sync is feasible or if translation is needed

🧪 **Let me analyze the files now.**


#### ChatGPT:
Looks like I only have access to **one file** right now: `checkpoint.dat`.

The second version (likely the one from the other launcher) wasn’t renamed during upload, so both files had the same name and **only one got saved**.

### What I need from you:

📌 Please re-upload the second file and **rename it before uploading** — for example:

- `checkpoint_epic.dat`
- `checkpoint_steam.dat`

Once both are in place, I’ll compare them byte-for-byte and check if StrandLink can safely switch them or if we need a converter.

Ready when you are. 🔄


#### You:
Both are epic. I have npone on steam yet

#### ChatGPT:
🔥 Perfect clarity, Justin. If both `checkpoint.dat` files are from **Epic**, then we now have:

- ✅ A **reference format** (Epic’s save structure)
- 🚫 No Steam save yet — so no cross-compat check yet possible

That’s actually a great starting point. Let’s reverse-engineer **Epic's `checkpoint.dat`** and prepare StrandLink to:

1. **Extract internal structure**
2. **Look for user ID bindings or launcher-specific flags**
3. **Prepare a save manager system for backup, switching, and syncing later**

---

## 🔍 Next Step: Dissect the Epic Save Format

I’ll now:

- Scan the file for readable strings or patterns
- Identify any header/footer structures
- Estimate offsets for game state (binary blob vs structured save)

Let’s surgically dive into the uploaded Epic `checkpoint.dat`. 🧪


#### ChatGPT:
🧠 Nice—**Epic’s `checkpoint.dat` is partially human-readable** and includes embedded metadata. Here's what we learned from the first 20 ASCII strings:

---

## 🔎 Key Extracted Data from Epic Save

| 🔹 Field           | 🔍 Value                                                      |
| ------------------ | ------------------------------------------------------------- |
| `Title`            | **Order In Progress: No. 4 – Smart Drug Delivery**            |
| `SubTitle`         | **DEATH STRANDING DIRECTOR'S CUT - Manual Save**              |
| `Detail`           | **Head west! Capital Knot City**                              |
| `UserParam`        | `#004356D3` → Possible **user hash or slot ID**               |
| `ModificationTime` | `63883292448000000` → Likely a **Windows FILETIME** timestamp |

Also found:

- `[Slot]` header: Suggests save is part of a slot-based system
- PNG headers `IHDR` and `IDAT`: Game probably embeds **screenshot thumbnails** or icons inside the save file

---

## 🛠️ StrandLink Feature Planning – Phase 1 (Epic Ready)

Let’s define initial capabilities for **StrandLink v0.1**:

### ✅ What it will do now:

- Detect and parse Epic save structure
- Extract metadata: Title, mission, timestamp, location
- Backup saves with slot number and timestamp in filename
- Prep the GUI for Steam/Epic switching

### 🚧 What we’ll add once you have Steam saves:

- Identify any Steam-specific fields (e.g., SteamID, encryption)
- Attempt cross-launcher save translation
- Enable one-click switch with format compatibility

---

## 💡 Want to Build StrandLink Now?

You want this as a **Tkinter app** to run locally, right?

I can now:

- Build `StrandLink v0.1` GUI (Tkinter)
- Add the basic Epic save viewer + backup features
- Prep Steam compatibility logic as a placeholder

Let me know if you want:

- ✅ GUI version now
- 🖥 CLI prototype first
- 💾 Or raw code to run in your own environment

Let’s link these strands, brother. 🌈👶📦


#### You:
https://www.reddit.com/r/DeathStranding/comments/14uxzax/full_guide_to_transferring_save_data_between/

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
Here’s an in‑depth look at how the Death Stranding community handles cross‑platform save file transfers—especially between Epic and Steam—and how we can integrate that knowledge into **StrandLink**:

---

## 🔍 Key Findings from Reddit

A highly upvoted guide explains that:

> “The save data of Death Stranding is connected to the account that bought the game. Therefore, it is normally impossible to transfer save data between different platforms… In order to convert your saves, you have to manipulate the verification mechanism in Death Stranding DC.” citeturn0search1

They describe a **hex-edit maneuver**:

1. Locate the DC executable (Steam or Epic).
2. Search for bytes:
   ```
   75 05 41 C6 46 3A 11 48 8D 8D
   ```
3. Replace with:
   ```
   EB 05 41 C6 46 3A 11 48 8D 8D
   ```
4. This bypasses the platform-check, removes save file account binding, and allows DC to import saves from another platform. citeturn0search1

One user confirms it works by saying:

> “I bought the Director’s Cut on Steam, changed the hex code of Director’s Cut exe … and moved my save data from standard to DC. … Online works fine …” citeturn0search7

---

## 🛠️ How StrandLink Can Automate This Process

Here's how we can integrate this hex‑patch method into **StrandLink v0.2**:

### 1. **Auto‑Patch the DC EXE**

- Detect DC executable (Steam or Epic path).
- Verify presence of the hex‑sequence.
- Back up the original `.exe`.
- Apply the **save‑import bypass patch** automatically.
- Provide an unpatch/restore option.

### 2. **Safe Save Injection**

- After patching, **copy Epic save files** into the Steam DC save folder (or vice versa).
- Confirm correct folder structure:
  - Steam: `%LOCALAPPDATA%\KojimaProductions\DeathStranding\<steamID>\`
  - Epic: `%LocalAppData%\LocalLow\KojimaProductions\DeathStranding\<epicID>\`
- Use patching to bypass account mismatch checks, then launch Steam DC to trigger conversion.

### 3. **Verification UI**

- StrandLink GUI can display:
  - ✅ Status of patch (active/in-active)
  - 📂 Preview of detected save slots
  - 🔄 “Inject Saves → Launch DC” button

### 4. **Restore Flow**

- Guide the user to make a new DC save, then:
  - Press `Restore EXE` button to revert to official binary for Steam/EGS integrity.

---

## 🧭 Next Steps

Let’s integrate Step 1 and Step 2 into StrandLink v0.2:

- ✅ GUI button to “Patch DC EXE”
- 🔨 Auto-apply hex replace
- ✅ Also: ability to rollback easily
- ✅ Copy Epic saves to Steam DC
- ✅ Launch Steam DC silently (or prompt)
- ✅ Inform user to make a new save before restore

Would you like me to build this version as:

- **Tkinter GUI** (quick and easy)
- **CLI tool** (power user only)
- Or both?

Once you give the go‑ahead, I’ll start building the patch + transfer core.
