# Multiplier Effects

## Overview

The Multiplier effect applies various multiplication and division operations to pixel values, creating brightness adjustments and special effects. It supports multiple modes including doubling, halving, and special operations like inverting non-zero pixels or setting non-white pixels to black. The effect uses optimized processing for performance and can be used for creative visual manipulations.

## C# Implementation

### Properties

```csharp
/// <summary>
/// Whether the effect is enabled
/// </summary>
public bool Enabled { get; set; } = true;

/// <summary>
/// Current multiplication mode
/// </summary>
public MultiplierMode Mode { get; set; } = MultiplierMode.X2;

/// <summary>
/// Effect intensity multiplier
/// </summary>
public float Intensity { get; set; } = 1.0f;
```

### Enums

```csharp
/// <summary>
/// Available multiplier modes
/// </summary>
public enum MultiplierMode
{
    /// <summary>
    /// Invert non-zero pixels to white
    /// </summary>
    Invert = 0,
    
    /// <summary>
    /// Multiply by 8 (triple brightness)
    /// </summary>
    X8 = 1,
    
    /// <summary>
    /// Multiply by 4 (double brightness)
    /// </summary>
    X4 = 2,
    
    /// <summary>
    /// Multiply by 2 (increase brightness)
    /// </summary>
    X2 = 3,
    
    /// <summary>
    /// Divide by 2 (decrease brightness)
    /// </summary>
    X05 = 4,
    
    /// <summary>
    /// Divide by 4 (quarter brightness)
    /// </summary>
    X025 = 5,
    
    /// <summary>
    /// Divide by 8 (eighth brightness)
    /// </summary>
    X0125 = 6,
    
    /// <summary>
    /// Set non-white pixels to black
    /// </summary>
    XS = 7
}
```

### Private Fields

```csharp
/// <summary>
/// Whether the effect has been initialized
/// </summary>
private bool _isInitialized = false;

/// <summary>
/// Pre-calculated masks for bit operations
/// </summary>
private static readonly ulong[] _bitMasks = {
    0x7F7F7F7F7F7F7F7F, // For X05 (divide by 2)
    0x3F3F3F3F3F3F3F3F, // For X025 (divide by 4)
    0x1F1F1F1F1F1F1F1F  // For X0125 (divide by 8)
};
```

### Constructor

