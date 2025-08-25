# Brightness Effects

## Overview

The Brightness effect provides comprehensive color adjustment capabilities for image enhancement and color correction. It allows independent control of red, green, and blue color channels with precise brightness and contrast adjustments. The effect supports multiple blending modes, color exclusion based on similarity, and can be synchronized across all channels or operated independently for advanced color manipulation.

## C# Implementation

### BrightnessEffectsNode Class

```csharp
using System;
using System.Collections.Generic;
using System.Drawing;
using PhoenixVisualizer.Core.Effects.Models;
using PhoenixVisualizer.Core.Models;

namespace PhoenixVisualizer.Core.Effects.Nodes.AvsEffects
{
    public class BrightnessEffectsNode : BaseEffectNode
    {
        #region Properties

        /// <summary>
        /// Enable/disable the brightness effect
        /// </summary>
        public bool Enabled { get; set; } = true;

        /// <summary>
        /// Red channel adjustment (-4096 to 4096)
        /// </summary>
        public int RedAdjustment { get; set; } = 0;

        /// <summary>
        /// Green channel adjustment (-4096 to 4096)
        /// </summary>
        public int GreenAdjustment { get; set; } = 0;

        /// <summary>
        /// Blue channel adjustment (-4096 to 4096)
        /// </summary>
        public int BlueAdjustment { get; set; } = 0;

        /// <summary>
        /// Blending mode - 0=none, 1=additive, 2=50/50
        /// </summary>
        public int BlendMode { get; set; } = 0;

        /// <summary>
        /// Enable 50/50 blending mode
        /// </summary>
        public bool BlendAverage { get; set; } = true;

        /// <summary>
        /// Disassociate color channels (independent control)
        /// </summary>
        public bool Disassociate { get; set; } = false;

        /// <summary>
        /// Reference color for exclusion mode
        /// </summary>
        public Color ReferenceColor { get; set; } = Color.Black;

        /// <summary>
        /// Enable color exclusion mode
        /// </summary>
        public bool ExcludeMode { get; set; } = false;

        /// <summary>
        /// Color similarity threshold for exclusion (0-255)
        /// </summary>
        public int DistanceThreshold { get; set; } = 16;

        /// <summary>
        /// Effect intensity multiplier
        /// </summary>
        public float Intensity { get; set; } = 1.0f;

        #endregion

        #region Private Fields

        private int[] _redTable;
        private int[] _greenTable;
        private int[] _blueTable;
        private bool _tablesNeedInit;

        #endregion

        #region Constructor

        public BrightnessEffectsNode()
        {
            _redTable = new int[256];
            _greenTable = new int[256];
            _blueTable = new int[256];
            _tablesNeedInit = true;
        }

        #endregion

        #region Processing

        public override void ProcessFrame(ImageBuffer imageBuffer, AudioFeatures audioFeatures)
        {
            if (!Enabled) return;

            // Initialize lookup tables if needed
            if (_tablesNeedInit)
            {
                InitializeLookupTables();
            }

            // Apply brightness adjustments
            ApplyBrightnessEffect(imageBuffer);
        }

        private void InitializeLookupTables()
        {
            // Calculate multipliers for each channel
            int redMultiplier = CalculateChannelMultiplier(RedAdjustment);
            int greenMultiplier = CalculateChannelMultiplier(GreenAdjustment);
            int blueMultiplier = CalculateChannelMultiplier(BlueAdjustment);

            // Generate lookup tables for each channel
            for (int i = 0; i < 256; i++)
            {
                // Red channel (16-bit precision)
                int redValue = (i * redMultiplier) & 0xFFFF0000;
                _redTable[i] = Math.Max(0, Math.Min(0xFF0000, redValue));

                // Green channel (8-bit precision)
                int greenValue = ((i * greenMultiplier) >> 8) & 0xFFFF00;
                _greenTable[i] = Math.Max(0, Math.Min(0xFF00, greenValue));

                // Blue channel (16-bit precision)
                int blueValue = ((i * blueMultiplier) >> 16) & 0xFFFF;
                _blueTable[i] = Math.Max(0, Math.Min(0xFF, blueValue));
            }

            _tablesNeedInit = false;
        }

        private int CalculateChannelMultiplier(int adjustment)
        {
            // Convert adjustment to multiplier with 16-bit precision
            if (adjustment < 0)
            {
                return (int)((1.0f + adjustment / 4096.0f) * 65536.0f);
            }
            else
            {
                return (int)((1.0f + (adjustment / 4096.0f) * 16.0f) * 65536.0f);
            }
        }

        private void ApplyBrightnessEffect(ImageBuffer imageBuffer)
        {
            int width = imageBuffer.Width;
            int height = imageBuffer.Height;

            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    Color originalColor = imageBuffer.GetPixel(x, y);
                    Color adjustedColor = CalculateAdjustedColor(originalColor);

                    // Apply blending if enabled
                    if (BlendMode > 0 || BlendAverage)
                    {
                        adjustedColor = ApplyBlending(originalColor, adjustedColor);
                    }

                    imageBuffer.SetPixel(x, y, adjustedColor);
                }
            }
        }

        private Color CalculateAdjustedColor(Color originalColor)
        {
            // Check if color should be excluded
            if (ExcludeMode && IsColorInRange(originalColor, ReferenceColor, DistanceThreshold))
            {
                return originalColor; // No adjustment for excluded colors
            }

            // Apply channel adjustments using lookup tables
            int red = _redTable[originalColor.R];
            int green = _greenTable[originalColor.G];
            int blue = _blueTable[originalColor.B];

            // Combine adjusted channels
            int adjustedRGB = red | green | blue;

            // Extract individual components
            int adjustedRed = (adjustedRGB >> 16) & 0xFF;
            int adjustedGreen = (adjustedRGB >> 8) & 0xFF;
            int adjustedBlue = adjustedRGB & 0xFF;

            // Apply intensity multiplier
            adjustedRed = (int)(adjustedRed * Intensity);
            adjustedGreen = (int)(adjustedGreen * Intensity);
            adjustedBlue = (int)(adjustedBlue * Intensity);

            // Clamp values to valid range
            adjustedRed = Math.Max(0, Math.Min(255, adjustedRed));
            adjustedGreen = Math.Max(0, Math.Min(255, adjustedGreen));
            adjustedBlue = Math.Max(0, Math.Min(255, adjustedBlue));

            return Color.FromArgb(originalColor.A, adjustedRed, adjustedGreen, adjustedBlue);
        }

        private bool IsColorInRange(Color color1, Color color2, int threshold)
        {
            // Check if colors are within similarity threshold
            int redDiff = Math.Abs(color1.R - color2.R);
            int greenDiff = Math.Abs(color1.G - color2.G);
            int blueDiff = Math.Abs(color1.B - color2.B);

            return redDiff <= threshold && greenDiff <= threshold && blueDiff <= threshold;
        }

        private Color ApplyBlending(Color original, Color adjusted)
        {
            if (BlendMode == 1) // Additive blending
            {
                return BlendAdditive(original, adjusted);
            }
            else if (BlendAverage) // 50/50 blending
            {
                return BlendAverage(original, adjusted);
            }

            return adjusted; // No blending
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
            RedAdjustment = Math.Max(-4096, Math.Min(4096, RedAdjustment));
            GreenAdjustment = Math.Max(-4096, Math.Min(4096, GreenAdjustment));
            BlueAdjustment = Math.Max(-4096, Math.Min(4096, BlueAdjustment));
            DistanceThreshold = Math.Max(0, Math.Min(255, DistanceThreshold));
            Intensity = Math.Max(0.1f, Math.Min(5.0f, Intensity));

            // Handle channel synchronization if not disassociated
            if (!Disassociate)
            {
                // Synchronize all channels to the first changed one
                if (RedAdjustment != 0)
                {
                    GreenAdjustment = RedAdjustment;
                    BlueAdjustment = RedAdjustment;
                }
                else if (GreenAdjustment != 0)
                {
                    RedAdjustment = GreenAdjustment;
                    BlueAdjustment = GreenAdjustment;
                }
                else if (BlueAdjustment != 0)
                {
                    RedAdjustment = BlueAdjustment;
                    GreenAdjustment = BlueAdjustment;
                }
            }

            // Mark tables for reinitialization if adjustments changed
            _tablesNeedInit = true;

            return true;
        }

        public override string GetSettingsSummary()
        {
            string blendMode = BlendMode == 0 ? "None" : BlendMode == 1 ? "Additive" : "50/50";
            string channelMode = Disassociate ? "Independent" : "Synchronized";
            string exclusionMode = ExcludeMode ? $"Exclude (Threshold: {DistanceThreshold})" : "None";

            return $"Brightness Effect - Enabled: {Enabled}, " +
                   $"Adjustments: R:{RedAdjustment}, G:{GreenAdjustment}, B:{BlueAdjustment}, " +
                   $"Mode: {channelMode}, Blend: {blendMode}, " +
                   $"Exclusion: {exclusionMode}, Intensity: {Intensity:F2}";
        }

        #endregion

        #region Public Methods

        /// <summary>
        /// Reset all channel adjustments to zero
        /// </summary>
        public void ResetAdjustments()
        {
            RedAdjustment = 0;
            GreenAdjustment = 0;
            BlueAdjustment = 0;
            _tablesNeedInit = true;
        }

        /// <summary>
        /// Set all channels to the same adjustment value
        /// </summary>
        /// <param name="adjustment">Adjustment value for all channels</param>
        public void SetAllChannels(int adjustment)
        {
            RedAdjustment = adjustment;
            GreenAdjustment = adjustment;
            BlueAdjustment = adjustment;
            _tablesNeedInit = true;
        }

        /// <summary>
        /// Increase brightness by a percentage
        /// </summary>
        /// <param name="percentage">Brightness increase percentage (0-100)</param>
        public void IncreaseBrightness(float percentage)
        {
            int adjustment = (int)(percentage * 40.96f); // Convert to adjustment range
            SetAllChannels(adjustment);
        }

        /// <summary>
        /// Decrease brightness by a percentage
        /// </summary>
        /// <param name="percentage">Brightness decrease percentage (0-100)</param>
        public void DecreaseBrightness(float percentage)
        {
            int adjustment = -(int)(percentage * 40.96f); // Convert to adjustment range
            SetAllChannels(adjustment);
        }

        #endregion
    }
}
```

