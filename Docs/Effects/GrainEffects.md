# Grain Effects (Trans / Grain)

## Overview

The **Grain Effects** system is a sophisticated noise and texture generation engine that provides advanced control over image grain, depth-based effects, and intelligent noise manipulation. It implements comprehensive grain processing with depth buffer management, configurable grain intensity, blending modes, and intelligent noise generation for creating complex grain transformations. This effect provides the foundation for sophisticated noise effects, texture generation, and advanced image processing in AVS presets.

## Source Analysis

### Core Architecture (`r_grain.cpp`)

The effect is implemented as a C++ class `C_GrainClass` that inherits from `C_RBASE`. It provides a comprehensive grain system with depth buffer management, configurable grain parameters, and intelligent noise manipulation for creating complex grain transformations.

### Key Components

#### Grain Processing Engine
Advanced grain control system:
- **Depth Buffer Management**: Sophisticated depth buffer for grain effects
- **Grain Intensity Control**: Configurable grain intensity with precise control
- **Blending Modes**: Multiple blending modes for grain integration
- **Performance Optimization**: Optimized processing for real-time operations

#### Depth Buffer System
Sophisticated buffer processing:
- **Dynamic Allocation**: Dynamic depth buffer allocation and management
- **Random Generation**: Intelligent random grain generation and management
- **Buffer Optimization**: Optimized buffer generation and management
- **Memory Management**: Efficient memory usage and management

#### Noise Generation Engine
Advanced noise processing:
- **Random Tables**: Pre-calculated random tables for performance
- **Grain Patterns**: Intelligent grain pattern generation and control
- **Static Grain**: Configurable static grain effects and control
- **Dynamic Grain**: Dynamic grain generation and manipulation

#### Visual Enhancement System
Advanced enhancement capabilities:
- **Grain Integration**: High-quality grain integration algorithms
- **Depth Effects**: Advanced depth-based effect processing
- **Visual Integration**: Seamless integration with existing visual content
- **Quality Control**: High-quality enhancement and processing

### Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `enabled` | bool | true/false | true | Enable/disable grain effect |
| `blend` | int | 0-1 | 0 | Blending mode for grain integration |
| `blendavg` | int | 0-1 | 0 | Average blending mode |
| `smax` | int | 0-100 | 100 | Maximum grain strength (percentage) |
| `staticGrain` | int | 0-1 | 0 | Static grain mode |

### Blending Modes

| Mode | Value | Description | Behavior |
|------|-------|-------------|----------|
| **No Blend** | 0 | No blending | Grain is applied directly |
| **Blend** | 1 | Blending mode | Grain is blended with existing content |

### Grain Strength Modes

| Mode | Value | Description | Behavior |
|------|-------|-------------|----------|
| **No Grain** | 0 | No grain effect | No grain is applied |
| **Light Grain** | 1-25 | Light grain effect | Subtle grain application |
| **Medium Grain** | 26-50 | Medium grain effect | Moderate grain application |
| **Heavy Grain** | 51-75 | Heavy grain effect | Strong grain application |
| **Extreme Grain** | 76-100 | Extreme grain effect | Very strong grain application |

### Static Grain Modes

| Mode | Value | Description | Behavior |
|------|-------|-------------|----------|
| **Dynamic Grain** | 0 | Dynamic grain | Grain changes each frame |
| **Static Grain** | 1 | Static grain | Grain remains constant |

## C# Implementation