```csharp
public MultiplierEffectsNode()
{
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

    // Apply multiplier effect based on current mode
    switch (Mode)
    {
        case MultiplierMode.Invert:
            ApplyInvertMode(imageBuffer);
            break;
            
        case MultiplierMode.X8:
            ApplyMultiplyMode(imageBuffer, 8);
            break;
            
        case MultiplierMode.X4:
            ApplyMultiplyMode(imageBuffer, 4);
            break;
            
        case MultiplierMode.X2:
            ApplyMultiplyMode(imageBuffer, 2);
            break;
            
        case MultiplierMode.X05:
            ApplyDivideMode(imageBuffer, 2);
            break;
            
        case MultiplierMode.X025:
            ApplyDivideMode(imageBuffer, 4);
            break;
            
        case MultiplierMode.X0125:
            ApplyDivideMode(imageBuffer, 8);
            break;
            
        case MultiplierMode.XS:
            ApplySpecialMode(imageBuffer);
            break;
    }
}

/// <summary>
/// Initialize the effect
/// </summary>
private void InitializeEffect()
{
    _isInitialized = true;
}

/// <summary>
/// Apply invert mode (non-zero pixels become white)
/// </summary>
private void ApplyInvertMode(ImageBuffer imageBuffer)
{
    int width = imageBuffer.Width;
    int height = imageBuffer.Height;
    
    for (int y = 0; y < height; y++)
    {
        for (int x = 0; x < width; x++)
        {
            Color pixel = imageBuffer.GetPixel(x, y);
            
            // Check if pixel is non-zero (not black)
            if (pixel.R > 0 || pixel.G > 0 || pixel.B > 0)
            {
                // Set to white
                imageBuffer.SetPixel(x, y, Color.White);
            }
        }
    }
}

/// <summary>
/// Apply multiplication mode
/// </summary>
private void ApplyMultiplyMode(ImageBuffer imageBuffer, int multiplier)
{
    int width = imageBuffer.Width;
    int height = imageBuffer.Height;
    
    for (int y = 0; y < height; y++)
    {
        for (int x = 0; x < width; x++)
        {
            Color pixel = imageBuffer.GetPixel(x, y);
            
            // Multiply each color channel
            int r = Math.Min(255, pixel.R * multiplier);
            int g = Math.Min(255, pixel.G * multiplier);
            int b = Math.Min(255, pixel.B * multiplier);
            
            // Preserve alpha
            Color newPixel = Color.FromArgb(pixel.A, r, g, b);
            imageBuffer.SetPixel(x, y, newPixel);
        }
    }
}

/// <summary>
/// Apply division mode
/// </summary>
private void ApplyDivideMode(ImageBuffer imageBuffer, int divisor)
{
    int width = imageBuffer.Width;
    int height = imageBuffer.Height;
    
    for (int y = 0; y < height; y++)
    {
        for (int x = 0; x < width; x++)
        {
            Color pixel = imageBuffer.GetPixel(x, y);
            
            // Divide each color channel
            int r = pixel.R / divisor;
            int g = pixel.G / divisor;
            int b = pixel.B / divisor;
            
            // Preserve alpha
            Color newPixel = Color.FromArgb(pixel.A, r, g, b);
            imageBuffer.SetPixel(x, y, newPixel);
        }
    }
}

/// <summary>
/// Apply special mode (non-white pixels become black)
/// </summary>
private void ApplySpecialMode(ImageBuffer imageBuffer)
{
    int width = imageBuffer.Width;
    int height = imageBuffer.Height;
    
    for (int y = 0; y < height; y++)
    {
        for (int x = 0; x < width; x++)
        {
            Color pixel = imageBuffer.GetPixel(x, y);
            
            // Check if pixel is not white
            if (pixel.R < 255 || pixel.G < 255 || pixel.B < 255)
            {
                // Set to black
                imageBuffer.SetPixel(x, y, Color.Black);
            }
        }
    }
}
```

### Optimized Processing Methods

