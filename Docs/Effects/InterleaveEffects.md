# Interleave Effects

## Overview

The Interleave effect creates alternating patterns by filling every other pixel or line with a specified color, creating a striped or checkerboard appearance. This effect can be used to create various visual patterns and can respond to audio input for dynamic effects.

## C# Implementation

### Properties

```csharp
/// <summary>
/// Whether the effect is enabled
/// </summary>
public bool Enabled { get; set; } = true;

/// <summary>
/// Primary X offset for interleaving pattern
/// </summary>
public int XOffset { get; set; } = 0;

/// <summary>
/// Primary Y offset for interleaving pattern
/// </summary>
public int YOffset { get; set; } = 0;

/// <summary>
/// Secondary X offset for complex patterns
/// </summary>
public int XOffset2 { get; set; } = 0;

/// <summary>
/// Secondary Y offset for complex patterns
/// </summary>
public int YOffset2 { get; set; } = 0;

/// <summary>
/// Beat duration for audio-responsive patterns
/// </summary>
public int BeatDuration { get; set; } = 1;

/// <summary>
/// Whether to respond to audio beats
/// </summary>
public bool BeatResponse { get; set; } = false;

/// <summary>
/// Whether to blend with existing pixels
/// </summary>
public bool BlendEnabled { get; set; } = false;

/// <summary>
/// Whether to use 50/50 blending
/// </summary>
public bool BlendAverage { get; set; } = false;

/// <summary>
/// Color to use for interleaving
/// </summary>
public Color InterleaveColor { get; set; } = Color.Black;

/// <summary>
/// Effect intensity multiplier
/// </summary>
public float Intensity { get; set; } = 1.0f;
```

### Private Fields

```csharp
/// <summary>
/// Current X position for animation
/// </summary>
private double _currentX;

/// <summary>
/// Current Y position for animation
/// </summary>
private double _currentY;

/// <summary>
/// Frame counter for timing
/// </summary>
private int _frameCounter = 0;

/// <summary>
/// Beat counter for audio response
/// </summary>
private int _beatCounter = 0;

/// <summary>
/// Whether the effect has been initialized
/// </summary>
private bool _isInitialized = false;
```

### Constructor

