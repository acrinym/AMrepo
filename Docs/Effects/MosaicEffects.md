# Mosaic Effects

## Overview

The Mosaic effect creates a pixelated, mosaic-like appearance by reducing the resolution of the image and then scaling it back up. This effect can be used to create retro-style visuals, reduce detail for artistic purposes, or create beat-responsive pixelation effects. The effect supports smooth transitions between different quality levels and various blending modes.

## C# Implementation

### Properties

```csharp
/// <summary>
/// Whether the effect is enabled
/// </summary>
public bool Enabled { get; set; } = true;

/// <summary>
/// Base quality level (1-100, lower = more pixelated)
/// </summary>
public int Quality { get; set; } = 50;

/// <summary>
/// Beat-responsive quality level (1-100)
/// </summary>
public int BeatQuality { get; set; } = 50;

/// <summary>
/// Whether to blend with original pixels using additive blending
/// </summary>
public bool BlendEnabled { get; set; } = false;

/// <summary>
/// Whether to blend with original pixels using 50/50 averaging
/// </summary>
public bool BlendAverage { get; set; } = false;

/// <summary>
/// Whether to respond to audio beats
/// </summary>
public bool BeatResponse { get; set; } = false;

/// <summary>
/// Duration of beat effect in frames
/// </summary>
public int BeatDuration { get; set; } = 15;

/// <summary>
/// Effect intensity multiplier
/// </summary>
public float Intensity { get; set; } = 1.0f;
```

### Private Fields

```csharp
/// <summary>
/// Current quality level being applied
/// </summary>
private int _currentQuality;

/// <summary>
/// Frame counter for beat effect
/// </summary>
private int _beatFrameCounter = 0;

/// <summary>
/// Whether the effect has been initialized
/// </summary>
private bool _isInitialized = false;

/// <summary>
/// Previous width and height for resize detection
/// </summary>
private int _previousWidth, _previousHeight;

/// <summary>
/// Pre-calculated step increments for efficient processing
/// </summary>
private int _stepXIncrement, _stepYIncrement;
```

### Constructor

