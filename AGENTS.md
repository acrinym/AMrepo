# 🤖 Code Agent Guidelines for Pull Requests

## Project Status: UNIFIED AVS SYSTEM IMPLEMENTED ✅

**Current Milestone:** Regex-Free AVS Import Pipeline Complete - Zero Regex Architecture
**Date:** January 2025
**Impact:** Complete elimination of regex-based parsing nightmares

### **🎯 MAJOR NEW MILESTONE ACHIEVED**
- ✅ **Unified AVS Architecture:** Complete regex elimination and type-based parsing
- ✅ **AvsFileDetector.cs:** Structured file type detection with confidence scoring
- ✅ **PhoenixAvsParser.cs:** Multi-superscope text parsing with state machine logic
- ✅ **WinampAvsParser.cs:** Safe binary framing with ASCII extraction from config blobs
- ✅ **UnifiedAvsService.cs:** Single orchestration point for all AVS file types
- ✅ **UnifiedAvsVisualizer.cs:** Clean visualization ready for PEL integration
- ✅ **Entry Point Updates:** MainWindow, PresetManager updated to use new system
- ✅ **Debug Logging:** Extensive `### JUSTIN DEBUG:` logging throughout pipeline
- ✅ **Build Success:** Perfect compilation with new architecture

### **🚨 CRITICAL ISSUES IDENTIFIED**
- **Phoenix AVS Files:** Show NO debug logs when loading (generic pattern displayed)
- **Preset Switching:** Memory leaks - cannot cleanly switch between presets
- **Debug Pipeline:** Need to trace why Phoenix files fall back to generic rendering

---

## Overview
This document provides mandatory guidelines for all code agents creating pull requests. These guidelines ensure consistent, informative, and actionable PR descriptions that enable effective code review and project management.

## Mandatory PR Description Format

Every pull request MUST include the following sections in this exact order:

### 1. Summary
```markdown
## Summary
Brief 1-2 sentence description of the primary change/feature/fix.
```

### 2. What Was Done
```markdown
## What Was Done
✅ **Completed:**
- [x] Specific task 1 with details
- [x] Specific task 2 with details
- [x] Specific task 3 with details

📝 **Changes Made:**
- File/component changes with reasoning
- New features implemented
- Bug fixes applied
- Refactoring performed
```

### 3. What Needs To Be Done Next
```markdown
## What Needs To Be Done Next
🔄 **Immediate Next Steps:**
- [ ] Task 1 (priority: high/medium/low)
- [ ] Task 2 (priority: high/medium/low)
- [ ] Task 3 (priority: high/medium/low)

🎯 **Future Considerations:**
- [ ] Enhancement 1
- [ ] Feature 2
- [ ] Technical debt item 3
```

### 4. Build Status
```markdown
## Build Status
🏗️ **Build Result:** ✅ SUCCESS / ❌ FAILED / ⚠️ WARNINGS

**Build Command Used:**
```bash
dotnet build Solution.sln -c Release --verbosity minimal
```

**Exit Code:** [0 for success, non-zero for failure]
```

### 5. Issues & Warnings
```markdown
## Issues & Warnings

### ❌ Build Errors (if any)
```
[Copy exact error messages here with file paths and line numbers]
```

### ⚠️ Build Warnings
```
[Copy exact warning messages here - even if build succeeds]
```

### 🐛 Runtime Issues (if known)
- Issue 1: Description and impact
- Issue 2: Description and impact
```

### 6. How To Fix Build Failures
```markdown
## How To Fix Build Failures

### If Build Fails:
1. **Error Analysis:**
   - Primary error: [Main blocking issue]
   - Secondary errors: [Dependency issues]

2. **Recommended Fixes:**
   ```bash
   # Step 1: Command to run
   # Step 2: Another command
   ```

3. **Root Cause:**
   - [Explanation of why it failed]

### If Warnings Exist:
1. **Warning Categories:**
   - Nullable reference warnings: [Count and significance]
   - Obsolete API warnings: [Count and upgrade path]
   - XAML binding warnings: [Count and UI impact]

2. **Fixing Priority:**
   - 🔥 Critical: [Warnings that will become errors]
   - ⚡ Important: [Warnings affecting functionality]
   - 📝 Optional: [Style/best practice warnings]
```

