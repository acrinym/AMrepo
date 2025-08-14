# Consolidated Ritual 14

**Date**: 2025-08-10
**Conversation ID**: 17
**Parts Consolidated**: 1
**Content Hash**: 79d8d868b28af8a71f0336eea0ba67e4

---

## COMPLETE CONSOLIDATED RITUAL INSTRUCTIONS

**NO SUMMARIZATION - ALL PARTS COMBINED BELOW**

Got you, Justin. The one you want is **Organic Art** (the morphing 3D screensaver bundled with **Microsoft Plus! 98**, made by Computer Artworks). Here’s a clean, step-by-step path to **download, extract, and decompile** it.

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