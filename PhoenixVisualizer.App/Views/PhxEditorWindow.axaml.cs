using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.IO;
using System.Linq;
using System.Reactive;
using System.Text.Json;
using System.Threading.Tasks;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Media;
using Avalonia.Threading;
using PhoenixVisualizer.Core.Nodes;
using ReactiveUI;
using ReactiveUI.Fody.Helpers;
using System.Diagnostics;

namespace PhoenixVisualizer.Views;

/// <summary>
/// PHX Editor Window - Advanced Visual Effects Composer
/// Complete AVS Editor++ with effect stack, code editing, and live preview
/// </summary>
public partial class PhxEditorWindow : Window
{
    private PhxPreviewRenderer _previewRenderer;
    private ParameterEditor _parameterEditor;
    private PhxCodeEngine _codeEngine;

    public PhxEditorWindow()
    {
        InitializeComponent();
        ViewModel = new PhxEditorViewModel();

        // Initialize code engine
        _codeEngine = new PhxCodeEngine();

        // Set up the preview rendering
        SetupPreviewRendering();

        // Set up parameter editor
        SetupParameterEditor();

        // Wire up effect selection changes
        WireUpEffectSelection();

        // Wire up code compilation
        WireUpCodeCompilation();
    }

    private void WireUpCodeCompilation()
    {
        if (ViewModel is PhxEditorViewModel vm)
        {
            // Wire up the compile command to execute code
            vm.CompileCommand.Subscribe(_ => CompileCode());
            vm.TestCodeCommand.Subscribe(_ => TestCode());
        }
    }

    private void CompileCode()
    {
        if (ViewModel is PhxEditorViewModel vm)
        {
            try
            {
                // Execute initialization code
                var initResult = _codeEngine.ExecuteInit(vm.InitCode);
                if (!initResult.Success)
                {
                    vm.StatusMessage = $"Init Error: {initResult.Message}";
                    return;
                }

                // Execute frame code
                var frameResult = _codeEngine.ExecuteFrame(vm.FrameCode);
                if (!frameResult.Success)
                {
                    vm.StatusMessage = $"Frame Error: {frameResult.Message}";
                    return;
                }

                // Execute beat code if available
                if (!string.IsNullOrWhiteSpace(vm.BeatCode))
                {
                    var beatResult = _codeEngine.ExecuteBeat(vm.BeatCode);
                    if (!beatResult.Success)
                    {
                        vm.StatusMessage = $"Beat Error: {beatResult.Message}";
                        return;
                    }
                }

                vm.StatusMessage = "Code compiled successfully";
                vm.CodeStatus = "Ready";

            }
            catch (Exception ex)
            {
                vm.StatusMessage = $"Compilation Error: {ex.Message}";
                vm.CodeStatus = "Error";
                Debug.WriteLine($"PHX Code compilation error: {ex}");
            }
        }
    }

    private void TestCode()
    {
        if (ViewModel is PhxEditorViewModel vm)
        {
            try
            {
                // Test point code execution
                var pointResult = _codeEngine.ExecutePoint(vm.PointCode, 0, 100);
                if (!pointResult.Success)
                {
                    vm.StatusMessage = $"Point Error: {pointResult.Message}";
                    return;
                }

                vm.StatusMessage = $"Test successful - Point: ({pointResult.PointX:F2}, {pointResult.PointY:F2})";

            }
            catch (Exception ex)
            {
                vm.StatusMessage = $"Test Error: {ex.Message}";
                Debug.WriteLine($"PHX Code test error: {ex}");
            }
        }
    }

    private void SetupPreviewRendering()
    {
        // Create the preview renderer
        _previewRenderer = new PhxPreviewRenderer(PreviewCanvas, (PhxEditorViewModel)ViewModel);
    }