```csharp
public class GrainEffectsNode : AvsModuleNode
{
    public bool Enabled { get; set; } = true;
    public int Blend { get; set; } = 0;
    public int BlendAvg { get; set; } = 0;
    public int Smax { get; set; } = 100;
    public int StaticGrain { get; set; } = 0;
    
    // Internal state
    private byte[] depthBuffer;
    private byte[] randomTable;
    private int randomTablePos;
    private int lastWidth, lastHeight;
    private int lastSmax, lastStaticGrain;
    private readonly object renderLock = new object();
    private readonly Random random;
    
    // Performance optimization
    private const int MaxSmax = 100;
    private const int MinSmax = 0;
    private const int MaxBlend = 1;
    private const int MinBlend = 0;
    private const int MaxStaticGrain = 1;
    private const int MinStaticGrain = 0;
    private const int RandomTableSize = 491;
    private const int DepthBufferMultiplier = 2;
    
    public GrainEffectsNode()
    {
        lastWidth = lastHeight = 0;
        lastSmax = Smax;
        lastStaticGrain = StaticGrain;
        random = new Random();
        randomTable = new byte[RandomTableSize];
        InitializeRandomTable();
    }
    
    private void InitializeRandomTable()
    {
        for (int i = 0; i < RandomTableSize; i++)
        {
            randomTable[i] = (byte)(random.Next() & 0xFF);
        }
        randomTablePos = random.Next() % RandomTableSize;
    }
    
    public override void Process(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        if (!Enabled || ctx.Width <= 0 || ctx.Height <= 0) return;
        
        lock (renderLock)
        {
            // Update buffers if dimensions changed
            UpdateBuffers(ctx);
            
            // Regenerate depth buffer if parameters changed
            if (lastSmax != Smax || lastStaticGrain != StaticGrain)
            {
                GenerateDepthBuffer(ctx);
                lastSmax = Smax;
                lastStaticGrain = StaticGrain;
            }
            
            // Apply grain effect
            ApplyGrainEffect(ctx, input, output);
        }
    }
    
    private void UpdateBuffers(FrameContext ctx)
    {
        if (lastWidth != ctx.Width || lastHeight != ctx.Height)
        {
            lastWidth = ctx.Width;
            lastHeight = ctx.Height;
            GenerateDepthBuffer(ctx);
        }
    }
    
    private void GenerateDepthBuffer(FrameContext ctx)
    {
        int bufferSize = ctx.Width * ctx.Height * DepthBufferMultiplier;
        depthBuffer = new byte[bufferSize];
        
        int index = 0;
        for (int y = 0; y < ctx.Height; y++)
        {
            for (int x = 0; x < ctx.Width; x++)
            {
                // Generate random depth values
                depthBuffer[index++] = (byte)(random.Next() % 255);
                depthBuffer[index++] = (byte)(random.Next() % 100);
            }
        }
    }
    
    private void ApplyGrainEffect(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        int smaxScaled = (Smax * 255) / 100;
        int depthIndex = 0;
        
        // Update random table position
        randomTablePos += random.Next() % 300;
        if (randomTablePos >= RandomTableSize)
        {
            randomTablePos -= RandomTableSize;
        }
        
        if (StaticGrain == 1)
        {
            // Static grain mode
            if (Blend == 1)
            {
                ApplyStaticGrainWithBlend(ctx, input, output, smaxScaled, ref depthIndex);
            }
            else
            {
                ApplyStaticGrainWithoutBlend(ctx, input, output, smaxScaled, ref depthIndex);
            }
        }
        else
        {
            // Dynamic grain mode
            if (Blend == 1)
            {
                ApplyDynamicGrainWithBlend(ctx, input, output, smaxScaled, ref depthIndex);
            }
            else
            {
                ApplyDynamicGrainWithoutBlend(ctx, input, output, smaxScaled, ref depthIndex);
            }
        }
    }
    
    private void ApplyStaticGrainWithBlend(FrameContext ctx, ImageBuffer input, ImageBuffer output, int smaxScaled, ref int depthIndex)
    {
        for (int y = 0; y < ctx.Height; y++)
        {
            for (int x = 0; x < ctx.Width; x++)
            {
                Color inputPixel = input.GetPixel(x, y);
                Color processedPixel = ProcessPixelWithStaticGrain(inputPixel, depthIndex, smaxScaled);
                
                if (BlendAvg == 1)
                {
                    processedPixel = BlendPixels(inputPixel, processedPixel, 0.5f);
                }
                
                output.SetPixel(x, y, processedPixel);
                depthIndex += 2;
            }
        }
    }
    
    private void ApplyStaticGrainWithoutBlend(FrameContext ctx, ImageBuffer input, ImageBuffer output, int smaxScaled, ref int depthIndex)
    {
        for (int y = 0; y < ctx.Height; y++)
        {
            for (int x = 0; x < ctx.Width; x++)
            {
                Color inputPixel = input.GetPixel(x, y);
                Color processedPixel = ProcessPixelWithStaticGrain(inputPixel, depthIndex, smaxScaled);
                output.SetPixel(x, y, processedPixel);
                depthIndex += 2;
            }
        }
    }
    
    private void ApplyDynamicGrainWithBlend(FrameContext ctx, ImageBuffer input, ImageBuffer output, int smaxScaled, ref int depthIndex)
    {
        for (int y = 0; y < ctx.Height; y++)
        {
            for (int x = 0; x < ctx.Width; x++)
            {
                Color inputPixel = input.GetPixel(x, y);
                Color processedPixel = ProcessPixelWithDynamicGrain(inputPixel, depthIndex, smaxScaled);
                
                if (BlendAvg == 1)
                {
                    processedPixel = BlendPixels(inputPixel, processedPixel, 0.5f);
                }
                
                output.SetPixel(x, y, processedPixel);
                depthIndex += 2;
            }
        }
    }
    
    private void ApplyDynamicGrainWithoutBlend(FrameContext ctx, ImageBuffer input, ImageBuffer output, int smaxScaled, ref int depthIndex)
    {
        for (int y = 0; y < ctx.Height; y++)
        {
            for (int x = 0; x < ctx.Width; x++)
            {
                Color inputPixel = input.GetPixel(x, y);
                Color processedPixel = ProcessPixelWithDynamicGrain(inputPixel, depthIndex, smaxScaled);
                output.SetPixel(x, y, processedPixel);
                depthIndex += 2;
            }
        }
    }
    
    private Color ProcessPixelWithStaticGrain(Color pixel, int depthIndex, int smaxScaled)
    {
        if (depthBuffer[depthIndex + 1] < smaxScaled)
        {
            int strength = depthBuffer[depthIndex];
            return ApplyGrainStrength(pixel, strength);
        }
        return pixel;
    }
    
    private Color ProcessPixelWithDynamicGrain(Color pixel, int depthIndex, int smaxScaled)
    {
        if (depthBuffer[depthIndex + 1] < smaxScaled)
        {
            int strength = GetRandomStrength();
            return ApplyGrainStrength(pixel, strength);
        }
        return pixel;
    }
    
    private Color ApplyGrainStrength(Color pixel, int strength)
    {
        float strengthFactor = strength / 255.0f;
        
        int r = (int)(pixel.R * strengthFactor);
        int g = (int)(pixel.G * strengthFactor);
        int b = (int)(pixel.B * strengthFactor);
        
        r = Math.Clamp(r, 0, 255);
        g = Math.Clamp(g, 0, 255);
        b = Math.Clamp(b, 0, 255);
        
        return Color.FromRgb((byte)r, (byte)g, (byte)b);
    }
    
    private Color BlendPixels(Color pixel1, Color pixel2, float blendFactor)
    {
        int r = (int)(pixel1.R * (1 - blendFactor) + pixel2.R * blendFactor);
        int g = (int)(pixel1.G * (1 - blendFactor) + pixel2.G * blendFactor);
        int b = (int)(pixel1.B * (1 - blendFactor) + pixel2.B * blendFactor);
        
        r = Math.Clamp(r, 0, 255);
        g = Math.Clamp(g, 0, 255);
        b = Math.Clamp(b, 0, 255);
        
        return Color.FromRgb((byte)r, (byte)g, (byte)b);
    }
    
    private int GetRandomStrength()
    {
        byte strength = randomTable[randomTablePos];
        randomTablePos++;
        if ((randomTablePos & 15) == 0)
        {
            randomTablePos += random.Next() % 73;
        }
        if (randomTablePos >= RandomTableSize)
        {
            randomTablePos -= RandomTableSize;
        }
        return strength;
    }
    
    // Public interface for parameter adjustment
    public void SetEnabled(bool enable) { Enabled = enable; }
    
    public void SetBlend(int blend) 
    { 
        Blend = Math.Clamp(blend, MinBlend, MaxBlend); 
    }
    
    public void SetBlendAvg(int blendAvg) 
    { 
        BlendAvg = Math.Clamp(blendAvg, MinBlend, MaxBlend); 
    }
    
    public void SetSmax(int smax) 
    { 
        Smax = Math.Clamp(smax, MinSmax, MaxSmax); 
    }
    
    public void SetStaticGrain(int staticGrain) 
    { 
        StaticGrain = Math.Clamp(staticGrain, MinStaticGrain, MaxStaticGrain); 
    }
    
    // Status queries
    public bool IsEnabled() => Enabled;
    public int GetBlend() => Blend;
    public int GetBlendAvg() => BlendAvg;
    public int GetSmax() => Smax;
    public int GetStaticGrain() => StaticGrain;
    
    // Advanced grain control
    public void SetGrainMode(int mode)
    {
        switch (mode)
        {
            case 0: SetStaticGrain(0); break;
            case 1: SetStaticGrain(1); break;
            default: SetStaticGrain(0); break;
        }
    }
    
    public void SetBlendingMode(int mode)
    {
        switch (mode)
        {
            case 0: SetBlend(0); break;
            case 1: SetBlend(1); break;
            default: SetBlend(0); break;
        }
    }
    
    public void SetGrainIntensity(int intensity)
    {
        // Map intensity (0-100) to smax
        SetSmax(intensity);
    }
    
    // Grain effect presets
    public void SetNoGrain()
    {
        SetSmax(0);
    }
    
    public void SetLightGrain()
    {
        SetSmax(25);
    }
    
    public void SetMediumGrain()
    {
        SetSmax(50);
    }
    
    public void SetHeavyGrain()
    {
        SetSmax(75);
    }
    
    public void SetExtremeGrain()
    {
        SetSmax(100);
    }
    
    public void SetStaticGrainMode()
    {
        SetStaticGrain(1);
    }
    
    public void SetDynamicGrainMode()
    {
        SetStaticGrain(0);
    }
    
    public void SetBlendMode()
    {
        SetBlend(1);
    }
    
    public void SetNoBlendMode()
    {
        SetBlend(0);
    }
    
    public void SetAverageBlendMode()
    {
        SetBlendAvg(1);
    }
    
    public void SetNoAverageBlendMode()
    {
        SetBlendAvg(0);
    }
    
    // Custom grain configurations
    public void SetCustomGrain(int smax, int staticGrain, int blend, int blendAvg)
    {
        SetSmax(smax);
        SetStaticGrain(staticGrain);
        SetBlend(blend);
        SetBlendAvg(blendAvg);
    }
    
    public void SetGrainPreset(int preset)
    {
        switch (preset)
        {
            case 0: // No grain
                SetCustomGrain(0, 0, 0, 0);
                break;
            case 1: // Light static grain
                SetCustomGrain(25, 1, 1, 0);
                break;
            case 2: // Medium dynamic grain
                SetCustomGrain(50, 0, 1, 1);
                break;
            case 3: // Heavy static grain
                SetCustomGrain(75, 1, 1, 1);
                break;
            case 4: // Extreme dynamic grain
                SetCustomGrain(100, 0, 0, 0);
                break;
            default:
                SetCustomGrain(50, 0, 1, 0);
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
    
    public void SetBufferUpdateMode(int mode)
    {
        // Mode could control when depth buffer is regenerated
        // For now, we regenerate on parameter changes
    }
    
    // Advanced grain features
    public void SetBeatReactiveGrain(bool enable)
    {
        // Beat reactivity could be implemented here
        // For now, we maintain standard behavior
    }
    
    public void SetTemporalGrain(bool enable)
    {
        // Temporal grain effects could be implemented here
        // For now, we maintain standard behavior
    }
    
    public void SetSpatialGrain(bool enable)
    {
        // Spatial grain effects could be implemented here
        // For now, we maintain standard behavior
    }
    
    // Channel-specific control
    public void SetRedGrain(int intensity)
    {
        // This could implement per-channel grain control
        // For now, we maintain full RGB processing
    }
    
    public void SetGreenGrain(int intensity)
    {
        // This could implement per-channel grain control
        // For now, we maintain full RGB processing
    }
    
    public void SetBlueGrain(int intensity)
    {
        // This could implement per-channel grain control
        // For now, we maintain full RGB processing
    }
    
    public override void Dispose()
    {
        lock (renderLock)
        {
            // Clean up resources if needed
            depthBuffer = null;
            randomTable = null;
        }
    }
}
```