```csharp
/// <summary>
/// Apply optimized multiplication using bit shifting
/// </summary>
private void ApplyOptimizedMultiply(ImageBuffer imageBuffer, int shiftCount)
{
    int width = imageBuffer.Width;
    int height = imageBuffer.Height;
    
    for (int y = 0; y < height; y++)
    {
        for (int x = 0; x < width; x++)
        {
            Color pixel = imageBuffer.GetPixel(x, y);
            
            // Use bit shifting for multiplication (equivalent to multiplying by 2^shiftCount)
            int r = Math.Min(255, pixel.R << shiftCount);
            int g = Math.Min(255, pixel.G << shiftCount);
            int b = Math.Min(255, pixel.B << shiftCount);
            
            // Preserve alpha
            Color newPixel = Color.FromArgb(pixel.A, r, g, b);
            imageBuffer.SetPixel(x, y, newPixel);
        }
    }
}

/// <summary>
/// Apply optimized division using bit shifting
/// </summary>
private void ApplyOptimizedDivide(ImageBuffer imageBuffer, int shiftCount)
{
    int width = imageBuffer.Width;
    int height = imageBuffer.Height;
    
    for (int y = 0; y < height; y++)
    {
        for (int x = 0; x < width; x++)
        {
            Color pixel = imageBuffer.GetPixel(x, y);
            
            // Use bit shifting for division (equivalent to dividing by 2^shiftCount)
            int r = pixel.R >> shiftCount;
            int g = pixel.G >> shiftCount;
            int b = pixel.B >> shiftCount;
            
            // Preserve alpha
            Color newPixel = Color.FromArgb(pixel.A, r, g, b);
            imageBuffer.SetPixel(x, y, newPixel);
        }
    }
}

/// <summary>
/// Apply optimized processing with MMX-like operations
/// </summary>
private void ApplyOptimizedProcessing(ImageBuffer imageBuffer, MultiplierMode mode)
{
    int width = imageBuffer.Width;
    int height = imageBuffer.Height;
    
    // Process pixels in groups for better performance
    for (int y = 0; y < height; y++)
    {
        for (int x = 0; x < width; x += 2)
        {
            if (x + 1 < width)
            {
                // Process two pixels at once
                Color pixel1 = imageBuffer.GetPixel(x, y);
                Color pixel2 = imageBuffer.GetPixel(x + 1, y);
                
                Color newPixel1 = ProcessPixelOptimized(pixel1, mode);
                Color newPixel2 = ProcessPixelOptimized(pixel2, mode);
                
                imageBuffer.SetPixel(x, y, newPixel1);
                imageBuffer.SetPixel(x + 1, y, newPixel2);
            }
            else
            {
                // Process single pixel
                Color pixel = imageBuffer.GetPixel(x, y);
                Color newPixel = ProcessPixelOptimized(pixel, mode);
                imageBuffer.SetPixel(x, y, newPixel);
            }
        }
    }
}

/// <summary>
/// Process a single pixel with optimized operations
/// </summary>
private Color ProcessPixelOptimized(Color pixel, MultiplierMode mode)
{
    switch (mode)
    {
        case MultiplierMode.X8:
            return Color.FromArgb(
                pixel.A,
                Math.Min(255, pixel.R << 3),
                Math.Min(255, pixel.G << 3),
                Math.Min(255, pixel.B << 3)
            );
            
        case MultiplierMode.X4:
            return Color.FromArgb(
                pixel.A,
                Math.Min(255, pixel.R << 2),
                Math.Min(255, pixel.G << 2),
                Math.Min(255, pixel.B << 2)
            );
            
        case MultiplierMode.X2:
            return Color.FromArgb(
                pixel.A,
                Math.Min(255, pixel.R << 1),
                Math.Min(255, pixel.G << 1),
                Math.Min(255, pixel.B << 1)
            );
            
        case MultiplierMode.X05:
            return Color.FromArgb(
                pixel.A,
                pixel.R >> 1,
                pixel.G >> 1,
                pixel.B >> 1
            );
            
        case MultiplierMode.X025:
            return Color.FromArgb(
                pixel.A,
                pixel.R >> 2,
                pixel.G >> 2,
                pixel.B >> 2
            );
            
        case MultiplierMode.X0125:
            return Color.FromArgb(
                pixel.A,
                pixel.R >> 3,
                pixel.G >> 3,
                pixel.B >> 3
            );
            
        default:
            return pixel;
    }
}
```

### Configuration Validation

```csharp
public override bool ValidateConfiguration()
{
    if (Intensity < 0.0f || Intensity > 10.0f) return false;
    
    return true;
}
```

### Preset Methods

```csharp
/// <summary>
/// Load a brightness boost preset
/// </summary>
public void LoadBrightnessBoostPreset()
{
    Mode = MultiplierMode.X2;
    Intensity = 1.0f;
    _isInitialized = false;
}

/// <summary>
/// Load a high brightness preset
/// </summary>
public void LoadHighBrightnessPreset()
{
    Mode = MultiplierMode.X4;
    Intensity = 1.0f;
    _isInitialized = false;
}

/// <summary>
/// Load a maximum brightness preset
/// </summary>
public void LoadMaximumBrightnessPreset()
{
    Mode = MultiplierMode.X8;
    Intensity = 1.0f;
    _isInitialized = false;
}

/// <summary>
/// Load a darkness preset
/// </summary>
public void LoadDarknessPreset()
{
    Mode = MultiplierMode.X05;
    Intensity = 1.0f;
    _isInitialized = false;
}

/// <summary>
/// Load a very dark preset
/// </summary>
public void LoadVeryDarkPreset()
{
    Mode = MultiplierMode.X025;
    Intensity = 1.0f;
    _isInitialized = false;
}

/// <summary>
/// Load an invert preset
/// </summary>
public void LoadInvertPreset()
{
    Mode = MultiplierMode.Invert;
    Intensity = 1.0f;
    _isInitialized = false;
}

/// <summary>
/// Load a special effect preset
/// </summary>
public void LoadSpecialEffectPreset()
{
    Mode = MultiplierMode.XS;
    Intensity = 1.0f;
    _isInitialized = false;
}
```

### Utility Methods