```csharp
public InterleaveEffectsNode()
{
    _currentX = XOffset;
    _currentY = YOffset;
    _isInitialized = false;
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

    // Update frame counter
    _frameCounter++;

    // Handle beat response
    if (BeatResponse && audioFeatures.IsBeat)
    {
        HandleBeatResponse();
    }

    // Update current positions
    UpdatePositions();

    // Apply interleaving effect
    ApplyInterleaving(imageBuffer);
}

/// <summary>
/// Initialize the effect with default values
/// </summary>
private void InitializeEffect()
{
    _currentX = XOffset;
    _currentY = YOffset;
    _frameCounter = 0;
    _beatCounter = 0;
    _isInitialized = true;
}

/// <summary>
/// Handle audio beat response
/// </summary>
private void HandleBeatResponse()
{
    _beatCounter++;
    
    // Update positions based on beat duration
    if (_beatCounter >= BeatDuration)
    {
        _currentX = XOffset2;
        _currentY = YOffset2;
        _beatCounter = 0;
    }
    else
    {
        _currentX = XOffset;
        _currentY = YOffset;
    }
}

/// <summary>
/// Update current positions for animation
/// </summary>
private void UpdatePositions()
{
    // Smooth interpolation between primary and secondary positions
    if (BeatResponse)
    {
        double progress = (double)_beatCounter / BeatDuration;
        _currentX = XOffset + (XOffset2 - XOffset) * progress;
        _currentY = YOffset + (YOffset2 - YOffset) * progress;
    }
    else
    {
        _currentX = XOffset;
        _currentY = YOffset;
    }
}

/// <summary>
/// Apply the interleaving effect to the image buffer
/// </summary>
private void ApplyInterleaving(ImageBuffer imageBuffer)
{
    int width = imageBuffer.Width;
    int height = imageBuffer.Height;
    
    // Calculate interleaving pattern
    int xPattern = Math.Max(1, Math.Abs((int)_currentX));
    int yPattern = Math.Max(1, Math.Abs((int)_currentY));
    
    // Create output buffer
    ImageBuffer outputBuffer = new ImageBuffer(width, height);
    
    // Copy original image
    outputBuffer.CopyFrom(imageBuffer);
    
    // Apply horizontal interleaving
    if (xPattern > 1)
    {
        ApplyHorizontalInterleaving(outputBuffer, xPattern);
    }
    
    // Apply vertical interleaving
    if (yPattern > 1)
    {
        ApplyVerticalInterleaving(outputBuffer, yPattern);
    }
    
    // Copy result back to input buffer
    imageBuffer.CopyFrom(outputBuffer);
}

/// <summary>
/// Apply horizontal interleaving pattern
/// </summary>
private void ApplyHorizontalInterleaving(ImageBuffer buffer, int pattern)
{
    int width = buffer.Width;
    int height = buffer.Height;
    
    for (int y = 0; y < height; y++)
    {
        for (int x = 0; x < width; x++)
        {
            // Check if this pixel should be interleaved
            if ((x % pattern) == 0)
            {
                Color currentPixel = buffer.GetPixel(x, y);
                Color newPixel = InterleaveColor;
                
                if (BlendEnabled)
                {
                    // Additive blending
                    newPixel = BlendPixelsAdditive(currentPixel, InterleaveColor);
                }
                else if (BlendAverage)
                {
                    // 50/50 blending
                    newPixel = BlendPixelsAverage(currentPixel, InterleaveColor);
                }
                
                buffer.SetPixel(x, y, newPixel);
            }
        }
    }
}

/// <summary>
/// Apply vertical interleaving pattern
/// </summary>
private void ApplyVerticalInterleaving(ImageBuffer buffer, int pattern)
{
    int width = buffer.Width;
    int height = buffer.Height;
    
    for (int y = 0; y < height; y++)
    {
        // Check if this line should be interleaved
        if ((y % pattern) == 0)
        {
            for (int x = 0; x < width; x++)
            {
                Color currentPixel = buffer.GetPixel(x, y);
                Color newPixel = InterleaveColor;
                
                if (BlendEnabled)
                {
                    // Additive blending
                    newPixel = BlendPixelsAdditive(currentPixel, InterleaveColor);
                }
                else if (BlendAverage)
                {
                    // 50/50 blending
                    newPixel = BlendPixelsAverage(currentPixel, InterleaveColor);
                }
                
                buffer.SetPixel(x, y, newPixel);
            }
        }
    }
}

/// <summary>
/// Blend two pixels using additive blending
/// </summary>
private Color BlendPixelsAdditive(Color pixel1, Color pixel2)
{
    int r = Math.Min(255, pixel1.R + pixel2.R);
    int g = Math.Min(255, pixel1.G + pixel2.G);
    int b = Math.Min(255, pixel1.B + pixel2.B);
    int a = Math.Min(255, pixel1.A + pixel2.A);
    
    return Color.FromArgb(a, r, g, b);
}

/// <summary>
/// Blend two pixels using 50/50 averaging
/// </summary>
private Color BlendPixelsAverage(Color pixel1, Color pixel2)
{
    int r = (pixel1.R + pixel2.R) / 2;
    int g = (pixel1.G + pixel2.G) / 2;
    int b = (pixel1.B + pixel2.B) / 2;
    int a = (pixel1.A + pixel2.A) / 2;
    
    return Color.FromArgb(a, r, g, b);
}
```

### Configuration Validation

```csharp
public override bool ValidateConfiguration()
{
    if (XOffset < 0 || XOffset > 64) return false;
    if (YOffset < 0 || YOffset > 64) return false;
    if (XOffset2 < 0 || XOffset2 > 64) return false;
    if (YOffset2 < 0 || YOffset2 > 64) return false;
    if (BeatDuration < 1 || BeatDuration > 64) return false;
    if (Intensity < 0.0f || Intensity > 10.0f) return false;
    
    return true;
}
```

### Preset Methods

