# Clear Screen Effects

The Clear Screen effect provides comprehensive screen clearing capabilities with multiple blending modes, customizable colors, and flexible timing options. It can be used to reset the visualizer, create fade effects, or establish background colors.

## Overview

The Clear Screen effect fills the entire screen with a specified color using various blending techniques. It supports multiple blending modes for different visual effects, can be limited to the first frame only, and provides efficient pixel-level operations for optimal performance.

## Properties

### Core Settings
- **Enabled**: Controls whether the Clear Screen effect is active
- **Color**: The color used to fill the screen (default: black)
- **BlendMode**: Determines how the clear color interacts with existing content
- **OnlyFirstFrame**: Limits the effect to only the first frame when enabled
- **Intensity**: Overall intensity of the effect (0.0 to 1.0)

### Blending Modes
- **Replace (0)**: Completely replaces all pixels with the clear color
- **Additive (1)**: Adds the clear color to existing pixels
- **DefRenderBlend (2)**: Uses the default renderer blending mode
- **50/50 Blend**: Averages the clear color with existing pixels

## Blending Behavior

### Replace Mode
- Completely overwrites all existing pixel content
- Provides a clean slate for subsequent effects
- Fastest rendering mode
- Useful for resetting the visualizer state

### Additive Blending
- Adds the clear color to existing pixel values
- Creates brightening effects
- Maintains some original content visibility
- Useful for creating light overlays

### DefRenderBlend Mode
- Uses the system's default blending algorithm
- Provides consistent behavior across different renderers
- Optimized for performance
- Maintains visual quality standards

### 50/50 Blending
- Averages the clear color with existing pixels
- Creates smooth transitions
- Preserves original content to some degree
- Useful for creating fade effects

## Implementation Details

### Pixel Processing
The effect processes every pixel in the image buffer:

1. **Frame Counter**: Tracks frame count for first-frame-only mode
2. **Blend Selection**: Determines the appropriate blending algorithm
3. **Pixel Processing**: Applies the selected blending mode to each pixel
4. **Color Application**: Ensures consistent color application across the entire frame

### Performance Optimization
- Processes pixels in efficient loops
- Minimal conditional branching during pixel operations
- Optimized blending operations for each mode
- Efficient memory access patterns

### Frame Timing Control
- **First Frame Only**: Can be limited to clear only the initial frame
- **Continuous Mode**: Clears every frame when enabled
- **Counter Management**: Tracks frame execution for timing control
- **Beat Response**: Respects beat detection for timing

## C# Implementation