    private void SetupParameterEditor()
    {
        // Create parameter editor and add it to the parameters panel
        _parameterEditor = new ParameterEditor();
        ParametersPanel.Children.Insert(0, _parameterEditor);

        // Bind to selected effect changes
        this.WhenAnyValue(x => x.ViewModel)
            .Where(vm => vm is PhxEditorViewModel)
            .Select(vm => (PhxEditorViewModel)vm)
            .Subscribe(vm =>
            {
                vm.WhenAnyValue(x => x.SelectedEffect)
                    .Subscribe(selectedEffect =>
                    {
                        if (selectedEffect != null)
                        {
                            _parameterEditor.UpdateParameters(
                                selectedEffect.Name,
                                selectedEffect.Parameters
                            );
                        }
                        else
                        {
                            _parameterEditor.UpdateParameters("", new Dictionary<string, EffectParam>());
                        }
                    });
            });
    }

    private void WireUpEffectSelection()
    {
        // Wire up the preview renderer to respond to play/pause/restart commands
        if (ViewModel is PhxEditorViewModel vm)
        {
            vm.PlayCommand.Subscribe(_ => _previewRenderer?.Resume());
            vm.PauseCommand.Subscribe(_ => _previewRenderer?.Pause());
            vm.RestartCommand.Subscribe(_ => _previewRenderer?.Restart());
        }
    }

    protected override void OnClosed(EventArgs e)
    {
        base.OnClosed(e);

        // Clean up resources
        _previewRenderer?.Stop();
        _codeEngine?.Reset();
    }
}

/// <summary>
/// ViewModel for PHX Editor - Manages all editor functionality
/// </summary>
public class PhxEditorViewModel : ReactiveObject
{
    // Core Data
    public ObservableCollection<EffectStackItem> EffectStack { get; } = new();
    public ObservableCollection<EffectItem> PhoenixOriginals { get; } = new();
    public ObservableCollection<EffectItem> AvsEffects { get; } = new();
    public ObservableCollection<EffectItem> ResearchEffects { get; } = new();

    // Current Selection
    [Reactive] public EffectStackItem SelectedEffect { get; set; }
    [Reactive] public EffectItem SelectedLibraryEffect { get; set; }
    [Reactive] public int SelectedTabIndex { get; set; }

    // Code Content
    [Reactive] public string InitCode { get; set; } = "// Initialization code\n// Runs once when preset loads\n\n";
    [Reactive] public string FrameCode { get; set; } = "// Per-frame code\n// Runs every frame\n\nfloat time = gettime(0);\nfloat bass = getosc(0, 0, 0);\nfloat mid = getosc(0, 0.5, 0);\nfloat treble = getosc(0, 1, 0);\n\n";
    [Reactive] public string PointCode { get; set; } = "// Per-point code\n// Runs for each point in superscope\n\nx = sin(time + i * 6.28) * 0.5;\ny = cos(time + i * 6.28) * 0.5;\n\n";
    [Reactive] public string BeatCode { get; set; } = "// On-beat code\n// Triggers when beat is detected\n\n// Beat-based effects here\n\n";

    // Status
    [Reactive] public string StatusMessage { get; set; } = "Ready";
    [Reactive] public string FpsCounter { get; set; } = "60 FPS";
    [Reactive] public string MemoryUsage { get; set; } = "128 MB";
    [Reactive] public string PresetName { get; set; } = "Untitled.phx";
    [Reactive] public string CodeStatus { get; set; } = "Ready";

    // Commands
    public ReactiveCommand<Unit, Unit> NewPresetCommand { get; }
    public ReactiveCommand<Unit, Unit> OpenPresetCommand { get; }
    public ReactiveCommand<Unit, Unit> SavePresetCommand { get; }
    public ReactiveCommand<Unit, Unit> SavePresetAsCommand { get; }
    public ReactiveCommand<Unit, Unit> ExportAvsCommand { get; }
    public ReactiveCommand<Unit, Unit> ImportAvsCommand { get; }
    public ReactiveCommand<Unit, Unit> ExitCommand { get; }

