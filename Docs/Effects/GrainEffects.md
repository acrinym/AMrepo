# Grain Effects

The Grain effect adds noise and texture to images, creating a film grain or digital noise appearance. It supports both static and dynamic grain patterns with various blending modes for realistic texture simulation.

## Effect Overview

The Grain effect works by:
1. Generating random noise patterns for each pixel
2. Supporting both static (persistent) and dynamic (changing) grain
3. Providing multiple blending modes for integration with existing content
4. Using depth buffers for realistic grain distribution
5. Offering configurable grain intensity and threshold controls

## C# Implementation

```csharp
using System;
using System.Collections.Generic;
using System.Drawing;
using PhoenixVisualizer.Core.Effects.Models;
using PhoenixVisualizer.Core.Models;

namespace PhoenixVisualizer.Core.Effects.Nodes.AvsEffects
{
    public class GrainEffectsNode : BaseEffectNode
    {
        #region Properties
        
        /// <summary>
        /// Whether the effect is enabled
        /// </summary>
        public bool Enabled { get; set; } = true;
        
        /// <summary>
        /// Maximum grain intensity (0-100)
        /// </summary>
        public int MaxIntensity { get; set; } = 100;
        
        /// <summary>
        /// Whether to use static grain (persistent pattern)
        /// </summary>
        public bool UseStaticGrain { get; set; } = false;
        
        /// <summary>
        /// Blending mode for grain application
        /// </summary>
        public GrainBlendMode BlendMode { get; set; } = GrainBlendMode.Replace;
        
        /// <summary>
        /// Effect intensity multiplier
        /// </summary>
        public float Intensity { get; set; } = 1.0f;
        
        /// <summary>
        /// Whether to respond to beat detection
        /// </summary>
        public bool BeatResponse { get; set; } = false;
        
        /// <summary>
        /// Beat response intensity multiplier
        /// </summary>
        public float BeatIntensity { get; set; } = 1.0f;
        
        /// <summary>
        /// Grain color (null = use original pixel color)
        /// </summary>
        public Color? GrainColor { get; set; } = null;
        
        /// <summary>
        /// Whether to preserve alpha channel
        /// </summary>
        public bool PreserveAlpha { get; set; } = true;
        
        #endregion
        
        #region Enums
        
        /// <summary>
        /// Available blending modes for grain application
        /// </summary>
        public enum GrainBlendMode
        {
            /// <summary>
            /// Replace pixels with grain
            /// </summary>
            Replace = 0,
            
            /// <summary>
            /// Additive blending with grain
            /// </summary>
            Additive = 1,
            
            /// <summary>
            /// 50/50 average blending with grain
            /// </summary>
            Average = 2
        }
        
        #endregion
        
        #region Private Fields
        
        /// <summary>
        /// Pre-calculated random table for fast random number generation
        /// </summary>
        private byte[] _randomTable;
        
        /// <summary>
        /// Current position in random table
        /// </summary>
        private int _randomTablePosition;
        
        /// <summary>
        /// Depth buffer for static grain patterns
        /// </summary>
        private GrainDepthBuffer[] _depthBuffer;
        
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
        /// Random number generator for additional randomness
        /// </summary>
        private Random _random;
        
        #endregion
        
        #region Structures
        
        /// <summary>
        /// Represents a grain depth buffer entry
        /// </summary>
        private struct GrainDepthBuffer
        {
            /// <summary>
            /// Grain intensity value
            /// </summary>
            public byte Intensity;
            
            /// <summary>
            /// Grain threshold value
            /// </summary>
            public byte Threshold;
        }
        
        #endregion
        
        #region Constructor
        
        public GrainEffectsNode()
        {
            _randomTable = new byte[491];
            _depthBuffer = new GrainDepthBuffer[0];
            _random = new Random();
            
            // Set default values
            MaxIntensity = 100;
            UseStaticGrain = false;
            BlendMode = GrainBlendMode.Replace;
            
            // Initialize random table
            InitializeRandomTable();
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
            
            // Initialize depth buffer
            InitializeDepthBuffer(width, height);
            
            _isInitialized = true;
        }
        
        /// <summary>
        /// Initialize the random number table
        /// </summary>
        private void InitializeRandomTable()
        {
            for (int i = 0; i < _randomTable.Length; i++)
            {
                _randomTable[i] = (byte)_random.Next(256);
            }
            _randomTablePosition = _random.Next(_randomTable.Length);
        }
        
        /// <summary>
        /// Initialize the depth buffer for static grain
        /// </summary>
        private void InitializeDepthBuffer(int width, int height)
        {
            int bufferSize = width * height;
            _depthBuffer = new GrainDepthBuffer[bufferSize];
            
            for (int i = 0; i < bufferSize; i++)
            {
                _depthBuffer[i].Intensity = (byte)_random.Next(256);
                _depthBuffer[i].Threshold = (byte)_random.Next(100);
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
            
            // Update random table position
            UpdateRandomTablePosition();
            
            // Apply grain effect
            ApplyGrainEffect(imageBuffer, audioFeatures);
        }
        
        /// <summary>
        /// Update the random table position for dynamic grain
        /// </summary>
        private void UpdateRandomTablePosition()
        {
            if (!UseStaticGrain)
            {
                _randomTablePosition += _random.Next(300);
                if (_randomTablePosition >= _randomTable.Length)
                {
                    _randomTablePosition -= _randomTable.Length;
                }
            }
        }
        
        /// <summary>
        /// Apply the grain effect to the image buffer
        /// </summary>
        private void ApplyGrainEffect(ImageBuffer imageBuffer, AudioFeatures audioFeatures)
        {
            int width = imageBuffer.Width;
            int height = imageBuffer.Height;
            
            // Calculate beat response
            float beatMultiplier = 1.0f;
            if (BeatResponse && audioFeatures != null && audioFeatures.IsBeat)
            {
                beatMultiplier = BeatIntensity;
            }
            
            // Calculate scaled maximum intensity
            int scaledMaxIntensity = (MaxIntensity * 255) / 100;
            
            // Apply grain based on mode
            if (UseStaticGrain)
            {
                ApplyStaticGrain(imageBuffer, scaledMaxIntensity, beatMultiplier);
            }
            else
            {
                ApplyDynamicGrain(imageBuffer, scaledMaxIntensity, beatMultiplier);
            }
        }
        
        /// <summary>
        /// Apply static grain using depth buffer
        /// </summary>
        private void ApplyStaticGrain(ImageBuffer imageBuffer, int maxIntensity, float beatMultiplier)
        {
            int width = imageBuffer.Width;
            int height = imageBuffer.Height;
            
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    int bufferIndex = y * width + x;
                    GrainDepthBuffer depthEntry = _depthBuffer[bufferIndex];
                    
                    // Check if grain should be applied based on threshold
                    if (depthEntry.Threshold < maxIntensity)
                    {
                        Color pixel = imageBuffer.GetPixel(x, y);
                        Color grainColor = GenerateGrainColor(pixel, depthEntry.Intensity);
                        
                        // Apply blending based on mode
                        Color finalColor = ApplyBlending(pixel, grainColor, BlendMode);
                        
                        // Apply beat response and intensity
                        finalColor = ApplyEffects(finalColor, beatMultiplier);
                        
                        // Preserve alpha if requested
                        if (PreserveAlpha)
                        {
                            finalColor = Color.FromArgb(pixel.A, finalColor.R, finalColor.G, finalColor.B);
                        }
                        
                        imageBuffer.SetPixel(x, y, finalColor);
                    }
                }
            }
        }
        
        /// <summary>
        /// Apply dynamic grain using random generation
        /// </summary>
        private void ApplyDynamicGrain(ImageBuffer imageBuffer, int maxIntensity, float beatMultiplier)
        {
            int width = imageBuffer.Width;
            int height = imageBuffer.Height;
            
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    Color pixel = imageBuffer.GetPixel(x, y);
                    
                    // Check if grain should be applied based on random threshold
                    if (GetFastRandomByte() < maxIntensity)
                    {
                        byte grainIntensity = GetFastRandomByte();
                        Color grainColor = GenerateGrainColor(pixel, grainIntensity);
                        
                        // Apply blending based on mode
                        Color finalColor = ApplyBlending(pixel, grainColor, BlendMode);
                        
                        // Apply beat response and intensity
                        finalColor = ApplyEffects(finalColor, beatMultiplier);
                        
                        // Preserve alpha if requested
                        if (PreserveAlpha)
                        {
                            finalColor = Color.FromArgb(pixel.A, finalColor.R, finalColor.G, finalColor.B);
                        }
                        
                        imageBuffer.SetPixel(x, y, finalColor);
                    }
                }
            }
        }
        
        /// <summary>
        /// Generate grain color based on original pixel and intensity
        /// </summary>
        private Color GenerateGrainColor(Color originalPixel, byte intensity)
        {
            if (GrainColor.HasValue)
            {
                // Use specified grain color
                return GrainColor.Value;
            }
            else
            {
                // Use original pixel color modulated by intensity
                int r = (originalPixel.R * intensity) >> 8;
                int g = (originalPixel.G * intensity) >> 8;
                int b = (originalPixel.B * intensity) >> 8;
                
                // Clamp values
                r = Math.Min(255, r);
                g = Math.Min(255, g);
                b = Math.Min(255, b);
                
                return Color.FromArgb(255, r, g, b);
            }
        }
        
        /// <summary>
        /// Apply blending between original and grain colors
        /// </summary>
        private Color ApplyBlending(Color originalColor, Color grainColor, GrainBlendMode mode)
        {
            switch (mode)
            {
                case GrainBlendMode.Replace:
                    return grainColor;
                    
                case GrainBlendMode.Additive:
                    return BlendAdditive(originalColor, grainColor);
                    
                case GrainBlendMode.Average:
                    return BlendAverage(originalColor, grainColor);
                    
                default:
                    return grainColor;
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
        /// Apply beat response and intensity effects
        /// </summary>
        private Color ApplyEffects(Color color, float beatMultiplier)
        {
            int r = color.R;
            int g = color.G;
            int b = color.B;
            
            // Apply beat response
            if (beatMultiplier != 1.0f)
            {
                r = (int)(r * beatMultiplier);
                g = (int)(g * beatMultiplier);
                b = (int)(b * beatMultiplier);
            }
            
            // Apply intensity
            r = (int)(r * Intensity);
            g = (int)(g * Intensity);
            b = (int)(b * Intensity);
            
            // Clamp values
            r = Math.Min(255, r);
            g = Math.Min(255, g);
            b = Math.Min(255, b);
            
            return Color.FromArgb(255, r, g, b);
        }
        
        /// <summary>
        /// Get a fast random byte from the pre-calculated table
        /// </summary>
        private byte GetFastRandomByte()
        {
            byte result = _randomTable[_randomTablePosition];
            _randomTablePosition++;
            
            // Add additional randomness every 16 calls
            if ((_randomTablePosition & 15) == 0)
            {
                _randomTablePosition += _random.Next(73);
            }
            
            // Wrap around if needed
            if (_randomTablePosition >= _randomTable.Length)
            {
                _randomTablePosition -= _randomTable.Length;
            }
            
            return result;
        }
        
        #endregion
        
        #region Configuration Validation
        
        public override bool ValidateConfiguration()
        {
            if (MaxIntensity < 0 || MaxIntensity > 100) return false;
            if (Intensity < 0.1f || Intensity > 10.0f) return false;
            if (BeatIntensity < 0.1f || BeatIntensity > 5.0f) return false;
            
            return true;
        }
        
        #endregion
        
        #region Preset Methods
        
        /// <summary>
        /// Load a subtle grain preset
        /// </summary>
        public void LoadSubtleGrainPreset()
        {
            MaxIntensity = 30;
            UseStaticGrain = false;
            BlendMode = GrainBlendMode.Average;
            Intensity = 0.8f;
            BeatResponse = false;
            GrainColor = null;
        }
        
        /// <summary>
        /// Load a strong grain preset
        /// </summary>
        public void LoadStrongGrainPreset()
        {
            MaxIntensity = 80;
            UseStaticGrain = false;
            BlendMode = GrainBlendMode.Replace;
            Intensity = 1.5f;
            BeatResponse = false;
            GrainColor = null;
        }
        
        /// <summary>
        /// Load a static grain preset
        /// </summary>
        public void LoadStaticGrainPreset()
        {
            MaxIntensity = 50;
            UseStaticGrain = true;
            BlendMode = GrainBlendMode.Additive;
            Intensity = 1.0f;
            BeatResponse = false;
            GrainColor = null;
        }
        
        /// <summary>
        /// Load a beat-responsive grain preset
        /// </summary>
        public void LoadBeatResponsivePreset()
        {
            MaxIntensity = 60;
            UseStaticGrain = false;
            BlendMode = GrainBlendMode.Additive;
            Intensity = 1.0f;
            BeatResponse = true;
            BeatIntensity = 1.8f;
            GrainColor = null;
        }
        
        /// <summary>
        /// Load a colored grain preset
        /// </summary>
        public void LoadColoredGrainPreset()
        {
            MaxIntensity = 70;
            UseStaticGrain = false;
            BlendMode = GrainBlendMode.Average;
            Intensity = 1.2f;
            BeatResponse = false;
            GrainColor = Color.White;
        }
        
        #endregion
        
        #region Utility Methods
        
        /// <summary>
        /// Get the current grain intensity
        /// </summary>
        public int GetCurrentGrainIntensity()
        {
            return MaxIntensity;
        }
        
        /// <summary>
        /// Set the grain intensity
        /// </summary>
        public void SetGrainIntensity(int newIntensity)
        {
            MaxIntensity = Math.Max(0, Math.Min(100, newIntensity));
        }
        
        /// <summary>
        /// Toggle between static and dynamic grain
        /// </summary>
        public void ToggleGrainMode()
        {
            UseStaticGrain = !UseStaticGrain;
        }
        
        /// <summary>
        /// Get the current grain mode
        /// </summary>
        public string GetGrainMode()
        {
            return UseStaticGrain ? "Static" : "Dynamic";
        }
        
        /// <summary>
        /// Get the current blending mode
        /// </summary>
        public GrainBlendMode GetCurrentBlendMode()
        {
            return BlendMode;
        }
        
        /// <summary>
        /// Regenerate the random table
        /// </summary>
        public void RegenerateRandomTable()
        {
            InitializeRandomTable();
        }
        
        /// <summary>
        /// Regenerate the depth buffer
        /// </summary>
        public void RegenerateDepthBuffer()
        {
            if (_currentWidth > 0 && _currentHeight > 0)
            {
                InitializeDepthBuffer(_currentWidth, _currentHeight);
            }
        }
        
        /// <summary>
        /// Reset the effect to initial state
        /// </summary>
        public void Reset()
        {
            MaxIntensity = 100;
            UseStaticGrain = false;
            BlendMode = GrainBlendMode.Replace;
            Intensity = 1.0f;
            BeatResponse = false;
            BeatIntensity = 1.0f;
            GrainColor = null;
            PreserveAlpha = true;
            _frameCounter = 0;
            _isInitialized = false;
            
            // Regenerate tables
            InitializeRandomTable();
            if (_currentWidth > 0 && _currentHeight > 0)
            {
                InitializeDepthBuffer(_currentWidth, _currentHeight);
            }
        }
        
        /// <summary>
        /// Get effect execution statistics
        /// </summary>
        public string GetExecutionStats()
        {
            return $"Frame: {_frameCounter}, Intensity: {MaxIntensity}, Mode: {GetGrainMode()}, Blend: {BlendMode}, Random Pos: {_randomTablePosition}";
        }
        
        #endregion
        
        #region Advanced Features
        
        /// <summary>
        /// Get a copy of the current random table
        /// </summary>
        public byte[] GetRandomTable()
        {
            return (byte[])_randomTable.Clone();
        }
        
        /// <summary>
        /// Set the random table directly (for advanced users)
        /// </summary>
        public void SetRandomTable(byte[] newTable)
        {
            if (newTable != null && newTable.Length == 491)
            {
                Array.Copy(newTable, _randomTable, newTable.Length);
            }
        }
        
        /// <summary>
        /// Get a copy of the current depth buffer
        /// </summary>
        public GrainDepthBuffer[] GetDepthBuffer()
        {
            return (GrainDepthBuffer[])_depthBuffer.Clone();
        }
        
        /// <summary>
        /// Set the depth buffer directly (for advanced users)
        /// </summary>
        public void SetDepthBuffer(GrainDepthBuffer[] newBuffer)
        {
            if (newBuffer != null && newBuffer.Length == _depthBuffer.Length)
            {
                Array.Copy(newBuffer, _depthBuffer, newBuffer.Length);
            }
        }
        
        #endregion
    }
}
```

