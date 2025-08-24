# NFClear Effects

## Overview

The NFClear effect clears the screen with a specified color when audio beats are detected. It can be configured to clear every N beats and supports both replace and blend modes. This effect is useful for creating rhythmic visual breaks, clearing accumulated effects, or providing visual punctuation synchronized with music.

## C# Implementation

### Properties

```csharp
/// <summary>
/// Whether the effect is enabled
/// </summary>
public bool Enabled { get; set; } = true;

/// <summary>
/// Clear color (default: white)
/// </summary>
public Color ClearColor { get; set; } = Color.White;

/// <summary>
/// Whether to blend with existing pixels instead of replacing
/// </summary>
public bool BlendEnabled { get; set; } = false;

/// <summary>
/// Number of beats to wait before clearing (1-100)
/// </summary>
public int BeatCount { get; set; } = 1;

/// <summary>
/// Effect intensity multiplier
/// </summary>
public float Intensity { get; set; } = 1.0f;
```

### Private Fields

```csharp
/// <summary>
/// Current beat counter
/// </summary>
private int _currentBeatCount = 0;

/// <summary>
/// Delay counter for timing
/// </summary>
private int _delayCounter = 0;

/// <summary>
/// Whether the effect has been initialized
/// </summary>
private bool _isInitialized = false;

/// <summary>
/// Whether a clear operation is pending
/// </summary>
private bool _clearPending = false;
```

### Constructor

```csharp
public NFClearEffectsNode()
{
    _currentBeatCount = 0;
    _delayCounter = 0;
    _isInitialized = false;
    _clearPending = false;
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

    // Handle beat detection
    if (audioFeatures.IsBeat)
    {
        HandleBeatDetection();
    }

    // Check if clear is pending
    if (_clearPending)
    {
        ApplyClear(imageBuffer);
        _clearPending = false;
    }

    // Update delay counter
    _delayCounter++;
}

/// <summary>
/// Initialize the effect
/// </summary>
private void InitializeEffect()
{
    _currentBeatCount = 0;
    _delayCounter = 0;
    _clearPending = false;
    _isInitialized = true;
}

/// <summary>
/// Handle beat detection
/// </summary>
private void HandleBeatDetection()
{
    _currentBeatCount++;
    
    // Check if we should clear on this beat
    if (_currentBeatCount >= BeatCount)
    {
        _clearPending = true;
        _currentBeatCount = 0;
    }
    
    // Reset delay counter
    _delayCounter = 0;
}

/// <summary>
/// Apply the clear effect to the image buffer
/// </summary>
private void ApplyClear(ImageBuffer imageBuffer)
{
    int width = imageBuffer.Width;
    int height = imageBuffer.Height;
    
    if (BlendEnabled)
    {
        // Blend with existing pixels
        ApplyBlendedClear(imageBuffer);
    }
    else
    {
        // Replace all pixels
        ApplyReplacementClear(imageBuffer);
    }
}

/// <summary>
/// Apply replacement clear (overwrite all pixels)
/// </summary>
private void ApplyReplacementClear(ImageBuffer imageBuffer)
{
    int width = imageBuffer.Width;
    int height = imageBuffer.Height;
    
    // Fill entire buffer with clear color
    for (int y = 0; y < height; y++)
    {
        for (int x = 0; x < width; x++)
        {
            imageBuffer.SetPixel(x, y, ClearColor);
        }
    }
}

/// <summary>
/// Apply blended clear (50/50 blend with existing pixels)
/// </summary>
private void ApplyBlendedClear(ImageBuffer imageBuffer)
{
    int width = imageBuffer.Width;
    int height = imageBuffer.Height;
    
    for (int y = 0; y < height; y++)
    {
        for (int x = 0; x < width; x++)
        {
            Color existingPixel = imageBuffer.GetPixel(x, y);
            Color blendedPixel = BlendPixels(existingPixel, ClearColor);
            imageBuffer.SetPixel(x, y, blendedPixel);
        }
    }
}

/// <summary>
/// Blend two pixels using 50/50 averaging
/// </summary>
private Color BlendPixels(Color pixel1, Color pixel2)
{
    int r = (pixel1.R + pixel2.R) / 2;
    int g = (pixel1.G + pixel2.G) / 2;
    int b = (pixel1.B + pixel2.B) / 2;
    int a = (pixel1.A + pixel2.A) / 2;
    
    return Color.FromArgb(a, r, g, b);
}
```

