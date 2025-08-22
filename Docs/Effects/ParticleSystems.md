# Particle Systems (Render / Moving Particle)

## Overview

The **Particle Systems** is a sophisticated physics-based particle simulation that creates dynamic, moving particles with realistic motion, beat reactivity, and multiple blending modes. It implements a spring-damper physics system where particles are attracted to beat-reactive targets, creating organic, flowing animations. This effect is essential for creating dynamic particle trails, organic motion, and beat-reactive visual elements in AVS presets.

## Source Analysis

### Core Architecture (`r_parts.cpp`)

The effect is implemented as a C++ class `C_BPartsClass` that inherits from `C_RBASE`. It provides a complete particle physics engine with spring-damper dynamics, beat-reactive target positioning, and sophisticated rendering with multiple blending algorithms.

### Key Components

#### Physics Simulation Engine
The effect implements a sophisticated physics system:
- **Spring-Damper Model**: Particles are attracted to targets with spring force and damping
- **Velocity Integration**: Uses Euler integration for smooth particle motion
- **Beat-Reactive Targets**: Dynamic target positions based on audio beat events
- **Momentum Conservation**: Realistic particle behavior with velocity decay

#### Particle Rendering System
Advanced rendering with multiple blending modes:
- **Circular Particles**: Renders particles as filled circles with configurable sizes
- **Multiple Blending Modes**: Replace, blend, average, and linear blending options
- **Size Animation**: Dynamic particle sizing with beat-reactive scaling
- **Boundary Handling**: Proper clipping and edge case management

#### Audio Integration
Deep integration with audio data:
- **Beat Detection**: Uses `isBeat` for target position randomization
- **Dynamic Parameters**: Adjusts particle behavior based on audio events
- **Size Modulation**: Beat-reactive particle size changes
- **Target Variation**: Random target positions on beat events

### Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `enabled` | int | Bit flags | 1 | Enable flags (1=active, 2=beat size) |
| `colors` | int | RGB color | White | Particle color |
| `maxdist` | int | 1-32 | 16 | Maximum distance multiplier |
| `size` | int | 1-128 | 8 | Base particle size |
| `size2` | int | 1-128 | 8 | Beat-reactive particle size |
| `blend` | int | 0-3 | 1 | Blending mode (0=replace, 1=blend, 2=average, 3=linear) |

### Rendering Pipeline

1. **Physics Update**: Update particle position and velocity using spring-damper model
2. **Beat Processing**: Handle beat events and update target positions
3. **Position Calculation**: Convert normalized coordinates to screen coordinates
4. **Size Animation**: Apply beat-reactive size changes
5. **Particle Rendering**: Render circular particles with selected blending mode
6. **Boundary Clipping**: Ensure particles stay within screen bounds

## C# Implementation

