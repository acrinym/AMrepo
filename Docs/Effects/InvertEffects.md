# Invert Effects

## Overview

The Invert effect provides a fundamental color inversion capability that transforms images by inverting all color values. It creates a photographic negative effect by subtracting each color component from the maximum value (255), effectively flipping the color spectrum. This effect is useful for creating dramatic visual transformations, artistic effects, and can be combined with other effects for complex visual compositions.

## C# Implementation

### InvertEffectsNode Class

```csharp
using System;
using System.Collections.Generic;
using System.Drawing;
using PhoenixVisualizer.Core.Effects.Models;
using PhoenixVisualizer.Core.Models;

namespace PhoenixVisualizer.Core.Effects.Nodes.AvsEffects
{
    public class InvertEffectsNode : BaseEffectNode
    {
        #region Properties

        /// <summary>
        /// Enable/disable the invert effect
        /// </summary>
        public bool Enabled { get; set; } = true;

        /// <summary>
        /// Effect intensity (0.0 to 1.0)
        /// </summary>
        public float Intensity { get; set; } = 1.0f;

        /// <summary>
        /// Invert only specific color channels
        /// </summary>
        public bool InvertRed { get; set; } = true;

        /// <summary>
        /// Invert only specific color channels
        /// </summary>
        public bool InvertGreen { get; set; } = true;

        /// <summary>
        /// Invert only specific color channels
        /// </summary>
        public bool InvertBlue { get; set; } = true;

        /// <summary>
        /// Preserve alpha channel
        /// </summary>
        public bool PreserveAlpha { get; set; } = true;

        /// <summary>
        /// Blending mode - 0=replace, 1=additive, 2=50/50
        /// </summary>
        public int BlendMode { get; set; } = 0;

        #endregion

        #region Processing

        public override void ProcessFrame(ImageBuffer imageBuffer, AudioFeatures audioFeatures)
        {
            if (!Enabled) return;

            int width = imageBuffer.Width;
            int height = imageBuffer.Height;

            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    Color originalColor = imageBuffer.GetPixel(x, y);
                    Color invertedColor = InvertColor(originalColor);

                    // Apply blending if enabled
                    if (BlendMode > 0)
                    {
                        invertedColor = ApplyBlending(originalColor, invertedColor);
                    }

                    imageBuffer.SetPixel(x, y, invertedColor);
                }
            }
        }

        private Color InvertColor(Color originalColor)
        {
            int red = originalColor.R;
            int green = originalColor.G;
            int blue = originalColor.B;
            byte alpha = originalColor.A;

            // Invert selected channels
            if (InvertRed)
            {
                red = 255 - red;
            }

            if (InvertGreen)
            {
                green = 255 - green;
            }

            if (InvertBlue)
            {
                blue = 255 - blue;
            }

            // Apply intensity
            if (Intensity != 1.0f)
            {
                red = (int)(red * Intensity + (255 - red) * (1.0f - Intensity));
                green = (int)(green * Intensity + (255 - green) * (1.0f - Intensity));
                blue = (int)(blue * Intensity + (255 - blue) * (1.0f - Intensity));
            }

            // Clamp values
            red = Math.Max(0, Math.Min(255, red));
            green = Math.Max(0, Math.Min(255, green));
            blue = Math.Max(0, Math.Min(255, blue));

            // Preserve or modify alpha
            if (PreserveAlpha)
            {
                return Color.FromArgb(alpha, red, green, blue);
            }
            else
            {
                // Invert alpha as well
                byte invertedAlpha = (byte)(255 - alpha);
                return Color.FromArgb(invertedAlpha, red, green, blue);
            }
        }

        private Color ApplyBlending(Color original, Color inverted)
        {
            switch (BlendMode)
            {
                case 1: // Additive blending
                    return BlendAdditive(original, inverted);
                case 2: // 50/50 blending
                    return BlendAverage(original, inverted);
                default:
                    return inverted;
            }
        }

        private Color BlendAdditive(Color a, Color b)
        {
            return Color.FromArgb(
                Math.Min(255, a.R + b.R),
                Math.Min(255, a.G + b.G),
                Math.Min(255, a.B + b.B)
            );
        }

        private Color BlendAverage(Color a, Color b)
        {
            return Color.FromArgb(
                (a.R + b.R) / 2,
                (a.G + b.G) / 2,
                (a.B + b.B) / 2
            );
        }

        #endregion

        #region Configuration

        public override bool ValidateConfiguration()
        {
            // Validate property ranges
            Intensity = Math.Max(0.0f, Math.Min(1.0f, Intensity);
            BlendMode = Math.Max(0, Math.Min(2, BlendMode));

            return true;
        }

        public override string GetSettingsSummary()
        {
            string channels = "";
            if (InvertRed) channels += "R";
            if (InvertGreen) channels += "G";
            if (InvertBlue) channels += "B";
            if (string.IsNullOrEmpty(channels)) channels = "None";

            string blendMode = BlendMode switch
            {
                0 => "Replace",
                1 => "Additive",
                2 => "50/50",
                _ => "Unknown"
            };

            return $"Invert Effect - Enabled: {Enabled}, Channels: {channels}, " +
                   $"Intensity: {Intensity:F2}, Blend: {blendMode}, " +
                   $"Preserve Alpha: {PreserveAlpha}";
        }

        #endregion

        #region Public Methods

        /// <summary>
        /// Invert all color channels
        /// </summary>
        public void InvertAllChannels()
        {
            InvertRed = true;
            InvertGreen = true;
            InvertBlue = true;
        }

        /// <summary>
        /// Invert only red channel
        /// </summary>
        public void InvertRedOnly()
        {
            InvertRed = true;
            InvertGreen = false;
            InvertBlue = false;
        }

        /// <summary>
        /// Invert only green channel
        /// </summary>
        public void InvertGreenOnly()
        {
            InvertRed = false;
            InvertGreen = true;
            InvertBlue = false;
        }

        /// <summary>
        /// Invert only blue channel
        /// </summary>
        public void InvertBlueOnly()
        {
            InvertRed = false;
            InvertGreen = false;
            InvertBlue = true;
        }

        /// <summary>
        /// Create a full negative effect
        /// </summary>
        public void SetFullNegative()
        {
            InvertAllChannels();
            Intensity = 1.0f;
            BlendMode = 0;
        }

        /// <summary>
        /// Create a partial negative effect
        /// </summary>
        public void SetPartialNegative()
        {
            InvertAllChannels();
            Intensity = 0.5f;
            BlendMode = 2; // 50/50 blending
        }

        /// <summary>
        /// Create a red channel inversion effect
        /// </summary>
        public void SetRedInversion()
        {
            InvertRedOnly();
            Intensity = 1.0f;
            BlendMode = 0;
        }

        /// <summary>
        /// Create a green channel inversion effect
        /// </summary>
        public void SetGreenInversion()
        {
            InvertGreenOnly();
            Intensity = 1.0f;
            BlendMode = 0;
        }

        /// <summary>
        /// Create a blue channel inversion effect
        /// </summary>
        public void SetBlueInversion()
        {
            InvertBlueOnly();
            Intensity = 1.0f;
            BlendMode = 0;
        }

        #endregion

        #region Utility Methods

        /// <summary>
        /// Invert a single color value
        /// </summary>
        /// <param name="value">Color component value (0-255)</param>
        /// <returns>Inverted value</returns>
        public static int InvertColorComponent(int value)
        {
            return 255 - value;
        }

        /// <summary>
        /// Invert a color with full intensity
        /// </summary>
        /// <param name="color">Original color</param>
        /// <returns>Fully inverted color</returns>
        public static Color InvertColor(Color color)
        {
            return Color.FromArgb(
                color.A,
                255 - color.R,
                255 - color.G,
                255 - color.B
            );
        }

        /// <summary>
        /// Check if a color is inverted
        /// </summary>
        /// <param name="original">Original color</param>
        /// <param name="inverted">Potentially inverted color</param>
        /// <returns>True if colors are inverted</returns>
        public static bool IsInverted(Color original, Color inverted)
        {
            return (original.R + inverted.R == 255) &&
                   (original.G + inverted.G == 255) &&
                   (original.B + inverted.B == 255);
        }

        #endregion
    }
}
```

