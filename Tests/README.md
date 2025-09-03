# PhoenixVisualizer Tests Directory

This directory contains all test-related files and projects that were moved from the PhoenixVisualizer root directory to maintain a clean project structure.

## 📁 Directory Structure

```
Tests/
├── README.md                           # This file
├── Core/                               # Core functionality tests
│   └── Effects/
│       └── Nodes/
│           └── AvsEffects/
│               └── test_cache.py       # AVS effects cache testing
├── AudioTestRunner.cs                  # Audio test runner implementation
├── AudioTestRunner.csproj              # Audio test runner project file
├── test_avs_parsing.cs                 # AVS parsing test implementation
├── test_log.txt                        # Test log output
├── test_log_v2.txt                     # Updated test log output
├── VlcTest.cs                          # VLC integration test implementation
├── VlcTest.csproj                      # VLC test project file
├── AudioDataTest/                      # Audio data processing tests
│   ├── AudioDataTest.csproj
│   └── Program.cs
├── CheckExports/                       # Export validation tests
│   ├── CheckExports.csproj
│   └── Program.cs
├── EffectsGraphTestApp/                # Effects graph testing application
│   ├── EffectsGraphTestApp.csproj
│   └── Program.cs
├── PluginTest/                         # Plugin system tests
│   └── Program.cs
├── RealAudioTest/                      # Real-time audio processing tests
│   ├── Program.cs
│   └── RealAudioTest.csproj
└── VlcTestStandalone/                  # Standalone VLC testing
    ├── Program.cs
    └── VlcTestStandalone.csproj
```

## 🧪 Test Categories

### **Core Tests**
- **AVS Effects Cache Testing:** `Core/Effects/Nodes/AvsEffects/test_cache.py`
  - Tests the caching mechanism for AVS effects
  - Validates effect loading and performance

### **Audio System Tests**
- **AudioTestRunner:** `AudioTestRunner.cs` & `AudioTestRunner.csproj`
  - Main audio testing framework
  - LibVLCSharp integration validation
  - Audio format support testing

- **VLC Integration:** `VlcTest.cs` & `VlcTest.csproj`
  - VLC media player integration tests
  - Audio stream processing validation

- **Real-time Audio:** `RealAudioTest/`
  - Real-time audio processing tests
  - Performance and latency validation

- **Audio Data Processing:** `AudioDataTest/`
  - Audio data manipulation tests
  - FFT and waveform analysis validation

### **Effects System Tests**
- **Effects Graph:** `EffectsGraphTestApp/`
  - Effects graph construction and execution
  - Node connectivity and data flow testing

### **Plugin System Tests**
- **Plugin Testing:** `PluginTest/`
  - Plugin loading and execution
  - Plugin API validation

### **Utility Tests**
- **Export Validation:** `CheckExports/`
  - Export functionality testing
  - File format validation

- **AVS Parsing:** `test_avs_parsing.cs`
  - AVS file parsing and interpretation
  - Syntax validation and error handling

### **Standalone Tests**
- **VLC Standalone:** `VlcTestStandalone/`
  - Independent VLC functionality testing
  - Cross-platform compatibility validation

## 📊 Test Logs

- **test_log.txt:** Basic test execution logs
- **test_log_v2.txt:** Enhanced test logging with detailed output

## 🚀 Running Tests

### **Individual Test Projects**
```bash
# Audio Test Runner
cd Tests
dotnet run --project AudioTestRunner.csproj

# VLC Test
dotnet run --project VlcTest.csproj

# Effects Graph Test App
cd EffectsGraphTestApp
dotnet run

# Real Audio Test
cd RealAudioTest
dotnet run
```

### **All Tests**
```bash
# Run all test projects
cd Tests
dotnet build
dotnet test
```

## 🔧 Test Configuration

### **Audio Testing Requirements**
- **LibVLCSharp:** Required for audio system tests
- **Test Audio Files:** MP3, WAV, FLAC samples needed
- **Hardware:** Audio output device for real-time testing

### **Effects Testing Requirements**
- **AVS Files:** Sample AVS files for parsing tests
- **Graphics:** SkiaSharp rendering context for visual tests

### **Plugin Testing Requirements**
- **Plugin DLLs:** Sample plugins for loading tests
- **Sandbox Environment:** Isolated execution environment

## 📝 Test Documentation

### **Adding New Tests**
1. Create test project in appropriate subdirectory
2. Follow naming convention: `[Component]Test.csproj`
3. Include comprehensive test coverage
4. Update this README with new test information

### **Test Standards**
- **Unit Tests:** Test individual components in isolation
- **Integration Tests:** Test component interactions
- **Performance Tests:** Validate performance requirements
- **Regression Tests:** Ensure existing functionality remains intact

## 🎯 Test Coverage Goals

- **Audio System:** 100% coverage of LibVLCSharp integration
- **Effects System:** Complete AVS compatibility validation
- **Plugin System:** Full plugin lifecycle testing
- **Performance:** 60 FPS rendering validation
- **Cross-platform:** Windows, macOS, Linux compatibility

## 🔗 Related Documentation

- **Main Project:** `../README.md`
- **Audio System:** `../PhoenixVisualizer.Audio/`
- **Effects System:** `../PhoenixVisualizer.Core/Effects/`
- **Plugin System:** `../PhoenixVisualizer.Plugins.*/`

---

**Status:** ✅ **All test files moved and organized**  
**Last Updated:** January 2025  
**Test Coverage:** Comprehensive audio, effects, and plugin testing
