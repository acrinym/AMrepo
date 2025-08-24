# Fade Out Effects

The Fade Out effect gradually reduces the brightness of pixels in an image, either fading them toward a specific color or simply darkening them. It creates a smooth transition effect that can be used for transitions, mood lighting, or gradual image dimming.

## Effect Overview

The Fade Out effect works by:
1. Creating lookup tables for each color channel (red, green, blue)
2. Processing each pixel to gradually move its color values toward a target color
3. Supporting both color-based fading and simple brightness reduction
4. Using optimized processing for different color modes
5. Providing configurable fade length and target color

## C# Implementation

```csharp
using System;
using System.Collections.Generic;
using System.Drawing;
using PhoenixVisualizer.Core.Effects.Models;
using PhoenixVisualizer.Core.Models;

namespace PhoenixVisualizer.Core.Effects.Nodes.AvsEffects
{
    public class FadeOutEffectsNode : BaseEffectNode
    {
        #region Properties
        
        /// <summary>
        /// Whether the effect is enabled
        /// </summary>
        public bool Enabled { get; set; } = true;
        
        /// <summary>
        /// Length of the fade effect (0-92)
        /// </summary>
        public int FadeLength { get; set; } = 16;
        
        /// <summary>
        /// Target color to fade toward (0 = simple brightness reduction)
        /// </summary>
        public Color TargetColor { get; set; } = Color.Black;
        
        /// <summary>
        /// Effect intensity multiplier
        /// </summary>
        public float Intensity { get; set; } = 1.0f;
        
        /// <summary>
        /// Whether to use color-based fading
        /// </summary>
        public bool UseColorFading { get; set; } = true;
        
        /// <summary>
        /// Fade mode for the effect
        /// </summary>
        public FadeMode Mode { get; set; } = FadeMode.ColorBased;
        
        /// <summary>
        /// Whether to respond to beat detection
        /// </summary>
        public bool BeatResponse { get; set; } = false;
        
        /// <summary>
        /// Beat response intensity multiplier
        /// </summary>
        public float BeatIntensity { get; set; } = 1.0f;
        
        #endregion
        
        #region Enums
        
        /// <summary>
        /// Available fade modes for the effect
        /// </summary>
        public enum FadeMode
        {
            /// <summary>
            /// Simple brightness reduction
            /// </summary>
            BrightnessReduction = 0,
            
            /// <summary>
            /// Fade toward target color
            /// </summary>
            ColorBased = 1,
            
            /// <summary>
            /// Adaptive fading based on pixel values
            /// </summary>
            Adaptive = 2
        }
        
        #endregion
        
        #region Private Fields
        
        /// <summary>
        /// Pre-calculated fade lookup tables for each color channel
        /// </summary>
        private byte[,] _fadeTables;
        
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
        
        /// <summary>
        /// Whether fade tables need regeneration
        /// </summary>
        private bool _fadeTablesNeedUpdate = true;
        
        #endregion
        
        #region Constructor
        
        public FadeOutEffectsNode()
        {
            _fadeTables = new byte[3, 256];
            
            // Set default values
            FadeLength = 16;
            TargetColor = Color.Black;
            UseColorFading = true;
            Mode = FadeMode.ColorBased;
        }
        
        #endregion
        
        #region Initialization Methods
        
        /// <summary>
        /// Initialize the effect for the current dimensions
        /// </summary>
        private void InitializeEffect(int width, int height)
        {
            if (_currentWidth == width && _currentHeight == height && _isInitialized)
                return;
            
            _currentWidth = width;
            _currentHeight = height;
            _isInitialized = true;
        }
        
        /// <summary>
        /// Generate fade lookup tables for efficient processing
        /// </summary>
        private void GenerateFadeTables()
        {
            if (!_fadeTablesNeedUpdate) return;
            
            int fadeLength = Math.Max(0, Math.Min(92, FadeLength));
            
            if (UseColorFading && TargetColor != Color.Black)
            {
                // Generate color-based fade tables
                GenerateColorBasedFadeTables(fadeLength);
            }
            else
            {
                // Generate simple brightness reduction tables
                GenerateBrightnessReductionTables(fadeLength);
            }
            
            _fadeTablesNeedUpdate = false;
        }
        
        /// <summary>
        /// Generate fade tables for color-based fading
        /// </summary>
        private void GenerateColorBasedFadeTables(int fadeLength)
        {
            int targetRed = TargetColor.R;
            int targetGreen = TargetColor.G;
            int targetBlue = TargetColor.B;
            
            for (int x = 0; x < 256; x++)
            {
                // Calculate red channel fade
                int red = x;
                if (red <= targetRed - fadeLength)
                    red += fadeLength;
                else if (red >= targetRed + fadeLength)
                    red -= fadeLength;
                else
                    red = targetRed;
                
                // Calculate green channel fade
                int green = x;
                if (green <= targetGreen - fadeLength)
                    green += fadeLength;
                else if (green >= targetGreen + fadeLength)
                    green -= fadeLength;
                else
                    green = targetGreen;
                
                // Calculate blue channel fade
                int blue = x;
                if (blue <= targetBlue - fadeLength)
                    blue += fadeLength;
                else if (blue >= targetBlue + fadeLength)
                    blue -= fadeLength;
                else
                    blue = targetBlue;
                
                // Clamp values and store in tables
                _fadeTables[0, x] = (byte)Math.Max(0, Math.Min(255, red));
                _fadeTables[1, x] = (byte)Math.Max(0, Math.Min(255, green));
                _fadeTables[2, x] = (byte)Math.Max(0, Math.Min(255, blue));
            }
        }
        
        /// <summary>
        /// Generate fade tables for simple brightness reduction
        /// </summary>
        private void GenerateBrightnessReductionTables(int fadeLength)
        {
            for (int x = 0; x < 256; x++)
            {
                // Simple brightness reduction
                int value = Math.Max(0, x - fadeLength);
                
                _fadeTables[0, x] = (byte)value;  // Red
                _fadeTables[1, x] = (byte)value;  // Green
                _fadeTables[2, x] = (byte)value;  // Blue
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
            
            // Update fade tables if needed
            GenerateFadeTables();
            
            // Apply fade out effect
            ApplyFadeOutEffect(imageBuffer, audioFeatures);
        }
        
        /// <summary>
        /// Apply the fade out effect to the image buffer
        /// </summary>
        private void ApplyFadeOutEffect(ImageBuffer imageBuffer, AudioFeatures audioFeatures)
        {
            int width = imageBuffer.Width;
            int height = imageBuffer.Height;
            
            // Calculate beat response
            float beatMultiplier = 1.0f;
            if (BeatResponse && audioFeatures != null && audioFeatures.IsBeat)
            {
                beatMultiplier = BeatIntensity;
            }
            
            // Apply effect based on mode
            switch (Mode)
            {
                case FadeMode.ColorBased:
                    ApplyColorBasedFade(imageBuffer, beatMultiplier);
                    break;
                    
                case FadeMode.BrightnessReduction:
                    ApplyBrightnessReduction(imageBuffer, beatMultiplier);
                    break;
                    
                case FadeMode.Adaptive:
                    ApplyAdaptiveFade(imageBuffer, beatMultiplier);
                    break;
            }
        }
        
        /// <summary>
        /// Apply color-based fade effect
        /// </summary>
        private void ApplyColorBasedFade(ImageBuffer imageBuffer, float beatMultiplier)
        {
            int width = imageBuffer.Width;
            int height = imageBuffer.Height;
            
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    Color pixel = imageBuffer.GetPixel(x, y);
                    
                    // Apply fade using lookup tables
                    byte newRed = _fadeTables[0, pixel.R];
                    byte newGreen = _fadeTables[1, pixel.G];
                    byte newBlue = _fadeTables[2, pixel.B];
                    
                    // Apply beat response
                    if (beatMultiplier != 1.0f)
                    {
                        newRed = ApplyBeatResponse(newRed, beatMultiplier);
                        newGreen = ApplyBeatResponse(newGreen, beatMultiplier);
                        newBlue = ApplyBeatResponse(newBlue, beatMultiplier);
                    }
                    
                    // Apply intensity
                    newRed = ApplyIntensity(newRed, Intensity);
                    newGreen = ApplyIntensity(newGreen, Intensity);
                    newBlue = ApplyIntensity(newBlue, Intensity);
                    
                    Color newPixel = Color.FromArgb(pixel.A, newRed, newGreen, newBlue);
                    imageBuffer.SetPixel(x, y, newPixel);
                }
            }
        }
        
        /// <summary>
        /// Apply simple brightness reduction
        /// </summary>
        private void ApplyBrightnessReduction(ImageBuffer imageBuffer, float beatMultiplier)
        {
            int width = imageBuffer.Width;
            int height = imageBuffer.Height;
            
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    Color pixel = imageBuffer.GetPixel(x, y);
                    
                    // Apply brightness reduction using lookup tables
                    byte newRed = _fadeTables[0, pixel.R];
                    byte newGreen = _fadeTables[1, pixel.G];
                    byte newBlue = _fadeTables[2, pixel.B];
                    
                    // Apply beat response
                    if (beatMultiplier != 1.0f)
                    {
                        newRed = ApplyBeatResponse(newRed, beatMultiplier);
                        newGreen = ApplyBeatResponse(newGreen, beatMultiplier);
                        newBlue = ApplyBeatResponse(newBlue, beatMultiplier);
                    }
                    
                    // Apply intensity
                    newRed = ApplyIntensity(newRed, Intensity);
                    newGreen = ApplyIntensity(newGreen, Intensity);
                    newBlue = ApplyIntensity(newBlue, Intensity);
                    
                    Color newPixel = Color.FromArgb(pixel.A, newRed, newGreen, newBlue);
                    imageBuffer.SetPixel(x, y, newPixel);
                }
            }
        }
        
        /// <summary>
        /// Apply adaptive fade effect
        /// </summary>
        private void ApplyAdaptiveFade(ImageBuffer imageBuffer, float beatMultiplier)
        {
            int width = imageBuffer.Width;
            int height = imageBuffer.Height;
            
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    Color pixel = imageBuffer.GetPixel(x, y);
                    
                    // Calculate adaptive fade based on pixel brightness
                    float brightness = (pixel.R + pixel.G + pixel.B) / 765.0f; // 0.0 to 1.0
                    float adaptiveFadeLength = FadeLength * (1.0f - brightness);
                    
                    // Apply adaptive fade
                    byte newRed = ApplyAdaptiveFadeToChannel(pixel.R, adaptiveFadeLength);
                    byte newGreen = ApplyAdaptiveFadeToChannel(pixel.G, adaptiveFadeLength);
                    byte newBlue = ApplyAdaptiveFadeToChannel(pixel.B, adaptiveFadeLength);
                    
                    // Apply beat response
                    if (beatMultiplier != 1.0f)
                    {
                        newRed = ApplyBeatResponse(newRed, beatMultiplier);
                        newGreen = ApplyBeatResponse(newGreen, beatMultiplier);
                        newBlue = ApplyBeatResponse(newBlue, beatMultiplier);
                    }
                    
                    // Apply intensity
                    newRed = ApplyIntensity(newRed, Intensity);
                    newGreen = ApplyIntensity(newGreen, Intensity);
                    newBlue = ApplyIntensity(newBlue, Intensity);
                    
                    Color newPixel = Color.FromArgb(pixel.A, newRed, newGreen, newBlue);
                    imageBuffer.SetPixel(x, y, newPixel);
                }
            }
        }
        
        /// <summary>
        /// Apply adaptive fade to a single color channel
        /// </summary>
        private byte ApplyAdaptiveFadeToChannel(byte channelValue, float fadeLength)
        {
            int fadeInt = (int)fadeLength;
            int newValue = Math.Max(0, channelValue - fadeInt);
            return (byte)Math.Min(255, newValue);
        }
        
        /// <summary>
        /// Apply beat response to a color value
        /// </summary>
        private byte ApplyBeatResponse(byte colorValue, float beatMultiplier)
        {
            if (beatMultiplier <= 1.0f) return colorValue;
            
            int newValue = (int)(colorValue * beatMultiplier);
            return (byte)Math.Min(255, newValue);
        }
        
        /// <summary>
        /// Apply intensity multiplier to a color value
        /// </summary>
        private byte ApplyIntensity(byte colorValue, float intensity)
        {
            if (intensity <= 1.0f) return colorValue;
            
            int newValue = (int)(colorValue * intensity);
            return (byte)Math.Min(255, newValue);
        }
        
        #endregion
        
        #region Configuration Validation
        
        public override bool ValidateConfiguration()
        {
            if (FadeLength < 0 || FadeLength > 92) return false;
            if (Intensity < 0.1f || Intensity > 10.0f) return false;
            if (BeatIntensity < 0.1f || BeatIntensity > 5.0f) return false;
            
            return true;
        }
        
        #endregion
        
        #region Preset Methods
        
        /// <summary>
        /// Load a gentle fade preset
        /// </summary>
        public void LoadGentleFadePreset()
        {
            FadeLength = 8;
            TargetColor = Color.Black;
            UseColorFading = false;
            Mode = FadeMode.BrightnessReduction;
            Intensity = 1.0f;
            BeatResponse = false;
        }
        
        /// <summary>
        /// Load a strong fade preset
        /// </summary>
        public void LoadStrongFadePreset()
        {
            FadeLength = 32;
            TargetColor = Color.Black;
            UseColorFading = false;
            Mode = FadeMode.BrightnessReduction;
            Intensity = 1.5f;
            BeatResponse = false;
        }
        
        /// <summary>
        /// Load a color fade preset
        /// </summary>
        public void LoadColorFadePreset()
        {
            FadeLength = 16;
            TargetColor = Color.DarkBlue;
            UseColorFading = true;
            Mode = FadeMode.ColorBased;
            Intensity = 1.2f;
            BeatResponse = false;
        }
        
        /// <summary>
        /// Load a beat-responsive fade preset
        /// </summary>
        public void LoadBeatResponsivePreset()
        {
            FadeLength = 24;
            TargetColor = Color.Black;
            UseColorFading = false;
            Mode = FadeMode.BrightnessReduction;
            Intensity = 1.0f;
            BeatResponse = true;
            BeatIntensity = 1.5f;
        }
        
        /// <summary>
        /// Load an adaptive fade preset
        /// </summary>
        public void LoadAdaptiveFadePreset()
        {
            FadeLength = 20;
            TargetColor = Color.Black;
            UseColorFading = false;
            Mode = FadeMode.Adaptive;
            Intensity = 1.0f;
            BeatResponse = false;
        }
        
        #endregion
        
        #region Utility Methods
        
        /// <summary>
        /// Get the current fade length
        /// </summary>
        public int GetCurrentFadeLength()
        {
            return FadeLength;
        }
        
        /// <summary>
        /// Set the fade length and trigger table regeneration
        /// </summary>
        public void SetFadeLength(int newLength)
        {
            FadeLength = Math.Max(0, Math.Min(92, newLength));
            _fadeTablesNeedUpdate = true;
        }
        
        /// <summary>
        /// Set the target color and trigger table regeneration
        /// </summary>
        public void SetTargetColor(Color newColor)
        {
            TargetColor = newColor;
            _fadeTablesNeedUpdate = true;
        }
        
        /// <summary>
        /// Toggle between color-based and brightness reduction modes
        /// </summary>
        public void ToggleFadeMode()
        {
            UseColorFading = !UseColorFading;
            _fadeTablesNeedUpdate = true;
        }
        
        /// <summary>
        /// Get the current fade mode
        /// </summary>
        public FadeMode GetCurrentFadeMode()
        {
            return Mode;
        }
        
        /// <summary>
        /// Reset the effect to initial state
        /// </summary>
        public void Reset()
        {
            FadeLength = 16;
            TargetColor = Color.Black;
            UseColorFading = true;
            Mode = FadeMode.ColorBased;
            Intensity = 1.0f;
            BeatResponse = false;
            BeatIntensity = 1.0f;
            _frameCounter = 0;
            _isInitialized = false;
            _fadeTablesNeedUpdate = true;
        }
        
        /// <summary>
        /// Get effect execution statistics
        /// </summary>
        public string GetExecutionStats()
        {
            return $"Frame: {_frameCounter}, Fade Length: {FadeLength}, Mode: {Mode}, Color Fading: {UseColorFading}, Tables Valid: {!_fadeTablesNeedUpdate}";
        }
        
        #endregion
        
        #region Advanced Features
        
        /// <summary>
        /// Create a custom fade curve
        /// </summary>
        public void CreateCustomFadeCurve(Func<byte, byte> redCurve, Func<byte, byte> greenCurve, Func<byte, byte> blueCurve)
        {
            for (int x = 0; x < 256; x++)
            {
                _fadeTables[0, x] = redCurve((byte)x);
                _fadeTables[1, x] = greenCurve((byte)x);
                _fadeTables[2, x] = blueCurve((byte)x);
            }
            
            _fadeTablesNeedUpdate = false;
        }
        
        /// <summary>
        /// Get a copy of the current fade tables
        /// </summary>
        public byte[,] GetFadeTables()
        {
            return (byte[,])_fadeTables.Clone();
        }
        
        /// <summary>
        /// Set fade tables directly (for advanced users)
        /// </summary>
        public void SetFadeTables(byte[,] newTables)
        {
            if (newTables != null && newTables.GetLength(0) == 3 && newTables.GetLength(1) == 256)
            {
                Array.Copy(newTables, _fadeTables, newTables.Length);
                _fadeTablesNeedUpdate = false;
            }
        }
        
        #endregion
    }
}
```

