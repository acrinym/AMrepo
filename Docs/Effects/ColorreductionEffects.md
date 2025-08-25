# Color Reduction Effects

The Color Reduction effect reduces the number of color levels in an image, creating a posterized or quantized appearance. It works by masking color values to specific bit depths, effectively reducing the color palette and creating distinct color bands.

## Effect Overview

The Color Reduction effect works by:
1. Calculating a bit mask based on the specified number of levels
2. Applying the mask to each color channel (red, green, blue)
3. Reducing the effective color depth from 8 bits per channel to a lower value
4. Creating distinct color bands and posterized effects

## C# Implementation

```csharp
using System;
using System.Drawing;
using PhoenixVisualizer.Core.Effects.Models;
using PhoenixVisualizer.Core.Models;

namespace PhoenixVisualizer.Core.Effects.Nodes.AvsEffects
{
    public class ColorReductionEffectsNode : BaseEffectNode
    {
        #region Properties
        
        /// <summary>
        /// Whether the effect is enabled
        /// </summary>
        public bool Enabled { get; set; } = true;
        
        /// <summary>
        /// Number of color levels (1-8, where 8 = no reduction, 1 = maximum reduction)
        /// </summary>
        public int ColorLevels { get; set; } = 7;
        
        /// <summary>
        /// Effect intensity multiplier
        /// </summary>
        public float Intensity { get; set; } = 1.0f;
        
        /// <summary>
        /// Whether to apply the effect on every frame or only on beats
        /// </summary>
        public bool BeatResponseOnly { get; set; } = false;
        
        /// <summary>
        /// Minimum color value threshold for reduction
        /// </summary>
        public int MinThreshold { get; set; } = 0;
        
        /// <summary>
        /// Maximum color value threshold for reduction
        /// </summary>
        public int MaxThreshold { get; set; } = 255;
        
        #endregion
        
        #region Private Fields
        
        /// <summary>
        /// Pre-calculated bit mask for color reduction
        /// </summary>
        private int _bitMask;
        
        /// <summary>
        /// Number of actual colors after reduction
        /// </summary>
        private int _actualColors;
        
        /// <summary>
        /// Whether the bit mask needs recalculation
        /// </summary>
        private bool _maskDirty = true;
        
        #endregion
        
        #region Constructor
        
        public ColorReductionEffectsNode()
        {
            ColorLevels = 7;
            UpdateBitMask();
        }
        
        #endregion
        
        #region Processing Methods
        
        public override void ProcessFrame(ImageBuffer imageBuffer, AudioFeatures audioFeatures)
        {
            if (!Enabled || imageBuffer == null) return;
            
            // Skip processing if beat response only and no beat detected
            if (BeatResponseOnly && !audioFeatures.IsBeat) return;
            
            // Update bit mask if needed
            if (_maskDirty)
            {
                UpdateBitMask();
            }
            
            ApplyColorReduction(imageBuffer);
        }
        
        /// <summary>
        /// Update the bit mask based on current color levels
        /// </summary>
        private void UpdateBitMask()
        {
            if (ColorLevels < 1 || ColorLevels > 8)
            {
                ColorLevels = Math.Max(1, Math.Min(8, ColorLevels));
            }
            
            // Calculate bit mask: 8 - ColorLevels gives us how many bits to mask
            int bitsToMask = 8 - ColorLevels;
            _bitMask = 0xFF;
            
            // Shift and mask to create the appropriate bit pattern
            for (int i = 0; i < bitsToMask; i++)
            {
                _bitMask = (_bitMask << 1) & 0xFF;
            }
            
            // Calculate actual number of colors after reduction
            _actualColors = 1 << ColorLevels;
            
            _maskDirty = false;
        }
        
        /// <summary>
        /// Apply color reduction to the image buffer
        /// </summary>
        private void ApplyColorReduction(ImageBuffer imageBuffer)
        {
            int width = imageBuffer.Width;
            int height = imageBuffer.Height;
            
            // Create a 32-bit mask for all channels
            int fullMask = _bitMask | (_bitMask << 8) | (_bitMask << 16);
            
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    Color pixel = imageBuffer.GetPixel(x, y);
                    Color reducedPixel = ReducePixelColor(pixel, fullMask);
                    imageBuffer.SetPixel(x, y, reducedPixel);
                }
            }
        }
        
        /// <summary>
        /// Reduce the color of a single pixel using the bit mask
        /// </summary>
        private Color ReducePixelColor(Color pixel, int fullMask)
        {
            // Apply the bit mask to each color channel
            int r = pixel.R & _bitMask;
            int g = pixel.G & _bitMask;
            int b = pixel.B & _bitMask;
            
            // Apply intensity scaling
            if (Intensity != 1.0f)
            {
                r = (int)(r * Intensity);
                g = (int)(g * Intensity);
                b = (int)(b * Intensity);
            }
            
            // Apply threshold limits
            r = Math.Max(MinThreshold, Math.Min(MaxThreshold, r));
            g = Math.Max(MinThreshold, Math.Min(MaxThreshold, g));
            b = Math.Max(MinThreshold, Math.Min(MaxThreshold, b));
            
            return Color.FromArgb(pixel.A, r, g, b);
        }
        
        #endregion
        
        #region Configuration Validation
        
        public override bool ValidateConfiguration()
        {
            if (ColorLevels < 1 || ColorLevels > 8) return false;
            if (MinThreshold < 0 || MinThreshold > 255) return false;
            if (MaxThreshold < 0 || MaxThreshold > 255) return false;
            if (MinThreshold > MaxThreshold) return false;
            if (Intensity < 0.0f || Intensity > 10.0f) return false;
            
            return true;
        }
        
        #endregion
        
        #region Utility Methods
        
        /// <summary>
        /// Get the current number of actual colors after reduction
        /// </summary>
        public int GetActualColorCount()
        {
            if (_maskDirty)
            {
                UpdateBitMask();
            }
            return _actualColors;
        }
        
        /// <summary>
        /// Get the current bit mask value
        /// </summary>
        public int GetBitMask()
        {
            if (_maskDirty)
            {
                UpdateBitMask();
            }
            return _bitMask;
        }
        
        /// <summary>
        /// Set color levels and mark mask as dirty for recalculation
        /// </summary>
        public void SetColorLevels(int levels)
        {
            ColorLevels = levels;
            _maskDirty = true;
        }
        
        /// <summary>
        /// Create a maximum reduction effect (1 color level)
        /// </summary>
        public void SetMaximumReduction()
        {
            ColorLevels = 1;
            _maskDirty = true;
        }
        
        /// <summary>
        /// Create a moderate reduction effect (4 color levels)
        /// </summary>
        public void SetModerateReduction()
        {
            ColorLevels = 4;
            _maskDirty = true;
        }
        
        /// <summary>
        /// Create a minimal reduction effect (6 color levels)
        /// </summary>
        public void SetMinimalReduction()
        {
            ColorLevels = 6;
            _maskDirty = true;
        }
        
        /// <summary>
        /// Disable color reduction (8 color levels)
        /// </summary>
        public void DisableReduction()
        {
            ColorLevels = 8;
            _maskDirty = true;
        }
        
        /// <summary>
        /// Create a high contrast effect with threshold limits
        /// </summary>
        public void SetHighContrastMode()
        {
            MinThreshold = 0;
            MaxThreshold = 255;
            Intensity = 1.5f;
        }
        
        /// <summary>
        /// Create a subtle posterization effect
        /// </summary>
        public void SetPosterizationMode()
        {
            ColorLevels = 5;
            MinThreshold = 32;
            MaxThreshold = 223;
            Intensity = 1.0f;
        }
        
        /// <summary>
        /// Create a vintage film look
        /// </summary>
        public void SetVintageMode()
        {
            ColorLevels = 3;
            MinThreshold = 16;
            MaxThreshold = 239;
            Intensity = 0.8f;
        }
        
        #endregion
        
        #region Advanced Methods
        
        /// <summary>
        /// Apply adaptive color reduction based on image content
        /// </summary>
        public void ApplyAdaptiveReduction(ImageBuffer imageBuffer)
        {
            if (imageBuffer == null) return;
            
            // Analyze image to determine optimal color levels
            int optimalLevels = AnalyzeImageForOptimalLevels(imageBuffer);
            ColorLevels = optimalLevels;
            _maskDirty = true;
            
            // Apply the reduction
            ProcessFrame(imageBuffer, null);
        }
        
        /// <summary>
        /// Analyze image to find optimal color reduction levels
        /// </summary>
        private int AnalyzeImageForOptimalLevels(ImageBuffer imageBuffer)
        {
            int width = imageBuffer.Width;
            int height = imageBuffer.Height;
            
            // Count unique colors
            HashSet<Color> uniqueColors = new HashSet<Color>();
            
            for (int y = 0; y < height; y += 4) // Sample every 4th pixel for performance
            {
                for (int x = 0; x < width; x += 4)
                {
                    uniqueColors.Add(imageBuffer.GetPixel(x, y));
                }
            }
            
            int uniqueColorCount = uniqueColors.Count;
            
            // Determine optimal levels based on unique color count
            if (uniqueColorCount < 16) return 4;
            if (uniqueColorCount < 64) return 6;
            if (uniqueColorCount < 256) return 7;
            
            return 8; // No reduction needed
        }
        
        /// <summary>
        /// Create a custom color palette based on reduced levels
        /// </summary>
        public Color[] GenerateCustomPalette()
        {
            if (_maskDirty)
            {
                UpdateBitMask();
            }
            
            Color[] palette = new Color[_actualColors];
            int step = 256 / _actualColors;
            
            for (int i = 0; i < _actualColors; i++)
            {
                int value = i * step;
                // Apply the bit mask to ensure consistency
                value = value & _bitMask;
                palette[i] = Color.FromArgb(255, value, value, value);
            }
            
            return palette;
        }
        
        /// <summary>
        /// Apply color reduction with dithering for smoother transitions
        /// </summary>
        public void ApplyDitheredReduction(ImageBuffer imageBuffer)
        {
            if (imageBuffer == null) return;
            
            int width = imageBuffer.Width;
            int height = imageBuffer.Height;
            
            // Floyd-Steinberg dithering matrix
            float[,] ditherMatrix = {
                { 0, 0, 7.0f/16.0f },
                { 3.0f/16.0f, 5.0f/16.0f, 1.0f/16.0f }
            };
            
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    Color pixel = imageBuffer.GetPixel(x, y);
                    Color reducedPixel = ReducePixelColor(pixel, 0);
                    
                    // Calculate quantization error
                    int errorR = pixel.R - reducedPixel.R;
                    int errorG = pixel.G - reducedPixel.G;
                    int errorB = pixel.B - reducedPixel.B;
                    
                    // Distribute error to neighboring pixels
                    DistributeDitherError(imageBuffer, x, y, width, height, errorR, errorG, errorB, ditherMatrix);
                    
                    imageBuffer.SetPixel(x, y, reducedPixel);
                }
            }
        }
        
        /// <summary>
        /// Distribute dithering error to neighboring pixels
        /// </summary>
        private void DistributeDitherError(ImageBuffer imageBuffer, int x, int y, int width, int height, 
            int errorR, int errorG, int errorB, float[,] ditherMatrix)
        {
            for (int dy = 0; dy < 2; dy++)
            {
                for (int dx = -1; dx < 2; dx++)
                {
                    int nx = x + dx;
                    int ny = y + dy;
                    
                    if (nx >= 0 && nx < width && ny < height)
                    {
                        float factor = ditherMatrix[dy, dx + 1];
                        if (factor > 0)
                        {
                            Color neighbor = imageBuffer.GetPixel(nx, ny);
                            int newR = (int)(neighbor.R + errorR * factor);
                            int newG = (int)(neighbor.G + errorG * factor);
                            int newB = (int)(neighbor.B + errorB * factor);
                            
                            newR = Math.Max(0, Math.Min(255, newR));
                            newG = Math.Max(0, Math.Min(255, newG));
                            newB = Math.Max(0, Math.Min(255, newB));
                            
                            imageBuffer.SetPixel(nx, ny, Color.FromArgb(neighbor.A, newR, newG, newB));
                        }
                    }
                }
            }
        }
        
        #endregion
    }
}
```

