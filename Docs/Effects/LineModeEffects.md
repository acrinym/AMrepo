# Line Mode Effects

## Overview

The Line Mode effect controls the global rendering mode for line-based visualizations in the AVS system. It sets the blending mode and alpha values that affect how lines are drawn across all line-based effects. This is a system-level effect that doesn't render visual content itself but configures the rendering pipeline.

## C# Implementation

### Properties

```csharp
/// <summary>
/// Whether the effect is enabled
/// </summary>
public bool Enabled { get; set; } = true;

/// <summary>
/// Current line blend mode
/// </summary>
public LineBlendMode BlendMode { get; set; } = LineBlendMode.Replace;

/// <summary>
/// Alpha value for blending (0-255)
/// </summary>
public int Alpha { get; set; } = 255;

/// <summary>
/// Output value for adjustable blend mode (0-255)
/// </summary>
public int OutputValue { get; set; } = 128;

/// <summary>
/// Whether to apply the mode globally
/// </summary>
public bool ApplyGlobally { get; set; } = true;

/// <summary>
/// Effect intensity multiplier
/// </summary>
public float Intensity { get; set; } = 1.0f;
```

### Enums

```csharp
/// <summary>
/// Available line blending modes
/// </summary>
public enum LineBlendMode
{
    /// <summary>
    /// Replace existing pixels
    /// </summary>
    Replace = 0,
    
    /// <summary>
    /// Additive blending
    /// </summary>
    Additive = 1,
    
    /// <summary>
    /// Maximum value blending
    /// </summary>
    MaximumBlend = 2,
    
    /// <summary>
    /// 50/50 average blending
    /// </summary>
    FiftyFiftyBlend = 3,
    
    /// <summary>
    /// Subtractive blending (type 1)
    /// </summary>
    SubtractiveBlend1 = 4,
    
    /// <summary>
    /// Subtractive blending (type 2)
    /// </summary>
    SubtractiveBlend2 = 5,
    
    /// <summary>
    /// Multiply blending
    /// </summary>
    MultiplyBlend = 6,
    
    /// <summary>
    /// Adjustable blending with custom output value
    /// </summary>
    AdjustableBlend = 7,
    
    /// <summary>
    /// XOR blending
    /// </summary>
    Xor = 8,
    
    /// <summary>
    /// Minimum value blending
    /// </summary>
    MinimumBlend = 9
}
```

### Private Fields

```csharp
/// <summary>
/// Global line blend mode manager
/// </summary>
private static LineBlendMode _globalLineBlendMode = LineBlendMode.Replace;

/// <summary>
/// Global alpha value
/// </summary>
private static int _globalAlpha = 255;

/// <summary>
/// Global output value for adjustable blend
/// </summary>
private static int _globalOutputValue = 128;

/// <summary>
/// Whether the effect has been initialized
/// </summary>
private bool _isInitialized = false;

/// <summary>
/// Previous configuration for change detection
/// </summary>
private LineModeConfiguration _previousConfig;
```

### Structs

```csharp
/// <summary>
/// Configuration structure for line mode settings
/// </summary>
public struct LineModeConfiguration
{
    public LineBlendMode BlendMode;
    public int Alpha;
    public int OutputValue;
    public bool ApplyGlobally;
    
    public LineModeConfiguration(LineBlendMode blendMode, int alpha, int outputValue, bool applyGlobally)
    {
        BlendMode = blendMode;
        Alpha = alpha;
        OutputValue = outputValue;
        ApplyGlobally = applyGlobally;
    }
}
```

### Constructor

```csharp
public LineModeEffectsNode()
{
    _isInitialized = false;
    _previousConfig = new LineModeConfiguration(BlendMode, Alpha, OutputValue, ApplyGlobally);
}
```

### Processing Methods

