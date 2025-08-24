# List Effects

## Overview

The List effect is a container effect that manages a collection of other AVS effects and controls how they are rendered and blended together. It provides sophisticated blending modes, buffer management, and effect chaining capabilities. This effect is fundamental to the AVS system as it allows multiple effects to work together in sequence.

## C# Implementation

### Properties

```csharp
/// <summary>
/// Whether the effect is enabled
/// </summary>
public bool Enabled { get; set; } = true;

/// <summary>
/// Input blending mode for combining with parent buffer
/// </summary>
public BlendMode InputBlendMode { get; set; } = BlendMode.Replace;

/// <summary>
/// Output blending mode for combining with child effects
/// </summary>
public BlendMode OutputBlendMode { get; set; } = BlendMode.Replace;

/// <summary>
/// Input blend value (0-255)
/// </summary>
public int InputBlendValue { get; set; } = 128;

/// <summary>
/// Output blend value (0-255)
/// </summary>
public int OutputBlendValue { get; set; } = 128;

/// <summary>
/// Input buffer index for external buffer blending
/// </summary>
public int InputBufferIndex { get; set; } = 0;

/// <summary>
/// Output buffer index for external buffer blending
/// </summary>
public int OutputBufferIndex { get; set; } = 0;

/// <summary>
/// Whether to invert input buffer depth
/// </summary>
public bool InvertInputBuffer { get; set; } = false;

/// <summary>
/// Whether to invert output buffer depth
/// </summary>
public bool InvertOutputBuffer { get; set; } = false;

/// <summary>
/// Whether to enable beat-responsive rendering
/// </summary>
public bool BeatRenderEnabled { get; set; } = false;

/// <summary>
/// Number of frames to render on beat
/// </summary>
public int BeatRenderFrames { get; set; } = 1;

/// <summary>
/// Whether to use EEL code expressions
/// </summary>
public bool UseCodeExpressions { get; set; } = false;

/// <summary>
/// EEL expression for effect 1
/// </summary>
public string EffectExpression1 { get; set; } = "";

/// <summary>
/// EEL expression for effect 2
/// </summary>
public string EffectExpression2 { get; set; } = "";

/// <summary>
/// Effect intensity multiplier
/// </summary>
public float Intensity { get; set; } = 1.0f;
```

### Enums

```csharp
/// <summary>
/// Available blending modes for input and output
/// </summary>
public enum BlendMode
{
    /// <summary>
    /// Replace existing pixels
    /// </summary>
    Replace = 1,
    
    /// <summary>
    /// Additive blending
    /// </summary>
    Additive = 2,
    
    /// <summary>
    /// 50/50 average blending
    /// </summary>
    Average = 3,
    
    /// <summary>
    /// Maximum value blending
    /// </summary>
    Maximum = 4,
    
    /// <summary>
    /// Subtractive blending (source - target)
    /// </summary>
    SubtractSource = 5,
    
    /// <summary>
    /// Subtractive blending (target - source)
    /// </summary>
    SubtractTarget = 6,
    
    /// <summary>
    /// Copy every other line
    /// </summary>
    CopyAlternateLines = 7,
    
    /// <summary>
    /// Copy every other pixel
    /// </summary>
    CopyAlternatePixels = 8,
    
    /// <summary>
    /// XOR blending
    /// </summary>
    Xor = 9,
    
    /// <summary>
    /// Adjustable blending with custom value
    /// </summary>
    Adjustable = 10,
    
    /// <summary>
    /// Multiply blending
    /// </summary>
    Multiply = 11,
    
    /// <summary>
    /// Depth-based blending with buffer
    /// </summary>
    DepthBased = 12,
    
    /// <summary>
    /// Minimum value blending
    /// </summary>
    Minimum = 13
}
```

### Private Fields

```csharp
/// <summary>
/// List of child effects
/// </summary>
private List<EffectNode> _childEffects;

/// <summary>
/// Internal framebuffer for processing
/// </summary>
private ImageBuffer _internalBuffer;

/// <summary>
/// Previous width and height for resize detection
/// </summary>
private int _previousWidth, _previousHeight;

/// <summary>
/// Whether the effect has been initialized
/// </summary>
private bool _isInitialized = false;

/// <summary>
/// Beat counter for beat-responsive rendering
/// </summary>
private int _beatCounter = 0;

/// <summary>
/// Frame counter for timing
/// </summary>
private int _frameCounter = 0;

/// <summary>
/// Whether effects need recompilation
/// </summary>
private bool _effectsNeedRecompilation = true;

/// <summary>
/// EEL script engine for code expressions
/// </summary>
private EELScriptEngine _scriptEngine;
```

