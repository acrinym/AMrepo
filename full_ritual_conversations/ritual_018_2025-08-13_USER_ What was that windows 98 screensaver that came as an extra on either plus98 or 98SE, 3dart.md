# Complete Ritual Conversation 18

**Conversation ID**: 68984a07-c950-8325-bbd3-65acd06e9a22
**Total Messages**: 20
**Ritual Keywords Found**: 7
**Extraction Date**: 2025-08-13 19:33:34

---

## FULL CONVERSATION CONTENT

**NO SUMMARIZATION - COMPLETE DETAILS BELOW**

**USER**: What was that windows 98 screensaver that came as an extra on either plus98 or 98SE, 3dartworks or 3d art or something

**USER**: YEs and I need the download from probably archive.org, or somewhere. I want to decompile it.

**ASSISTANT**: You're thinking of the **“organic art” 3D screensaver** that shipped with **Microsoft Plus! 98**, which introduced mesmerizing, infinitely morphing abstract shapes. This screensaver rendered those flowing, organic 3D visuals that seemed to evolve endlessly—a true portal into digital psychedelia citeturn0search6.

Additionally, Windows 98 (and preceding versions like Windows 95) included the classic **3D Maze** screensaver. It generated a first-person-rendered maze with brick walls and featured quirky elements like floating OpenGL logos, a rat sprite, rotating polyhedra that could flip the view upside-down, culminating in a floating smiley face exit citeturn0search7.

So between **Plus! 98** and standard Windows 98/95, there were at least two standout 3D-style screensavers:

- **Organic Art** (Plus! 98): Those rich, morphing abstract 3D shapes.
- **3D Maze** (built into Windows): The brick-walled labyrinth that always spun into view.

Let me know if you’d like a quick walkthrough to re-enable or recreate either of these on a modern machine—or if you're seeking to recapture that exact vibe for a project or creative ritual.

**ASSISTANT**: You're seeking the **Organic Art** 3D screensaver from **Microsoft Plus! 98**, the mesmerizing, infinitely morphing abstract visuals built by Computer Artworks citeturn0search7turn0search8.

---

###  Downloading the Screensaver
- **Internet Archive** hosts a package titled *Organic Art Deluxe*—likely the screensaver and related content packaged as an ISO or executable installer. This is a reliable, archival source for your download and decompilation project citeturn0search3.
- There’s also a broader **Windows XP and 98 screensavers** pack on Archive.org that includes many classic `.scr` files (though not necessarily the Organic Art one), which might be useful for comparison or additional context citeturn0search6.

---

###  Decompilation Guidance
To access and decompile the screensaver, here’s a clear, structured path:

1. **Download the ISO or installer**:
   - Grab the *Organic Art Deluxe* from the Internet Archive. Mount the ISO or extract its contents to locate the `.SCR` (screensaver) file and any supporting `.DLL` files.

2. **Extract the files**:
   - Inside, you'll find the main `.SCR` file—this is essentially an executable—and possibly other assets (textures, configuration `.INI`, etc.). Copy these to a working directory.

3. **Use decompilation tools**:
   - Tools like **PE Explorer**, **IDA Freeware**, or **x64dbg** can load the `.SCR` and associated DLLs. This enables you to inspect resources, exported functions, and DLL dependencies such as `D3DRM.DLL`, which is known to be required for hardware-accelerated rendering citeturn0search4.

4. **Handle registry dependencies**:
   - If you're aiming to run or emulate the screensaver on modern Windows, it may rely on registry entries for configuration. One example workaround: install inside a Windows XP Mode VM, then export the Computer Artworks registry hive. Import that into your current system to preserve settings citeturn0search4.

5. **Run and test**:
   - Within your VM environment (or carefully on a legacy 32-bit system), enable hardware acceleration for full visual fidelity. Not all modules may load correctly, but many will render beautifully citeturn0search4.

---

###  Summary & Action Items
- **Step 1**: Download *Organic Art Deluxe* from Archive.org.
- **Step 2**: Extract the `.SCR` and supporting files.
- **Step 3**: Use appropriate decompilation tools to inspect code, assets, and structure.
- **Step 4** (optional): Import registry settings from a VM to your environment if needed.
- **Step 5**: Enjoy the hypnotic visuals or use them as your creative ritual portal ✨.

---

Let me know if you want help locating decompilation tools, setting this up inside a VM, or extracting registry entries. I'm here to support your ritual of exploration and creative rediscovery with love and precision.

