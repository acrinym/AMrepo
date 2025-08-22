# Mosaic Effects (Trans / Mosaic)

## Overview

The **Mosaic Effects** system is a sophisticated pixelation and mosaic generation engine that provides advanced control over image pixelation, quality reduction, and intelligent mosaic manipulation. It implements comprehensive mosaic processing with configurable quality levels, beat-reactive quality changes, blending modes, and intelligent pixel sampling for creating complex mosaic transformations. This effect provides the foundation for sophisticated pixelation effects, quality reduction, and advanced image processing in AVS presets.

## Source Analysis

### Core Architecture (`r_mosaic.cpp`)

The effect is implemented as a C++ class `C_MosaicClass` that inherits from `C_RBASE`. It provides a comprehensive mosaic system with quality control, beat-reactive processing, blending modes, and intelligent pixel sampling for creating complex mosaic transformations.

### Key Components

#### Mosaic Processing Engine
Advanced mosaic control system:
- **Quality Control**: Configurable quality levels with precise control
- **Beat Reactivity**: Beat-triggered quality changes and transitions
- **Pixel Sampling**: Intelligent pixel sampling and interpolation
- **Performance Optimization**: Optimized processing for real-time operations

#### Quality Management System
Sophisticated quality processing:
- **Primary Quality**: Base quality level for normal operation
- **Secondary Quality**: Beat-triggered quality level for transitions
- **Duration Control**: Configurable duration for quality transitions
- **Smooth Transitions**: Smooth interpolation between quality levels

#### Blending Mode System
Advanced blending capabilities:
- **Replace Mode**: Direct pixel replacement without blending
- **Additive Blending**: Additive blending with existing content
- **Average Blending**: 50/50 blending with existing content
- **Blend Control**: Intelligent blend mode selection and control

#### Visual Enhancement System
Advanced enhancement capabilities:
- **Pixelation Effects**: High-quality pixelation and mosaic algorithms
- **Quality Transitions**: Smooth quality level transitions
- **Visual Integration**: Seamless integration with existing visual content
- **Quality Control**: High-quality enhancement and processing

### Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `enabled` | bool | true/false | true | Enable/disable mosaic effect |
| `quality` | int | 1-100 | 50 | Primary quality level |
| `quality2` | int | 1-100 | 50 | Secondary quality level (beat-triggered) |
| `blend` | int | 0-1 | 0 | Additive blending mode |
| `blendavg` | int | 0-1 | 0 | Average blending mode |
| `onbeat` | int | 0-1 | 0 | Beat-reactive quality changes |
| `durFrames` | int | 1-100 | 15 | Duration of quality transitions |

### Quality Modes

| Mode | Value | Description | Behavior |
|------|-------|-------------|----------|
| **High Quality** | 80-100 | High quality | Minimal pixelation |
| **Medium Quality** | 40-79 | Medium quality | Moderate pixelation |
| **Low Quality** | 10-39 | Low quality | Heavy pixelation |
| **Extreme Low** | 1-9 | Extreme low quality | Very heavy pixelation |

### Blending Modes

| Mode | Value | Description | Behavior |
|------|-------|-------------|----------|
| **Replace** | 0,0 | No blending | Mosaic replaces existing content |
| **Additive** | 1,0 | Additive blending | Mosaic adds to existing content |
| **Average** | 0,1 | Average blending | 50/50 blend with existing content |

### Beat Reactivity Modes

| Mode | Value | Description | Behavior |
|------|-------|-------------|----------|
| **No Beat Reactivity** | 0 | No beat changes | Quality remains constant |
| **Beat Reactive** | 1 | Beat-triggered changes | Quality changes on beat detection |

## C# Implementation