## Effect Properties

### Core Properties
- **Enabled**: Toggle the effect on/off
- **FadeLength**: Length of the fade effect (0-92)
- **TargetColor**: Color to fade toward (0 = brightness reduction)
- **Intensity**: Overall effect strength multiplier
- **UseColorFading**: Whether to use color-based fading

### Mode Properties
- **Mode**: Fade mode selection
- **BeatResponse**: Whether to respond to beat detection
- **BeatIntensity**: Beat response intensity multiplier

### Internal Properties
- **FadeTables**: Pre-calculated lookup tables for each color channel
- **FrameCounter**: Frame counter for timing
- **FadeTablesNeedUpdate**: Whether tables need regeneration

## Fade Modes

### Brightness Reduction Mode
- Simple pixel darkening
- Fastest processing mode
- Uniform effect across all pixels
- Good for general dimming

### Color-Based Mode
- Fades toward specific target color
- Creates color tinting effects
- More complex color transformations
- Good for mood lighting

### Adaptive Mode
- Fade intensity based on pixel brightness
- Brighter pixels fade more
- Creates natural-looking effects
- Good for realistic lighting

## Lookup Table System

The effect uses pre-calculated tables:
- **Red Channel Table**: Fade values for red component
- **Green Channel Table**: Fade values for green component
- **Blue Channel Table**: Fade values for blue component
- **Efficient Processing**: Fast pixel value lookups
- **Dynamic Updates**: Tables regenerate when parameters change