### 7. Testing Status
```markdown
## Testing Status
🧪 **Testing Performed:**
- [ ] Build verification
- [ ] Basic functionality test
- [ ] Unit tests (if applicable)
- [ ] Integration tests (if applicable)
- [ ] Manual UI testing (if applicable)

**Test Results:**
- [Description of what was tested and results]
```

### 8. Dependencies & Requirements
```markdown
## Dependencies & Requirements
📦 **New Dependencies Added:**
- Package 1: Version X.Y.Z (reason)
- Package 2: Version A.B.C (reason)

⚙️ **System Requirements:**
- .NET SDK version: [e.g., 8.0.413]
- Operating System: [if specific]
- External tools: [if any]

🔗 **Related Issues/PRs:**
- Closes #123
- Related to #456
- Depends on #789
```

---

## 🚨 **CRITICAL: Codebase Backup Requirements**

### **MANDATORY: Run Codebase Backup on Every Assistant Startup**

**EVERY TIME** an AI assistant starts working on this project, they **MUST** run the codebase backup script **IMMEDIATELY**:

```bash
# From the PhoenixVisualizer directory:
cd PhoenixVisualizer
./create_codebase_export.sh

# OR for PowerShell (Windows):
# .\export_with_build_status.ps1
```

**WHY THIS IS CRITICAL:**
- **Immediate Backup**: Captures current state before any changes
- **Build Status Tracking**: Records current compilation status and any issues
- **Complete Source Export**: Text export of ALL source files, documentation, and project structure
- **Error Tracking**: Captures any existing build errors or warnings for reference
- **Recovery Point**: Provides restore point if changes break the build

**BACKUP OUTPUT:**
- Creates: `phoenix_visualizer_source_export_YYYY-MM-DD.txt`
- Includes: All C# files, XAML files, documentation, build status
- Size: Typically 1-2MB of comprehensive project data
- Location: Project root directory

**FAILURE TO BACKUP = RISK OF DATA LOSS**

---

## 🧹 **Obsolete Files Review - Action Required**

### **IMMEDIATE CLEANUP RECOMMENDATIONS:**

#### **Safe to Remove Immediately:**
- ✅ `out.txt` - Build output log (~7.5KB)
- ✅ `phoenix_visualizer_source_export_2025-08-28.txt` - Outdated export (~45MB)
- ✅ `COMPLETE_CODEBASE_EXPORT.txt` - Redundant export (~9MB)

#### **Needs Review:**
- ❓ `VlcTest.cs` - Test file in root (move to `tests/` ?)
- ❓ `check_exports.cs` - DLL checker (move to `tools/` ?)
- ❓ `bass.dll` - Move from root to `libs/bass/`
- ❓ Export scripts consolidation into `tools/export/`

#### **Keep:**
- ✅ `add-debug-code.disabled` - Useful debug documentation

**ACTION**: Review and clean obsolete files before making changes.

---

## Agent-Specific Instructions

### For Code Agents:
1. **🚨 FIRST: Run `./create_codebase_export.sh` (MANDATORY)**
2. **ALWAYS** run a build before creating the PR
3. **CAPTURE** the complete build output (errors AND warnings)
4. **DOCUMENT** any workarounds or temporary fixes
5. **EXPLAIN** technical decisions made during implementation
6. **IDENTIFY** areas that need future attention

### For Build Status:
- ✅ **SUCCESS**: Exit code 0, no errors, warnings acceptable
- ⚠️ **WARNINGS**: Exit code 0, but warnings present that should be addressed
- ❌ **FAILED**: Non-zero exit code, compilation errors present

### Warning Categories:
- **Critical**: CS0xxx compilation errors
- **Important**: CS8xxx nullable reference warnings, AVLN3000 Avalonia errors
- **Style**: CS1xxx documentation warnings
- **Obsolete**: CS0618 obsolete API warnings

### Error Reporting Rules:
1. **Always include line numbers** and file paths
2. **Copy exact error text** - don't paraphrase
3. **Limit to first 10 errors** if there are many (mention total count)
4. **Group related errors** when they stem from the same root cause

---

## Example PR Description