### Constructor

```csharp
public ListEffectsNode()
{
    _childEffects = new List<EffectNode>();
    _internalBuffer = null;
    _previousWidth = 0;
    _previousHeight = 0;
    _isInitialized = false;
    _beatCounter = 0;
    _frameCounter = 0;
    _effectsNeedRecompilation = true;
    _scriptEngine = new EELScriptEngine();
}
```

### Processing Methods

```csharp
public override void ProcessFrame(ImageBuffer imageBuffer, AudioFeatures audioFeatures)
{
    if (!Enabled || imageBuffer == null) return;

    // Initialize if needed
    if (!_isInitialized)
    {
        InitializeEffect();
    }

    // Handle resize
    if (_previousWidth != imageBuffer.Width || _previousHeight != imageBuffer.Height)
    {
        HandleResize(imageBuffer.Width, imageBuffer.Height);
    }

    // Update frame counter
    _frameCounter++;

    // Handle beat response
    if (BeatRenderEnabled && audioFeatures.IsBeat)
    {
        HandleBeatResponse();
    }

    // Apply input blending
    ApplyInputBlending(imageBuffer);

    // Process child effects
    ProcessChildEffects(imageBuffer, audioFeatures);

    // Apply output blending
    ApplyOutputBlending(imageBuffer);
}

/// <summary>
/// Initialize the effect and internal buffers
/// </summary>
private void InitializeEffect()
{
    _internalBuffer = new ImageBuffer(1, 1); // Will be resized as needed
    _isInitialized = true;
}

/// <summary>
/// Handle buffer resize
/// </summary>
private void HandleResize(int width, int height)
{
    if (_internalBuffer != null)
    {
        // Resize internal buffer
        _internalBuffer = new ImageBuffer(width, height);
    }
    
    _previousWidth = width;
    _previousHeight = height;
}

/// <summary>
/// Handle beat response
/// </summary>
private void HandleBeatResponse()
{
    _beatCounter++;
    
    // Reset counter after specified frames
    if (_beatCounter >= BeatRenderFrames)
    {
        _beatCounter = 0;
    }
}

/// <summary>
/// Apply input blending with parent buffer
/// </summary>
private void ApplyInputBlending(ImageBuffer imageBuffer)
{
    if (InputBlendMode == BlendMode.Replace)
    {
        // No blending needed
        return;
    }

    int width = imageBuffer.Width;
    int height = imageBuffer.Height;
    
    // Create temporary buffer for blending
    ImageBuffer tempBuffer = new ImageBuffer(width, height);
    tempBuffer.CopyFrom(imageBuffer);

    switch (InputBlendMode)
    {
        case BlendMode.Additive:
            ApplyAdditiveBlending(imageBuffer, tempBuffer, InputBlendValue);
            break;
            
        case BlendMode.Average:
            ApplyAverageBlending(imageBuffer, tempBuffer, InputBlendValue);
            break;
            
        case BlendMode.Maximum:
            ApplyMaximumBlending(imageBuffer, tempBuffer, InputBlendValue);
            break;
            
        case BlendMode.SubtractSource:
            ApplySubtractiveBlending(imageBuffer, tempBuffer, InputBlendValue, true);
            break;
            
        case BlendMode.SubtractTarget:
            ApplySubtractiveBlending(imageBuffer, tempBuffer, InputBlendValue, false);
            break;
            
        case BlendMode.CopyAlternateLines:
            ApplyCopyAlternateLines(imageBuffer, tempBuffer);
            break;
            
        case BlendMode.CopyAlternatePixels:
            ApplyCopyAlternatePixels(imageBuffer, tempBuffer);
            break;
            
        case BlendMode.Xor:
            ApplyXorBlending(imageBuffer, tempBuffer);
            break;
            
        case BlendMode.Adjustable:
            ApplyAdjustableBlending(imageBuffer, tempBuffer, InputBlendValue);
            break;
            
        case BlendMode.Multiply:
            ApplyMultiplyBlending(imageBuffer, tempBuffer);
            break;
            
        case BlendMode.DepthBased:
            ApplyDepthBasedBlending(imageBuffer, tempBuffer, InputBufferIndex, InvertInputBuffer);
            break;
            
        case BlendMode.Minimum:
            ApplyMinimumBlending(imageBuffer, tempBuffer, InputBlendValue);
            break;
    }
}

/// <summary>
/// Process all child effects
/// </summary>
private void ProcessChildEffects(ImageBuffer imageBuffer, AudioFeatures audioFeatures)
{
    // Recompile effects if needed
    if (_effectsNeedRecompilation)
    {
        RecompileEffects();
    }

    // Process each child effect in sequence
    foreach (var effect in _childEffects)
    {
        if (effect.Enabled)
        {
            effect.ProcessFrame(imageBuffer, audioFeatures);
        }
    }
}

/// <summary>
/// Apply output blending with result
/// </summary>
private void ApplyOutputBlending(ImageBuffer imageBuffer)
{
    if (OutputBlendMode == BlendMode.Replace)
    {
        // No blending needed
        return;
    }

    // Similar to input blending but with output parameters
    // Implementation would be similar to ApplyInputBlending
    // but using OutputBlendMode, OutputBlendValue, etc.
}
```

