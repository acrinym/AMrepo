# Consolidated Ritual 152

**Date**: 2025-06-21
**Conversation ID**: 222
**Parts Consolidated**: 1
**Content Hash**: 4f42176d1134a0b0f7818770846fad24

---

## COMPLETE CONSOLIDATED RITUAL INSTRUCTIONS

**NO SUMMARIZATION - ALL PARTS COMBINED BELOW**

Absolutely, Justin. Let’s take it up several notches—**deep, explicit detail for every major component** so Codex (or any agent) can scaffold with maximum precision and minimal ambiguity.

I’ll break each section into technical and functional requirements, UI details, and any interactions—leaving no gaps. Here’s a much more granular spec:

---

**Phoenix Visualizer: Detailed Technical & Functional Specification**

---

**1. Application Overview**

- Desktop application using Avalonia UI (.NET/C#) for cross-platform support (Windows, Mac, Linux).
- Standalone—no dependencies on other music players.
- Core: Animated phoenix visualizer, real-time audio analysis, simple built-in music player, screensaver/idle mode.

---

**2. User Interface (UI)**

**2.1 Main Window**
- Title bar: “Phoenix Visualizer”
- Central canvas: Phoenix visualization area (resizable, auto-fullscreen toggle button).
- Bottom/side panel:  
  - Play/Pause button  
  - Stop button  
  - Track progress slider  
  - Track title, artist, album fields (read from metadata)  
  - “Open File” button (opens file picker for local tracks; initial support for MP3, later FLAC, WAV, OGG)
  - Current BPM, detected genre, and phoenix “vibe” display (for debugging/interest)
  - Volume control slider

**2.2 Screensaver/Idle Mode**
- Auto-activates after X minutes idle (configurable, default 3 min).
- Phoenix canvas goes fullscreen, UI controls fade away.
- Any mouse or keyboard activity brings back UI and exits screensaver.

---

**3. Audio Engine**

**3.1 Playback**
- Use BASS.NET (preferred) or NAudio for reliable cross-platform playback.
- Support for MP3 at minimum; stretch goal: FLAC, OGG, WAV.
- Must expose: play, pause, stop, seek, volume adjust.

**3.2 Real-Time Audio Analysis**
- FFT: 1024 or 2048 band for frequency spectrum (bass, mid, treble extraction).
- BPM Detection: Real-time BPM analysis (auto-detect on track load, then ongoing update as needed).
- Peak/Energy Analysis: Compute track “energy” for visual intensity mapping.
- Audio event hooks: Beat, drop, quiet, and chorus detection for animation triggers.

**3.3 Genre Detection**
- Primary: Read from ID3 tags/metadata (Genre field).
- Fallback: Simple algorithmic guess based on spectrum (optional, for unlabeled tracks).
- Expose genre, BPM, and “intensity” as variables for the phoenix engine.

---

**4. Phoenix Visualizer Engine**

**4.1 Core Visual Logic**
- Render a stylized phoenix bird (body, wings, tail, eyes/flames). Vector preferred for smooth scaling.
- Animation states:  
  - Idle/calm (wings gently flapping, soft glow)
  - Active/beat (wings flare, fire bursts, color surges)
  - Cocoon (quiet music: wings wrap, glow dims)
  - Burst/rebirth (chorus/drop: phoenix erupts in flame, wings spread)
- All motion, glow, and particle effects tied to audio input.

**4.2 Color/Vibe Mapping**
- Genre sets base color and mood (one primary color per track; see mapping table below).
- BPM modulates animation speed (higher = faster wingbeat, energetic movements).
- Frequency bands:  
  - Bass → body/wing flame intensity  
  - Mids → eye glow, aura pulse  
  - Treble → feather tips, tail sparkles
- Color palette can subtly shift shade with energy, but does not blend genres within a single track.

**4.3 Vibe Mapping Table**  
| Genre        | Base Color     | Animation Style                  |
|--------------|---------------|----------------------------------|
| Blues/Jazz   | Deep Blue     | Smooth, flowing, gentle waves    |
| Bluegrass    | Sky Blue      | Lively, bouncy wing movement     |
| Classical    | Gold/Yellow   | Elegant, graceful, slow arcs     |
| Metal        | Purple/Red    | Sharp, wild, aggressive motion   |
| Love/Trance  | Pink/Gold     | Spirals, gentle bursts, uplifting|
| Hip hop/Rap  | Silver/Green  | Rippling, rhythmic, street vibe  |
| Pop          | Orange/Yellow | Bright, peppy, energetic flaps   |
| Electronic   | Neon tones    | Strobing, fast, particle-heavy   |

**4.4 Configurability (Phase 2)**
- Genre-color mapping editable via settings (JSON or simple UI).
- “Field” mode toggle: overlays subtle energy auras or ritual symbols.
- Optional: user-defined phoenix skins or backgrounds.

---

**5. Application Flow**

1. User launches app, sees main window.
2. User clicks “Open File” and loads a track.
3. App starts playback; displays track info, visualizer activates.
4. Audio engine runs real-time analysis:  
   - Detects genre, BPM, frequency spectrum.  
   - Passes data to phoenix engine.
5. Phoenix appears with genre-mapped color and animation style.
6. As music plays:  
   - Beat triggers wing flaps, flame bursts.  
   - Energy/loudness increases brightness or fire trails.  
   - Quiet/lulls cocoon the phoenix.
7. Screensaver mode triggers after idle; phoenix remains active.
8. User interacts; screensaver exits; UI reappears.
9. On track end, phoenix enters rest/idle animation.

---

**6. Stretch Goals (Phase 2+)**

- Playlist and folder support.
- Visualization presets and user scripts (Lua or JSON).
- Export/share phoenix “moments” as GIF/video.
- Microphone/line-in visualizer mode.

---

**7. Libraries & Dependencies**

- Avalonia UI (main framework)
- SkiaSharp (drawing/animation)
- BASS.NET or NAudio (audio playback/analysis)
- TagLib# (metadata parsing)
- Newtonsoft.Json (settings/config)

---

**8. Dev/Testing Notes**

- All drawing and animation logic should be separated from playback engine for easy refactoring.
- Core animation and genre-mapping tables exposed for rapid prototyping.
- App should handle errors gracefully (e.g., unsupported file types, missing metadata).
- Visualizer performance target: 60 FPS on mid-tier hardware.

---

This spec gives Codecs or any agent the granular detail they need to scaffold the project, leaving minimal guesswork and room for later expansion.  
Want to lock this in, or tweak any section? If you have additions—like ritual field overlays, extra UI features, or custom phoenix actions—let’s add those now so your first build is as close to your vision as possible.