```csharp
public class ParticleSystemsNode : AvsModuleNode
{
    public bool Enabled { get; set; } = true;
    public bool BeatSizeEnabled { get; set; } = false;
    public Color ParticleColor { get; set; } = Color.White;
    public int MaxDistance { get; set; } = 16;
    public int BaseSize { get; set; } = 8;
    public int BeatSize { get; set; } = 8;
    public ParticleBlendMode BlendMode { get; set; } = ParticleBlendMode.Blend;
    
    // Internal state
    private double[] currentPosition;
    private double[] currentVelocity;
    private double[] targetPosition;
    private int currentSize;
    private int targetSize;
    private bool wasBeat;
    
    // Audio data
    private float[] leftChannelData;
    private float[] rightChannelData;
    private float[] centerChannelData;
    
    // Physics constants
    private const double SpringForce = 0.004;
    private const double DampingFactor = 0.991;
    private const double BeatRandomRange = 16.0 / 48.0;
    
    // Performance optimization
    private int[] particleBuffer;
    private bool bufferInitialized;
    
    public ParticleSystemsNode()
    {
        currentPosition = new double[2] { -0.6, 0.3 };
        currentVelocity = new double[2] { -0.01551, 0.0 };
        targetPosition = new double[2] { 0.0, 0.0 };
        currentSize = BaseSize;
        targetSize = BaseSize;
        InitializeBuffer();
    }
    
    public override void Process(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        if (!Enabled) 
        {
            CopyInputToOutput(ctx, input, output);
            return;
        }
        
        UpdateAudioData(ctx);
        UpdatePhysics(ctx);
        RenderParticles(ctx, input, output);
    }
    
    private void UpdateAudioData(FrameContext ctx)
    {
        if (ctx.AudioData != null)
        {
            leftChannelData = ctx.AudioData.LeftChannel;
            rightChannelData = ctx.AudioData.RightChannel;
            centerChannelData = ctx.AudioData.CenterChannel;
        }
    }
    
    private void UpdatePhysics(FrameContext ctx)
    {
        // Handle beat events
        if (ctx.IsBeat && !wasBeat)
        {
            HandleBeatEvent();
            wasBeat = true;
        }
        else if (!ctx.IsBeat)
        {
            wasBeat = false;
        }
        
        // Update physics simulation
        UpdateParticlePhysics();
        
        // Update size animation
        UpdateParticleSize(ctx);
    }
    
    private void HandleBeatEvent()
    {
        // Randomize target position on beat
        Random random = new Random();
        targetPosition[0] = ((random.Next(33) - 16) / 48.0);
        targetPosition[1] = ((random.Next(33) - 16) / 48.0);
        
        // Set beat-reactive size if enabled
        if (BeatSizeEnabled)
        {
            targetSize = BeatSize;
        }
    }
    
    private void UpdateParticlePhysics()
    {
        // Apply spring force towards target
        currentVelocity[0] -= SpringForce * (currentPosition[0] - targetPosition[0]);
        currentVelocity[1] -= SpringForce * (currentPosition[1] - targetPosition[1]);
        
        // Update position using velocity
        currentPosition[0] += currentVelocity[0];
        currentPosition[1] += currentVelocity[1];
        
        // Apply damping to velocity
        currentVelocity[0] *= DampingFactor;
        currentVelocity[1] *= DampingFactor;
    }
    
    private void UpdateParticleSize(FrameContext ctx)
    {
        // Smooth size transition
        if (BeatSizeEnabled && ctx.IsBeat)
        {
            targetSize = BeatSize;
        }
        else
        {
            targetSize = BaseSize;
        }
        
        // Smooth interpolation to target size
        currentSize = (currentSize + targetSize) / 2;
    }
    
    private void RenderParticles(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        // Copy input to output first
        CopyInputToOutput(ctx, input, output);
        
        // Calculate screen coordinates
        int width = output.Width;
        int height = output.Height;
        int scale = Math.Min(height / 2, (width * 3) / 8);
        
        // Convert normalized position to screen coordinates
        int screenX = (int)(currentPosition[0] * scale * (MaxDistance / 32.0)) + width / 2;
        int screenY = (int)(currentPosition[1] * scale * (MaxDistance / 32.0)) + height / 2;
        
        // Clamp size to reasonable range
        int particleSize = Math.Clamp(currentSize, 1, 128);
        
        // Render particle
        if (particleSize <= 1)
        {
            RenderSinglePixel(output, screenX, screenY, width, height);
        }
        else
        {
            RenderCircularParticle(output, screenX, screenY, particleSize, width, height);
        }
    }
    
    private void RenderSinglePixel(ImageBuffer output, int x, int y, int width, int height)
    {
        if (x >= 0 && y >= 0 && x < width && y < height)
        {
            Color currentColor = output.GetPixel(x, y);
            Color newColor = ApplyBlending(currentColor, ParticleColor, BlendMode);
            output.SetPixel(x, y, newColor);
        }
    }
    
    private void RenderCircularParticle(ImageBuffer output, int centerX, int centerY, int size, int width, int height)
    {
        int radius = size / 2;
        double maxDistanceSquared = size * size * 0.25;
        
        // Calculate bounds
        int startY = Math.Max(0, centerY - radius);
        int endY = Math.Min(height, centerY + radius);
        
        for (int y = startY; y < endY; y++)
        {
            double yDistance = (y - centerY);
            double xDistance = Math.Sqrt(maxDistanceSquared - yDistance * yDistance);
            
            if (xDistance > 0)
            {
                int xRadius = (int)(xDistance + 0.99);
                if (xRadius < 1) xRadius = 1;
                
                int startX = Math.Max(0, centerX - xRadius);
                int endX = Math.Min(width, centerX + xRadius);
                
                for (int x = startX; x < endX; x++)
                {
                    Color currentColor = output.GetPixel(x, y);
                    Color newColor = ApplyBlending(currentColor, ParticleColor, BlendMode);
                    output.SetPixel(x, y, newColor);
                }
            }
        }
    }
    
    private Color ApplyBlending(Color current, Color particle, ParticleBlendMode mode)
    {
        switch (mode)
        {
            case ParticleBlendMode.Replace:
                return particle;
                
            case ParticleBlendMode.Blend:
                return BlendColors(current, particle, 0.5f);
                
            case ParticleBlendMode.Average:
                return BlendColorsAverage(current, particle);
                
            case ParticleBlendMode.Linear:
                return BlendColorsLinear(current, particle, 0.5f);
                
            default:
                return particle;
        }
    }
    
    private Color BlendColors(Color color1, Color color2, float alpha)
    {
        return Color.FromArgb(
            (int)(color1.A * (1 - alpha) + color2.A * alpha),
            (int)(color1.R * (1 - alpha) + color2.R * alpha),
            (int)(color1.G * (1 - alpha) + color2.G * alpha),
            (int)(color1.B * (1 - alpha) + color2.B * alpha)
        );
    }
    
    private Color BlendColorsAverage(Color color1, Color color2)
    {
        return Color.FromArgb(
            (color1.A + color2.A) / 2,
            (color1.R + color2.R) / 2,
            (color1.G + color2.G) / 2,
            (color1.B + color2.B) / 2
        );
    }
    
    private Color BlendColorsLinear(Color color1, Color color2, float alpha)
    {
        return Color.FromArgb(
            (int)(color1.A + (color2.A - color1.A) * alpha),
            (int)(color1.R + (color2.R - color1.R) * alpha),
            (int)(color1.G + (color2.G - color1.G) * alpha),
            (int)(color1.B + (color2.B - color1.B) * alpha)
        );
    }
    
    private void CopyInputToOutput(FrameContext ctx, ImageBuffer input, ImageBuffer output)
    {
        int width = input.Width;
        int height = input.Height;
        
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                Color pixel = input.GetPixel(x, y);
                output.SetPixel(x, y, pixel);
            }
        }
    }
    
    private void InitializeBuffer()
    {
        particleBuffer = new int[1024 * 768]; // Default size
        bufferInitialized = true;
    }
    
    // Public interface for parameter adjustment
    public void SetEnabled(bool enabled) { Enabled = enabled; }
    public void SetBeatSizeEnabled(bool enabled) { BeatSizeEnabled = enabled; }
    public void SetParticleColor(Color color) { ParticleColor = color; }
    public void SetMaxDistance(int distance) { MaxDistance = distance; }
    public void SetBaseSize(int size) { BaseSize = size; }
    public void SetBeatSize(int size) { BeatSize = size; }
    public void SetBlendMode(ParticleBlendMode mode) { BlendMode = mode; }
    
    // Status queries
    public double[] GetCurrentPosition() => (double[])currentPosition.Clone();
    public double[] GetCurrentVelocity() => (double[])currentVelocity.Clone();
    public double[] GetTargetPosition() => (double[])targetPosition.Clone();
    public int GetCurrentSize() => currentSize;
    public int GetTargetSize() => targetSize;
    public bool IsBeatSizeEnabled() => BeatSizeEnabled;
    
    public override void Dispose()
    {
        // Cleanup if needed
    }
}

public enum ParticleBlendMode
{
    Replace = 0,    // Replace existing pixels
    Blend = 1,      // Alpha blending
    Average = 2,    // Average colors
    Linear = 3      // Linear interpolation
}
```

