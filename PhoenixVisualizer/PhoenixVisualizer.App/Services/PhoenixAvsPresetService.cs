using PhoenixVisualizer.Core.Avs;
using PhoenixVisualizer.PluginHost;

namespace PhoenixVisualizer.Services;

/// <summary>
/// Service that integrates CompleteAvsPresetLoader into the main application
/// Provides a bridge between the Core AVS components and the application layer
/// </summary>
public class PhoenixAvsPresetService
{
    private readonly CompleteAvsPresetLoader _presetLoader;
    
    public PhoenixAvsPresetService()
    {
        // Create the loader with NS-EEL evaluator if available
        INsEelEvaluator? evaluator = null;
        try
        {
            // Create evaluator from PluginHost project with adapter
            var nsEelEvaluator = new NsEelEvaluator();
            evaluator = new NsEelEvaluatorAdapter(nsEelEvaluator);
        }
        catch
        {
            // Fall back to no evaluator if PluginHost is not available
            evaluator = null;
        }
        
        _presetLoader = new CompleteAvsPresetLoader(evaluator);
    }
    
    /// <summary>
    /// Check if a file can be loaded as an AVS preset using Phoenix components
    /// </summary>
    public bool CanLoadPreset(string filePath)
    {
        try
        {
            if (!File.Exists(filePath)) return false;
            if (!filePath.EndsWith(".avs", StringComparison.OrdinalIgnoreCase)) return false;
            
            // Quick validation by trying to get preset info
            var info = _presetLoader.GetPresetInfo(filePath);
            return info.LoadError == null;
        }
        catch
        {
            return false;
        }
    }
    
    /// <summary>
    /// Load an AVS preset and return effect chain information
    /// </summary>
    public AvsLoadResult LoadPreset(string filePath)
    {
        try
        {
            // Get preset information
            var info = _presetLoader.GetPresetInfo(filePath);
            if (info.LoadError != null)
            {
                return new AvsLoadResult
                {
                    Success = false,
                    ErrorMessage = info.LoadError,
                    FilePath = filePath
                };
            }
            
            // Load the full effect chain
            var effectChain = _presetLoader.LoadFromFile(filePath);
            
            return new AvsLoadResult
            {
                Success = true,
                FilePath = filePath,
                EffectChain = effectChain,
                PresetInfo = info,
                SupportedEffectCount = info.SupportedEffectCount,
                UnsupportedEffectCount = info.UnsupportedEffectCount,
                TotalEffectCount = info.TotalEffectCount
            };
        }
        catch (Exception ex)
        {
            return new AvsLoadResult
            {
                Success = false,
                ErrorMessage = ex.Message,
                FilePath = filePath
            };
        }
    }
    
    /// <summary>
    /// Load multiple AVS presets from a directory
    /// </summary>
    public List<AvsLoadResult> LoadPresetsFromDirectory(string directoryPath)
    {
        var results = new List<AvsLoadResult>();
        
        if (!Directory.Exists(directoryPath))
            return results;
            
        var avsFiles = Directory.GetFiles(directoryPath, "*.avs", SearchOption.AllDirectories);
        
        foreach (var file in avsFiles)
        {
            var result = LoadPreset(file);
            results.Add(result);
        }
        
        return results;
    }
    
    /// <summary>
    /// Get quick information about an AVS preset without full loading
    /// </summary>
    public AvsPresetAnalysisInfo GetPresetInfo(string filePath)
    {
        return _presetLoader.GetPresetInfo(filePath);
    }
}

/// <summary>
/// Result of loading an AVS preset with Phoenix components
/// </summary>
public class AvsLoadResult
{
    public bool Success { get; set; }
    public string? ErrorMessage { get; set; }
    public string FilePath { get; set; } = "";
    public EffectChain? EffectChain { get; set; }
    public AvsPresetAnalysisInfo? PresetInfo { get; set; }
    public int SupportedEffectCount { get; set; }
    public int UnsupportedEffectCount { get; set; }
    public int TotalEffectCount { get; set; }
    
    public string StatusSummary => Success 
        ? $"✅ Loaded {SupportedEffectCount}/{TotalEffectCount} effects"
        : $"❌ {ErrorMessage}";
}

/// <summary>
/// Adapter to make NsEelEvaluator compatible with INsEelEvaluator interface
/// </summary>
internal class NsEelEvaluatorAdapter : INsEelEvaluator
{
    private readonly NsEelEvaluator _evaluator;

    public NsEelEvaluatorAdapter(NsEelEvaluator evaluator)
    {
        _evaluator = evaluator;
    }

    public double Evaluate(string expression)
    {
        return _evaluator.Evaluate(expression);
    }

    public void SetAudioData(float bass, float mid, float treble, float volume, bool beat)
    {
        _evaluator.SetAudioData(bass, mid, treble, volume, beat);
    }

    public void SetFrameContext(int frame, double frameTime, double beatTime)
    {
        _evaluator.SetFrameContext(frame, frameTime, beatTime);
    }

    public void Dispose()
    {
        // NsEelEvaluator doesn't implement IDisposable, so nothing to dispose
    }
}