```csharp
public override void ProcessFrame(ImageBuffer imageBuffer, AudioFeatures audioFeatures)
{
    if (!Enabled) return;

    // Initialize if needed
    if (!_isInitialized)
    {
        InitializeEffect();
    }

    // Check if configuration has changed
    if (HasConfigurationChanged())
    {
        UpdateGlobalSettings();
        _previousConfig = GetCurrentConfiguration();
    }
}

/// <summary>
/// Initialize the effect and global settings
/// </summary>
private void InitializeEffect()
{
    if (ApplyGlobally)
    {
        _globalLineBlendMode = BlendMode;
        _globalAlpha = Alpha;
        _globalOutputValue = OutputValue;
    }
    
    _isInitialized = true;
}

/// <summary>
/// Check if the configuration has changed since last update
/// </summary>
private bool HasConfigurationChanged()
{
    var currentConfig = GetCurrentConfiguration();
    return !currentConfig.Equals(_previousConfig);
}

/// <summary>
/// Get the current configuration
/// </summary>
private LineModeConfiguration GetCurrentConfiguration()
{
    return new LineModeConfiguration(BlendMode, Alpha, OutputValue, ApplyGlobally);
}

/// <summary>
/// Update global line rendering settings
/// </summary>
private void UpdateGlobalSettings()
{
    if (ApplyGlobally)
    {
        _globalLineBlendMode = BlendMode;
        _globalAlpha = Alpha;
        _globalOutputValue = OutputValue;
    }
}
```

### Global Access Methods

```csharp
/// <summary>
/// Get the current global line blend mode
/// </summary>
public static LineBlendMode GetGlobalLineBlendMode()
{
    return _globalLineBlendMode;
}

/// <summary>
/// Get the current global alpha value
/// </summary>
public static int GetGlobalAlpha()
{
    return _globalAlpha;
}

/// <summary>
/// Get the current global output value
/// </summary>
public static int GetGlobalOutputValue()
{
    return _globalOutputValue;
}

/// <summary>
/// Set the global line blend mode
/// </summary>
public static void SetGlobalLineBlendMode(LineBlendMode blendMode)
{
    _globalLineBlendMode = blendMode;
}

/// <summary>
/// Set the global alpha value
/// </summary>
public static void SetGlobalAlpha(int alpha)
{
    _globalAlpha = Math.Max(0, Math.Min(255, alpha));
}

/// <summary>
/// Set the global output value
/// </summary>
public static void SetGlobalOutputValue(int outputValue)
{
    _globalOutputValue = Math.Max(0, Math.Min(255, outputValue));
}
```

### Line Rendering Methods