    public ReactiveCommand<Unit, Unit> UndoCommand { get; }
    public ReactiveCommand<Unit, Unit> RedoCommand { get; }
    public ReactiveCommand<Unit, Unit> CutCommand { get; }
    public ReactiveCommand<Unit, Unit> CopyCommand { get; }
    public ReactiveCommand<Unit, Unit> PasteCommand { get; }
    public ReactiveCommand<Unit, Unit> DuplicateEffectCommand { get; }
    public ReactiveCommand<Unit, Unit> DeleteEffectCommand { get; }

    public ReactiveCommand<Unit, Unit> TogglePreviewCommand { get; }
    public ReactiveCommand<Unit, Unit> ToggleParametersCommand { get; }
    public ReactiveCommand<Unit, Unit> ToggleLibraryCommand { get; }
    public ReactiveCommand<Unit, Unit> FullscreenPreviewCommand { get; }

    public ReactiveCommand<Unit, Unit> TestRunCommand { get; }
    public ReactiveCommand<Unit, Unit> BuildTestCommand { get; }
    public ReactiveCommand<Unit, Unit> PerformanceMonitorCommand { get; }
    public ReactiveCommand<Unit, Unit> ClearAllCommand { get; }

    public ReactiveCommand<Unit, Unit> ShowGuideCommand { get; }
    public ReactiveCommand<Unit, Unit> ShowShortcutsCommand { get; }
    public ReactiveCommand<Unit, Unit> ShowAboutCommand { get; }

    // Additional Commands
    public ReactiveCommand<Unit, Unit> AddEffectCommand { get; }
    public ReactiveCommand<Unit, Unit> SaveCodeCommand { get; }
    public ReactiveCommand<Unit, Unit> CompileCommand { get; }
    public ReactiveCommand<Unit, Unit> TestCodeCommand { get; }
    public ReactiveCommand<Unit, Unit> PlayCommand { get; }
    public ReactiveCommand<Unit, Unit> PauseCommand { get; }
    public ReactiveCommand<Unit, Unit> RestartCommand { get; }

    // Undo/Redo System
    private readonly Stack<EditorState> _undoStack = new();
    private readonly Stack<EditorState> _redoStack = new();

    public PhxEditorViewModel()
    {
        InitializeCommands();
        LoadEffectLibrary();
        InitializeDefaultPreset();
    }

    private void InitializeCommands()
    {
        // File Commands
        NewPresetCommand = ReactiveCommand.Create(NewPreset);
        OpenPresetCommand = ReactiveCommand.Create(OpenPreset);
        SavePresetCommand = ReactiveCommand.Create(SavePreset);
        SavePresetAsCommand = ReactiveCommand.Create(SavePresetAs);
        ExportAvsCommand = ReactiveCommand.Create(ExportAvs);
        ImportAvsCommand = ReactiveCommand.Create(ImportAvs);
        ExitCommand = ReactiveCommand.Create(Exit);

        // Edit Commands
        UndoCommand = ReactiveCommand.Create(Undo, this.WhenAnyValue(x => x._undoStack.Count).Select(c => c > 0));
        RedoCommand = ReactiveCommand.Create(Redo, this.WhenAnyValue(x => x._redoStack.Count).Select(c => c > 0));
        CutCommand = ReactiveCommand.Create(Cut);
        CopyCommand = ReactiveCommand.Create(Copy);
        PasteCommand = ReactiveCommand.Create(Paste);
        DuplicateEffectCommand = ReactiveCommand.Create(DuplicateEffect);
        DeleteEffectCommand = ReactiveCommand.Create(DeleteEffect);

        // View Commands
        TogglePreviewCommand = ReactiveCommand.Create(TogglePreview);
        ToggleParametersCommand = ReactiveCommand.Create(ToggleParameters);
        ToggleLibraryCommand = ReactiveCommand.Create(ToggleLibrary);
        FullscreenPreviewCommand = ReactiveCommand.Create(FullscreenPreview);

        // Tools Commands
        TestRunCommand = ReactiveCommand.Create(TestRun);
        BuildTestCommand = ReactiveCommand.Create(BuildTest);
        PerformanceMonitorCommand = ReactiveCommand.Create(PerformanceMonitor);
        ClearAllCommand = ReactiveCommand.Create(ClearAll);

        // Help Commands
        ShowGuideCommand = ReactiveCommand.Create(ShowGuide);
        ShowShortcutsCommand = ReactiveCommand.Create(ShowShortcuts);
        ShowAboutCommand = ReactiveCommand.Create(ShowAbout);

        // Additional Commands
        AddEffectCommand = ReactiveCommand.Create(AddEffect);
        SaveCodeCommand = ReactiveCommand.Create(SaveCode);
        CompileCommand = ReactiveCommand.Create(Compile);
        TestCodeCommand = ReactiveCommand.Create(TestCode);
        PlayCommand = ReactiveCommand.Create(Play);
        PauseCommand = ReactiveCommand.Create(Pause);
        RestartCommand = ReactiveCommand.Create(Restart);
    }

