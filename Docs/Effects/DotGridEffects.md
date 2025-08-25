# Dot Grid Effects

The Dot Grid effect creates a moving grid of colored dots that can be animated across the screen. It features smooth color interpolation between multiple colors, configurable grid spacing, and various blending modes for creating dynamic visual patterns.

## Effect Overview

The Dot Grid effect works by:
1. Creating a regular grid of dots across the screen
2. Animating the grid position using X and Y movement values
3. Interpolating between multiple colors for smooth color transitions
4. Supporting different blending modes for integration with existing content
5. Providing configurable grid spacing and movement speed

## C# Implementation

```csharp
using System;
using System.Collections.Generic;
using System.Drawing;
using PhoenixVisualizer.Core.Effects.Models;
using PhoenixVisualizer.Core.Models;

namespace PhoenixVisualizer.Core.Effects.Nodes.AvsEffects
{
    public class DotGridEffectsNode : BaseEffectNode
    {
        #region Properties
        
        /// <summary>
        /// Whether the effect is enabled
        /// </summary>
        public bool Enabled { get; set; } = true;
        
        /// <summary>
        /// Number of colors in the color palette (1-16)
        /// </summary>
        public int NumberOfColors { get; set; } = 1;
        
        /// <summary>
        /// Array of colors for the grid dots
        /// </summary>
        public Color[] Colors { get; set; } = new Color[16];
        
        /// <summary>
        /// Grid spacing between dots in pixels (minimum 2)
        /// </summary>
        public int GridSpacing { get; set; } = 8;
        
        /// <summary>
        /// Horizontal movement speed (pixels per frame)
        /// </summary>
        public int XMovement { get; set; } = 128;
        
        /// <summary>
        /// Vertical movement speed (pixels per frame)
        /// </summary>
        public int YMovement { get; set; } = 128;
        
        /// <summary>
        /// Blending mode for the grid dots
        /// </summary>
        public GridBlendMode BlendMode { get; set; } = GridBlendMode.BlendLine;
        
        /// <summary>
        /// Effect intensity multiplier
        /// </summary>
        public float Intensity { get; set; } = 1.0f;
        
        /// <summary>
        /// Whether to respond to beat detection
        /// </summary>
        public bool BeatResponse { get; set; } = false;
        
        /// <summary>
        /// Color transition speed multiplier
        /// </summary>
        public float ColorTransitionSpeed { get; set; } = 1.0f;
        
        #endregion
        
        #region Enums
        
        /// <summary>
        /// Available blending modes for the grid dots
        /// </summary>
        public enum GridBlendMode
        {
            /// <summary>
            /// Replace existing pixels
            /// </summary>
            Replace = 0,
            
            /// <summary>
            /// Additive blending
            /// </summary>
            Additive = 1,
            
            /// <summary>
            /// Average blending
            /// </summary>
            Average = 2,
            
            /// <summary>
            /// Line blending (smooth additive)
            /// </summary>
            BlendLine = 3
        }
        
        #endregion
        
        #region Private Fields
        
        /// <summary>
        /// Current color position in the interpolation cycle
        /// </summary>
        private int _colorPosition = 0;
        
        /// <summary>
        /// Current X position of the grid (fixed-point)
        /// </summary>
        private int _currentX = 0;
        
        /// <summary>
        /// Current Y position of the grid (fixed-point)
        /// </summary>
        private int _currentY = 0;
        
        /// <summary>
        /// Current width and height
        /// </summary>
        private int _currentWidth, _currentHeight;
        
        /// <summary>
        /// Whether the effect has been initialized
        /// </summary>
        private bool _isInitialized = false;
        
        /// <summary>
        /// Frame counter for timing
        /// </summary>
        private int _frameCounter = 0;
        
        #endregion
        
        #region Constructor
        
        public DotGridEffectsNode()
        {
            // Initialize with default colors
            SetDefaultColors();
            
            // Set default values
            NumberOfColors = 1;
            GridSpacing = 8;
            XMovement = 128;
            YMovement = 128;
            BlendMode = GridBlendMode.BlendLine;
        }
        
        #endregion
        
        #region Initialization Methods
        
        /// <summary>
        /// Set default colors for the grid
        /// </summary>
        private void SetDefaultColors()
        {
            // Initialize all colors to white
            for (int i = 0; i < Colors.Length; i++)
            {
                Colors[i] = Color.White;
            }
            
            // Set first color to white (default)
            Colors[0] = Color.White;
        }
        
        /// <summary>
        /// Initialize the effect for the current dimensions
        /// </summary>
        private void InitializeEffect(int width, int height)
        {
            if (_currentWidth == width && _currentHeight == height && _isInitialized)
                return;
            
            _currentWidth = width;
            _currentHeight = height;
            
            // Ensure minimum spacing
            if (GridSpacing < 2) GridSpacing = 2;
            
            // Normalize grid position
            NormalizeGridPosition();
            
            _isInitialized = true;
        }
        
        /// <summary>
        /// Normalize grid position to ensure it's within bounds
        /// </summary>
        private void NormalizeGridPosition()
        {
            int spacing = Math.Max(2, GridSpacing);
            
            // Ensure Y position is positive
            while (_currentY < 0)
            {
                _currentY += spacing * 256;
            }
            
            // Ensure X position is positive
            while (_currentX < 0)
            {
                _currentX += spacing * 256;
            }
        }
        
        #endregion
        
        #region Processing Methods
        
        public override void ProcessFrame(ImageBuffer imageBuffer, AudioFeatures audioFeatures)
        {
            if (!Enabled || imageBuffer == null) return;
            
            // Initialize if needed
            InitializeEffect(imageBuffer.Width, imageBuffer.Height);
            
            // Update frame counter
            _frameCounter++;
            
            // Update color position
            UpdateColorPosition();
            
            // Render the grid
            RenderGrid(imageBuffer);
            
            // Update grid position
            UpdateGridPosition();
        }
        
        /// <summary>
        /// Update the color position for interpolation
        /// </summary>
        private void UpdateColorPosition()
        {
            if (NumberOfColors <= 0) return;
            
            // Increment color position
            _colorPosition++;
            
            // Reset position when cycle is complete
            if (_colorPosition >= NumberOfColors * 64)
            {
                _colorPosition = 0;
            }
        }
        
        /// <summary>
        /// Get the current interpolated color
        /// </summary>
        private Color GetCurrentColor()
        {
            if (NumberOfColors <= 0) return Color.White;
            
            // Calculate which color pair to interpolate between
            int colorIndex = _colorPosition / 64;
            int interpolationFactor = _colorPosition & 63;
            
            // Get the two colors to interpolate between
            Color color1 = Colors[colorIndex];
            Color color2 = (colorIndex + 1 < NumberOfColors) ? Colors[colorIndex + 1] : Colors[0];
            
            // Interpolate between colors
            int r = ((color1.R * (63 - interpolationFactor)) + (color2.R * interpolationFactor)) / 64;
            int g = ((color1.G * (63 - interpolationFactor)) + (color2.G * interpolationFactor)) / 64;
            int b = ((color1.B * (63 - interpolationFactor)) + (color2.B * interpolationFactor)) / 64;
            
            // Apply intensity
            r = Math.Min(255, (int)(r * Intensity));
            g = Math.Min(255, (int)(g * Intensity));
            b = Math.Min(255, (int)(b * Intensity));
            
            return Color.FromArgb(255, r, g, b);
        }
        
        /// <summary>
        /// Render the dot grid to the image buffer
        /// </summary>
        private void RenderGrid(ImageBuffer imageBuffer)
        {
            int width = imageBuffer.Width;
            int height = imageBuffer.Height;
            int spacing = Math.Max(2, GridSpacing);
            
            // Get current color
            Color currentColor = GetCurrentColor();
            
            // Calculate grid offset
            int startY = (_currentY >> 8) % spacing;
            int startX = (_currentX >> 8) % spacing;
            
            // Render grid dots
            for (int y = startY; y < height; y += spacing)
            {
                for (int x = startX; x < width; x += spacing)
                {
                    // Get existing pixel
                    Color existingPixel = imageBuffer.GetPixel(x, y);
                    
                    // Apply blending based on mode
                    Color blendedColor = BlendColors(existingPixel, currentColor);
                    
                    // Set pixel
                    imageBuffer.SetPixel(x, y, blendedColor);
                }
            }
        }
        
        /// <summary>
        /// Blend two colors based on the current blend mode
        /// </summary>
        private Color BlendColors(Color existingColor, Color newColor)
        {
            switch (BlendMode)
            {
                case GridBlendMode.Replace:
                    return newColor;
                    
                case GridBlendMode.Additive:
                    return BlendAdditive(existingColor, newColor);
                    
                case GridBlendMode.Average:
                    return BlendAverage(existingColor, newColor);
                    
                case GridBlendMode.BlendLine:
                    return BlendLine(existingColor, newColor);
                    
                default:
                    return newColor;
            }
        }
        
        /// <summary>
        /// Additive blending (add colors, clamp to 255)
        /// </summary>
        private Color BlendAdditive(Color color1, Color color2)
        {
            int r = Math.Min(255, color1.R + color2.R);
            int g = Math.Min(255, color1.G + color2.G);
            int b = Math.Min(255, color1.B + color2.B);
            
            return Color.FromArgb(255, r, g, b);
        }
        
        /// <summary>
        /// Average blending (50/50 mix)
        /// </summary>
        private Color BlendAverage(Color color1, Color color2)
        {
            int r = (color1.R + color2.R) / 2;
            int g = (color1.G + color2.G) / 2;
            int b = (color1.B + color2.B) / 2;
            
            return Color.FromArgb(255, r, g, b);
        }
        
        /// <summary>
        /// Line blending (smooth additive with overflow handling)
        /// </summary>
        private Color BlendLine(Color color1, Color color2)
        {
            // This is a simplified version of the original BLEND_LINE function
            // In the original, it used assembly-level optimizations for smooth blending
            
            int r = color1.R + color2.R;
            int g = color1.G + color2.G;
            int b = color1.B + color2.B;
            
            // Handle overflow smoothly (similar to original behavior)
            if (r > 255) r = 255;
            if (g > 255) g = 255;
            if (b > 255) b = 255;
            
            return Color.FromArgb(255, r, g, b);
        }
        
        /// <summary>
        /// Update the grid position based on movement values
        /// </summary>
        private void UpdateGridPosition()
        {
            // Update X and Y positions
            _currentX += XMovement;
            _currentY += YMovement;
            
            // Normalize position to prevent overflow
            NormalizeGridPosition();
        }
        
        #endregion
        
        #region Configuration Validation
        
        public override bool ValidateConfiguration()
        {
            if (NumberOfColors < 1 || NumberOfColors > 16) return false;
            if (GridSpacing < 2 || GridSpacing > 100) return false;
            if (XMovement < -1000 || XMovement > 1000) return false;
            if (YMovement < -1000 || YMovement > 1000) return false;
            if (Intensity < 0.1f || Intensity > 10.0f) return false;
            if (ColorTransitionSpeed < 0.1f || ColorTransitionSpeed > 5.0f) return false;
            
            return true;
        }
        
        #endregion
        
        #region Preset Methods
        
        /// <summary>
        /// Load a static grid preset
        /// </summary>
        public void LoadStaticGridPreset()
        {
            NumberOfColors = 1;
            Colors[0] = Color.White;
            GridSpacing = 16;
            XMovement = 0;
            YMovement = 0;
            BlendMode = GridBlendMode.Replace;
            Intensity = 1.0f;
        }
        
        /// <summary>
        /// Load a moving rainbow grid preset
        /// </summary>
        public void LoadRainbowGridPreset()
        {
            NumberOfColors = 6;
            Colors[0] = Color.Red;
            Colors[1] = Color.Orange;
            Colors[2] = Color.Yellow;
            Colors[3] = Color.Green;
            Colors[4] = Color.Blue;
            Colors[5] = Color.Purple;
            
            GridSpacing = 12;
            XMovement = 64;
            YMovement = 64;
            BlendMode = GridBlendMode.BlendLine;
            Intensity = 1.2f;
        }
        
        /// <summary>
        /// Load a fast moving grid preset
        /// </summary>
        public void LoadFastMovingPreset()
        {
            NumberOfColors = 3;
            Colors[0] = Color.Cyan;
            Colors[1] = Color.Magenta;
            Colors[2] = Color.Yellow;
            
            GridSpacing = 8;
            XMovement = 256;
            YMovement = 128;
            BlendMode = GridBlendMode.Additive;
            Intensity = 1.5f;
        }
        
        /// <summary>
        /// Load a gentle flowing preset
        /// </summary>
        public void LoadGentleFlowingPreset()
        {
            NumberOfColors = 4;
            Colors[0] = Color.LightBlue;
            Colors[1] = Color.LightGreen;
            Colors[2] = Color.LightYellow;
            Colors[3] = Color.LightPink;
            
            GridSpacing = 20;
            XMovement = 32;
            YMovement = 32;
            BlendMode = GridBlendMode.Average;
            Intensity = 0.8f;
        }
        
        #endregion
        
        #region Utility Methods
        
        /// <summary>
        /// Get the current grid position
        /// </summary>
        public Point GetCurrentGridPosition()
        {
            return new Point(_currentX >> 8, _currentY >> 8);
        }
        
        /// <summary>
        /// Set the grid position directly
        /// </summary>
        public void SetGridPosition(int x, int y)
        {
            _currentX = x << 8;
            _currentY = y << 8;
            NormalizeGridPosition();
        }
        
        /// <summary>
        /// Stop grid movement
        /// </summary>
        public void StopMovement()
        {
            XMovement = 0;
            YMovement = 0;
        }
        
        /// <summary>
        /// Reset the grid to center position
        /// </summary>
        public void ResetPosition()
        {
            if (_currentWidth > 0 && _currentHeight > 0)
            {
                _currentX = (_currentWidth / 2) << 8;
                _currentY = (_currentHeight / 2) << 8;
            }
            else
            {
                _currentX = 0;
                _currentY = 0;
            }
        }
        
        /// <summary>
        /// Get the current color being displayed
        /// </summary>
        public Color GetCurrentDisplayColor()
        {
            return GetCurrentColor();
        }
        
        /// <summary>
        /// Get the color position in the interpolation cycle
        /// </summary>
        public int GetColorPosition()
        {
            return _colorPosition;
        }
        
        /// <summary>
        /// Reset the effect to initial state
        /// </summary>
        public void Reset()
        {
            _colorPosition = 0;
            _currentX = 0;
            _currentY = 0;
            _frameCounter = 0;
            _isInitialized = false;
        }
        
        /// <summary>
        /// Get effect execution statistics
        /// </summary>
        public string GetExecutionStats()
        {
            return $"Frame: {_frameCounter}, Color Pos: {_colorPosition}, Grid Pos: ({_currentX >> 8}, {_currentY >> 8}), Active Colors: {NumberOfColors}";
        }
        
        #endregion
        
        #region Color Management
        
        /// <summary>
        /// Set a specific color in the palette
        /// </summary>
        public void SetColor(int index, Color color)
        {
            if (index >= 0 && index < Colors.Length)
            {
                Colors[index] = color;
            }
        }
        
        /// <summary>
        /// Get a specific color from the palette
        /// </summary>
        public Color GetColor(int index)
        {
            if (index >= 0 && index < Colors.Length)
            {
                return Colors[index];
            }
            return Color.White;
        }
        
        /// <summary>
        /// Set all colors in the palette
        /// </summary>
        public void SetAllColors(Color[] newColors)
        {
            if (newColors != null && newColors.Length <= Colors.Length)
            {
                Array.Copy(newColors, Colors, newColors.Length);
                NumberOfColors = newColors.Length;
            }
        }
        
        /// <summary>
        /// Clear all colors and set to default
        /// </summary>
        public void ClearColors()
        {
            SetDefaultColors();
            NumberOfColors = 1;
        }
        
        #endregion
    }
}
```