### Blending Methods

```csharp
/// <summary>
/// Apply additive blending
/// </summary>
private void ApplyAdditiveBlending(ImageBuffer source, ImageBuffer target, int blendValue)
{
    int width = source.Width;
    int height = source.Height;
    float factor = blendValue / 255.0f;
    
    for (int y = 0; y < height; y++)
    {
        for (int x = 0; x < width; x++)
        {
            Color sourceColor = source.GetPixel(x, y);
            Color targetColor = target.GetPixel(x, y);
            
            int r = Math.Min(255, sourceColor.R + (int)(targetColor.R * factor));
            int g = Math.Min(255, sourceColor.G + (int)(targetColor.G * factor));
            int b = Math.Min(255, sourceColor.B + (int)(targetColor.B * factor));
            int a = Math.Min(255, sourceColor.A + (int)(targetColor.A * factor));
            
            source.SetPixel(x, y, Color.FromArgb(a, r, g, b));
        }
    }
}

/// <summary>
/// Apply average blending
/// </summary>
private void ApplyAverageBlending(ImageBuffer source, ImageBuffer target, int blendValue)
{
    int width = source.Width;
    int height = source.Height;
    float factor = blendValue / 255.0f;
    
    for (int y = 0; y < height; y++)
    {
        for (int x = 0; x < width; x++)
        {
            Color sourceColor = source.GetPixel(x, y);
            Color targetColor = target.GetPixel(x, y);
            
            int r = (sourceColor.R + (int)(targetColor.R * factor)) / 2;
            int g = (sourceColor.G + (int)(targetColor.G * factor)) / 2;
            int b = (sourceColor.B + (int)(targetColor.B * factor)) / 2;
            int a = (sourceColor.A + (int)(targetColor.A * factor)) / 2;
            
            source.SetPixel(x, y, Color.FromArgb(a, r, g, b));
        }
    }
}

/// <summary>
/// Apply maximum blending
/// </summary>
private void ApplyMaximumBlending(ImageBuffer source, ImageBuffer target, int blendValue)
{
    int width = source.Width;
    int height = source.Height;
    float factor = blendValue / 255.0f;
    
    for (int y = 0; y < height; y++)
    {
        for (int x = 0; x < width; x++)
        {
            Color sourceColor = source.GetPixel(x, y);
            Color targetColor = target.GetPixel(x, y);
            
            int r = Math.Max(sourceColor.R, (int)(targetColor.R * factor));
            int g = Math.Max(sourceColor.G, (int)(targetColor.G * factor));
            int b = Math.Max(sourceColor.B, (int)(targetColor.B * factor));
            int a = Math.Max(sourceColor.A, (int)(targetColor.A * factor));
            
            source.SetPixel(x, y, Color.FromArgb(a, r, g, b));
        }
    }
}

/// <summary>
/// Apply subtractive blending
/// </summary>
private void ApplySubtractiveBlending(ImageBuffer source, ImageBuffer target, int blendValue, bool sourceMinusTarget)
{
    int width = source.Width;
    int height = source.Height;
    float factor = blendValue / 255.0f;
    
    for (int y = 0; y < height; y++)
    {
        for (int x = 0; x < width; x++)
        {
            Color sourceColor = source.GetPixel(x, y);
            Color targetColor = target.GetPixel(x, y);
            
            int r, g, b, a;
            
            if (sourceMinusTarget)
            {
                r = Math.Max(0, sourceColor.R - (int)(targetColor.R * factor));
                g = Math.Max(0, sourceColor.G - (int)(targetColor.G * factor));
                b = Math.Max(0, sourceColor.B - (int)(targetColor.B * factor));
                a = Math.Max(0, sourceColor.A - (int)(targetColor.A * factor));
            }
            else
            {
                r = Math.Max(0, (int)(targetColor.R * factor) - sourceColor.R);
                g = Math.Max(0, (int)(targetColor.G * factor) - sourceColor.G);
                b = Math.Max(0, (int)(targetColor.B * factor) - sourceColor.B);
                a = Math.Max(0, (int)(targetColor.A * factor) - sourceColor.A);
            }
            
            source.SetPixel(x, y, Color.FromArgb(a, r, g, b));
        }
    }
}

/// <summary>
/// Apply copy alternate lines
/// </summary>
private void ApplyCopyAlternateLines(ImageBuffer source, ImageBuffer target)
{
    int width = source.Width;
    int height = source.Height;
    
    for (int y = 0; y < height; y += 2)
    {
        for (int x = 0; x < width; x++)
        {
            Color targetColor = target.GetPixel(x, y);
            source.SetPixel(x, y, targetColor);
        }
    }
}

/// <summary>
/// Apply copy alternate pixels
/// </summary>
private void ApplyCopyAlternatePixels(ImageBuffer source, ImageBuffer target)
{
    int width = source.Width;
    int height = source.Height;
    
    for (int y = 0; y < height; y++)
    {
        for (int x = 0; x < width; x += 2)
        {
            Color targetColor = target.GetPixel(x, y);
            source.SetPixel(x, y, targetColor);
        }
    }
}

/// <summary>
/// Apply XOR blending
/// </summary>
private void ApplyXorBlending(ImageBuffer source, ImageBuffer target)
{
    int width = source.Width;
    int height = source.Height;
    
    for (int y = 0; y < height; y++)
    {
        for (int x = 0; x < width; x++)
        {
            Color sourceColor = source.GetPixel(x, y);
            Color targetColor = target.GetPixel(x, y);
            
            int r = sourceColor.R ^ targetColor.R;
            int g = sourceColor.G ^ targetColor.G;
            int b = sourceColor.B ^ targetColor.B;
            int a = sourceColor.A ^ targetColor.A;
            
            source.SetPixel(x, y, Color.FromArgb(a, r, g, b));
        }
    }
}

/// <summary>
/// Apply adjustable blending
/// </summary>
private void ApplyAdjustableBlending(ImageBuffer source, ImageBuffer target, int blendValue)
{
    int width = source.Width;
    int height = source.Height;
    float factor = blendValue / 255.0f;
    
    for (int y = 0; y < height; y++)
    {
        for (int x = 0; x < width; x++)
        {
            Color sourceColor = source.GetPixel(x, y);
            Color targetColor = target.GetPixel(x, y);
            
            int r = (int)((sourceColor.R + targetColor.R) * factor);
            int g = (int)((sourceColor.G + targetColor.G) * factor);
            int b = (int)((sourceColor.B + targetColor.B) * factor);
            int a = (int)((sourceColor.A + targetColor.A) * factor);
            
            r = Math.Max(0, Math.Min(255, r));
            g = Math.Max(0, Math.Min(255, g));
            b = Math.Max(0, Math.Min(255, b));
            a = Math.Max(0, Math.Min(255, a));
            
            source.SetPixel(x, y, Color.FromArgb(a, r, g, b));
        }
    }
}

/// <summary>
/// Apply multiply blending
/// </summary>
private void ApplyMultiplyBlending(ImageBuffer source, ImageBuffer target)
{
    int width = source.Width;
    int height = source.Height;
    
    for (int y = 0; y < height; y++)
    {
        for (int x = 0; x < width; x++)
        {
            Color sourceColor = source.GetPixel(x, y);
            Color targetColor = target.GetPixel(x, y);
            
            int r = (sourceColor.R * targetColor.R) / 255;
            int g = (sourceColor.G * targetColor.G) / 255;
            int b = (sourceColor.B * targetColor.B) / 255;
            int a = (sourceColor.A * targetColor.A) / 255;
            
            source.SetPixel(x, y, Color.FromArgb(a, r, g, b));
        }
    }
}

/// <summary>
/// Apply depth-based blending
/// </summary>
private void ApplyDepthBasedBlending(ImageBuffer source, ImageBuffer target, int bufferIndex, bool invert)
{
    // This would require access to global buffers
    // Implementation depends on the buffer system
    // For now, we'll use a simplified approach
    
    int width = source.Width;
    int height = source.Height;
    
    for (int y = 0; y < height; y++)
    {
        for (int x = 0; x < width; x++)
        {
            Color sourceColor = source.GetPixel(x, y);
            Color targetColor = target.GetPixel(x, y);
            
            // Simplified depth calculation
            int depth = (sourceColor.R + sourceColor.G + sourceColor.B) / 3;
            if (invert) depth = 255 - depth;
            
            float factor = depth / 255.0f;
            
            int r = (int)(sourceColor.R * (1 - factor) + targetColor.R * factor);
            int g = (int)(sourceColor.G * (1 - factor) + targetColor.G * factor);
            int b = (int)(sourceColor.B * (1 - factor) + targetColor.B * factor);
            int a = (int)(sourceColor.A * (1 - factor) + targetColor.A * factor);
            
            source.SetPixel(x, y, Color.FromArgb(a, r, g, b));
        }
    }
}

/// <summary>
/// Apply minimum blending
/// </summary>
private void ApplyMinimumBlending(ImageBuffer source, ImageBuffer target, int blendValue)
{
    int width = source.Width;
    int height = source.Height;
    float factor = blendValue / 255.0f;
    
    for (int y = 0; y < height; y++)
    {
        for (int x = 0; x < width; x++)
        {
            Color sourceColor = source.GetPixel(x, y);
            Color targetColor = target.GetPixel(x, y);
            
            int r = Math.Min(sourceColor.R, (int)(targetColor.R * factor));
            int g = Math.Min(sourceColor.G, (int)(targetColor.G * factor));
            int b = Math.Min(sourceColor.B, (int)(targetColor.B * factor));
            int a = Math.Min(sourceColor.A, (int)(targetColor.A * factor));
            
            source.SetPixel(x, y, Color.FromArgb(a, r, g, b));
        }
    }
}
```