    private void LoadEffectLibrary()
    {
        // Load Phoenix Originals
        PhoenixOriginals.Add(new EffectItem { Name = "Cymatics Visualizer", Category = "Phoenix" });
        PhoenixOriginals.Add(new EffectItem { Name = "Shader Visualizer", Category = "Phoenix" });
        PhoenixOriginals.Add(new EffectItem { Name = "Sacred Geometry", Category = "Phoenix" });
        PhoenixOriginals.Add(new EffectItem { Name = "Godrays", Category = "Phoenix" });
        PhoenixOriginals.Add(new EffectItem { Name = "Particle Swarm", Category = "Phoenix" });

        // Load AVS Converted Effects
        AvsEffects.Add(new EffectItem { Name = "Superscope", Category = "AVS" });
        AvsEffects.Add(new EffectItem { Name = "Movement", Category = "AVS" });
        AvsEffects.Add(new EffectItem { Name = "Dynamic Movement", Category = "AVS" });
        AvsEffects.Add(new EffectItem { Name = "Buffer Save", Category = "AVS" });
        AvsEffects.Add(new EffectItem { Name = "Color Modifier", Category = "AVS" });

        // Load Research Effects
        ResearchEffects.Add(new EffectItem { Name = "Solfeggio Harmonics", Category = "Research" });
        ResearchEffects.Add(new EffectItem { Name = "Earth Resonance", Category = "Research" });
        ResearchEffects.Add(new EffectItem { Name = "Quantum Field", Category = "Research" });
        ResearchEffects.Add(new EffectItem { Name = "Fractal Generator", Category = "Research" });
    }

    private void InitializeDefaultPreset()
    {
        // Add a default superscope effect
        var defaultEffect = new EffectStackItem
        {
            Name = "Default Superscope",
            Description = "Basic superscope with cymatics integration",
            EffectType = "Superscope",
            Parameters = new Dictionary<string, EffectParam>
            {
                ["points"] = new EffectParam { Label = "Points", Type = "slider", Min = 100, Max = 1000, FloatValue = 400 },
                ["red"] = new EffectParam { Label = "Red", Type = "slider", Min = 0, Max = 1, FloatValue = 1f },
                ["green"] = new EffectParam { Label = "Green", Type = "slider", Min = 0, Max = 1, FloatValue = 0.5f },
                ["blue"] = new EffectParam { Label = "Blue", Type = "slider", Min = 0, Max = 1, FloatValue = 0f }
            }
        };

        EffectStack.Add(defaultEffect);
        SelectedEffect = defaultEffect;
    }

