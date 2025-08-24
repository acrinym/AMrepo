# Color Replace Effects

The Color Replace effect (also known as Color Clip) replaces colors below a specified threshold with a custom replacement color. It works by analyzing the RGB values of each pixel and replacing colors that fall below the threshold values with the specified replacement color.

## Effect Overview

The Color Replace effect works by:
1. Setting a color threshold for red, green, and blue channels
2. Analyzing each pixel's RGB values
3. Replacing pixels where all channels are below their respective thresholds
4. Preserving the original alpha channel during replacement

## C# Implementation

```csharp
using System;
using System.Drawing;
using PhoenixVisualizer.Core.Effects.Models;
using PhoenixVisualizer.Core.Models;

namespace PhoenixVisualizer.Core.Effects.Nodes.AvsEffects
{
    public class ColorReplaceEffectsNode : BaseEffectNode
    {
        #region Properties
        
        /// <summary>
        /// Whether the effect is enabled
        /// </summary>
        public bool Enabled { get; set; } = true;
        
        /// <summary>
        /// Color threshold for replacement (RGB values below this will be replaced)
        /// </summary>
        public Color ColorThreshold { get; set; } = Color.FromArgb(255, 32, 32, 32);
        
        /// <summary>
        /// Color to replace threshold colors with
        /// </summary>
        public Color ReplacementColor { get; set; } = Color.FromArgb(255, 128, 128, 128);
        
        /// <summary>
        /// Effect intensity multiplier
        /// </summary>
        public float Intensity { get; set; } = 1.0f;
        
        /// <summary>
        /// Whether to apply the effect on every frame or only on beats
        /// </summary>
        public bool BeatResponseOnly { get; set; } = false;
        
        /// <summary>
        /// Threshold tolerance for color matching
        /// </summary>
        public int Tolerance { get; set; } = 0;
        
        /// <summary>
        /// Whether to use individual channel thresholds or combined threshold
        /// </summary>
        public bool UseIndividualThresholds { get; set; } = true;
        
        /// <summary>
        /// Individual threshold values for red, green, and blue channels
        /// </summary>
        public int[] IndividualThresholds { get; set; } = { 32, 32, 32 };
        
        #endregion
        
        #region Private Fields
        
        /// <summary>
        /// Cached threshold values for performance
        /// </summary>
        private int _thresholdR, _thresholdG, _thresholdB;
        
        /// <summary>
        /// Cached replacement color values for performance
        /// </summary>
        private int _replacementR, _replacementG, _replacementB;
        
        /// <summary>
        /// Whether cached values need updating
        /// </summary>
        private bool _cacheDirty = true;
        
        #endregion
        
        #region Constructor
        
        public ColorReplaceEffectsNode()
        {
            ColorThreshold = Color.FromArgb(255, 32, 32, 32);
            ReplacementColor = Color.FromArgb(255, 128, 128, 128);
            IndividualThresholds = new int[] { 32, 32, 32 };
            UpdateCache();
        }
        
        #endregion
        
        #region Processing Methods
        
        public override void ProcessFrame(ImageBuffer imageBuffer, AudioFeatures audioFeatures)
        {
            if (!Enabled || imageBuffer == null) return;
            
            // Skip processing if beat response only and no beat detected
            if (BeatResponseOnly && !audioFeatures.IsBeat) return;
            
            // Update cached values if needed
            if (_cacheDirty)
            {
                UpdateCache();
            }
            
            ApplyColorReplacement(imageBuffer);
        }
        
        /// <summary>
        /// Update cached threshold and replacement values for performance
        /// </summary>
        private void UpdateCache()
        {
            if (UseIndividualThresholds)
            {
                _thresholdR = IndividualThresholds[0];
                _thresholdG = IndividualThresholds[1];
                _thresholdB = IndividualThresholds[2];
            }
            else
            {
                _thresholdR = ColorThreshold.R;
                _thresholdG = ColorThreshold.G;
                _thresholdB = ColorThreshold.B;
            }
            
            _replacementR = ReplacementColor.R;
            _replacementG = ReplacementColor.G;
            _replacementB = ReplacementColor.B;
            
            _cacheDirty = false;
        }
        
        /// <summary>
        /// Apply color replacement to the image buffer
        /// </summary>
        private void ApplyColorReplacement(ImageBuffer imageBuffer)
        {
            int width = imageBuffer.Width;
            int height = imageBuffer.Height;
            
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    Color pixel = imageBuffer.GetPixel(x, y);
                    Color replacedPixel = ReplacePixelColor(pixel);
                    imageBuffer.SetPixel(x, y, replacedPixel);
                }
            }
        }
        
        /// <summary>
        /// Replace a single pixel's color if it meets the threshold criteria
        /// </summary>
        private Color ReplacePixelColor(Color pixel)
        {
            int r = pixel.R;
            int g = pixel.G;
            int b = pixel.B;
            
            // Check if pixel meets replacement criteria
            bool shouldReplace = ShouldReplacePixel(r, g, b);
            
            if (shouldReplace)
            {
                // Apply intensity scaling to replacement color
                if (Intensity != 1.0f)
                {
                    int newR = (int)(_replacementR * Intensity);
                    int newG = (int)(_replacementG * Intensity);
                    int newB = (int)(_replacementB * Intensity);
                    
                    // Clamp values to valid range
                    newR = Math.Max(0, Math.Min(255, newR));
                    newG = Math.Max(0, Math.Min(255, newG));
                    newB = Math.Max(0, Math.Min(255, newB));
                    
                    return Color.FromArgb(pixel.A, newR, newG, newB);
                }
                else
                {
                    return Color.FromArgb(pixel.A, _replacementR, _replacementG, _replacementB);
                }
            }
            
            return pixel; // No replacement needed
        }
        
        /// <summary>
        /// Determine if a pixel should be replaced based on threshold values
        /// </summary>
        private bool ShouldReplacePixel(int r, int g, int b)
        {
            if (Tolerance > 0)
            {
                // Use tolerance-based comparison
                return (r <= _thresholdR + Tolerance) && 
                       (g <= _thresholdG + Tolerance) && 
                       (b <= _thresholdB + Tolerance);
            }
            else
            {
                // Exact threshold comparison
                return (r <= _thresholdR) && (g <= _thresholdG) && (b <= _thresholdB);
            }
        }
        
        #endregion
        
        #region Configuration Validation
        
        public override bool ValidateConfiguration()
        {
            if (IndividualThresholds == null || IndividualThresholds.Length != 3) return false;
            if (IndividualThresholds[0] < 0 || IndividualThresholds[0] > 255) return false;
            if (IndividualThresholds[1] < 0 || IndividualThresholds[1] > 255) return false;
            if (IndividualThresholds[2] < 0 || IndividualThresholds[2] > 255) return false;
            if (Tolerance < 0 || Tolerance > 255) return false;
            if (Intensity < 0.0f || Intensity > 10.0f) return false;
            
            return true;
        }
        
        #endregion
        
        #region Utility Methods
        
        /// <summary>
        /// Set threshold values for all channels at once
        /// </summary>
        public void SetThreshold(int threshold)
        {
            IndividualThresholds[0] = threshold;
            IndividualThresholds[1] = threshold;
            IndividualThresholds[2] = threshold;
            _cacheDirty = true;
        }
        
        /// <summary>
        /// Set individual channel thresholds
        /// </summary>
        public void SetThresholds(int red, int green, int blue)
        {
            IndividualThresholds[0] = red;
            IndividualThresholds[1] = green;
            IndividualThresholds[2] = blue;
            _cacheDirty = true;
        }
        
        /// <summary>
        /// Set replacement color from RGB values
        /// </summary>
        public void SetReplacementColor(int red, int green, int blue)
        {
            ReplacementColor = Color.FromArgb(255, red, green, blue);
            _cacheDirty = true;
        }
        
        /// <summary>
        /// Create a black and white effect by replacing dark colors with black
        /// </summary>
        public void SetBlackAndWhiteMode()
        {
            SetThreshold(64);
            ReplacementColor = Color.Black;
            _cacheDirty = true;
        }
        
        /// <summary>
        /// Create a high contrast effect by replacing mid-tones with white
        /// </summary>
        public void SetHighContrastMode()
        {
            SetThreshold(128);
            ReplacementColor = Color.White;
            _cacheDirty = true;
        }
        
        /// <summary>
        /// Create a sepia effect by replacing blue tones with brown
        /// </summary>
        public void SetSepiaMode()
        {
            SetThresholds(64, 64, 32);
            ReplacementColor = Color.FromArgb(255, 139, 69, 19); // Saddle Brown
            _cacheDirty = true;
        }
        
        /// <summary>
        /// Create a night vision effect by replacing dark colors with green
        /// </summary>
        public void SetNightVisionMode()
        {
            SetThreshold(48);
            ReplacementColor = Color.FromArgb(255, 0, 255, 0); // Bright Green
            _cacheDirty = true;
        }
        
        /// <summary>
        /// Create a fire effect by replacing cool colors with warm colors
        /// </summary>
        public void SetFireMode()
        {
            SetThresholds(64, 64, 128);
            ReplacementColor = Color.FromArgb(255, 255, 69, 0); // Orange Red
            _cacheDirty = true;
        }
        
        /// <summary>
        /// Create an ice effect by replacing warm colors with cool colors
        /// </summary>
        public void SetIceMode()
        {
            SetThresholds(128, 64, 64);
            ReplacementColor = Color.FromArgb(255, 135, 206, 235); // Sky Blue
            _cacheDirty = true;
        }
        
        #endregion
        
        #region Advanced Methods
        
        /// <summary>
        /// Apply color replacement with smooth blending for gradual transitions
        /// </summary>
        public void ApplySmoothReplacement(ImageBuffer imageBuffer)
        {
            if (imageBuffer == null) return;
            
            int width = imageBuffer.Width;
            int height = imageBuffer.Height;
            
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    Color pixel = imageBuffer.GetPixel(x, y);
                    Color replacedPixel = ApplySmoothReplacement(pixel);
                    imageBuffer.SetPixel(x, y, replacedPixel);
                }
            }
        }
        
        /// <summary>
        /// Apply smooth color replacement with blending based on threshold distance
        /// </summary>
        private Color ApplySmoothReplacement(Color pixel)
        {
            int r = pixel.R;
            int g = pixel.G;
            int b = pixel.B;
            
            // Calculate distance from threshold
            float distanceR = Math.Max(0, _thresholdR - r) / (float)_thresholdR;
            float distanceG = Math.Max(0, _thresholdG - g) / (float)_thresholdG;
            float distanceB = Math.Max(0, _thresholdB - b) / (float)_thresholdB;
            
            // Use the maximum distance to determine blend factor
            float blendFactor = Math.Max(distanceR, Math.Max(distanceG, distanceB));
            
            if (blendFactor > 0)
            {
                // Blend between original and replacement color
                int newR = (int)(r + (_replacementR - r) * blendFactor);
                int newG = (int)(g + (_replacementG - g) * blendFactor);
                int newB = (int)(b + (_replacementB - b) * blendFactor);
                
                // Apply intensity scaling
                if (Intensity != 1.0f)
                {
                    newR = (int)(newR * Intensity);
                    newG = (int)(newG * Intensity);
                    newB = (int)(newB * Intensity);
                }
                
                // Clamp values
                newR = Math.Max(0, Math.Min(255, newR));
                newG = Math.Max(0, Math.Min(255, newG));
                newB = Math.Max(0, Math.Min(255, newB));
                
                return Color.FromArgb(pixel.A, newR, newG, newB);
            }
            
            return pixel;
        }
        
        /// <summary>
        /// Apply color replacement with selective channel processing
        /// </summary>
        public void ApplySelectiveReplacement(ImageBuffer imageBuffer, bool processRed, bool processGreen, bool processBlue)
        {
            if (imageBuffer == null) return;
            
            int width = imageBuffer.Width;
            int height = imageBuffer.Height;
            
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    Color pixel = imageBuffer.GetPixel(x, y);
                    Color replacedPixel = ApplySelectiveReplacement(pixel, processRed, processGreen, processBlue);
                    imageBuffer.SetPixel(x, y, replacedPixel);
                }
            }
        }
        
        /// <summary>
        /// Apply selective color replacement to specific channels
        /// </summary>
        private Color ApplySelectiveReplacement(Color pixel, bool processRed, bool processGreen, bool processBlue)
        {
            int r = pixel.R;
            int g = pixel.G;
            int b = pixel.B;
            
            bool shouldReplace = false;
            
            // Check if any enabled channel meets replacement criteria
            if (processRed && r <= _thresholdR) shouldReplace = true;
            if (processGreen && g <= _thresholdG) shouldReplace = true;
            if (processBlue && b <= _thresholdB) shouldReplace = true;
            
            if (shouldReplace)
            {
                int newR = processRed ? _replacementR : r;
                int newG = processGreen ? _replacementG : g;
                int newB = processBlue ? _replacementB : b;
                
                // Apply intensity scaling
                if (Intensity != 1.0f)
                {
                    if (processRed) newR = (int)(newR * Intensity);
                    if (processGreen) newG = (int)(newG * Intensity);
                    if (processBlue) newB = (int)(newB * Intensity);
                }
                
                // Clamp values
                newR = Math.Max(0, Math.Min(255, newR));
                newG = Math.Max(0, Math.Min(255, newG));
                newB = Math.Max(0, Math.Min(255, newB));
                
                return Color.FromArgb(pixel.A, newR, newG, newB);
            }
            
            return pixel;
        }
        
        /// <summary>
        /// Create a custom color palette based on threshold analysis
        /// </summary>
        public Color[] GenerateThresholdPalette()
        {
            Color[] palette = new Color[256];
            
            for (int i = 0; i < 256; i++)
            {
                if (i <= _thresholdR && i <= _thresholdG && i <= _thresholdB)
                {
                    palette[i] = ReplacementColor;
                }
                else
                {
                    palette[i] = Color.FromArgb(255, i, i, i);
                }
            }
            
            return palette;
        }
        
        #endregion
    }
}
```