### Optimized Processing Methods

```csharp
/// <summary>
/// Apply optimized replacement clear using bulk operations
/// </summary>
private void ApplyOptimizedReplacementClear(ImageBuffer imageBuffer)
{
    int width = imageBuffer.Width;
    int height = imageBuffer.Height;
    
    // Process multiple pixels at once for better performance
    for (int y = 0; y < height; y++)
    {
        for (int x = 0; x < width; x += 4)
        {
            // Process 4 pixels at once
            if (x + 3 < width)
            {
                imageBuffer.SetPixel(x, y, ClearColor);
                imageBuffer.SetPixel(x + 1, y, ClearColor);
                imageBuffer.SetPixel(x + 2, y, ClearColor);
                imageBuffer.SetPixel(x + 3, y, ClearColor);
            }
            else
            {
                // Process remaining pixels
                for (int i = 0; i < width - x; i++)
                {
                    imageBuffer.SetPixel(x + i, y, ClearColor);
                }
            }
        }
    }
}

/// <summary>
/// Apply optimized blended clear using bulk operations
/// </summary>
private void ApplyOptimizedBlendedClear(ImageBuffer imageBuffer)
{
    int width = imageBuffer.Width;
    int height = imageBuffer.Height;
    
    // Process multiple pixels at once for better performance
    for (int y = 0; y < height; y++)
    {
        for (int x = 0; x < width; x += 4)
        {
            if (x + 3 < width)
            {
                // Process 4 pixels at once
                Color pixel1 = imageBuffer.GetPixel(x, y);
                Color pixel2 = imageBuffer.GetPixel(x + 1, y);
                Color pixel3 = imageBuffer.GetPixel(x + 2, y);
                Color pixel4 = imageBuffer.GetPixel(x + 3, y);
                
                Color blended1 = BlendPixels(pixel1, ClearColor);
                Color blended2 = BlendPixels(pixel2, ClearColor);
                Color blended3 = BlendPixels(pixel3, ClearColor);
                Color blended4 = BlendPixels(pixel4, ClearColor);
                
                imageBuffer.SetPixel(x, y, blended1);
                imageBuffer.SetPixel(x + 1, y, blended2);
                imageBuffer.SetPixel(x + 2, y, blended3);
                imageBuffer.SetPixel(x + 3, y, blended4);
            }
            else
            {
                // Process remaining pixels
                for (int i = 0; i < width - x; i++)
                {
                    Color existingPixel = imageBuffer.GetPixel(x + i, y);
                    Color blendedPixel = BlendPixels(existingPixel, ClearColor);
                    imageBuffer.SetPixel(x + i, y, blendedPixel);
                }
            }
        }
    }
}
```

### Configuration Validation

```csharp
public override bool ValidateConfiguration()
{
    if (BeatCount < 1 || BeatCount > 100) return false;
    if (Intensity < 0.0f || Intensity > 10.0f) return false;
    
    return true;
}
```

### Preset Methods

```csharp
/// <summary>
/// Load a basic beat clear preset
/// </summary>
public void LoadBasicBeatClearPreset()
{
    ClearColor = Color.White;
    BlendEnabled = false;
    BeatCount = 1;
    Intensity = 1.0f;
    _isInitialized = false;
}

/// <summary>
/// Load a every 4 beats clear preset
/// </summary>
public void LoadEveryFourBeatsPreset()
{
    ClearColor = Color.Black;
    BlendEnabled = false;
    BeatCount = 4;
    Intensity = 1.0f;
    _isInitialized = false;
}

/// <summary>
/// Load a blended clear preset
/// </summary>
public void LoadBlendedClearPreset()
{
    ClearColor = Color.White;
    BlendEnabled = true;
    BeatCount = 2;
    Intensity = 1.0f;
    _isInitialized = false;
}

/// <summary>
/// Load a color clear preset
/// </summary>
public void LoadColorClearPreset()
{
    ClearColor = Color.Red;
    BlendEnabled = false;
    BeatCount = 8;
    Intensity = 1.0f;
    _isInitialized = false;
}

/// <summary>
/// Load a slow clear preset
/// </summary>
public void LoadSlowClearPreset()
{
    ClearColor = Color.Blue;
    BlendEnabled = true;
    BeatCount = 16;
    Intensity = 1.0f;
    _isInitialized = false;
}
```

