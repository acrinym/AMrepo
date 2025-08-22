# Fadeout Effects (Trans / Fadeout)

## Overview

The **Fadeout Effects** system is a sophisticated color fading and attenuation engine that provides advanced control over image color fading, color targeting, and intelligent color manipulation. It implements comprehensive fadeout processing with color targeting algorithms, configurable fade lengths, and intelligent color processing for creating complex fadeout transformations. This effect provides the foundation for sophisticated color fading, color targeting, and advanced image processing in AVS presets.

## Source Analysis

### Core Architecture (`r_fadeout.cpp`)

The effect is implemented as a C++ class `C_FadeOutClass` that inherits from `C_RBASE`. It provides a comprehensive fadeout system with color targeting, configurable fade lengths, and intelligent color manipulation for creating complex fadeout transformations.

### Key Components

#### Fadeout Processing Engine
Advanced fadeout control system:
- **Color Targeting**: Intelligent color targeting and fade processing
- **Fade Length Control**: Configurable fade length with precise control
- **Color Processing**: Advanced color processing and manipulation
- **Performance Optimization**: Optimized processing for real-time operations

#### Color Targeting System
Sophisticated color processing:
- **Target Color**: Configurable target color for fade processing
- **Fade Length**: Configurable fade length for color transitions
- **Color Distance**: Intelligent color distance calculation and processing
- **Threshold Control**: Advanced threshold control and manipulation

#### Fade Table Generation
Advanced table processing:
- **RGB Tables**: Pre-calculated RGB fade tables for performance
- **Color Mapping**: Intelligent color mapping and transformation
- **Table Optimization**: Optimized table generation and management
- **Memory Management**: Efficient memory usage and management

#### Visual Enhancement System
Advanced enhancement capabilities:
- **Color Fading**: High-quality color fading algorithms
- **Color Processing**: Advanced color processing and manipulation
- **Visual Integration**: Seamless integration with existing visual content
- **Quality Control**: High-quality enhancement and processing

### Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `enabled` | bool | true/false | true | Enable/disable fadeout effect |
| `fadeLength` | int | 0-92 | 16 | Fade length for color transitions |
| `targetColor` | int | 0x000000-0xFFFFFF | 0x000000 | Target color for fade processing |

### Fade Length Modes

| Mode | Value | Description | Behavior |
|------|-------|-------------|----------|
| **No Fade** | 0 | No fade processing | Colors remain unchanged |
| **Light Fade** | 1-30 | Light color fading | Subtle color transitions |
| **Medium Fade** | 31-60 | Medium color fading | Moderate color transitions |
| **Heavy Fade** | 61-92 | Heavy color fading | Strong color transitions |

### Color Targeting Modes

| Mode | Value | Description | Behavior |
|------|-------|-------------|----------|
| **Black Target** | 0x000000 | Fade to black | Colors fade toward black |
| **Custom Target** | Configurable | Custom color target | Colors fade toward specified color |
| **White Target** | 0xFFFFFF | Fade to white | Colors fade toward white |

## C# Implementation