## Effect Properties

### Core Properties
- **Enabled**: Toggle the effect on/off
- **MaxIntensity**: Maximum grain intensity (0-100)
- **UseStaticGrain**: Whether to use static (persistent) grain
- **BlendMode**: Blending mode for grain application
- **Intensity**: Overall effect strength multiplier

### Advanced Properties
- **BeatResponse**: Whether to respond to beat detection
- **BeatIntensity**: Beat response intensity multiplier
- **GrainColor**: Custom grain color (null = use original pixel)
- **PreserveAlpha**: Whether to preserve alpha channel values

### Internal Properties
- **RandomTable**: Pre-calculated random number table
- **DepthBuffer**: Buffer for static grain patterns
- **FrameCounter**: Frame counter for timing
- **RandomTablePosition**: Current position in random table

## Grain Modes

### Static Grain Mode
- Uses persistent grain patterns
- Stored in depth buffer for consistency
- Good for film grain simulation
- Consistent across frames

### Dynamic Grain Mode
- Generates new grain each frame
- Uses fast random number generation
- Good for digital noise effects
- Varies over time

## Blending Modes

### Replace Mode
- Completely replaces pixels with grain
- Maximum grain visibility
- Good for strong effects
- May lose original image detail

### Additive Mode
- Adds grain to existing pixels
- Preserves original image
- Creates brightening effect
- Good for subtle enhancement