## Color Processing

The effect processes colors by:
- **Channel Separation**: Independent processing of RGB channels
- **Lookup Optimization**: Pre-calculated fade values
- **Value Clamping**: Ensures colors stay in valid range
- **Intensity Control**: Adjustable effect strength

## Beat Response

When enabled, the effect responds to music by:
- **Beat Detection**: Enhanced effect on musical beats
- **Intensity Multiplier**: Configurable beat response strength
- **Dynamic Fading**: Varying fade intensity with music
- **Synchronization**: Visual effects timed with audio

## Performance Optimizations

- **Pre-calculated Tables**: Fast color value lookups
- **Efficient Processing**: Optimized pixel iteration
- **Memory Management**: Minimal memory allocation
- **Table Caching**: Tables only regenerate when needed

## Use Cases

- **Transitions**: Smooth scene changes
- **Mood Lighting**: Atmospheric color adjustments
- **Beat Visualization**: Music-synchronized effects
- **Image Processing**: Gradual brightness reduction
- **Special Effects**: Cinematic fade effects

## Preset Effects

### Basic Presets
- **Gentle Fade**: Subtle brightness reduction
- **Strong Fade**: Dramatic darkening effect
- **Color Fade**: Fade toward specific color
- **Beat Responsive**: Music-synchronized fading

### Advanced Presets
- **Adaptive Fade**: Brightness-based adaptive effect
- **Custom Curves**: User-defined fade patterns
- **Dynamic Fading**: Real-time parameter adjustment

## Mathematical Functions

The effect uses:
- **Lookup Tables**: Pre-calculated color transformations
- **Value Clamping**: Ensures valid color ranges
- **Linear Interpolation**: Smooth color transitions
- **Adaptive Calculations**: Dynamic fade intensity

## Error Handling

The effect includes:
- **Parameter Validation**: Ensures configuration values are within ranges
- **Table Validation**: Verifies fade table integrity
- **Color Safety**: Prevents invalid color operations
- **Memory Safety**: Handles table allocation gracefully