```csharp
public class FadeoutEffectsNode : AvsModuleNode
{
    public bool Enabled { get; set; } = true;
    public int FadeLength { get; set; } = 16;
    public int TargetColor { get; set; } = 0x000000;
    
    // Internal state
    private byte[,] fadeTables;
    private int lastWidth, lastHeight;
    private int lastFadeLength, lastTargetColor;
    private readonly object renderLock = new object();
    
    // Performance optimization
    private const int MaxFadeLength = 92;
    private const int MinFadeLength = 0;
    private const int MaxColorValue = 0xFFFFFF;
    private const int MinColorValue = 0x000000;
    private const int TableSize = 256;
    
    public FadeoutEffectsNode()
    {
        lastWidth = lastHeight = 0;
        lastFadeLength = FadeLength;
        lastTargetColor = TargetColor;
        fadeTables = new byte[3, TableSize];
        GenerateFadeTables();
    }
    
    public override void Process(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        if (!Enabled || ctx.Width <= 0 || ctx.Height <= 0 || FadeLength == 0) return;
        
        lock (renderLock)
        {
            // Update buffers if dimensions changed
            UpdateBuffers(ctx);
            
            // Regenerate tables if parameters changed
            if (lastFadeLength != FadeLength || lastTargetColor != TargetColor)
            {
                GenerateFadeTables();
                lastFadeLength = FadeLength;
                lastTargetColor = TargetColor;
            }
            
            // Apply fadeout effect
            ApplyFadeoutEffect(ctx, input, output);
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
    
    private void GenerateFadeTables()
    {
        // Extract target color components
        int targetR = (TargetColor >> 16) & 0xFF;
        int targetG = (TargetColor >> 8) & 0xFF;
        int targetB = TargetColor & 0xFF;
        
        // Generate fade tables for each color channel
        for (int x = 0; x < TableSize; x++)
        {
            // Red channel
            int r = x;
            if (r <= targetR - FadeLength) r += FadeLength;
            else if (r >= targetR + FadeLength) r -= FadeLength;
            else r = targetR;
            fadeTables[0, x] = (byte)Math.Clamp(r, 0, 255);
            
            // Green channel
            int g = x;
            if (g <= targetG - FadeLength) g += FadeLength;
            else if (g >= targetG + FadeLength) g -= FadeLength;
            else g = targetG;
            fadeTables[1, x] = (byte)Math.Clamp(g, 0, 255);
            
            // Blue channel
            int b = x;
            if (b <= targetB - FadeLength) b += FadeLength;
            else if (b >= targetB + FadeLength) b -= FadeLength;
            else b = targetB;
            fadeTables[2, x] = (byte)Math.Clamp(b, 0, 255);
        }
    }
    
    private void ApplyFadeoutEffect(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        // Process each pixel using fade tables
        for (int y = 0; y < ctx.Height; y++)
        {
            for (int x = 0; x < ctx.Width; x++)
            {
                Color inputPixel = input.GetPixel(x, y);
                Color processedPixel = ProcessPixel(inputPixel);
                output.SetPixel(x, y, processedPixel);
            }
        }
    }
    
    private Color ProcessPixel(Color pixel)
    {
        // Apply fade tables to each color channel
        byte r = fadeTables[0, pixel.R];
        byte g = fadeTables[1, pixel.G];
        byte b = fadeTables[2, pixel.B];
        
        return Color.FromRgb(r, g, b);
    }
    
    // Public interface for parameter adjustment
    public void SetEnabled(bool enable) { Enabled = enable; }
    
    public void SetFadeLength(int fadeLength) 
    { 
        FadeLength = Math.Clamp(fadeLength, MinFadeLength, MaxFadeLength); 
    }
    
    public void SetTargetColor(int targetColor) 
    { 
        TargetColor = Math.Clamp(targetColor, MinColorValue, MaxColorValue); 
    }
    
    // Status queries
    public bool IsEnabled() => Enabled;
    public int GetFadeLength() => FadeLength;
    public int GetTargetColor() => TargetColor;
    
    // Advanced fadeout control
    public void SetRGBTarget(int r, int g, int b)
    {
        int targetColor = (r << 16) | (g << 8) | b;
        SetTargetColor(targetColor);
    }
    
    public void SetFadeIntensity(int intensity)
    {
        // Map intensity (0-100) to fade length (0-92)
        int fadeLength = (int)((intensity / 100.0f) * MaxFadeLength);
        SetFadeLength(fadeLength);
    }
    
    public void SetFadeDirection(int direction)
    {
        // Direction could control fade behavior (toward/away from target)
        // For now, we maintain standard behavior
    }
    
    // Fadeout effect presets
    public void SetNoFade()
    {
        SetFadeLength(0);
    }
    
    public void SetLightFade()
    {
        SetFadeLength(15);
    }
    
    public void SetMediumFade()
    {
        SetFadeLength(45);
    }
    
    public void SetHeavyFade()
    {
        SetFadeLength(75);
    }
    
    public void SetExtremeFade()
    {
        SetFadeLength(92);
    }
    
    public void SetFadeToBlack()
    {
        SetTargetColor(0x000000);
        SetFadeLength(16);
    }
    
    public void SetFadeToWhite()
    {
        SetTargetColor(0xFFFFFF);
        SetFadeLength(16);
    }
    
    public void SetFadeToGray()
    {
        SetTargetColor(0x808080);
        SetFadeLength(16);
    }
    
    public void SetFadeToRed()
    {
        SetTargetColor(0xFF0000);
        SetFadeLength(16);
    }
    
    public void SetFadeToGreen()
    {
        SetTargetColor(0x00FF00);
        SetFadeLength(16);
    }
    
    public void SetFadeToBlue()
    {
        SetTargetColor(0x0000FF);
        SetFadeLength(16);
    }
    
    public void SetFadeToCyan()
    {
        SetTargetColor(0x00FFFF);
        SetFadeLength(16);
    }
    
    public void SetFadeToMagenta()
    {
        SetTargetColor(0xFF00FF);
        SetFadeLength(16);
    }
    
    public void SetFadeToYellow()
    {
        SetTargetColor(0xFFFF00);
        SetFadeLength(16);
    }
    
    // Custom fade configurations
    public void SetCustomFade(int targetColor, int fadeLength)
    {
        SetTargetColor(targetColor);
        SetFadeLength(fadeLength);
    }
    
    public void SetRGBFade(int r, int g, int b, int fadeLength)
    {
        SetRGBTarget(r, g, b);
        SetFadeLength(fadeLength);
    }
    
    public void SetSelectiveFade(int targetColor, int fadeLength, bool affectR, bool affectG, bool affectB)
    {
        // This could implement selective channel fading
        // For now, we maintain full RGB processing
        SetCustomFade(targetColor, fadeLength);
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
    
    public void SetTableUpdateMode(int mode)
    {
        // Mode could control when tables are regenerated
        // For now, we regenerate on parameter changes
    }
    
    // Advanced fadeout features
    public void SetBeatReactiveFade(bool enable)
    {
        // Beat reactivity could be implemented here
        // For now, we maintain standard behavior
    }
    
    public void SetTemporalFade(bool enable)
    {
        // Temporal fade effects could be implemented here
        // For now, we maintain standard behavior
    }
    
    public void SetSpatialFade(bool enable)
    {
        // Spatial fade effects could be implemented here
        // For now, we maintain standard behavior
    }
    
    public override void Dispose()
    {
        lock (renderLock)
        {
            // Clean up resources if needed
            fadeTables = null;
        }
    }
}
```