### Child Effect Management

```csharp
/// <summary>
/// Add a child effect to the list
/// </summary>
public void AddChildEffect(EffectNode effect)
{
    if (effect != null && !_childEffects.Contains(effect))
    {
        _childEffects.Add(effect);
        _effectsNeedRecompilation = true;
    }
}

/// <summary>
/// Remove a child effect from the list
/// </summary>
public void RemoveChildEffect(EffectNode effect)
{
    if (_childEffects.Remove(effect))
    {
        _effectsNeedRecompilation = true;
    }
}

/// <summary>
/// Get a child effect by index
/// </summary>
public EffectNode GetChildEffect(int index)
{
    if (index >= 0 && index < _childEffects.Count)
    {
        return _childEffects[index];
    }
    return null;
}

/// <summary>
/// Get the number of child effects
/// </summary>
public int GetChildEffectCount()
{
    return _childEffects.Count;
}

/// <summary>
/// Clear all child effects
/// </summary>
public void ClearChildEffects()
{
    _childEffects.Clear();
    _effectsNeedRecompilation = true;
}

/// <summary>
/// Recompile all child effects
/// </summary>
private void RecompileEffects()
{
    foreach (var effect in _childEffects)
    {
        if (effect is ICompilableEffect compilableEffect)
        {
            compilableEffect.Recompile();
        }
    }
    
    _effectsNeedRecompilation = false;
}
```