```csharp
using System;
using System.Drawing;
using PhoenixVisualizer.Core.Effects.Models;
using PhoenixVisualizer.Core.Models;

namespace PhoenixVisualizer.Core.Effects.Nodes.AvsEffects
{
    public class ClearScreenEffectsNode : BaseEffectNode
    {
        #region Enums

        /// <summary>
        /// Defines the available blending modes for screen clearing
        /// </summary>
        public enum BlendMode
        {
            /// <summary>
            /// Completely replaces all pixels with the clear color
            /// </summary>
            Replace = 0,

            /// <summary>
            /// Adds the clear color to existing pixels
            /// </summary>
            Additive = 1,

            /// <summary>
            /// Uses the default renderer blending mode
            /// </summary>
            DefRenderBlend = 2,

            /// <summary>
            /// Averages the clear color with existing pixels
            /// </summary>
            BlendAverage = 3
        }

        #endregion

        #region Properties

        /// <summary>
        /// Controls whether the Clear Screen effect is active
        /// </summary>
        public bool Enabled { get; set; } = true;

        /// <summary>
        /// The color used to fill the screen
        /// </summary>
        public Color Color { get; set; } = Color.Black;

        /// <summary>
        /// Determines how the clear color interacts with existing content
        /// </summary>
        public BlendMode BlendMode { get; set; } = BlendMode.Replace;

        /// <summary>
        /// Limits the effect to only the first frame when enabled
        /// </summary>
        public bool OnlyFirstFrame { get; set; } = false;

        /// <summary>
        /// Overall intensity of the effect (0.0 to 1.0)
        /// </summary>
        public float Intensity { get; set; } = 1.0f;

        #endregion

        #region Private Fields

        private int frameCounter = 0;
        private bool hasProcessedFirstFrame = false;

        #endregion

        #region Public Methods

        /// <summary>
        /// Processes the current frame with Clear Screen effect
        /// </summary>
        public override void ProcessFrame(ImageBuffer imageBuffer, AudioFeatures audioFeatures)
        {
            if (!Enabled)
                return;

            // Handle first-frame-only mode
            if (OnlyFirstFrame && hasProcessedFirstFrame)
                return;

            // Increment frame counter
            frameCounter++;

            // Apply the clear screen effect
            ApplyClearScreen(imageBuffer);

            // Mark first frame as processed
            if (OnlyFirstFrame)
                hasProcessedFirstFrame = true;
        }

        /// <summary>
        /// Sets the clear color
        /// </summary>
        public void SetColor(Color color)
        {
            Color = color;
        }

        /// <summary>
        /// Sets the blending mode
        /// </summary>
        public void SetBlendMode(BlendMode mode)
        {
            BlendMode = mode;
        }

        /// <summary>
        /// Enables or disables first-frame-only mode
        /// </summary>
        public void SetOnlyFirstFrame(bool enabled)
        {
            OnlyFirstFrame = enabled;
            if (enabled)
            {
                frameCounter = 0;
                hasProcessedFirstFrame = false;
            }
        }

        /// <summary>
        /// Clears the screen immediately with current settings
        /// </summary>
        public void ClearScreenNow(ImageBuffer imageBuffer)
        {
            if (!Enabled)
                return;

            ApplyClearScreen(imageBuffer);
        }

        /// <summary>
        /// Resets the frame counter and first frame processing state
        /// </summary>
        public void ResetFrameState()
        {
            frameCounter = 0;
            hasProcessedFirstFrame = false;
        }

        /// <summary>
        /// Gets the current frame count
        /// </summary>
        public int GetFrameCount()
        {
            return frameCounter;
        }

        #endregion

        #region Private Methods

        private void ApplyClearScreen(ImageBuffer imageBuffer)
        {
            int width = imageBuffer.Width;
            int height = imageBuffer.Height;

            // Apply intensity to the clear color
            Color adjustedColor = ApplyIntensityToColor(Color, Intensity);

            // Process each pixel based on blending mode
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    Color existingColor = imageBuffer.GetPixel(x, y);
                    Color finalColor = ApplyBlending(existingColor, adjustedColor);
                    imageBuffer.SetPixel(x, y, finalColor);
                }
            }
        }

        private Color ApplyBlending(Color existing, Color clear)
        {
            return BlendMode switch
            {
                BlendMode.Replace => clear,
                BlendMode.Additive => BlendAdditive(existing, clear),
                BlendMode.DefRenderBlend => BlendDefRender(existing, clear),
                BlendMode.BlendAverage => BlendAverage(existing, clear),
                _ => clear
            };
        }

        private Color BlendAdditive(Color existing, Color clear)
        {
            return Color.FromArgb(
                Math.Min(255, existing.A + clear.A),
                Math.Min(255, existing.R + clear.R),
                Math.Min(255, existing.G + clear.G),
                Math.Min(255, existing.B + clear.B)
            );
        }

        private Color BlendDefRender(Color existing, Color clear)
        {
            // Default renderer blending - similar to additive but with different weights
            return Color.FromArgb(
                Math.Min(255, existing.A + (clear.A / 2)),
                Math.Min(255, existing.R + (clear.R / 2)),
                Math.Min(255, existing.G + (clear.G / 2)),
                Math.Min(255, existing.B + (clear.B / 2))
            );
        }

        private Color BlendAverage(Color existing, Color clear)
        {
            return Color.FromArgb(
                (existing.A + clear.A) / 2,
                (existing.R + clear.R) / 2,
                (existing.G + clear.G) / 2,
                (existing.B + clear.B) / 2
            );
        }

        private Color ApplyIntensityToColor(Color color, float intensity)
        {
            if (intensity >= 1.0f)
                return color;

            if (intensity <= 0.0f)
                return Color.Transparent;

            return Color.FromArgb(
                (int)(color.A * intensity),
                (int)(color.R * intensity),
                (int)(color.G * intensity),
                (int)(color.B * intensity)
            );
        }

        #endregion

        #region Configuration

        /// <summary>
        /// Validates the current configuration
        /// </summary>
        public override bool ValidateConfiguration()
        {
            if (Intensity < 0.0f || Intensity > 1.0f)
                Intensity = 1.0f;

            // Ensure blend mode is valid
            if (!Enum.IsDefined(typeof(BlendMode), BlendMode))
                BlendMode = BlendMode.Replace;

            return true;
        }

        /// <summary>
        /// Returns a summary of current settings
        /// </summary>
        public override string GetSettingsSummary()
        {
            string blendDescription = BlendMode switch
            {
                BlendMode.Replace => "Replace",
                BlendMode.Additive => "Additive",
                BlendMode.DefRenderBlend => "DefRender",
                BlendMode.BlendAverage => "50/50",
                _ => "Unknown"
            };

            return $"Clear Screen: {(Enabled ? "Enabled" : "Disabled")}, " +
                   $"Color: {Color.Name}, " +
                   $"Blend: {blendDescription}, " +
                   $"First Frame Only: {(OnlyFirstFrame ? "Yes" : "No")}";
        }

        #endregion

        #region Advanced Operations

        /// <summary>
        /// Applies a gradient clear effect
        /// </summary>
        public void ApplyGradientClear(ImageBuffer imageBuffer, Color startColor, Color endColor, bool horizontal = true)
        {
            if (!Enabled)
                return;

            int width = imageBuffer.Width;
            int height = imageBuffer.Height;

            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    Color gradientColor;
                    if (horizontal)
                    {
                        float ratio = (float)x / (width - 1);
                        gradientColor = InterpolateColor(startColor, endColor, ratio);
                    }
                    else
                    {
                        float ratio = (float)y / (height - 1);
                        gradientColor = InterpolateColor(startColor, endColor, ratio);
                    }

                    Color existingColor = imageBuffer.GetPixel(x, y);
                    Color finalColor = ApplyBlending(existingColor, gradientColor);
                    imageBuffer.SetPixel(x, y, finalColor);
                }
            }
        }

        /// <summary>
        /// Applies a radial clear effect from center outward
        /// </summary>
        public void ApplyRadialClear(ImageBuffer imageBuffer, Color centerColor, Color edgeColor)
        {
            if (!Enabled)
                return;

            int width = imageBuffer.Width;
            int height = imageBuffer.Height;
            int centerX = width / 2;
            int centerY = height / 2;
            float maxDistance = (float)Math.Sqrt(centerX * centerX + centerY * centerY);

            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    float distance = (float)Math.Sqrt((x - centerX) * (x - centerX) + (y - centerY) * (y - centerY));
                    float ratio = distance / maxDistance;
                    Color radialColor = InterpolateColor(centerColor, edgeColor, ratio);

                    Color existingColor = imageBuffer.GetPixel(x, y);
                    Color finalColor = ApplyBlending(existingColor, radialColor);
                    imageBuffer.SetPixel(x, y, finalColor);
                }
            }
        }

        /// <summary>
        /// Applies a pattern-based clear effect
        /// </summary>
        public void ApplyPatternClear(ImageBuffer imageBuffer, Color color1, Color color2, int patternSize = 16)
        {
            if (!Enabled)
                return;

            int width = imageBuffer.Width;
            int height = imageBuffer.Height;

            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    bool useColor1 = ((x / patternSize) + (y / patternSize)) % 2 == 0;
                    Color patternColor = useColor1 ? color1 : color2;

                    Color existingColor = imageBuffer.GetPixel(x, y);
                    Color finalColor = ApplyBlending(existingColor, patternColor);
                    imageBuffer.SetPixel(x, y, finalColor);
                }
            }
        }

        private Color InterpolateColor(Color color1, Color color2, float ratio)
        {
            ratio = Math.Max(0.0f, Math.Min(1.0f, ratio));
            return Color.FromArgb(
                (int)(color1.A + (color2.A - color1.A) * ratio),
                (int)(color1.R + (color2.R - color1.R) * ratio),
                (int)(color1.G + (color2.G - color1.G) * ratio),
                (int)(color1.B + (color2.B - color1.B) * ratio)
            );
        }

        #endregion

        #region Preset Configurations

        /// <summary>
        /// Applies a fade to black effect
        /// </summary>
        public void ApplyFadeToBlack(ImageBuffer imageBuffer)
        {
            SetColor(Color.Black);
            SetBlendMode(BlendMode.BlendAverage);
            SetOnlyFirstFrame(false);
        }

        /// <summary>
        /// Applies a fade to white effect
        /// </summary>
        public void ApplyFadeToWhite(ImageBuffer imageBuffer)
        {
            SetColor(Color.White);
            SetBlendMode(BlendMode.BlendAverage);
            SetOnlyFirstFrame(false);
        }

        /// <summary>
        /// Applies a bright overlay effect
        /// </summary>
        public void ApplyBrightOverlay(ImageBuffer imageBuffer)
        {
            SetColor(Color.White);
            SetBlendMode(BlendMode.Additive);
            SetIntensity(0.3f);
            SetOnlyFirstFrame(false);
        }

        /// <summary>
        /// Applies a dark overlay effect
        /// </summary>
        public void ApplyDarkOverlay(ImageBuffer imageBuffer)
        {
            SetColor(Color.Black);
            SetBlendMode(BlendMode.BlendAverage);
            SetIntensity(0.5f);
            SetOnlyFirstFrame(false);
        }

        #endregion

        #region Initialization

        public ClearScreenEffectsNode()
        {
            ResetFrameState();
        }

        #endregion
    }
}
```