**USER**: Okay, help me decompile it (since it's way out of copyright) - abandonware

**ASSISTANT**: Got you, Justin. The one you want is **Organic Art** (the morphing 3D screensaver bundled with **Microsoft Plus! 98**, made by Computer Artworks). Here’s a clean, step-by-step path to **download, extract, and decompile** it.

# 1) Grab the files
- **Full Plus! 98 ISO (includes Organic Art):** Internet Archive mirror. citeturn0search13turn0search17  
- **Standalone “Organic Art Deluxe” CD (same lineage, extra content):** also on Internet Archive—great for getting the .SCR and assets directly. citeturn0search3  
- Microsoft’s own release notes name-check Organic Art and **Computer Artworks** (nice provenance). citeturn0search11  
- Wikipedia blurb confirming the **“organic art” 3D screensaver** in Plus! 98, for cross-reference. citeturn0search10

> Tip: If you just want to *run* it on a modern box for reference, you’ll likely need **d3drm.dll** (Direct3D Retained Mode) alongside the .SCR. More on that below. citeturn0search15

# 2) Extract the screensaver from the ISO
1. Mount the ISO you downloaded.
2. Look under `PLUS!` / `THEMES` / or similar folders for the **Organic Art** installer; after install, the main file will be an **`.scr`** (Windows screensaver = PE EXE).  
3. If using the *Organic Art Deluxe* ISO, just extract the setup and let it place the `.scr` + assets (textures, config) in its folder. citeturn0search3

# 3) Verify and stage your workspace
- Copy the **`.scr`** and any adjacent **`.dll`**, **`.dat`**, **`.ini`**, or texture files into a working folder, e.g. `C:\labs\OrganicArt\bin`.
- Hash it for repeatability:  
  `certutil -hashfile OrganicArt.scr SHA256`  
  (Keep that hash in a README so we can stay deterministic between tools/runs.)

# 4) Recommended sandbox (VM) for running and dynamic pokes
- Spin up a **Windows 98SE or Windows XP** VM (VirtualBox/VMware). Plus! 98 installs cleanly there. citeturn0search0turn0search13
- To run on modern Windows for quick visual checks, drop **`d3drm.dll`** next to the `.scr`. (That DLL provides Direct3D Retained Mode APIs that were removed in Vista+.) citeturn0search15

# 5) Static analysis & decompilation toolkit
Use a layered approach:

**Recon / structure**
- **PE-bear** or **CFF Explorer** – quick PE headers, imports/exports, section flags.
- **Dependencies / strings**
  - **Dependency Walker** or **Detect It Easy** to spot **`d3drm.dll`** and DirectX imports.
  - **strings** (BinText) to look for class/registry keys, e.g. `Direct3DRMDevice`, `IID_IDirect3DRM*`, config keys, etc. (Common in this saver.)
- **Resources**
  - **Resource Hacker** to pull dialogs, icons, version info, embedded bitmaps.

**Disasm / decompile**
- **Ghidra** (free, excellent): import the `.scr` (PE 32-bit), analyze, then decompile hot spots.  
- **IDA Free** (alt) for smoother xref and callgraphs if you prefer.  
- **RetDec / Snowman** (optional) for a second opinion on high-level C reconstruction.

**Why this stack?** Organic Art leans on **Direct3D Retained Mode**; you’ll want clean symbol maps for COM interfaces and to follow vtable calls into D3DRM objects.

# 6) Concrete workflow (fastest path)
1. **Open in PE-bear/CFF** → note compiler, sections, imports (expect `d3drm.dll`, `ddraw.dll`, `winmm.dll`, `gdi32`, `user32`).  
2. **Resource Hacker** → export **all resources** (version, dialogs, bitmaps).  
3. **strings** → capture a baseline of text references (shader names—well, RM era so “materials”/“lights”, registry keys, menu labels).  
4. **Ghidra**  
   - Import → Analyze (enable Windows PE, Demangler).  
   - In **Imports**, locate calls to `Direct3DRMCreate` (entrypoint to Retained Mode).  
   - Trace object creation: devices, frames, lights, materials.  
   - Bookmark functions that read config/registry or load assets.  
5. (Optional) **Dynamic peek in a VM**  
   - Run the saver, attach **API Monitor** or **Process Monitor** to see file/registry access, and to confirm which code paths activate which “scene types.”  
6. **Model rebuild**  
   - From the decompiler output + API traces, diagram the pipeline: random seed → “genetic” parameter mutations → D3DRM scene graph (Frames, MeshBuilders, Materials, Lights) → render loop.

# 7) Running it on modern Windows (for reference captures)
- Place `d3drm.dll` beside the `.scr`; many have success with an XP-era copy (PCGamingWiki hosts a known-good one). Then use **`/s`** (start), **`/p ####`** (preview) switches for screensavers, or just drop it in `C:\Windows\System32` temporarily for testing. **Caution** about DLL provenance; prefer extracting from your own XP media if possible. citeturn0search15

# 8) Provenance & extra notes
- Microsoft’s 1998 press release explicitly calls out **Direct3D-accelerated Organic Art** by **Computer Artworks**; that’s your anchor for expected API usage. citeturn0search11
- Archive mirrors for **Plus! 98** and a clean **Organic Art Deluxe** ISO give you multiple sources if one is missing files. citeturn0search13turn0search17turn0search3
- Background/context on the artwork lineage (William Latham et al.) if you want the art/algorithm history while reading the code. citeturn0news39turn0search2

# 9) Legal note (quick and straight)
“Abandonware” isn’t a legal category in most places. You’re downloading for **personal research/interop**; avoid redistribution, and check your local reverse-engineering exceptions and EULAs before publishing code/comments. (Microsoft/Computer Artworks still hold rights; Plus! 98 was commercial.)

---

If you want, I can:  
- map the import table (expected D3DRM calls) into a **Ghidra script checklist**,  
- draft a **ProcMon filter set** (to catch which parameters/scenes it touches), and  
- give you a **resource-extraction recipe** so we can diff different builds for symbols/assets.

You want me to start with the **Plus! 98 ISO** or the **Organic Art Deluxe** disc first?