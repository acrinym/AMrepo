# AMrepo
My Maps

## 🎵 PhoenixVisualizer Project

**Status:** ✅ **BUILD SYSTEM FULLY RESTORED**  
**Last Updated:** December 28, 2024  

### 🎯 **Project Overview**
PhoenixVisualizer is an advanced audio visualization application built with Avalonia (.NET 8) that provides:
- **Audio Playback:** LibVLCSharp integration for high-quality audio
- **Visual Effects:** Modular effect system with 60+ AVS-compatible effects
- **Real-time Processing:** Live audio analysis and visualization
- **Cross-platform:** Windows, macOS, and Linux support

### 🚀 **Current Status**
- **Build System:** ✅ Fully functional (0 errors, 0 warnings)
- **Core Infrastructure:** ✅ Complete and tested
- **Audio System:** ✅ VLC integration working
- **Effect Framework:** ✅ Architecture ready for implementation
- **Testing:** ✅ Standalone tests verified

### 📚 **Documentation**
- **[Status Report](./PHOENIXVISUALIZER_STATUS_REPORT.md)** - Complete project status
- **[Build Restoration](./BUILD_SYSTEM_RESTORATION_COMPLETE.md)** - Major milestone achieved
- **[Project Plan](./PROJECT_PHOENIX_PLAN.md)** - Development roadmap

### 🔧 **Quick Start**
```bash
# Build the solution
dotnet build PhoenixVisualizer/PhoenixVisualizer.sln

# Run standalone test
dotnet run --project PhoenixVisualizer/VlcTestStandalone

# Run main application (requires display)
dotnet run --project PhoenixVisualizer/PhoenixVisualizer.App
```

---

## 🤖 For Code Agents

**MANDATORY:** All code agents MUST follow these guidelines when creating pull requests:

- 📋 **[AGENTS.md](./AGENTS.md)** - Complete PR documentation guidelines
- ✅ **[AGENT_PR_CHECKLIST.md](./AGENT_PR_CHECKLIST.md)** - Quick compliance checklist  
- 📝 **[.github/pull_request_template.md](./.github/pull_request_template.md)** - GitHub PR template

### Key Requirements:
1. **ALWAYS** run build verification before creating PRs
2. **Document** complete build status (success/warnings/errors)
3. **Include** exact error messages with file paths and line numbers
4. **Specify** what needs to be done next with priorities
5. **Provide** actionable fix instructions for any failures

**⚠️ Non-compliant PRs will be rejected and require resubmission.**