```csharp
/// <summary>
/// Get the current multiplier value
/// </summary>
public float GetCurrentMultiplier()
{
    switch (Mode)
    {
        case MultiplierMode.X8: return 8.0f;
        case MultiplierMode.X4: return 4.0f;
        case MultiplierMode.X2: return 2.0f;
        case MultiplierMode.X05: return 0.5f;
        case MultiplierMode.X025: return 0.25f;
        case MultiplierMode.X0125: return 0.125f;
        case MultiplierMode.Invert: return 0.0f; // Special case
        case MultiplierMode.XS: return 0.0f; // Special case
        default: return 1.0f;
    }
}

/// <summary>
/// Check if the effect is currently multiplying
/// </summary>
public bool IsMultiplying()
{
    return Enabled && (Mode == MultiplierMode.X8 || Mode == MultiplierMode.X4 || Mode == MultiplierMode.X2);
}

/// <summary>
/// Check if the effect is currently dividing
/// </summary>
public bool IsDividing()
{
    return Enabled && (Mode == MultiplierMode.X05 || Mode == MultiplierMode.X025 || Mode == MultiplierMode.X0125);
}

/// <summary>
/// Check if the effect is using a special mode
/// </summary>
public bool IsSpecialMode()
{
    return Enabled && (Mode == MultiplierMode.Invert || Mode == MultiplierMode.XS);
}

/// <summary>
/// Get the effect description
/// </summary>
public string GetEffectDescription()
{
    switch (Mode)
    {
        case MultiplierMode.X8: return "Multiply by 8 (Triple Brightness)";
        case MultiplierMode.X4: return "Multiply by 4 (Double Brightness)";
        case MultiplierMode.X2: return "Multiply by 2 (Increase Brightness)";
        case MultiplierMode.X05: return "Divide by 2 (Decrease Brightness)";
        case MultiplierMode.X025: return "Divide by 4 (Quarter Brightness)";
        case MultiplierMode.X0125: return "Divide by 8 (Eighth Brightness)";
        case MultiplierMode.Invert: return "Invert Non-Zero Pixels to White";
        case MultiplierMode.XS: return "Set Non-White Pixels to Black";
        default: return "Unknown Mode";
    }
}

/// <summary>
/// Reset the effect to initial state
/// </summary>
public void Reset()
{
    _isInitialized = false;
}

/// <summary>
/// Get effect execution statistics
/// </summary>
public string GetExecutionStats()
{
    return $"Initialized: {_isInitialized}, Mode: {Mode}, Multiplier: {GetCurrentMultiplier()}";
}
```

## Usage Examples

### Basic Brightness Boost

```csharp
var multiplier = new MultiplierEffectsNode();
multiplier.Mode = MultiplierMode.X2;
multiplier.Intensity = 1.0f;
```

### High Brightness Effect

```csharp
var multiplier = new MultiplierEffectsNode();
multiplier.LoadHighBrightnessPreset();
multiplier.Intensity = 0.8f;
```

### Darkness Effect

```csharp
var multiplier = new MultiplierEffectsNode();
multiplier.LoadDarknessPreset();
multiplier.Intensity = 1.2f;
```

### Special Invert Effect

```csharp
var multiplier = new MultiplierEffectsNode();
multiplier.LoadInvertPreset();
multiplier.Intensity = 1.0f;
```

## Technical Details

The Multiplier effect applies various mathematical operations to pixel values for creative visual effects. Key features include:

- **Multiplication Modes**: X8, X4, X2 for increasing brightness
- **Division Modes**: X05, X025, X0125 for decreasing brightness
- **Special Modes**: Invert (non-zero to white) and XS (non-white to black)
- **Optimized Processing**: Bit shifting operations for performance
- **MMX-like Operations**: Grouped pixel processing for efficiency
- **Alpha Preservation**: Maintains transparency information

The effect uses bit shifting operations for multiplication and division, which are more efficient than traditional arithmetic operations. For example, multiplying by 2 is equivalent to a left shift by 1, and dividing by 2 is equivalent to a right shift by 1.

The special modes provide creative effects by manipulating pixel values based on their current state rather than applying mathematical operations. The invert mode turns any non-black pixel into white, while the XS mode turns any non-white pixel into black.

The effect is particularly useful for creating dramatic brightness changes, artistic effects, and for preparing images for further processing by other effects in the chain.
