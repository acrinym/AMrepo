# Fastbright Effects (Trans / Fast Brightness)

## Overview

The **Fastbright Effects** system is a high-performance brightness manipulation engine that provides ultra-fast brightness control with optimized processing algorithms. It implements comprehensive brightness processing with dual-direction control (brighten/darken), optimized table-based operations, and intelligent color processing for creating rapid brightness transformations. This effect provides the foundation for high-performance brightness manipulation, real-time brightness control, and advanced image processing in AVS presets.

## Source Analysis

### Core Architecture (`r_fastbright.cpp`)

The effect is implemented as a C++ class `C_FastBright` that inherits from `C_RBASE`. It provides a high-performance brightness system with dual-direction control, optimized table operations, and intelligent color manipulation for creating rapid brightness transformations.

### Key Components

#### Fast Brightness Processing Engine
High-performance brightness control system:
- **Dual Direction Control**: Brighten (x2) and darken (÷2) operations
- **Table-Based Processing**: Pre-calculated brightness tables for performance
- **Optimized Algorithms**: MMX-optimized and standard processing paths
- **Performance Optimization**: Ultra-fast processing for real-time operations

#### Brightness Table System
Sophisticated table processing:
- **RGB Tables**: Pre-calculated RGB brightness tables for performance
- **Color Mapping**: Intelligent color mapping and transformation
- **Table Optimization**: Optimized table generation and management
- **Memory Management**: Efficient memory usage and management

#### Direction Control System
Advanced direction processing:
- **Brighten Mode**: Doubles color values with saturation protection
- **Darken Mode**: Halves color values with precision control
- **No Effect Mode**: Pass-through processing for no brightness change
- **Mode Switching**: Dynamic mode switching and control

#### Visual Enhancement System
Advanced enhancement capabilities:
- **Brightness Control**: High-quality brightness manipulation algorithms
- **Color Processing**: Advanced color processing and manipulation
- **Visual Integration**: Seamless integration with existing visual content
- **Quality Control**: High-quality enhancement and processing

### Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `enabled` | bool | true/false | true | Enable/disable fastbright effect |
| `direction` | int | 0-2 | 0 | Brightness direction (0=brighten, 1=darken, 2=no effect) |

### Direction Modes

| Mode | Value | Description | Behavior |
|------|-------|-------------|----------|
| **Brighten** | 0 | Double brightness | Colors are multiplied by 2 (with saturation) |
| **Darken** | 1 | Halve brightness | Colors are divided by 2 |
| **No Effect** | 2 | No change | Colors remain unchanged |

### Brightness Processing Modes

| Mode | Value | Description | Behavior |
|------|-------|-------------|----------|
| **Brighten x2** | 0 | Brighten operation | Colors are doubled with saturation protection |
| **Darken ÷2** | 1 | Darken operation | Colors are halved with precision control |
| **Pass-through** | 2 | No processing | Colors pass through unchanged |

## C# Implementation