```markdown
# Implement Dynamic Plugin Discovery for Phoenix Visualizer Editor

## Summary
Added dynamic plugin/effect discovery system to PluginEditorWindow with real-time updating, file system monitoring, and automatic refresh capabilities.

## What Was Done
✅ **Completed:**
- [x] Implemented ObservableCollection-based data binding for automatic UI updates
- [x] Added FileSystemWatcher for real-time plugin directory monitoring
- [x] Created periodic refresh timer (5-second intervals) for effect discovery
- [x] Enhanced Add Effect dialog with manual refresh button and live count display
- [x] Fixed XAML binding issues with proper DataType declarations
- [x] Added proper resource cleanup on window close

📝 **Changes Made:**
- `PluginEditorWindow.axaml.cs`: Complete rewrite to support INotifyPropertyChanged pattern
- `PluginEditorWindow.axaml`: Enhanced UI with binding, refresh controls, and real-time counts
- `EffectDescriptor.cs`: Added Name property to resolve binding errors

## What Needs To Be Done Next
🔄 **Immediate Next Steps:**
- [ ] Fix remaining XAML binding errors in AvsEffectsConfigWindow.axaml (priority: medium)
- [ ] Update file dialog usage to modern Avalonia StorageProvider API (priority: low)
- [ ] Add error handling for plugin loading failures (priority: medium)

🎯 **Future Considerations:**
- [ ] Implement plugin hot-reloading without restart
- [ ] Add plugin validation and digital signature checking
- [ ] Create plugin marketplace integration

## Build Status
🏗️ **Build Result:** ⚠️ WARNINGS

**Build Command Used:**
```bash
dotnet build PhoenixVisualizer.sln -c Release --verbosity minimal
```

**Exit Code:** 1 (due to XAML binding errors in unrelated file)

## Issues & Warnings

### ❌ Build Errors
```
/workspace/PhoenixVisualizer/PhoenixVisualizer.App/Views/AvsEffectsConfigWindow.axaml(95,131): 
Avalonia error AVLN3000: Unable to find suitable setter for property ValueChanged
```

### ⚠️ Build Warnings
```
PluginEditorWindow.axaml.cs(69,23): warning CS0618: 'OpenFileDialog' is obsolete: 
'Use Window.StorageProvider API or TopLevel.StorageProvider API'
PluginEditorWindow.axaml.cs(75,13): warning CS8602: Dereference of a possibly null reference
```

### 🐛 Runtime Issues
- None known - dynamic updating functionality works correctly

## How To Fix Build Failures

### If Build Fails:
1. **Error Analysis:**
   - Primary error: XAML binding issues in AvsEffectsConfigWindow (not related to this PR)
   - Secondary errors: None

2. **Recommended Fixes:**
   ```bash
   # The PluginEditorWindow changes in this PR are working correctly
   # The errors are in AvsEffectsConfigWindow.axaml which needs separate fixing
   ```

3. **Root Cause:**
   - XAML binding errors in separate file using obsolete Avalonia event signatures

### If Warnings Exist:
1. **Warning Categories:**
   - Obsolete API warnings: 6 (CS0618 - file dialogs)
   - Nullable reference warnings: 1 (CS8602 - null check needed)
   - XAML binding warnings: 0 (fixed in this PR)

2. **Fixing Priority:**
   - 📝 Optional: File dialog warnings (functionality works, just deprecated API)
   - ⚡ Important: Null reference warning (add null check)

## Testing Status
🧪 **Testing Performed:**
- [x] Build verification 
- [x] Basic functionality test (PluginEditorWindow opens and populates)
- [ ] Unit tests (none exist yet)
- [ ] Integration tests (none exist yet)
- [x] Manual UI testing (Add Effect dialog, refresh button, real-time updates)

**Test Results:**
- Dynamic updating works correctly - effects list populates on startup
- Manual refresh button updates effect count properly  
- Add Effect dialog shows all 42+ available effects
- File system monitoring is active (watching plugin directories)

## Dependencies & Requirements
📦 **New Dependencies Added:**
- None (used existing ObservableCollection and FileSystemWatcher from .NET)

⚙️ **System Requirements:**
- .NET SDK version: 8.0.413
- Operating System: Linux/Windows/macOS
- External tools: None

🔗 **Related Issues/PRs:**
- Addresses user requirement for dynamic plugin discovery
- Enhances core Phoenix Visualizer Editor functionality
```