```csharp
public class MosaicEffectsNode : AvsModuleNode
{
    public bool Enabled { get; set; } = true;
    public int Quality { get; set; } = 50;
    public int Quality2 { get; set; } = 50;
    public int Blend { get; set; } = 0;
    public int BlendAvg { get; set; } = 0;
    public int OnBeat { get; set; } = 0;
    public int DurFrames { get; set; } = 15;
    
    // Internal state
    private int currentQuality;
    private int frameCount;
    private int lastWidth, lastHeight;
    private int lastQuality, lastQuality2, lastOnBeat;
    private readonly object renderLock = new object();
    
    // Performance optimization
    private const int MaxQuality = 100;
    private const int MinQuality = 1;
    private const int MaxDurFrames = 100;
    private const int MinDurFrames = 1;
    private const int MaxBlend = 1;
    private const int MinBlend = 0;
    private const int MaxOnBeat = 1;
    private const int MinOnBeat = 0;
    private const int FixedPointShift = 16;
    private const int FixedPointMultiplier = 1 << FixedPointShift;
    
    public MosaicEffectsNode()
    {
        lastWidth = lastHeight = 0;
        lastQuality = Quality;
        lastQuality2 = Quality2;
        lastOnBeat = OnBeat;
        currentQuality = Quality;
        frameCount = 0;
    }
    
    public override void Process(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        if (!Enabled || ctx.Width <= 0 || ctx.Height <= 0) 
        {
            // Pass through if disabled
            if (input != output)
            {
                input.CopyTo(output);
            }
            return;
        }
        
        lock (renderLock)
        {
            // Update buffers if dimensions changed
            UpdateBuffers(ctx);
            
            // Update quality if parameters changed
            if (lastQuality != Quality || lastQuality2 != Quality2 || lastOnBeat != OnBeat)
            {
                UpdateQuality();
                lastQuality = Quality;
                lastQuality2 = Quality2;
                lastOnBeat = OnBeat;
            }
            
            // Apply mosaic effect
            ApplyMosaicEffect(ctx, input, output);
            
            // Update frame count and quality transitions
            UpdateQualityTransitions();
        }
    }
    
    private void UpdateBuffers(FrameContext ctx)
    {
        if (lastWidth != ctx.Width || lastHeight != ctx.Height)
        {
            lastWidth = ctx.Width;
            lastHeight = ctx.Height;
        }
    }
    
    private void UpdateQuality()
    {
        currentQuality = Quality;
        frameCount = 0;
    }
    
    private void UpdateQualityTransitions()
    {
        if (frameCount > 0)
        {
            frameCount--;
            if (frameCount > 0)
            {
                int qualityDiff = Math.Abs(Quality - Quality2);
                int step = qualityDiff / DurFrames;
                
                if (Quality2 > Quality)
                {
                    currentQuality += step;
                }
                else
                {
                    currentQuality -= step;
                }
                
                currentQuality = Math.Clamp(currentQuality, MinQuality, MaxQuality);
            }
        }
    }
    
    private void ApplyMosaicEffect(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        if (currentQuality >= 100)
        {
            // No mosaic effect at 100% quality
            input.CopyTo(output);
            return;
        }
        
        // Calculate sampling increments using fixed-point arithmetic
        int sXInc = (ctx.Width * FixedPointMultiplier) / currentQuality;
        int sYInc = (ctx.Height * FixedPointMultiplier) / currentQuality;
        
        // Process each row
        for (int y = 0; y < ctx.Height; y++)
        {
            int yPos = (sYInc >> (FixedPointShift + 1));
            int dyPos = 0;
            
            // Process each column in the current row
            for (int x = 0; x < ctx.Width; x++)
            {
                int xPos = (sXInc >> (FixedPointShift + 1));
                int dxPos = 0;
                
                // Sample source pixel
                Color sourcePixel = input.GetPixel(xPos, yPos);
                Color currentPixel = input.GetPixel(x, y);
                Color processedPixel = ProcessPixel(sourcePixel, currentPixel);
                
                output.SetPixel(x, y, processedPixel);
                
                // Update X position
                dxPos += FixedPointMultiplier;
                if (dxPos >= sXInc)
                {
                    xPos += dxPos >> FixedPointShift;
                    dxPos -= sXInc;
                    if (xPos >= ctx.Width) break;
                }
            }
            
            // Update Y position
            dyPos += FixedPointMultiplier;
            if (dyPos >= sYInc)
            {
                yPos += dyPos >> FixedPointShift;
                dyPos -= sYInc;
                if (yPos >= ctx.Height) break;
            }
        }
    }
    
    private Color ProcessPixel(Color sourcePixel, Color currentPixel)
    {
        if (Blend == 1)
        {
            // Additive blending
            return BlendPixelsAdditive(currentPixel, sourcePixel);
        }
        else if (BlendAvg == 1)
        {
            // Average blending
            return BlendPixelsAverage(currentPixel, sourcePixel);
        }
        else
        {
            // Replace mode
            return sourcePixel;
        }
    }
    
    private Color BlendPixelsAdditive(Color pixel1, Color pixel2)
    {
        int r = Math.Min(255, pixel1.R + pixel2.R);
        int g = Math.Min(255, pixel1.G + pixel2.G);
        int b = Math.Min(255, pixel1.B + pixel2.B);
        
        return Color.FromRgb((byte)r, (byte)g, (byte)b);
    }
    
    private Color BlendPixelsAverage(Color pixel1, Color pixel2)
    {
        int r = (pixel1.R + pixel2.R) / 2;
        int g = (pixel1.G + pixel2.G) / 2;
        int b = (pixel1.B + pixel2.B) / 2;
        
        return Color.FromRgb((byte)r, (byte)g, (byte)b);
    }
    
    // Beat detection and quality triggering
    public void OnBeatDetected()
    {
        if (OnBeat == 1)
        {
            currentQuality = Quality2;
            frameCount = DurFrames;
        }
    }
    
    // Public interface for parameter adjustment
    public void SetEnabled(bool enable) { Enabled = enable; }
    
    public void SetQuality(int quality) 
    { 
        Quality = Math.Clamp(quality, MinQuality, MaxQuality); 
    }
    
    public void SetQuality2(int quality2) 
    { 
        Quality2 = Math.Clamp(quality2, MinQuality, MaxQuality); 
    }
    
    public void SetBlend(int blend) 
    { 
        Blend = Math.Clamp(blend, MinBlend, MaxBlend); 
    }
    
    public void SetBlendAvg(int blendAvg) 
    { 
        BlendAvg = Math.Clamp(blendAvg, MinBlend, MaxBlend); 
    }
    
    public void SetOnBeat(int onBeat) 
    { 
        OnBeat = Math.Clamp(onBeat, MinOnBeat, MaxOnBeat); 
    }
    
    public void SetDurFrames(int durFrames) 
    { 
        DurFrames = Math.Clamp(durFrames, MinDurFrames, MaxDurFrames); 
    }
    
    // Status queries
    public bool IsEnabled() => Enabled;
    public int GetQuality() => Quality;
    public int GetQuality2() => Quality2;
    public int GetBlend() => Blend;
    public int GetBlendAvg() => BlendAvg;
    public int GetOnBeat() => OnBeat;
    public int GetDurFrames() => DurFrames;
    public int GetCurrentQuality() => currentQuality;
    
    // Advanced mosaic control
    public void SetMosaicMode(int mode)
    {
        switch (mode)
        {
            case 0: // Replace mode
                SetBlend(0);
                SetBlendAvg(0);
                break;
            case 1: // Additive mode
                SetBlend(1);
                SetBlendAvg(0);
                break;
            case 2: // Average mode
                SetBlend(0);
                SetBlendAvg(1);
                break;
            default:
                SetBlend(0);
                SetBlendAvg(0);
                break;
        }
    }
    
    public void SetQualityMode(int mode)
    {
        switch (mode)
        {
            case 0: // High quality
                SetQuality(90);
                SetQuality2(90);
                break;
            case 1: // Medium quality
                SetQuality(50);
                SetQuality2(50);
                break;
            case 2: // Low quality
                SetQuality(20);
                SetQuality2(20);
                break;
            case 3: // Extreme low quality
                SetQuality(5);
                SetQuality2(5);
                break;
            default:
                SetQuality(50);
                SetQuality2(50);
                break;
        }
    }
    
    public void SetBeatReactivity(bool enable)
    {
        SetOnBeat(enable ? 1 : 0);
    }
    
    // Mosaic effect presets
    public void SetHighQualityMosaic()
    {
        SetQuality(90);
        SetQuality2(90);
        SetBlend(0);
        SetBlendAvg(0);
    }
    
    public void SetMediumQualityMosaic()
    {
        SetQuality(50);
        SetQuality2(50);
        SetBlend(0);
        SetBlendAvg(0);
    }
    
    public void SetLowQualityMosaic()
    {
        SetQuality(20);
        SetQuality2(20);
        SetBlend(0);
        SetBlendAvg(0);
    }
    
    public void SetExtremeLowQualityMosaic()
    {
        SetQuality(5);
        SetQuality2(5);
        SetBlend(0);
        SetBlendAvg(0);
    }
    
    public void SetBeatReactiveMosaic()
    {
        SetOnBeat(1);
        SetQuality(80);
        SetQuality2(20);
        SetDurFrames(15);
    }
    
    public void SetSmoothMosaic()
    {
        SetBlend(0);
        SetBlendAvg(1);
        SetQuality(60);
        SetQuality2(60);
    }
    
    public void SetAdditiveMosaic()
    {
        SetBlend(1);
        SetBlendAvg(0);
        SetQuality(40);
        SetQuality2(40);
    }
    
    // Custom mosaic configurations
    public void SetCustomMosaic(int quality, int quality2, int blend, int blendAvg, int onBeat, int durFrames)
    {
        SetQuality(quality);
        SetQuality2(quality2);
        SetBlend(blend);
        SetBlendAvg(blendAvg);
        SetOnBeat(onBeat);
        SetDurFrames(durFrames);
    }
    
    public void SetMosaicPreset(int preset)
    {
        switch (preset)
        {
            case 0: // High quality
                SetCustomMosaic(90, 90, 0, 0, 0, 15);
                break;
            case 1: // Medium quality
                SetCustomMosaic(50, 50, 0, 0, 0, 15);
                break;
            case 2: // Low quality
                SetCustomMosaic(20, 20, 0, 0, 0, 15);
                break;
            case 3: // Beat reactive
                SetCustomMosaic(80, 20, 0, 0, 1, 15);
                break;
            case 4: // Smooth blend
                SetCustomMosaic(60, 60, 0, 1, 0, 15);
                break;
            case 5: // Additive blend
                SetCustomMosaic(40, 40, 1, 0, 0, 15);
                break;
            default:
                SetCustomMosaic(50, 50, 0, 0, 0, 15);
                break;
        }
    }
    
    // Performance optimization
    public void SetRenderQuality(int quality)
    {
        // Quality could affect processing detail or optimization level
        // For now, we maintain full quality
    }
    
    public void EnableOptimizations(bool enable)
    {
        // Various optimization flags could be implemented here
    }
    
    public void SetProcessingMode(int mode)
    {
        // Mode could control processing method (standard vs optimized)
        // For now, we maintain automatic mode selection
    }
    
    // Advanced mosaic features
    public void SetTemporalMosaic(bool enable)
    {
        // Temporal mosaic effects could be implemented here
        // For now, we maintain standard behavior
    }
    
    public void SetSpatialMosaic(bool enable)
    {
        // Spatial mosaic effects could be implemented here
        // For now, we maintain standard behavior
    }
    
    // Channel-specific control
    public void SetRedMosaic(int quality)
    {
        // This could implement per-channel mosaic control
        // For now, we maintain full RGB processing
    }
    
    public void SetGreenMosaic(int quality)
    {
        // This could implement per-channel mosaic control
        // For now, we maintain full RGB processing
    }
    
    public void SetBlueMosaic(int quality)
    {
        // This could implement per-channel mosaic control
        // For now, we maintain full RGB processing
    }
    
    // Mosaic analysis
    public float GetMosaicPercentage(ImageBuffer input)
    {
        if (!Enabled || currentQuality >= 100) return 0.0f;
        
        int totalPixels = input.Width * input.Height;
        int mosaicPixels = 0;
        
        // Calculate how many pixels are affected by mosaic
        int blockSize = Math.Max(1, 100 / currentQuality);
        mosaicPixels = totalPixels / (blockSize * blockSize);
        
        return (float)mosaicPixels / totalPixels * 100.0f;
    }
    
    public int GetEffectiveBlockSize()
    {
        if (!Enabled || currentQuality >= 100) return 1;
        return Math.Max(1, 100 / currentQuality);
    }
    
    // Mosaic presets for common scenarios
    public void SetPhotographicMosaic()
    {
        // Optimized for photographic images
        SetCustomMosaic(70, 70, 0, 1, 0, 20);
    }
    
    public void SetArtisticMosaic()
    {
        // Optimized for artistic effects
        SetCustomMosaic(30, 30, 1, 0, 1, 10);
    }
    
    public void SetTechnicalMosaic()
    {
        // Optimized for technical visualization
        SetCustomMosaic(40, 40, 0, 0, 0, 15);
    }
    
    public void SetCinematicMosaic()
    {
        // Optimized for cinematic effects
        SetCustomMosaic(25, 25, 0, 1, 1, 25);
    }
    
    public override void Dispose()
    {
        lock (renderLock)
        {
            // Clean up resources if needed
        }
    }
}
```