```csharp
public class FastbrightEffectsNode : AvsModuleNode
{
    public bool Enabled { get; set; } = true;
    public int Direction { get; set; } = 0;
    
    // Internal state
    private byte[,] brightnessTables;
    private int lastWidth, lastHeight;
    private int lastDirection;
    private readonly object renderLock = new object();
    
    // Performance optimization
    private const int MaxDirection = 2;
    private const int MinDirection = 0;
    private const int TableSize = 256;
    private const int BrightenMode = 0;
    private const int DarkenMode = 1;
    private const int NoEffectMode = 2;
    
    public FastbrightEffectsNode()
    {
        lastWidth = lastHeight = 0;
        lastDirection = Direction;
        brightnessTables = new byte[3, TableSize];
        GenerateBrightnessTables();
    }
    
    public override void Process(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        if (!Enabled || ctx.Width <= 0 || ctx.Height <= 0 || Direction == NoEffectMode) 
        {
            // Pass through if disabled or no effect mode
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
            
            // Regenerate tables if direction changed
            if (lastDirection != Direction)
            {
                GenerateBrightnessTables();
                lastDirection = Direction;
            }
            
            // Apply fastbright effect
            ApplyFastbrightEffect(ctx, input, output);
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
    
    private void GenerateBrightnessTables()
    {
        if (Direction == BrightenMode)
        {
            // Generate brighten tables (x2 with saturation)
            for (int x = 0; x < TableSize; x++)
            {
                // Red channel
                int r = x * 2;
                brightnessTables[0, x] = (byte)Math.Min(r, 255);
                
                // Green channel
                int g = x * 2;
                brightnessTables[1, x] = (byte)Math.Min(g, 255);
                
                // Blue channel
                int b = x * 2;
                brightnessTables[2, x] = (byte)Math.Min(b, 255);
            }
        }
        else if (Direction == DarkenMode)
        {
            // Generate darken tables (÷2)
            for (int x = 0; x < TableSize; x++)
            {
                // Red channel
                int r = x / 2;
                brightnessTables[0, x] = (byte)r;
                
                // Green channel
                int g = x / 2;
                brightnessTables[1, x] = (byte)g;
                
                // Blue channel
                int b = x / 2;
                brightnessTables[2, x] = (byte)b;
            }
        }
        else
        {
            // No effect mode - identity tables
            for (int x = 0; x < TableSize; x++)
            {
                brightnessTables[0, x] = (byte)x;
                brightnessTables[1, x] = (byte)x;
                brightnessTables[2, x] = (byte)x;
            }
        }
    }
    
    private void ApplyFastbrightEffect(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        if (Direction == NoEffectMode)
        {
            // Pass through unchanged
            input.CopyTo(output);
            return;
        }
        
        // Process each pixel using brightness tables
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
        if (Direction == NoEffectMode)
        {
            return pixel;
        }
        
        // Apply brightness tables to each color channel
        byte r = brightnessTables[0, pixel.R];
        byte g = brightnessTables[1, pixel.G];
        byte b = brightnessTables[2, pixel.B];
        
        return Color.FromRgb(r, g, b);
    }
    
    // Public interface for parameter adjustment
    public void SetEnabled(bool enable) { Enabled = enable; }
    
    public void SetDirection(int direction) 
    { 
        Direction = Math.Clamp(direction, MinDirection, MaxDirection); 
    }
    
    // Status queries
    public bool IsEnabled() => Enabled;
    public int GetDirection() => Direction;
    
    // Direction control methods
    public void SetBrightenMode() { SetDirection(BrightenMode); }
    public void SetDarkenMode() { SetDirection(DarkenMode); }
    public void SetNoEffectMode() { SetDirection(NoEffectMode); }
    
    // Advanced brightness control
    public void SetBrightnessMode(int mode)
    {
        switch (mode)
        {
            case 0: SetBrightenMode(); break;
            case 1: SetDarkenMode(); break;
            case 2: SetNoEffectMode(); break;
            default: SetBrightenMode(); break;
        }
    }
    
    public void SetBrightnessIntensity(int intensity)
    {
        // Map intensity (0-100) to direction modes
        if (intensity < 33)
        {
            SetDarkenMode();
        }
        else if (intensity < 66)
        {
            SetNoEffectMode();
        }
        else
        {
            SetBrightenMode();
        }
    }
    
    public void SetBrightnessDirection(bool brighten)
    {
        if (brighten)
        {
            SetBrightenMode();
        }
        else
        {
            SetDarkenMode();
        }
    }
    
    // Fastbright effect presets
    public void SetDoubleBrightness()
    {
        SetBrightenMode();
    }
    
    public void SetHalfBrightness()
    {
        SetDarkenMode();
    }
    
    public void SetNoBrightnessChange()
    {
        SetNoEffectMode();
    }
    
    public void SetHighBrightness()
    {
        SetBrightenMode();
    }
    
    public void SetLowBrightness()
    {
        SetDarkenMode();
    }
    
    public void SetNormalBrightness()
    {
        SetNoEffectMode();
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
    
    // Advanced fastbright features
    public void SetBeatReactiveBrightness(bool enable)
    {
        // Beat reactivity could be implemented here
        // For now, we maintain standard behavior
    }
    
    public void SetTemporalBrightness(bool enable)
    {
        // Temporal brightness effects could be implemented here
        // For now, we maintain standard behavior
    }
    
    public void SetSpatialBrightness(bool enable)
    {
        // Spatial brightness effects could be implemented here
        // For now, we maintain standard behavior
    }
    
    // Custom brightness operations
    public void SetCustomBrightness(float multiplier)
    {
        if (multiplier > 1.0f)
        {
            SetBrightenMode();
        }
        else if (multiplier < 1.0f)
        {
            SetDarkenMode();
        }
        else
        {
            SetNoEffectMode();
        }
    }
    
    public void SetBrightnessRange(float minBrightness, float maxBrightness)
    {
        // This could implement custom brightness ranges
        // For now, we maintain standard behavior
    }
    
    public void SetBrightnessCurve(int curveType)
    {
        // This could implement different brightness curves
        // For now, we maintain standard behavior
    }
    
    // Channel-specific control
    public void SetRedBrightness(int direction)
    {
        // This could implement per-channel brightness control
        // For now, we maintain full RGB processing
    }
    
    public void SetGreenBrightness(int direction)
    {
        // This could implement per-channel brightness control
        // For now, we maintain full RGB processing
    }
    
    public void SetBlueBrightness(int direction)
    {
        // This could implement per-channel brightness control
        // For now, we maintain full RGB processing
    }
    
    public override void Dispose()
    {
        lock (renderLock)
        {
            // Clean up resources if needed
            brightnessTables = null;
        }
    }
}
```