## Integration Points

### Audio Data Integration
- **Beat Detection**: Uses `FrameContext.IsBeat` for target position randomization
- **Audio Analysis**: Processes left/right/center channel data for potential audio-reactive effects
- **Dynamic Parameters**: Adjusts particle behavior and size based on beat events

### Framebuffer Handling
- **Input/Output Buffers**: Processes `ImageBuffer` objects with full color support
- **Particle Rendering**: Renders circular particles with configurable sizes
- **Blending System**: Multiple blending modes for different visual effects
- **Boundary Management**: Proper clipping and edge case handling

### Performance Considerations
- **Physics Simulation**: Efficient spring-damper calculations
- **Circular Rendering**: Optimized circle drawing algorithm
- **Blending Operations**: Fast color blending with multiple modes
- **Memory Management**: Efficient buffer handling for particle data

## Usage Examples

### Basic Particle System
```csharp
var particleNode = new ParticleSystemsNode
{
    Enabled = true,
    ParticleColor = Color.White,
    BaseSize = 8,
    MaxDistance = 16,
    BlendMode = ParticleBlendMode.Blend
};
```

### Beat-Reactive Particles
```csharp
var particleNode = new ParticleSystemsNode
{
    Enabled = true,
    BeatSizeEnabled = true,
    BaseSize = 8,
    BeatSize = 16,
    ParticleColor = Color.Cyan,
    BlendMode = ParticleBlendMode.Average
};
```

### Large Organic Particles
```csharp
var particleNode = new ParticleSystemsNode
{
    Enabled = true,
    BaseSize = 32,
    BeatSize = 64,
    MaxDistance = 24,
    ParticleColor = Color.Magenta,
    BlendMode = ParticleBlendMode.Linear
};
```

## Technical Notes

### Physics Simulation
The effect implements a sophisticated physics system:
- **Spring-Damper Model**: Particles are attracted to targets with realistic force
- **Velocity Integration**: Uses Euler integration for smooth motion
- **Momentum Conservation**: Realistic particle behavior with velocity decay
- **Beat Reactivity**: Dynamic target positions based on audio events

### Rendering Algorithm
Advanced particle rendering with multiple options:
- **Circular Particles**: Filled circles with configurable radii
- **Multiple Blending**: Replace, blend, average, and linear modes
- **Size Animation**: Dynamic sizing with beat-reactive changes
- **Boundary Clipping**: Proper screen edge handling

### Performance Characteristics
- **CPU Moderate**: Physics calculations and circular rendering
- **Memory Access**: Efficient particle buffer management
- **Optimization**: Fast blending operations and boundary checking
- **Quality**: Smooth particle motion with realistic physics

This effect is essential for creating dynamic particle animations, organic motion, and beat-reactive visual elements in AVS presets, providing the foundation for many advanced particle-based visualization techniques.