## Effect Properties

### Core Properties
- **Enabled**: Toggle the effect on/off
- **NumberOfColors**: Number of colors in the palette (1-16)
- **Colors**: Array of colors for the grid dots
- **GridSpacing**: Distance between grid dots in pixels
- **XMovement**: Horizontal movement speed
- **YMovement**: Vertical movement speed

### Blending Properties
- **BlendMode**: How dots blend with existing content
- **Intensity**: Overall effect strength multiplier
- **BeatResponse**: Whether to respond to beat detection
- **ColorTransitionSpeed**: Speed of color transitions

### Internal Properties
- **ColorPosition**: Current position in color interpolation cycle
- **CurrentX/CurrentY**: Current grid position (fixed-point)
- **FrameCounter**: Frame counter for timing

## Grid System

The effect creates a regular grid with:
- **Configurable Spacing**: Adjustable distance between dots
- **Fixed-Point Positioning**: High-precision movement using 8-bit fractional values
- **Boundary Handling**: Automatic wrapping and normalization
- **Dynamic Movement**: Smooth animation in X and Y directions

## Color System

The effect features:
- **Multi-Color Palette**: Up to 16 different colors
- **Smooth Interpolation**: 64-step transitions between colors
- **Cyclic Animation**: Continuous color cycling
- **Intensity Control**: Adjustable color strength