### Average Mode
- 50/50 mix of original and grain
- Balanced effect
- Preserves image structure
- Good for natural appearance

## Random Number System

The effect uses an optimized random system:
- **Pre-calculated Table**: 491-byte random number table
- **Fast Access**: Direct table lookup for speed
- **Additional Randomness**: Periodic randomization every 16 calls
- **Efficient Wrapping**: Automatic table position management

## Depth Buffer System

For static grain:
- **Intensity Values**: Grain strength for each pixel
- **Threshold Values**: Probability of grain application
- **Persistent Storage**: Maintains grain patterns across frames
- **Memory Efficient**: Compact storage format

## Performance Optimizations

- **Pre-calculated Tables**: Fast random number generation
- **Efficient Blending**: Optimized color mixing algorithms
- **Conditional Processing**: Only applies grain when needed
- **Memory Management**: Efficient buffer allocation

## Beat Response

When enabled, the effect responds to music by:
- **Beat Detection**: Enhanced grain on musical beats
- **Intensity Multiplier**: Configurable beat response strength
- **Dynamic Variation**: Varying grain intensity with music
- **Synchronization**: Visual effects timed with audio

## Use Cases

- **Film Simulation**: Realistic film grain effects
- **Texture Addition**: Adding noise to flat images
- **Mood Enhancement**: Creating atmospheric effects
- **Beat Visualization**: Music-synchronized grain
- **Artistic Effects**: Creative noise patterns

## Preset Effects

### Basic Presets
- **Subtle Grain**: Light texture addition
- **Strong Grain**: Heavy noise effects
- **Static Grain**: Persistent grain patterns
- **Beat Responsive**: Music-synchronized grain

### Advanced Presets
- **Colored Grain**: Custom grain colors
- **Dynamic Patterns**: Varying grain effects
- **Film Simulation**: Authentic film look
- **Digital Noise**: Modern noise effects

## Mathematical Functions

The effect uses:
- **Random Generation**: Fast pseudo-random numbers
- **Color Blending**: Various mixing algorithms
- **Threshold Testing**: Probability-based grain application
- **Intensity Modulation**: Grain strength control

## Error Handling

The effect includes:
- **Parameter Validation**: Ensures configuration values are within ranges
- **Buffer Validation**: Verifies depth buffer integrity
- **Memory Safety**: Handles buffer allocation gracefully
- **Table Management**: Automatic random table maintenance