## Effect Properties

### Core Properties
- **Enabled**: Toggle the effect on/off
- **ColorThreshold**: Color threshold for replacement (RGB values below this will be replaced)
- **ReplacementColor**: Color to replace threshold colors with
- **Intensity**: Overall effect strength multiplier
- **BeatResponseOnly**: Apply effect only when beats are detected

### Threshold Properties
- **Tolerance**: Threshold tolerance for color matching (0-255)
- **UseIndividualThresholds**: Whether to use individual channel thresholds or combined threshold
- **IndividualThresholds**: Array of three integers (0-255) for red, green, and blue channel thresholds

### Internal Properties
- **ThresholdR/G/B**: Cached threshold values for performance
- **ReplacementR/G/B**: Cached replacement color values for performance

## Color Replacement Logic

The effect uses a sophisticated threshold-based replacement system:

1. **Threshold Analysis**: Each pixel's RGB values are compared against the threshold values
2. **Replacement Criteria**: Pixels where all channels are below their respective thresholds are replaced
3. **Color Preservation**: The original alpha channel is preserved during replacement
4. **Intensity Scaling**: Replacement colors can be scaled by the intensity multiplier

## Threshold Modes

### Individual Channel Thresholds
When `UseIndividualThresholds` is enabled, each color channel has its own threshold:
- Red channel threshold: `IndividualThresholds[0]`
- Green channel threshold: `IndividualThresholds[1]`
- Blue channel threshold: `IndividualThresholds[2]`