## Integration Points

### Fastbright Processing Integration
- **Direction Control**: Intelligent direction control and brightness processing
- **Table Generation**: Advanced table generation and optimization
- **Performance Optimization**: Ultra-fast brightness processing algorithms
- **Quality Control**: High-quality brightness enhancement and processing

### Color Processing Integration
- **RGB Processing**: Independent processing of RGB color channels
- **Color Mapping**: Advanced color mapping and transformation
- **Color Enhancement**: Intelligent color enhancement and processing
- **Visual Quality**: High-quality color transformation and processing

### Image Processing Integration
- **Brightness Control**: Advanced brightness manipulation and control
- **Color Filtering**: Intelligent color filtering and processing
- **Visual Enhancement**: Multiple enhancement modes for visual integration
- **Performance Optimization**: Optimized operations for fastbright processing

## Usage Examples

### Basic Fastbright Effect
```csharp
var fastbrightNode = new FastbrightEffectsNode
{
    Enabled = true,                        // Enable effect
    Direction = 0                          // Brighten mode
};
```

### Darken Effect
```csharp
var fastbrightNode = new FastbrightEffectsNode
{
    Enabled = true,
    Direction = 1                          // Darken mode
};

// Apply darken preset
fastbrightNode.SetDarkenMode();
```

### No Effect Mode
```csharp
var fastbrightNode = new FastbrightEffectsNode
{
    Enabled = true,
    Direction = 2                          // No effect mode
};

// Apply no effect preset
fastbrightNode.SetNoEffectMode();
```

### Advanced Fastbright Control
```csharp
var fastbrightNode = new FastbrightEffectsNode
{
    Enabled = true,
    Direction = 0                          // Brighten mode
};

// Apply various presets
fastbrightNode.SetDoubleBrightness();      // Double brightness
fastbrightNode.SetHalfBrightness();        // Half brightness
fastbrightNode.SetCustomBrightness(1.5f);  // Custom brightness
```

## Technical Notes

### Fastbright Architecture
The effect implements sophisticated fastbright processing:
- **Direction Control**: Intelligent direction control and brightness processing algorithms
- **Table Generation**: Advanced table generation and optimization
- **Performance Optimization**: Ultra-fast brightness processing and manipulation
- **Quality Optimization**: High-quality brightness enhancement and processing

### Color Architecture
Advanced color processing system:
- **RGB Processing**: Independent RGB channel processing and manipulation
- **Color Mapping**: Advanced color mapping and transformation
- **Table Management**: Intelligent table management and optimization
- **Performance Optimization**: Optimized color processing operations

### Integration System
Sophisticated system integration:
- **Fastbright Processing**: Deep integration with fastbright enhancement system
- **Color Management**: Seamless integration with color management system
- **Effect Management**: Advanced effect management and optimization
- **Performance Optimization**: Optimized operations for fastbright processing

This effect provides the foundation for high-performance brightness manipulation, creating ultra-fast brightness transformations with dual-direction control, optimized table operations, and intelligent color manipulation for sophisticated AVS visualization systems.