```csharp
public MosaicEffectsNode()
{
    _currentQuality = Quality;
    _beatFrameCounter = 0;
    _isInitialized = false;
    _previousWidth = 0;
    _previousHeight = 0;
    _stepXIncrement = 0;
    _stepYIncrement = 0;
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

    // Handle beat response
    if (BeatResponse && audioFeatures.IsBeat)
    {
        HandleBeatResponse();
    }

    // Update current quality
    UpdateQuality();

    // Apply mosaic effect
    if (_currentQuality < 100)
    {
        ApplyMosaicEffect(imageBuffer);
    }
}

/// <summary>
/// Initialize the effect
/// </summary>
private void InitializeEffect()
{
    _currentQuality = Quality;
    _beatFrameCounter = 0;
    _isInitialized = true;
}

/// <summary>
/// Handle buffer resize
/// </summary>
private void HandleResize(int width, int height)
{
    _previousWidth = width;
    _previousHeight = height;
    
    // Recalculate step increments
    CalculateStepIncrements();
}

/// <summary>
/// Calculate step increments for mosaic processing
/// </summary>
private void CalculateStepIncrements()
{
    if (_currentQuality > 0)
    {
        _stepXIncrement = (_previousWidth * 65536) / _currentQuality;
        _stepYIncrement = (_previousHeight * 65536) / _currentQuality;
    }
    else
    {
        _stepXIncrement = _stepYIncrement = 0;
    }
}

/// <summary>
/// Handle beat response
/// </summary>
private void HandleBeatResponse()
{
    _beatFrameCounter = BeatDuration;
}

/// <summary>
/// Update current quality level
/// </summary>
private void UpdateQuality()
{
    if (_beatFrameCounter > 0)
    {
        _beatFrameCounter--;
        
        if (_beatFrameCounter > 0)
        {
            // Smooth transition between quality levels
            int qualityDifference = Math.Abs(Quality - BeatQuality);
            int stepSize = qualityDifference / BeatDuration;
            
            if (BeatQuality > Quality)
            {
                _currentQuality = Math.Max(BeatQuality, _currentQuality - stepSize);
            }
            else
            {
                _currentQuality = Math.Min(BeatQuality, _currentQuality + stepSize);
            }
        }
        else
        {
            _currentQuality = Quality;
        }
    }
    else
    {
        _currentQuality = Quality;
    }
    
    // Recalculate step increments if quality changed
    if (_previousWidth > 0 && _previousHeight > 0)
    {
        CalculateStepIncrements();
    }
}

/// <summary>
/// Apply the mosaic effect to the image buffer
/// </summary>
private void ApplyMosaicEffect(ImageBuffer imageBuffer)
{
    int width = imageBuffer.Width;
    int height = imageBuffer.Height;
    
    // Create output buffer
    ImageBuffer outputBuffer = new ImageBuffer(width, height);
    
    // Calculate step increments for current quality
    int stepX = (_stepXIncrement >> 17);
    int stepY = (_stepYIncrement >> 17);
    
    // Ensure minimum step size
    if (stepX < 1) stepX = 1;
    if (stepY < 1) stepY = 1;
    
    // Process each pixel
    for (int y = 0; y < height; y++)
    {
        int sourceY = (y / stepY) * stepY;
        if (sourceY >= height) sourceY = height - 1;
        
        for (int x = 0; x < width; x++)
        {
            int sourceX = (x / stepX) * stepX;
            if (sourceX >= width) sourceX = width - 1;
            
            // Get source pixel
            Color sourcePixel = imageBuffer.GetPixel(sourceX, sourceY);
            Color originalPixel = imageBuffer.GetPixel(x, y);
            
            // Apply blending if enabled
            Color finalPixel = sourcePixel;
            
            if (BlendEnabled)
            {
                finalPixel = BlendPixelsAdditive(originalPixel, sourcePixel);
            }
            else if (BlendAverage)
            {
                finalPixel = BlendPixelsAverage(originalPixel, sourcePixel);
            }
            
            outputBuffer.SetPixel(x, y, finalPixel);
        }
    }
    
    // Copy result back to input buffer
    imageBuffer.CopyFrom(outputBuffer);
}
```

### Blending Methods

```csharp
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
    if (Quality < 1 || Quality > 100) return false;
    if (BeatQuality < 1 || BeatQuality > 100) return false;
    if (BeatDuration < 1 || BeatDuration > 100) return false;
    if (Intensity < 0.0f || Intensity > 10.0f) return false;
    
    return true;
}
```

### Preset Methods

```csharp
/// <summary>
/// Load a light pixelation preset
/// </summary>
public void LoadLightPixelationPreset()
{
    Quality = 80;
    BeatQuality = 60;
    BeatDuration = 10;
    BeatResponse = false;
    BlendEnabled = false;
    BlendAverage = false;
    _isInitialized = false;
}

/// <summary>
/// Load a heavy pixelation preset
/// </summary>
public void LoadHeavyPixelationPreset()
{
    Quality = 20;
    BeatQuality = 10;
    BeatDuration = 20;
    BeatResponse = false;
    BlendEnabled = false;
    BlendAverage = false;
    _isInitialized = false;
}

/// <summary>
/// Load a beat-responsive preset
/// </summary>
public void LoadBeatResponsivePreset()
{
    Quality = 70;
    BeatQuality = 30;
    BeatDuration = 15;
    BeatResponse = true;
    BlendEnabled = true;
    BlendAverage = false;
    _isInitialized = false;
}

/// <summary>
/// Load a smooth blending preset
/// </summary>
public void LoadSmoothBlendingPreset()
{
    Quality = 60;
    BeatQuality = 40;
    BeatDuration = 25;
    BeatResponse = true;
    BlendEnabled = false;
    BlendAverage = true;
    _isInitialized = false;
}

/// <summary>
/// Load a retro gaming preset
/// </summary>
public void LoadRetroGamingPreset()
{
    Quality = 16;
    BeatQuality = 8;
    BeatDuration = 30;
    BeatResponse = true;
    BlendEnabled = false;
    BlendAverage = false;
    _isInitialized = false;
}
```