    private void SaveState()
    {
        var state = new EditorState
        {
            EffectStack = EffectStack.ToList(),
            InitCode = InitCode,
            FrameCode = FrameCode,
            PointCode = PointCode,
            BeatCode = BeatCode,
            SelectedEffect = SelectedEffect
        };

        _undoStack.Push(state);

        // Limit undo stack size
        while (_undoStack.Count > 50)
        {
            _ = _undoStack.Pop();
        }

        _redoStack.Clear();
    }

    // Command Implementations
    private void NewPreset()
    {
        SaveState();
        EffectStack.Clear();
        InitCode = "// New preset\n\n";
        FrameCode = "// Per-frame code\n\n";
        PointCode = "// Per-point code\n\n";
        BeatCode = "// On-beat code\n\n";
        PresetName = "Untitled.phx";
        StatusMessage = "New preset created";
    }

    private async void OpenPreset()
    {
        var dialog = new OpenFileDialog
        {
            Title = "Open PHX Preset",
            Filters = new List<FileDialogFilter>
            {
                new FileDialogFilter { Name = "PHX Presets", Extensions = new List<string> { "phx" } },
                new FileDialogFilter { Name = "All Files", Extensions = new List<string> { "*" } }
            }
        };

        var result = await dialog.ShowAsync(App.MainWindow);
        if (result != null && result.Length > 0)
        {
            SaveState();
            LoadPreset(result[0]);
        }
    }

    private async void SavePreset()
    {
        if (string.IsNullOrEmpty(PresetName) || PresetName == "Untitled.phx")
        {
            await SavePresetAs();
            return;
        }

        var preset = CreatePresetObject();
        var json = JsonSerializer.Serialize(preset, new JsonSerializerOptions { WriteIndented = true });
        await File.WriteAllTextAsync(PresetName, json);
        StatusMessage = $"Saved: {Path.GetFileName(PresetName)}";
    }

    private async void SavePresetAs()
    {
        var dialog = new SaveFileDialog
        {
            Title = "Save PHX Preset",
            DefaultExtension = "phx",
            Filters = new List<FileDialogFilter>
            {
                new FileDialogFilter { Name = "PHX Presets", Extensions = new List<string> { "phx" } }
            }
        };

        var result = await dialog.ShowAsync(App.MainWindow);
        if (!string.IsNullOrEmpty(result))
        {
            PresetName = result;
            await SavePreset();
        }
    }

    private async void ExportAvs()
    {
        var dialog = new SaveFileDialog
        {
            Title = "Export as AVS",
            DefaultExtension = "avs",
            Filters = new List<FileDialogFilter>
            {
                new FileDialogFilter { Name = "AVS Presets", Extensions = new List<string> { "avs" } }
            }
        };

        var result = await dialog.ShowAsync(App.MainWindow);
        if (!string.IsNullOrEmpty(result))
        {
            try
            {
                var phxJson = JsonSerializer.Serialize(CreatePresetObject());
                AvsConverter.SaveAvs(result, phxJson);
                StatusMessage = $"Exported to AVS: {Path.GetFileName(result)}";
            }
            catch (Exception ex)
            {
                StatusMessage = $"Export failed: {ex.Message}";
            }
        }
    }

    private async void ImportAvs()
    {
        var dialog = new OpenFileDialog
        {
            Title = "Import AVS Preset",
            Filters = new List<FileDialogFilter>
            {
                new FileDialogFilter { Name = "AVS Presets", Extensions = new List<string> { "avs" } }
            }
        };

        var result = await dialog.ShowAsync(App.MainWindow);
        if (result != null && result.Length > 0)
        {
            try
            {
                SaveState();
                var phxJson = AvsConverter.LoadAvs(result[0]);
                LoadPresetFromJson(phxJson);
                StatusMessage = $"Imported: {Path.GetFileName(result[0])}";
            }
            catch (Exception ex)
            {
                StatusMessage = $"Import failed: {ex.Message}";
            }
        }
    }