## Integration Points

### Fadeout Processing Integration
- **Color Targeting**: Intelligent color targeting and fade processing
- **Fade Length Control**: Precise fade length control and manipulation
- **Table Generation**: Advanced table generation and optimization
- **Quality Control**: High-quality fadeout enhancement algorithms

### Color Processing Integration
- **RGB Processing**: Independent processing of RGB color channels
- **Color Mapping**: Advanced color mapping and transformation
- **Color Enhancement**: Intelligent color enhancement and processing
- **Visual Quality**: High-quality color transformation and processing

### Image Processing Integration
- **Color Fading**: Advanced color fading and attenuation
- **Color Filtering**: Intelligent color filtering and processing
- **Visual Enhancement**: Multiple enhancement modes for visual integration
- **Performance Optimization**: Optimized operations for fadeout processing

## Usage Examples

### Basic Fadeout Effect
```csharp
var fadeoutNode = new FadeoutEffectsNode
{
    Enabled = true,                        // Enable effect
    FadeLength = 16,                       // Medium fade length
    TargetColor = 0x000000                 // Fade to black
};
```

### Heavy Fadeout Effect
```csharp
var fadeoutNode = new FadeoutEffectsNode
{
    Enabled = true,
    FadeLength = 75,                       // Heavy fade length
    TargetColor = 0x808080                 // Fade to gray
};

// Apply heavy fade preset
fadeoutNode.SetHeavyFade();
```

### Color-Specific Fadeout
```csharp
var fadeoutNode = new FadeoutEffectsNode
{
    Enabled = true,
    FadeLength = 16,                       // Medium fade length
    TargetColor = 0xFF0000                 // Fade to red
};

// Apply red fade preset
fadeoutNode.SetFadeToRed();
```

### Advanced Fadeout Control
```csharp
var fadeoutNode = new FadeoutEffectsNode
{
    Enabled = true,
    FadeLength = 45,                       // Custom fade length
    TargetColor = 0x00FF00                 // Custom target color
};

// Apply various presets
fadeoutNode.SetExtremeFade();              // Extreme fade
fadeoutNode.SetCustomFade(0xFFFF00, 60);   // Custom fade to yellow
fadeoutNode.SetRGBFade(128, 64, 192, 30); // Custom RGB fade
```

## Technical Notes

### Fadeout Architecture
The effect implements sophisticated fadeout processing:
- **Color Targeting**: Intelligent color targeting and fade processing algorithms
- **Table Generation**: Advanced table generation and optimization
- **Fade Control**: Precise fade length control and manipulation
- **Quality Optimization**: High-quality fadeout enhancement and processing

### Color Architecture
Advanced color processing system:
- **RGB Processing**: Independent RGB channel processing and manipulation
- **Color Mapping**: Advanced color mapping and transformation
- **Table Management**: Intelligent table management and optimization
- **Performance Optimization**: Optimized color processing operations

### Integration System
Sophisticated system integration:
- **Fadeout Processing**: Deep integration with fadeout enhancement system
- **Color Management**: Seamless integration with color management system
- **Effect Management**: Advanced effect management and optimization
- **Performance Optimization**: Optimized operations for fadeout processing

This effect provides the foundation for sophisticated color fading, creating advanced fadeout transformations with color targeting, configurable fade lengths, and intelligent color manipulation for sophisticated AVS visualization systems.