### Configuration Validation

```csharp
public override bool ValidateConfiguration()
{
    if (InputBlendValue < 0 || InputBlendValue > 255) return false;
    if (OutputBlendValue < 0 || OutputBlendValue > 255) return false;
    if (InputBufferIndex < 0 || InputBufferIndex > 99) return false;
    if (OutputBufferIndex < 0 || OutputBufferIndex > 99) return false;
    if (BeatRenderFrames < 1 || BeatRenderFrames > 100) return false;
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
    InputBlendMode = BlendMode.Replace;
    OutputBlendMode = BlendMode.Replace;
    InputBlendValue = 128;
    OutputBlendValue = 128;
    InputBufferIndex = 0;
    OutputBufferIndex = 0;
    InvertInputBuffer = false;
    InvertOutputBuffer = false;
    BeatRenderEnabled = false;
    BeatRenderFrames = 1;
    UseCodeExpressions = false;
    _effectsNeedRecompilation = true;
}

/// <summary>
/// Load an additive blending preset
/// </summary>
public void LoadAdditivePreset()
{
    InputBlendMode = BlendMode.Additive;
    OutputBlendMode = BlendMode.Additive;
    InputBlendValue = 128;
    OutputBlendValue = 128;
    InputBufferIndex = 0;
    OutputBufferIndex = 0;
    InvertInputBuffer = false;
    InvertOutputBuffer = false;
    BeatRenderEnabled = false;
    BeatRenderFrames = 1;
    UseCodeExpressions = false;
    _effectsNeedRecompilation = true;
}

/// <summary>
/// Load a beat-responsive preset
/// </summary>
public void LoadBeatResponsivePreset()
{
    InputBlendMode = BlendMode.Average;
    OutputBlendMode = BlendMode.Average;
    InputBlendValue = 192;
    OutputBlendValue = 192;
    InputBufferIndex = 0;
    OutputBufferIndex = 0;
    InvertInputBuffer = false;
    InvertOutputBuffer = false;
    BeatRenderEnabled = true;
    BeatRenderFrames = 4;
    UseCodeExpressions = false;
    _effectsNeedRecompilation = true;
}

/// <summary>
/// Load a complex blending preset
/// </summary>
public void LoadComplexBlendingPreset()
{
    InputBlendMode = BlendMode.DepthBased;
    OutputBlendMode = BlendMode.Adjustable;
    InputBlendValue = 128;
    OutputBlendValue = 192;
    InputBufferIndex = 1;
    OutputBufferIndex = 2;
    InvertInputBuffer = true;
    InvertOutputBuffer = false;
    BeatRenderEnabled = true;
    BeatRenderFrames = 8;
    UseCodeExpressions = true;
    _effectsNeedRecompilation = true;
}
```