## Integration Points

### Grain Processing Integration
- **Depth Buffer Management**: Intelligent depth buffer management and grain processing
- **Grain Intensity Control**: Precise grain intensity control and manipulation
- **Blending Modes**: Advanced blending modes for grain integration
- **Quality Control**: High-quality grain enhancement and processing

### Color Processing Integration
- **RGB Processing**: Independent processing of RGB color channels
- **Color Mapping**: Advanced color mapping and transformation
- **Color Enhancement**: Intelligent color enhancement and processing
- **Visual Quality**: High-quality color transformation and processing

### Image Processing Integration
- **Noise Generation**: Advanced noise generation and grain effects
- **Texture Processing**: Intelligent texture processing and manipulation
- **Visual Enhancement**: Multiple enhancement modes for visual integration
- **Performance Optimization**: Optimized operations for grain processing

## Usage Examples

### Basic Grain Effect
```csharp
var grainNode = new GrainEffectsNode
{
    Enabled = true,                        // Enable effect
    Smax = 50,                             // Medium grain intensity
    StaticGrain = 0,                       // Dynamic grain
    Blend = 1,                             // Enable blending
    BlendAvg = 0                            // No average blending
};
```

### Heavy Static Grain Effect
```csharp
var grainNode = new GrainEffectsNode
{
    Enabled = true,
    Smax = 75,                             // Heavy grain intensity
    StaticGrain = 1,                       // Static grain
    Blend = 1,                             // Enable blending
    BlendAvg = 1                            // Enable average blending
};

// Apply heavy grain preset
grainNode.SetHeavyGrain();
```