## Usage Examples

### Basic Screen Clearing
```csharp
var clearNode = new ClearScreenEffectsNode();
clearNode.Enabled = true;
clearNode.SetColor(Color.Black);
clearNode.SetBlendMode(ClearScreenEffectsNode.BlendMode.Replace);
```

### Fade Effect
```csharp
var clearNode = new ClearScreenEffectsNode();
clearNode.Enabled = true;
clearNode.SetColor(Color.Black);
clearNode.SetBlendMode(ClearScreenEffectsNode.BlendMode.BlendAverage);
clearNode.SetIntensity(0.5f);
```

### First Frame Only
```csharp
var clearNode = new ClearScreenEffectsNode();
clearNode.Enabled = true;
clearNode.SetColor(Color.DarkBlue);
clearNode.SetBlendMode(ClearScreenEffectsNode.BlendMode.Replace);
clearNode.SetOnlyFirstFrame(true);
```

### Gradient Clear Effect
```csharp
var clearNode = new ClearScreenEffectsNode();
clearNode.Enabled = true;

// Apply horizontal gradient from black to white
clearNode.ApplyGradientClear(imageBuffer, Color.Black, Color.White, true);
```

### Pattern-Based Clear
```csharp
var clearNode = new ClearScreenEffectsNode();
clearNode.Enabled = true;

// Apply checkerboard pattern
clearNode.ApplyPatternClear(imageBuffer, Color.Black, Color.White, 32);
```

### Preset Effects
```csharp
var clearNode = new ClearScreenEffectsNode();
clearNode.Enabled = true;

// Apply fade to black
clearNode.ApplyFadeToBlack(imageBuffer);

// Or apply bright overlay
clearNode.ApplyBrightOverlay(imageBuffer);
```

## Performance Notes

- Replace mode is the fastest rendering option
- Blending modes add computational overhead
- Pattern and gradient effects scale with image resolution
- First-frame-only mode provides significant performance benefits

## Limitations

- Limited to solid colors and basic patterns
- Complex gradients may impact performance
- Blending modes are predefined and cannot be customized
- Intensity affects all color channels uniformly

## Future Enhancements

- Custom blending algorithms
- Advanced pattern generation
- Animated clear effects
- Real-time parameter modulation
- MIDI control for timing
- Custom color palette support