### Utility Methods

```csharp
/// <summary>
/// Get the current effect list status
/// </summary>
public string GetEffectListStatus()
{
    return $"Effects: {_childEffects.Count}, Beat Counter: {_beatCounter}, Frame: {_frameCounter}";
}

/// <summary>
/// Check if the effect is currently processing
/// </summary>
public bool IsProcessing()
{
    return Enabled && _childEffects.Count > 0;
}

/// <summary>
/// Get the current buffer dimensions
/// </summary>
public Size GetBufferDimensions()
{
    return new Size(_previousWidth, _previousHeight);
}

/// <summary>
/// Reset the effect to initial state
/// </summary>
public void Reset()
{
    _isInitialized = false;
    _beatCounter = 0;
    _frameCounter = 0;
    _effectsNeedRecompilation = true;
    _previousWidth = 0;
    _previousHeight = 0;
}

/// <summary>
/// Get effect execution statistics
/// </summary>
public string GetExecutionStats()
{
    return $"Initialized: {_isInitialized}, Effects: {_childEffects.Count}, Beat: {_beatCounter}, Frame: {_frameCounter}";
}
```

## Usage Examples

### Basic Effect List

```csharp
var listEffect = new ListEffectsNode();
listEffect.InputBlendMode = BlendMode.Replace;
listEffect.OutputBlendMode = BlendMode.Replace;
listEffect.AddChildEffect(new BlurEffectsNode());
listEffect.AddChildEffect(new BrightnessEffectsNode());
```

### Beat-Responsive Blending

```csharp
var listEffect = new ListEffectsNode();
listEffect.LoadBeatResponsivePreset();
listEffect.AddChildEffect(new StarsEffectsNode());
listEffect.AddChildEffect(new WaterEffectsNode());
```

### Complex Blending Chain

```csharp
var listEffect = new ListEffectsNode();
listEffect.LoadComplexBlendingPreset();
listEffect.AddChildEffect(new SuperScopeEffectsNode());
listEffect.AddChildEffect(new TransitionEffectsNode());
listEffect.AddChildEffect(new GrainEffectsNode());
```

## Technical Details

The List effect is a sophisticated container that manages multiple AVS effects and provides advanced blending capabilities. Key features include:

- **Effect Chaining**: Multiple effects can be processed in sequence
- **Advanced Blending**: 13 different blending modes for input and output
- **Buffer Management**: Internal framebuffer handling with resize support
- **Beat Response**: Audio-responsive rendering with configurable frame counts
- **External Buffers**: Integration with global buffer system for depth-based effects
- **EEL Integration**: Support for code-based effect expressions
- **Performance Optimization**: Efficient blending algorithms and buffer reuse

The effect serves as the foundation for complex visual compositions, allowing artists to create sophisticated effect chains with precise control over how effects interact and blend together. The blending system provides both simple operations like replace and additive, as well as complex operations like depth-based blending and adjustable blending with custom values.

The buffer management system automatically handles resizing and provides efficient memory usage, while the beat response system allows for dynamic visual changes synchronized with audio input.