```csharp
/// <summary>
/// Load a horizontal stripe pattern
/// </summary>
public void LoadHorizontalStripesPreset()
{
    XOffset = 2;
    YOffset = 0;
    XOffset2 = 2;
    YOffset2 = 0;
    BeatDuration = 1;
    BeatResponse = false;
    BlendEnabled = false;
    BlendAverage = false;
    InterleaveColor = Color.White;
    _isInitialized = false;
}

/// <summary>
/// Load a vertical stripe pattern
/// </summary>
public void LoadVerticalStripesPreset()
{
    XOffset = 0;
    YOffset = 2;
    XOffset2 = 0;
    YOffset2 = 2;
    BeatDuration = 1;
    BeatResponse = false;
    BlendEnabled = false;
    BlendAverage = false;
    InterleaveColor = Color.White;
    _isInitialized = false;
}

/// <summary>
/// Load a checkerboard pattern
/// </summary>
public void LoadCheckerboardPreset()
{
    XOffset = 2;
    YOffset = 2;
    XOffset2 = 2;
    YOffset2 = 2;
    BeatDuration = 1;
    BeatResponse = false;
    BlendEnabled = false;
    BlendAverage = false;
    InterleaveColor = Color.White;
    _isInitialized = false;
}

/// <summary>
/// Load a beat-responsive pattern
/// </summary>
public void LoadBeatResponsivePreset()
{
    XOffset = 1;
    YOffset = 1;
    XOffset2 = 4;
    YOffset2 = 4;
    BeatDuration = 4;
    BeatResponse = true;
    BlendEnabled = true;
    BlendAverage = false;
    InterleaveColor = Color.Red;
    _isInitialized = false;
}

/// <summary>
/// Load a pulsing pattern
/// </summary>
public void LoadPulsingPreset()
{
    XOffset = 1;
    YOffset = 1;
    XOffset2 = 8;
    YOffset2 = 8;
    BeatDuration = 8;
    BeatResponse = true;
    BlendEnabled = false;
    BlendAverage = true;
    InterleaveColor = Color.Cyan;
    _isInitialized = false;
}
```

### Utility Methods

```csharp
/// <summary>
/// Get the current interleaving pattern as a string
/// </summary>
public string GetCurrentPattern()
{
    return $"X: {_currentX:F1}, Y: {_currentY:F1}, Beat: {_beatCounter}/{BeatDuration}";
}

/// <summary>
/// Check if the effect is currently interleaving
/// </summary>
public bool IsInterleaving()
{
    return Enabled && (_currentX > 0 || _currentY > 0);
}

/// <summary>
/// Get the effective pattern size
/// </summary>
public Size GetPatternSize()
{
    return new Size(
        Math.Max(1, Math.Abs((int)_currentX)),
        Math.Max(1, Math.Abs((int)_currentY))
    );
}

/// <summary>
/// Reset the effect to initial state
/// </summary>
public void Reset()
{
    _isInitialized = false;
    _frameCounter = 0;
    _beatCounter = 0;
    _currentX = XOffset;
    _currentY = YOffset;
}

/// <summary>
/// Get effect execution statistics
/// </summary>
public string GetExecutionStats()
{
    return $"Frame: {_frameCounter}, Beat: {_beatCounter}, Pattern: {GetCurrentPattern()}";
}
```

## Usage Examples

### Basic Horizontal Stripes

```csharp
var interleave = new InterleaveEffectsNode();
interleave.XOffset = 2;
interleave.YOffset = 0;
interleave.InterleaveColor = Color.White;
interleave.BlendEnabled = false;
```

### Beat-Responsive Checkerboard

```csharp
var interleave = new InterleaveEffectsNode();
interleave.LoadBeatResponsivePreset();
interleave.Intensity = 0.8f;
```

### Animated Pattern

```csharp
var interleave = new InterleaveEffectsNode();
interleave.XOffset = 1;
interleave.XOffset2 = 8;
interleave.YOffset = 1;
interleave.YOffset2 = 8;
interleave.BeatDuration = 16;
interleave.BeatResponse = true;
interleave.BlendEnabled = true;
```

## Technical Details

The Interleave effect works by creating alternating patterns based on pixel or line positions. The effect can be configured with:

- **Primary Offsets**: Basic interleaving pattern (XOffset, YOffset)
- **Secondary Offsets**: Alternative pattern for animation (XOffset2, YOffset2)
- **Beat Response**: Automatic switching between patterns based on audio input
- **Blending Modes**: Replace, additive, or 50/50 blending with existing pixels
- **Pattern Animation**: Smooth interpolation between primary and secondary patterns

The effect is highly efficient as it only processes pixels that need to be modified, making it suitable for real-time applications. The pattern generation uses modulo arithmetic to determine which pixels should be interleaved, creating consistent and predictable visual results.