### Utility Methods

```csharp
/// <summary>
/// Get the current mosaic status
/// </summary>
public string GetMosaicStatus()
{
    return $"Quality: {_currentQuality}, Beat Frames: {_beatFrameCounter}, Step X: {_stepXIncrement >> 17}, Step Y: {_stepYIncrement >> 17}";
}

/// <summary>
/// Check if the effect is currently pixelating
/// </summary>
public bool IsPixelating()
{
    return Enabled && _currentQuality < 100;
}

/// <summary>
/// Get the effective block size
/// </summary>
public Size GetBlockSize()
{
    if (_currentQuality >= 100) return new Size(1, 1);
    
    int stepX = Math.Max(1, (_stepXIncrement >> 17));
    int stepY = Math.Max(1, (_stepYIncrement >> 17));
    
    return new Size(stepX, stepY);
}

/// <summary>
/// Get the current quality as a percentage
/// </summary>
public float GetQualityPercentage()
{
    return (_currentQuality / 100.0f) * 100.0f;
}

/// <summary>
/// Reset the effect to initial state
/// </summary>
public void Reset()
{
    _isInitialized = false;
    _beatFrameCounter = 0;
    _currentQuality = Quality;
    _previousWidth = 0;
    _previousHeight = 0;
    _stepXIncrement = 0;
    _stepYIncrement = 0;
}

/// <summary>
/// Get effect execution statistics
/// </summary>
public string GetExecutionStats()
{
    return $"Initialized: {_isInitialized}, Quality: {_currentQuality}, Beat Frames: {_beatFrameCounter}, Block Size: {GetBlockSize()}";
}
```

## Usage Examples

### Basic Mosaic Effect

```csharp
var mosaic = new MosaicEffectsNode();
mosaic.Quality = 30;
mosaic.BlendEnabled = false;
mosaic.Intensity = 1.0f;
```

### Beat-Responsive Pixelation

```csharp
var mosaic = new MosaicEffectsNode();
mosaic.LoadBeatResponsivePreset();
mosaic.Intensity = 0.8f;
```

### Retro Style Effect

```csharp
var mosaic = new MosaicEffectsNode();
mosaic.LoadRetroGamingPreset();
mosaic.Intensity = 1.2f;
```

### Smooth Quality Transitions

```csharp
var mosaic = new MosaicEffectsNode();
mosaic.Quality = 90;
mosaic.BeatQuality = 20;
mosaic.BeatDuration = 50;
mosaic.BeatResponse = true;
mosaic.BlendAverage = true;
```

## Technical Details

The Mosaic effect works by reducing the effective resolution of the image and then scaling it back up, creating a pixelated appearance. Key features include:

- **Quality Control**: Quality levels from 1-100 control the degree of pixelation
- **Beat Response**: Automatic quality changes synchronized with audio input
- **Smooth Transitions**: Gradual quality changes over multiple frames
- **Blending Modes**: Additive, 50/50 average, or replace blending with original pixels
- **Efficient Processing**: Pre-calculated step increments for optimal performance
- **Dynamic Block Sizing**: Automatic block size calculation based on quality and dimensions

The effect uses fixed-point arithmetic (16.16 format) for precise step calculations, ensuring smooth visual results even with small quality values. The beat response system allows for dynamic visual changes that can create interesting rhythmic effects when synchronized with music.

The mosaic algorithm works by dividing the image into blocks and using a single pixel color for each block, then scaling the result back to the original dimensions. This creates the characteristic pixelated appearance while maintaining the overall image structure.

The effect is particularly useful for creating retro-style visuals, reducing detail for artistic purposes, or adding dynamic pixelation effects that respond to audio input.