## Effect Properties

### Core Properties
- **Enabled**: Toggle the effect on/off
- **ColorLevels**: Number of color levels (1-8) where lower values create more dramatic reduction
- **Intensity**: Overall effect strength multiplier
- **BeatResponseOnly**: Apply effect only when beats are detected

### Threshold Properties
- **MinThreshold**: Minimum color value after reduction (0-255)
- **MaxThreshold**: Maximum color value after reduction (0-255)

### Internal Properties
- **BitMask**: Pre-calculated bit mask for efficient color reduction
- **ActualColors**: Number of distinct colors after reduction

## Color Level System

The effect uses a sophisticated bit-masking system:

- **Level 8**: No reduction (256 colors per channel)
- **Level 7**: 128 colors per channel (1 bit masked)
- **Level 6**: 64 colors per channel (2 bits masked)
- **Level 5**: 32 colors per channel (3 bits masked)
- **Level 4**: 16 colors per channel (4 bits masked)
- **Level 3**: 8 colors per channel (5 bits masked)
- **Level 2**: 4 colors per channel (6 bits masked)
- **Level 1**: 2 colors per channel (7 bits masked)

## Bit Masking Algorithm

The effect calculates a bit mask using the formula:
```csharp
int bitsToMask = 8 - ColorLevels;
int bitMask = 0xFF;
for (int i = 0; i < bitsToMask; i++)
{
    bitMask = (bitMask << 1) & 0xFF;
}
```

This creates a mask that preserves the most significant bits while zeroing out the least significant bits, effectively reducing color precision.

## Performance Optimizations

- **Pre-calculated Masks**: Bit masks are computed once and reused
- **Efficient Pixel Processing**: Processes pixels using optimized bitwise operations
- **Lazy Evaluation**: Masks are only recalculated when configuration changes
- **Sampling for Analysis**: Adaptive reduction uses pixel sampling for performance

## Use Cases

- **Posterization**: Create artistic poster-like effects with distinct color bands
- **Color Quantization**: Reduce color complexity for retro or vintage looks
- **Performance Optimization**: Reduce color depth for faster processing
- **Artistic Effects**: Create stylized, limited-palette visuals
- **Memory Reduction**: Reduce memory usage in embedded or mobile applications

## Advanced Features

### Adaptive Reduction
The effect can automatically analyze image content to determine optimal color levels, ensuring the best balance between visual quality and color reduction.

### Dithering Support
Optional Floyd-Steinberg dithering creates smoother transitions between color bands, reducing the harshness of color reduction.

### Custom Palettes
Generate custom color palettes based on the reduced color levels, useful for creating consistent visual themes.

### Preset Modes
Pre-configured settings for common effects like vintage film, high contrast, and subtle posterization.