### Combined Threshold
When `UseIndividualThresholds` is disabled, all channels use the same threshold from `ColorThreshold`.

## Tolerance System

The tolerance value allows for more flexible color matching:
- **Tolerance = 0**: Exact threshold matching
- **Tolerance > 0**: Colors within tolerance range of threshold are also replaced

## Performance Optimizations

- **Cached Values**: Threshold and replacement values are cached for faster processing
- **Efficient Pixel Processing**: Processes pixels using optimized color operations
- **Lazy Cache Updates**: Cached values are only updated when configuration changes
- **Selective Processing**: Optional selective channel processing for targeted effects

## Use Cases

- **Color Correction**: Replace unwanted colors with preferred alternatives
- **Artistic Effects**: Create stylized color schemes and palettes
- **Image Enhancement**: Improve contrast and visual appeal
- **Color Isolation**: Isolate specific color ranges for special effects
- **Thematic Consistency**: Maintain consistent color themes across visualizations

## Advanced Features

### Smooth Blending
Optional smooth blending creates gradual transitions between original and replacement colors, reducing harsh color boundaries.

### Selective Channel Processing
Process only specific color channels, allowing for targeted color manipulation while preserving others.

### Preset Modes
Pre-configured settings for common effects like black and white, high contrast, sepia, night vision, fire, and ice effects.

### Custom Palettes
Generate custom color palettes based on threshold analysis, useful for creating consistent visual themes.