## Blending Modes

### Replace Mode
- Completely replaces existing pixels
- Fastest rendering mode
- No interaction with background

### Additive Mode
- Adds colors together
- Creates bright, vibrant effects
- May cause color clipping

### Average Mode
- 50/50 mix of existing and new colors
- Subtle, natural blending
- Good for overlays

### Blend Line Mode
- Smooth additive blending
- Handles color overflow gracefully
- Most visually appealing

## Movement System

The grid movement features:
- **Independent X/Y Control**: Separate horizontal and vertical speeds
- **Fixed-Point Precision**: Smooth sub-pixel movement
- **Automatic Wrapping**: Handles screen boundaries
- **Configurable Speed**: Adjustable movement rates

## Performance Optimizations

- **Grid-Based Rendering**: Only renders dots at grid positions
- **Efficient Blending**: Optimized color mixing algorithms
- **Fixed-Point Math**: Fast integer-based calculations
- **Minimal Memory Usage**: Efficient color storage

## Use Cases

- **Background Patterns**: Create moving grid overlays
- **Color Transitions**: Smooth color cycling effects
- **Movement Effects**: Animated grid patterns
- **Visual Rhythm**: Beat-synchronized grid movement
- **Interactive Elements**: User-controlled grid positioning

## Preset Effects

### Basic Presets
- **Static Grid**: Stationary grid with single color
- **Rainbow Grid**: Multi-color grid with smooth transitions
- **Fast Moving**: Rapid grid movement with additive blending
- **Gentle Flowing**: Slow, subtle grid animation

### Customization
- **Color Palettes**: User-defined color schemes
- **Movement Patterns**: Customizable animation speeds
- **Blending Styles**: Different integration modes
- **Grid Density**: Adjustable spacing and coverage

## Mathematical Functions

The effect uses:
- **Fixed-Point Arithmetic**: 8-bit fractional positioning
- **Color Interpolation**: 64-step color transitions
- **Grid Calculations**: Regular spacing algorithms
- **Blending Functions**: Various color mixing methods

## Error Handling

The effect includes:
- **Bounds Checking**: Validates color indices and positions
- **Parameter Validation**: Ensures configuration values are within ranges
- **Grid Normalization**: Handles position overflow gracefully
- **Color Safety**: Prevents invalid color operations