```csharp
/// <summary>
/// Apply the current line blend mode to two colors
/// </summary>
public static Color ApplyLineBlendMode(Color sourceColor, Color targetColor)
{
    switch (_globalLineBlendMode)
    {
        case LineBlendMode.Replace:
            return targetColor;
            
        case LineBlendMode.Additive:
            return BlendColorsAdditive(sourceColor, targetColor, _globalAlpha);
            
        case LineBlendMode.MaximumBlend:
            return BlendColorsMaximum(sourceColor, targetColor, _globalAlpha);
            
        case LineBlendMode.FiftyFiftyBlend:
            return BlendColorsFiftyFifty(sourceColor, targetColor, _globalAlpha);
            
        case LineBlendMode.SubtractiveBlend1:
            return BlendColorsSubtractive1(sourceColor, targetColor, _globalAlpha);
            
        case LineBlendMode.SubtractiveBlend2:
            return BlendColorsSubtractive2(sourceColor, targetColor, _globalAlpha);
            
        case LineBlendMode.MultiplyBlend:
            return BlendColorsMultiply(sourceColor, targetColor, _globalAlpha);
            
        case LineBlendMode.AdjustableBlend:
            return BlendColorsAdjustable(sourceColor, targetColor, _globalAlpha, _globalOutputValue);
            
        case LineBlendMode.Xor:
            return BlendColorsXor(sourceColor, targetColor, _globalAlpha);
            
        case LineBlendMode.MinimumBlend:
            return BlendColorsMinimum(sourceColor, targetColor, _globalAlpha);
            
        default:
            return targetColor;
    }
}

/// <summary>
/// Additive blending with alpha
/// </summary>
private static Color BlendColorsAdditive(Color source, Color target, int alpha)
{
    float alphaFactor = alpha / 255.0f;
    int r = Math.Min(255, source.R + (int)(target.R * alphaFactor));
    int g = Math.Min(255, source.G + (int)(target.G * alphaFactor));
    int b = Math.Min(255, source.B + (int)(target.B * alphaFactor));
    int a = Math.Min(255, source.A + (int)(target.A * alphaFactor));
    
    return Color.FromArgb(a, r, g, b);
}

/// <summary>
/// Maximum value blending with alpha
/// </summary>
private static Color BlendColorsMaximum(Color source, Color target, int alpha)
{
    float alphaFactor = alpha / 255.0f;
    int r = Math.Max(source.R, (int)(target.R * alphaFactor));
    int g = Math.Max(source.G, (int)(target.G * alphaFactor));
    int b = Math.Max(source.B, (int)(target.B * alphaFactor));
    int a = Math.Max(source.A, (int)(target.A * alphaFactor));
    
    return Color.FromArgb(a, r, g, b);
}

/// <summary>
/// 50/50 blending with alpha
/// </summary>
private static Color BlendColorsFiftyFifty(Color source, Color target, int alpha)
{
    float alphaFactor = alpha / 255.0f;
    int r = (source.R + (int)(target.R * alphaFactor)) / 2;
    int g = (source.G + (int)(target.G * alphaFactor)) / 2;
    int b = (source.B + (int)(target.B * alphaFactor)) / 2;
    int a = (source.A + (int)(target.A * alphaFactor)) / 2;
    
    return Color.FromArgb(a, r, g, b);
}

/// <summary>
/// Subtractive blending type 1 with alpha
/// </summary>
private static Color BlendColorsSubtractive1(Color source, Color target, int alpha)
{
    float alphaFactor = alpha / 255.0f;
    int r = Math.Max(0, source.R - (int)(target.R * alphaFactor));
    int g = Math.Max(0, source.G - (int)(target.G * alphaFactor));
    int b = Math.Max(0, source.B - (int)(target.B * alphaFactor));
    int a = Math.Max(0, source.A - (int)(target.A * alphaFactor));
    
    return Color.FromArgb(a, r, g, b);
}

/// <summary>
/// Subtractive blending type 2 with alpha
/// </summary>
private static Color BlendColorsSubtractive2(Color source, Color target, int alpha)
{
    float alphaFactor = alpha / 255.0f;
    int r = Math.Max(0, (int)(target.R * alphaFactor) - source.R);
    int g = Math.Max(0, (int)(target.G * alphaFactor) - source.G);
    int b = Math.Max(0, (int)(target.B * alphaFactor) - source.B);
    int a = Math.Max(0, (int)(target.A * alphaFactor) - source.A);
    
    return Color.FromArgb(a, r, g, b);
}

/// <summary>
/// Multiply blending with alpha
/// </summary>
private static Color BlendColorsMultiply(Color source, Color target, int alpha)
{
    float alphaFactor = alpha / 255.0f;
    int r = (source.R * (int)(target.R * alphaFactor)) / 255;
    int g = (source.G * (int)(target.G * alphaFactor)) / 255;
    int b = (source.B * (int)(target.B * alphaFactor)) / 255;
    int a = (source.A * (int)(target.A * alphaFactor)) / 255;
    
    return Color.FromArgb(a, r, g, b);
}

/// <summary>
/// Adjustable blending with custom output value
/// </summary>
private static Color BlendColorsAdjustable(Color source, Color target, int alpha, int outputValue)
{
    float alphaFactor = alpha / 255.0f;
    float outputFactor = outputValue / 255.0f;
    
    int r = (int)((source.R + target.R * alphaFactor) * outputFactor);
    int g = (int)((source.G + target.G * alphaFactor) * outputFactor);
    int b = (int)((source.B + target.B * alphaFactor) * outputFactor);
    int a = (int)((source.A + target.A * alphaFactor) * outputFactor);
    
    r = Math.Max(0, Math.Min(255, r));
    g = Math.Max(0, Math.Min(255, g));
    b = Math.Max(0, Math.Min(255, b));
    a = Math.Max(0, Math.Min(255, a));
    
    return Color.FromArgb(a, r, g, b);
}

/// <summary>
/// XOR blending with alpha
/// </summary>
private static Color BlendColorsXor(Color source, Color target, int alpha)
{
    float alphaFactor = alpha / 255.0f;
    int r = source.R ^ (int)(target.R * alphaFactor);
    int g = source.G ^ (int)(target.G * alphaFactor);
    int b = source.B ^ (int)(target.B * alphaFactor);
    int a = source.A ^ (int)(target.A * alphaFactor);
    
    return Color.FromArgb(a, r, g, b);
}

/// <summary>
/// Minimum value blending with alpha
/// </summary>
private static Color BlendColorsMinimum(Color source, Color target, int alpha)
{
    float alphaFactor = alpha / 255.0f;
    int r = Math.Min(source.R, (int)(target.R * alphaFactor));
    int g = Math.Min(source.G, (int)(target.G * alphaFactor));
    int b = Math.Min(source.B, (int)(target.B * alphaFactor));
    int a = Math.Min(source.A, (int)(target.A * alphaFactor));
    
    return Color.FromArgb(a, r, g, b);
}
```

### Configuration Validation