## Effect Behavior

The Brightness effect provides comprehensive color adjustment by:

1. **Channel-Specific Control**: Independent adjustment of red, green, and blue channels
2. **Precision Adjustment**: 16-bit precision for smooth color transitions
3. **Multiple Blending Modes**: Replace, additive, and 50/50 blending options
4. **Color Exclusion**: Selective adjustment based on color similarity
5. **Channel Synchronization**: Option to link all channels for uniform adjustments
6. **Lookup Table Optimization**: Pre-calculated adjustments for performance

## Key Features

- **High Precision**: 16-bit color channel adjustments for smooth transitions
- **Flexible Blending**: Multiple blending modes for different visual effects
- **Color Exclusion**: Selective adjustment based on reference color similarity
- **Channel Synchronization**: Option to control all channels simultaneously
- **Performance Optimized**: Pre-calculated lookup tables for efficient processing
- **Range Validation**: Automatic clamping of adjustment values

## Adjustment Ranges

- **Red Channel**: -4096 to 4096 (negative = darker, positive = brighter)
- **Green Channel**: -4096 to 4096 (negative = darker, positive = brighter)
- **Blue Channel**: -4096 to 4096 (negative = darker, positive = brighter)
- **Distance Threshold**: 0-255 (color similarity for exclusion mode)
- **Intensity**: 0.1-5.0 (effect strength multiplier)

## Use Cases

- **Color Correction**: Adjust brightness and contrast for image enhancement
- **Color Grading**: Fine-tune individual color channels for artistic effects
- **Image Enhancement**: Improve visibility in dark or overexposed images
- **Color Balancing**: Correct color casts and achieve neutral color balance
- **Creative Effects**: Create stylized looks through selective color adjustment
- **Video Processing**: Real-time color adjustment for live video streams