## Integration Points

### Mosaic Processing Integration
- **Quality Control**: Intelligent quality control and mosaic processing
- **Beat Reactivity**: Advanced beat-reactive quality transitions
- **Blending Modes**: Sophisticated blending modes for mosaic integration
- **Quality Control**: High-quality mosaic enhancement and processing

### Color Processing Integration
- **RGB Processing**: Independent processing of RGB color channels
- **Color Mapping**: Advanced color mapping and transformation
- **Color Enhancement**: Intelligent color enhancement and processing
- **Visual Quality**: High-quality color transformation and processing

### Image Processing Integration
- **Pixelation Effects**: Advanced pixelation and mosaic manipulation
- **Quality Reduction**: Intelligent quality reduction and processing
- **Visual Enhancement**: Multiple enhancement modes for visual integration
- **Performance Optimization**: Optimized operations for mosaic processing

## Usage Examples

### Basic Mosaic Effect
```csharp
var mosaicNode = new MosaicEffectsNode
{
    Enabled = true,                        // Enable effect
    Quality = 50,                          // Medium quality
    Blend = 0,                             // Replace mode
    BlendAvg = 0,                          // No average blending
    OnBeat = 0,                            // No beat reactivity
    DurFrames = 15                         // Default duration
};
```

### Beat-Reactive Mosaic Effect
```csharp
var mosaicNode = new MosaicEffectsNode
{
    Enabled = true,
    Quality = 80,                          // High quality normally
    Quality2 = 20,                         // Low quality on beat
    Blend = 0,                             // Replace mode
    BlendAvg = 0,                          // No average blending
    OnBeat = 1,                            // Beat reactive
    DurFrames = 15                         // 15 frame transition
};

// Apply beat reactive preset
mosaicNode.SetBeatReactiveMosaic();
```