```csharp
public override bool ValidateConfiguration()
{
    if (Alpha < 0 || Alpha > 255) return false;
    if (OutputValue < 0 || OutputValue > 255) return false;
    if (Intensity < 0.0f || Intensity > 10.0f) return false;
    
    return true;
}
```

### Preset Methods

```csharp
/// <summary>
/// Load a standard replace mode preset
/// </summary>
public void LoadReplacePreset()
{
    BlendMode = LineBlendMode.Replace;
    Alpha = 255;
    OutputValue = 128;
    ApplyGlobally = true;
    _isInitialized = false;
}

/// <summary>
/// Load an additive blending preset
/// </summary>
public void LoadAdditivePreset()
{
    BlendMode = LineBlendMode.Additive;
    Alpha = 128;
    OutputValue = 128;
    ApplyGlobally = true;
    _isInitialized = false;
}

/// <summary>
/// Load a 50/50 blending preset
/// </summary>
public void LoadFiftyFiftyPreset()
{
    BlendMode = LineBlendMode.FiftyFiftyBlend;
    Alpha = 255;
    OutputValue = 128;
    ApplyGlobally = true;
    _isInitialized = false;
}

/// <summary>
/// Load an adjustable blend preset
/// </summary>
public void LoadAdjustablePreset()
{
    BlendMode = LineBlendMode.AdjustableBlend;
    Alpha = 128;
    OutputValue = 192;
    ApplyGlobally = true;
    _isInitialized = false;
}

/// <summary>
/// Load a maximum blend preset
/// </summary>
public void LoadMaximumPreset()
{
    BlendMode = LineBlendMode.MaximumBlend;
    Alpha = 255;
    OutputValue = 128;
    ApplyGlobally = true;
    _isInitialized = false;
}
```

### Utility Methods

```csharp
/// <summary>
/// Get the current global settings as a string
/// </summary>
public string GetGlobalSettings()
{
    return $"Mode: {_globalLineBlendMode}, Alpha: {_globalAlpha}, Output: {_globalOutputValue}";
}

/// <summary>
/// Check if the effect is currently affecting global settings
/// </summary>
public bool IsAffectingGlobalSettings()
{
    return Enabled && ApplyGlobally;
}

/// <summary>
/// Get the current configuration as a string
/// </summary>
public string GetCurrentConfiguration()
{
    return $"Mode: {BlendMode}, Alpha: {Alpha}, Output: {OutputValue}, Global: {ApplyGlobally}";
}

/// <summary>
/// Reset the effect to initial state
/// </summary>
public void Reset()
{
    _isInitialized = false;
    _previousConfig = new LineModeConfiguration(BlendMode, Alpha, OutputValue, ApplyGlobally);
}

/// <summary>
/// Get effect execution statistics
/// </summary>
public string GetExecutionStats()
{
    return $"Initialized: {_isInitialized}, Global Mode: {_globalLineBlendMode}, Global Alpha: {_globalAlpha}";
}
```

## Usage Examples

### Basic Line Mode Configuration

```csharp
var lineMode = new LineModeEffectsNode();
lineMode.BlendMode = LineBlendMode.Additive;
lineMode.Alpha = 128;
lineMode.ApplyGlobally = true;
```

### Adjustable Blend Mode

```csharp
var lineMode = new LineModeEffectsNode();
lineMode.LoadAdjustablePreset();
lineMode.OutputValue = 200;
lineMode.Intensity = 0.8f;
```

### Custom Blending

```csharp
var lineMode = new LineModeEffectsNode();
lineMode.BlendMode = LineBlendMode.MultiplyBlend;
lineMode.Alpha = 64;
lineMode.ApplyGlobally = true;
```

## Technical Details

The Line Mode effect is a system-level configuration effect that controls how line-based visualizations are rendered throughout the AVS system. Key features include:

- **Global Settings**: Changes affect all line-based effects in the system
- **Multiple Blending Modes**: 10 different blending algorithms for various visual effects
- **Alpha Control**: Precise control over blending intensity
- **Adjustable Blend**: Custom output value control for fine-tuning
- **Real-time Updates**: Configuration changes are applied immediately

The effect doesn't render visual content itself but provides the rendering pipeline configuration that other line-based effects use. This makes it essential for creating consistent visual styles across multiple effects and for fine-tuning the overall appearance of line-based visualizations.

The blending modes range from simple operations like replace and additive to complex mathematical operations like XOR and adjustable blending, providing artists with a wide range of creative possibilities for line rendering.