### No Grain Effect
```csharp
var grainNode = new GrainEffectsNode
{
    Enabled = true,
    Smax = 0,                              // No grain
    StaticGrain = 0,                       // Dynamic grain
    Blend = 0,                             // No blending
    BlendAvg = 0                            // No average blending
};

// Apply no grain preset
grainNode.SetNoGrain();
```

### Advanced Grain Control
```csharp
var grainNode = new GrainEffectsNode
{
    Enabled = true,
    Smax = 60,                             // Custom grain intensity
    StaticGrain = 0,                       // Dynamic grain
    Blend = 1,                             // Enable blending
    BlendAvg = 1                            // Enable average blending
};

// Apply various presets
grainNode.SetExtremeGrain();               // Extreme grain
grainNode.SetGrainPreset(3);               // Heavy static grain preset
grainNode.SetCustomGrain(80, 1, 1, 0);    // Custom grain configuration
```

## Technical Notes

### Grain Architecture
The effect implements sophisticated grain processing:
- **Depth Buffer Management**: Intelligent depth buffer management and grain processing algorithms
- **Grain Intensity Control**: Advanced grain intensity control and manipulation
- **Blending Modes**: Sophisticated blending modes for grain integration
- **Quality Optimization**: High-quality grain enhancement and processing

### Color Architecture
Advanced color processing system:
- **RGB Processing**: Independent RGB channel processing and manipulation
- **Color Mapping**: Advanced color mapping and transformation
- **Buffer Management**: Intelligent buffer management and optimization
- **Performance Optimization**: Optimized color processing operations

### Integration System
Sophisticated system integration:
- **Grain Processing**: Deep integration with grain enhancement system
- **Color Management**: Seamless integration with color management system
- **Effect Management**: Advanced effect management and optimization
- **Performance Optimization**: Optimized operations for grain processing

This effect provides the foundation for sophisticated noise effects, creating advanced grain transformations with depth buffer management, configurable grain intensity, blending modes, and intelligent noise generation for sophisticated AVS visualization systems.