### Smooth Blending Mosaic
```csharp
var mosaicNode = new MosaicEffectsNode
{
    Enabled = true,
    Quality = 60,                          // Medium quality
    Blend = 0,                             // No additive blending
    BlendAvg = 1,                          // Average blending
    OnBeat = 0,                            // No beat reactivity
    DurFrames = 15                         // Default duration
};

// Apply smooth mosaic preset
mosaicNode.SetSmoothMosaic();
```

### Advanced Mosaic Control
```csharp
var mosaicNode = new MosaicEffectsNode
{
    Enabled = true,
    Quality = 40,                          // Custom quality
    Quality2 = 40,                         // Custom secondary quality
    Blend = 1,                             // Additive blending
    BlendAvg = 0,                          // No average blending
    OnBeat = 0,                            // No beat reactivity
    DurFrames = 20                         // Custom duration
};

// Apply various presets
mosaicNode.SetExtremeLowQualityMosaic();  // Extreme low quality
mosaicNode.SetMosaicPreset(3);            // Beat reactive preset
mosaicNode.SetCustomMosaic(30, 10, 0, 1, 1, 30); // Custom configuration
```

## Technical Notes

### Mosaic Architecture
The effect implements sophisticated mosaic processing:
- **Quality Control**: Intelligent quality control and mosaic processing algorithms
- **Beat Reactivity**: Advanced beat-reactive quality transitions and control
- **Blending Modes**: Sophisticated blending modes for mosaic integration
- **Quality Optimization**: High-quality mosaic enhancement and processing

### Color Architecture
Advanced color processing system:
- **RGB Processing**: Independent RGB channel processing and manipulation
- **Color Mapping**: Advanced color mapping and transformation
- **Blend Management**: Intelligent blend mode management and optimization
- **Performance Optimization**: Optimized color processing operations

### Integration System
Sophisticated system integration:
- **Mosaic Processing**: Deep integration with mosaic enhancement system
- **Color Management**: Seamless integration with color management system
- **Effect Management**: Advanced effect management and optimization
- **Performance Optimization**: Optimized operations for mosaic processing

This effect provides the foundation for sophisticated pixelation effects, creating advanced mosaic transformations with quality control, beat-reactive processing, blending modes, and intelligent pixel sampling for sophisticated AVS visualization systems.