## Effect Behavior

The Invert effect transforms images by:

1. **Color Inversion**: Subtracts each color component from 255 (maximum value)
2. **Selective Channel Control**: Invert individual red, green, or blue channels
3. **Intensity Control**: Adjustable effect strength from 0% to 100%
4. **Alpha Channel Handling**: Option to preserve or invert transparency
5. **Multiple Blending Modes**: Replace, additive, or 50/50 blending options
6. **Performance Optimization**: Efficient pixel-by-pixel processing

## Color Inversion Process

### Full Inversion
- **Red Channel**: 255 - R
- **Green Channel**: 255 - G  
- **Blue Channel**: 255 - B
- **Result**: Complete photographic negative effect

### Partial Inversion
- **Intensity Control**: Blend between original and inverted colors
- **Channel Selection**: Invert only specific color channels
- **Blending Modes**: Combine original and inverted results

## Key Features

- **Channel-Specific Control**: Invert individual color channels independently
- **Intensity Adjustment**: Fine-tune effect strength for subtle to dramatic results
- **Alpha Channel Preservation**: Maintain transparency information
- **Multiple Blending Modes**: Different ways to combine original and inverted colors
- **Performance Optimized**: Efficient color processing algorithms
- **Flexible Configuration**: Customizable inversion behavior

## Configuration Options

- **Channel Selection**: Choose which color channels to invert
- **Intensity Control**: Adjust effect strength (0.0-1.0)
- **Alpha Handling**: Preserve or invert transparency
- **Blending Mode**: Select how to combine with original image
- **Enable/Disable**: Simple on/off control

## Use Cases

- **Photographic Negatives**: Create classic film negative effects
- **Artistic Transformations**: Dramatic color inversions for creative projects
- **Color Correction**: Invert specific channels for color balancing
- **Visual Effects**: Combine with other effects for complex compositions
- **Video Processing**: Real-time color inversion for live streams
- **Image Analysis**: Highlight inverted color relationships

## Mathematical Foundation

The inversion process follows the mathematical principle:
```
Inverted_Value = 255 - Original_Value
```

This creates a perfect complement where:
- Black (0) becomes White (255)
- White (255) becomes Black (0)
- Mid-gray (128) remains Mid-gray (128)
- All other values are symmetrically inverted around the midpoint