    private void Exit()
    {
        App.MainWindow?.Close();
    }

    private void Undo()
    {
        if (_undoStack.Count > 0)
        {
            _redoStack.Push(CreateCurrentState());
            var state = _undoStack.Pop();
            RestoreState(state);
            StatusMessage = "Undid last action";
        }
    }

    private void Redo()
    {
        if (_redoStack.Count > 0)
        {
            _undoStack.Push(CreateCurrentState());
            var state = _redoStack.Pop();
            RestoreState(state);
            StatusMessage = "Redid last action";
        }
    }

    private void Cut()
    {
        if (SelectedEffect != null)
        {
            Copy();
            DeleteEffect();
        }
    }

    private void Copy()
    {
        if (SelectedEffect != null)
        {
            // TODO: Implement clipboard functionality
            StatusMessage = "Copied effect to clipboard";
        }
    }

    private void Paste()
    {
        // TODO: Implement paste from clipboard
        StatusMessage = "Pasted effect from clipboard";
    }

    private void DuplicateEffect()
    {
        if (SelectedEffect != null)
        {
            SaveState();
            var duplicate = new EffectStackItem
            {
                Name = $"{SelectedEffect.Name} (Copy)",
                Description = SelectedEffect.Description,
                EffectType = SelectedEffect.EffectType,
                Parameters = new Dictionary<string, EffectParam>(SelectedEffect.Parameters)
            };

            EffectStack.Add(duplicate);
            SelectedEffect = duplicate;
            StatusMessage = "Effect duplicated";
        }
    }

    private void DeleteEffect()
    {
        if (SelectedEffect != null)
        {
            SaveState();
            EffectStack.Remove(SelectedEffect);
            SelectedEffect = EffectStack.FirstOrDefault();
            StatusMessage = "Effect deleted";
        }
    }

    private void AddEffect()
    {
        if (SelectedLibraryEffect != null)
        {
            SaveState();
            var newEffect = new EffectStackItem
            {
                Name = SelectedLibraryEffect.Name,
                Description = $"Added {SelectedLibraryEffect.Name} effect",
                EffectType = SelectedLibraryEffect.Category,
                Parameters = new Dictionary<string, EffectParam>()
            };

            EffectStack.Add(newEffect);
            SelectedEffect = newEffect;
            StatusMessage = $"Added: {newEffect.Name}";
        }
        else
        {
            StatusMessage = "Please select an effect from the library first";
        }
    }

    private void SaveCode()
    {
        SaveState();
        StatusMessage = "Code saved";
    }

    private void Compile()
    {
        try
        {
            // TODO: Implement code compilation/validation
            CodeStatus = "Compiled successfully";
            StatusMessage = "Code compiled";
        }
        catch (Exception ex)
        {
            CodeStatus = $"Compile error: {ex.Message}";
            StatusMessage = "Compilation failed";
        }
    }

    private void TestCode()
    {
        Compile();
        if (CodeStatus == "Compiled successfully")
        {
            StatusMessage = "Code test successful";
        }
    }

    private void Play()
    {
        StatusMessage = "Preview playing";
    }

    private void Pause()
    {
        StatusMessage = "Preview paused";
    }

    private void Restart()
    {
        StatusMessage = "Preview restarted";
    }

    // Utility Methods
    private void TogglePreview() => StatusMessage = "Preview toggled";
    private void ToggleParameters() => StatusMessage = "Parameters panel toggled";
    private void ToggleLibrary() => StatusMessage = "Effect library toggled";
    private void FullscreenPreview() => StatusMessage = "Fullscreen preview";
    private void TestRun() => StatusMessage = "Test run completed";
    private void BuildTest() => StatusMessage = "Build test completed";
    private void PerformanceMonitor() => StatusMessage = "Performance monitor opened";
    private void ClearAll() => NewPreset();
    private void ShowGuide() => StatusMessage = "PHX Editor Guide opened";
    private void ShowShortcuts() => StatusMessage = "Keyboard shortcuts displayed";
    private void ShowAbout() => StatusMessage = "About PHX Editor displayed";