---

## Compliance Checklist

Before submitting any PR, verify:

- [ ] All 8 mandatory sections are included
- [ ] Build command and exit code are documented
- [ ] Complete error/warning output is captured
- [ ] Next steps are clearly identified with priorities
- [ ] Fix instructions are actionable and specific
- [ ] Testing status is honestly reported
- [ ] Dependencies are properly documented

**Remember:** The goal is to provide reviewers and future developers with complete context to understand, review, and continue the work effectively.

🔗 Library Source & Documentation (Exact Links)

These entries reflect what’s actually referenced in the current .csproj files (versions included). If a package is removed or added, update this table in the PR. Versions verified in PhoenixVisualizer.App\PhoenixVisualizer.csproj and the LibVLC test projects. 
 

Avalonia (UI stack)

Avalonia 11.3.3 → Source: https://github.com/AvaloniaUI/Avalonia
 • Docs: https://docs.avaloniaui.net/
 
GitHub
Avalonia Docs

Avalonia.Desktop 11.3.3 → Source: https://github.com/AvaloniaUI/Avalonia
 • Docs: https://docs.avaloniaui.net/
 
GitHub
Avalonia Docs

Avalonia.Themes.Fluent 11.3.3 → Source: https://github.com/AvaloniaUI/Avalonia
 • Docs: https://docs.avaloniaui.net/
 
GitHub
Avalonia Docs

Avalonia.Fonts.Inter 11.3.3 → Source: https://github.com/AvaloniaUI/Avalonia
 • Docs: https://docs.avaloniaui.net/
 
GitHub
Avalonia Docs

Avalonia.Diagnostics 11.3.3 (Debug-only) → Source: https://github.com/AvaloniaUI/Avalonia
 • Docs: https://docs.avaloniaui.net/
 
GitHub
Avalonia Docs

Editor & MVVM

AvaloniaEdit 0.10.12 → Source: https://github.com/AvaloniaUI/AvaloniaEdit
 • Docs (NuGet page): https://www.nuget.org/packages/Avalonia.AvaloniaEdit
 
NuGet

CommunityToolkit.Mvvm 8.2.1 → Source: https://github.com/CommunityToolkit/dotnet
 • Docs: https://learn.microsoft.com/dotnet/communitytoolkit/mvvm/generators/overview
 
GitHub
Microsoft Learn

ReactiveUI 19.5.41 → Source: https://github.com/reactiveui/ReactiveUI
 • Docs: https://www.reactiveui.net/
 
ReactiveUI
+1

ReactiveUI.Fody 19.5.41 → Source: https://github.com/reactiveui/ReactiveUI
 (Fody package history/discussions) • Notes: Library has shifting support; prefer Toolkit source generators where practical. 
GitHub

Roslyn (runtime codegen / analyzers)

Microsoft.CodeAnalysis 4.8.0 (+ CSharp, CSharp.Workspaces)
Source: https://github.com/dotnet/roslyn
 • Docs: https://learn.microsoft.com/dotnet/csharp/roslyn-sdk/
 
GitHub
Microsoft Learn

Metrics / Diagnostics

System.Diagnostics.PerformanceCounter 8.0.1 (Windows-only API)
Docs: https://learn.microsoft.com/dotnet/api/system.diagnostics.performancecounter
 • Cross-platform alternative: EventCounters https://learn.microsoft.com/dotnet/core/diagnostics/event-counters
 
Microsoft Learn
+1

Media playback (✅ new stack)

LibVLCSharp 3.9.4 → Source: https://github.com/videolan/libvlcsharp
 • Docs: https://code.videolan.org/videolan/LibVLCSharp/-/tree/master/docs
 
GitHub
GitLab

VideoLAN.LibVLC.Windows 3.0.21 (native binaries) → Package: https://www.nuget.org/packages/VideoLAN.LibVLC.Windows
 • VLC Source: https://github.com/videolan/vlc
 
NuGet
GitHub

Internal projects : PhoenixVisualizer.Core, PhoenixVisualizer.AvsEngine, PhoenixVisualizer.Visuals, PhoenixVisualizer.Audio, PhoenixVisualizer.Plugins.*, PhoenixVisualizer.Plots, PhoenixVisualizer.Editor, etc.