### Utility Methods

```csharp
/// <summary>
/// Get the current clear status
/// </summary>
public string GetClearStatus()
{
    return $"Beat Count: {_currentBeatCount}/{BeatCount}, Delay: {_delayCounter}, Clear Pending: {_clearPending}";
}

/// <summary>
/// Check if the effect is currently waiting for beats
/// </summary>
public bool IsWaitingForBeats()
{
    return Enabled && _currentBeatCount < BeatCount;
}

/// <summary>
/// Check if a clear operation is pending
/// </summary>
public bool IsClearPending()
{
    return _clearPending;
}

/// <summary>
/// Get the next clear beat count
/// </summary>
public int GetNextClearBeat()
{
    return BeatCount - _currentBeatCount;
}

/// <summary>
/// Force an immediate clear
/// </summary>
public void ForceClear()
{
    _clearPending = true;
    _currentBeatCount = 0;
    _delayCounter = 0;
}

/// <summary>
/// Reset the beat counter
/// </summary>
public void ResetBeatCounter()
{
    _currentBeatCount = 0;
    _delayCounter = 0;
}

/// <summary>
/// Get the clear color as a string
/// </summary>
public string GetClearColorString()
{
    return $"R:{ClearColor.R}, G:{ClearColor.G}, B:{ClearColor.B}, A:{ClearColor.A}";
}

/// <summary>
/// Reset the effect to initial state
/// </summary>
public void Reset()
{
    _isInitialized = false;
    _currentBeatCount = 0;
    _delayCounter = 0;
    _clearPending = false;
}

/// <summary>
/// Get effect execution statistics
/// </summary>
public string GetExecutionStats()
{
    return $"Initialized: {_isInitialized}, Beat Count: {_currentBeatCount}/{BeatCount}, Clear Pending: {_clearPending}";
}
```

## Usage Examples

### Basic Beat Clear

```csharp
var nfClear = new NFClearEffectsNode();
nfClear.ClearColor = Color.White;
nfClear.BlendEnabled = false;
nfClear.BeatCount = 1;
```

### Every 4 Beats Clear

```csharp
var nfClear = new NFClearEffectsNode();
nfClear.LoadEveryFourBeatsPreset();
nfClear.Intensity = 0.8f;
```

### Blended Clear Effect

```csharp
var nfClear = new NFClearEffectsNode();
nfClear.LoadBlendedClearPreset();
nfClear.ClearColor = Color.Cyan;
```

### Colorful Beat Clear

```csharp
var nfClear = new NFClearEffectsNode();
nfClear.LoadColorClearPreset();
nfClear.Intensity = 1.2f;
```

## Technical Details

The NFClear effect provides rhythmic screen clearing synchronized with audio beats. Key features include:

- **Beat Synchronization**: Clears the screen every N detected beats
- **Flexible Timing**: Configurable beat count from 1 to 100
- **Clear Modes**: Replace (overwrite) or blend (50/50 mix) with existing pixels
- **Custom Colors**: Any color can be used for clearing
- **Performance Optimized**: Bulk pixel processing for efficiency
- **Alpha Channel Safe**: Preserves transparency information

The effect works by counting audio beats and triggering a clear operation when the specified beat count is reached. The clear operation can either replace all pixels with the clear color or blend the clear color with existing pixels for a more subtle effect.

The beat counting system automatically resets after each clear operation, ensuring consistent timing. The effect is particularly useful for creating visual breaks in complex visualizations, clearing accumulated effects, or providing visual punctuation that matches the musical rhythm.

The blending mode creates a softer effect by mixing the clear color with existing pixels rather than completely replacing them, which can be useful for creating fade effects or maintaining some visual continuity.