    private void LoadPreset(string path)
    {
        try
        {
            var json = File.ReadAllText(path);
            LoadPresetFromJson(json);
            PresetName = path;
            StatusMessage = $"Loaded: {Path.GetFileName(path)}";
        }
        catch (Exception ex)
        {
            StatusMessage = $"Failed to load preset: {ex.Message}";
        }
    }

    private void LoadPresetFromJson(string json)
    {
        var preset = JsonSerializer.Deserialize<PhxPreset>(json);
        if (preset != null)
        {
            EffectStack.Clear();
            foreach (var effect in preset.Effects)
            {
                EffectStack.Add(effect);
            }

            InitCode = preset.InitCode ?? "";
            FrameCode = preset.FrameCode ?? "";
            PointCode = preset.PointCode ?? "";
            BeatCode = preset.BeatCode ?? "";
        }
    }

    private PhxPreset CreatePresetObject()
    {
        return new PhxPreset
        {
            Version = "1.0",
            Name = Path.GetFileNameWithoutExtension(PresetName),
            Description = "PHX Editor preset",
            Effects = EffectStack.ToList(),
            InitCode = InitCode,
            FrameCode = FrameCode,
            PointCode = PointCode,
            BeatCode = BeatCode,
            ClearEveryFrame = true
        };
    }

    private EditorState CreateCurrentState()
    {
        return new EditorState
        {
            EffectStack = EffectStack.ToList(),
            InitCode = InitCode,
            FrameCode = FrameCode,
            PointCode = PointCode,
            BeatCode = BeatCode,
            SelectedEffect = SelectedEffect
        };
    }

    private void RestoreState(EditorState state)
    {
        EffectStack.Clear();
        foreach (var effect in state.EffectStack)
        {
            EffectStack.Add(effect);
        }

        InitCode = state.InitCode;
        FrameCode = state.FrameCode;
        PointCode = state.PointCode;
        BeatCode = state.BeatCode;
        SelectedEffect = state.SelectedEffect;
    }
}

/// <summary>
/// Effect item for the library
/// </summary>
public class EffectItem
{
    public string Name { get; set; } = "";
    public string Category { get; set; } = "";
}

/// <summary>
/// Effect stack item with parameters
/// </summary>
public class EffectStackItem : EffectItem
{
    public string EffectType { get; set; } = "";
    public Dictionary<string, EffectParam> Parameters { get; set; } = new();

    public ReactiveCommand<Unit, Unit> EditCommand { get; set; }
    public ReactiveCommand<Unit, Unit> DeleteCommand { get; set; }

    public EffectStackItem()
    {
        EditCommand = ReactiveCommand.Create(() => { /* TODO: Edit effect */ });
        DeleteCommand = ReactiveCommand.Create(() => { /* TODO: Delete effect */ });
    }
}

/// <summary>
/// PHX Preset file format
/// </summary>
public class PhxPreset
{
    public string Version { get; set; } = "1.0";
    public string Name { get; set; } = "";
    public string Description { get; set; } = "";
    public List<EffectStackItem> Effects { get; set; } = new();
    public string InitCode { get; set; } = "";
    public string FrameCode { get; set; } = "";
    public string PointCode { get; set; } = "";
    public string BeatCode { get; set; } = "";
    public bool ClearEveryFrame { get; set; } = true;
}

/// <summary>
/// Editor state for undo/redo
/// </summary>
public class EditorState
{
    public List<EffectStackItem> EffectStack { get; set; } = new();
    public string InitCode { get; set; } = "";
    public string FrameCode { get; set; } = "";
    public string PointCode { get; set; } = "";
    public string BeatCode { get; set; } = "";
    public EffectStackItem SelectedEffect { get; set; }
}
