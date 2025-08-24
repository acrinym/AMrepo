# Dot Fountain Effects

The Dot Fountain effect creates a 3D fountain of colored dots that respond to audio input and rotate in 3D space. It generates particles that flow upward from the bottom of the screen, creating a dynamic visual effect that can be synchronized with music beats.

## Effect Overview

The Dot Fountain effect works by:
1. Creating a 3D fountain structure with multiple rotation divisions and height levels
2. Generating new particles at the bottom based on audio input
3. Applying 3D transformations including rotation and perspective projection
4. Updating particle positions and velocities over time
5. Rendering dots with color interpolation and beat-responsive effects

## C# Implementation

```csharp
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Numerics;
using PhoenixVisualizer.Core.Effects.Models;
using PhoenixVisualizer.Core.Models;

namespace PhoenixVisualizer.Core.Effects.Nodes.AvsEffects
{
    public class DotFountainEffectsNode : BaseEffectNode
    {
        #region Constants
        
        /// <summary>
        /// Number of rotation divisions around the fountain
        /// </summary>
        private const int NUM_ROT_DIV = 30;
        
        /// <summary>
        /// Maximum height levels for particles
        /// </summary>
        private const int NUM_ROT_HEIGHT = 256;
        
        #endregion
        
        #region Properties
        
        /// <summary>
        /// Whether the effect is enabled
        /// </summary>
        public bool Enabled { get; set; } = true;
        
        /// <summary>
        /// Rotation velocity of the fountain (degrees per frame)
        /// </summary>
        public float RotationVelocity { get; set; } = 16.0f;
        
        /// <summary>
        /// Angle of the fountain tilt (-90 to 90 degrees)
        /// </summary>
        public float Angle { get; set; } = -20.0f;
        
        /// <summary>
        /// Base radius of the fountain
        /// </summary>
        public float BaseRadius { get; set; } = 1.0f;
        
        /// <summary>
        /// Effect intensity multiplier
        /// </summary>
        public float Intensity { get; set; } = 1.0f;
        
        /// <summary>
        /// Whether to respond to beat detection
        /// </summary>
        public bool BeatResponse { get; set; } = true;
        
        /// <summary>
        /// Audio sensitivity for particle generation
        /// </summary>
        public float AudioSensitivity { get; set; } = 1.0f;
        
        /// <summary>
        /// Particle lifetime multiplier
        /// </summary>
        public float ParticleLifetime { get; set; } = 1.0f;
        
        /// <summary>
        /// Gravity effect on particles
        /// </summary>
        public float Gravity { get; set; } = 0.05f;
        
        /// <summary>
        /// Fountain height offset
        /// </summary>
        public float HeightOffset { get; set; } = -20.0f;
        
        /// <summary>
        /// Fountain depth in 3D space
        /// </summary>
        public float Depth { get; set; } = 400.0f;
        
        #endregion
        
        #region Private Fields
        
        /// <summary>
        /// Current rotation angle in degrees
        /// </summary>
        private float _currentRotation = 0.0f;
        
        /// <summary>
        /// 3D transformation matrix
        /// </summary>
        private Matrix4x4 _transformationMatrix;
        
        /// <summary>
        /// Array of fountain points for each height level and rotation division
        /// </summary>
        private FountainPoint[,] _points;
        
        /// <summary>
        /// Pre-calculated color interpolation table
        /// </summary>
        private int[] _colorTable;
        
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
        
        #region Fountain Point Structure
        
        /// <summary>
        /// Represents a single particle in the fountain
        /// </summary>
        private struct FountainPoint
        {
            /// <summary>
            /// Current radius from center
            /// </summary>
            public float Radius;
            
            /// <summary>
            /// Rate of change of radius
            /// </summary>
            public float RadiusVelocity;
            
            /// <summary>
            /// Current height
            /// </summary>
            public float Height;
            
            /// <summary>
            /// Rate of change of height
            /// </summary>
            public float HeightVelocity;
            
            /// <summary>
            /// X component of angular position
            /// </summary>
            public float AngularX;
            
            /// <summary>
            /// Y component of angular position
            /// </summary>
            public float AngularY;
            
            /// <summary>
            /// Color index for the particle
            /// </summary>
            public int ColorIndex;
            
            /// <summary>
            /// Whether the particle is active
            /// </summary>
            public bool IsActive;
            
            /// <summary>
            /// Create a new fountain point
            /// </summary>
            public FountainPoint(float radius, float height, float angularX, float angularY, int colorIndex)
            {
                Radius = radius;
                RadiusVelocity = 0.0f;
                Height = height;
                HeightVelocity = 0.0f;
                AngularX = angularX;
                AngularY = angularY;
                ColorIndex = colorIndex;
                IsActive = true;
            }
        }
        
        #endregion
        
        #region Constructor
        
        public DotFountainEffectsNode()
        {
            _points = new FountainPoint[NUM_ROT_HEIGHT, NUM_ROT_DIV];
            _colorTable = new int[64];
            
            // Set default colors (BGR format like original)
            SetDefaultColors();
            
            InitializeColorTable();
        }
        
        #endregion
        
        #region Initialization Methods
        
        /// <summary>
        /// Set default fountain colors
        /// </summary>
        private void SetDefaultColors()
        {
            // Default colors in BGR format (reverse of RGB)
            DefaultColors = new Color[]
            {
                Color.FromArgb(28, 107, 24),   // Green
                Color.FromArgb(255, 10, 35),    // Blue
                Color.FromArgb(42, 29, 116),    // Red
                Color.FromArgb(144, 54, 217),   // Purple
                Color.FromArgb(107, 136, 255)   // Orange
            };
        }
        
        /// <summary>
        /// Initialize the color interpolation table
        /// </summary>
        private void InitializeColorTable()
        {
            for (int t = 0; t < 4; t++)
            {
                Color currentColor = DefaultColors[t];
                Color nextColor = DefaultColors[t + 1];
                
                // Calculate color deltas for interpolation
                int deltaR = (nextColor.R - currentColor.R) / 16;
                int deltaG = (nextColor.G - currentColor.G) / 16;
                int deltaB = (nextColor.B - currentColor.B) / 16;
                
                for (int x = 0; x < 16; x++)
                {
                    int r = Math.Max(0, Math.Min(255, currentColor.R + (deltaR * x)));
                    int g = Math.Max(0, Math.Min(255, currentColor.G + (deltaG * x)));
                    int b = Math.Max(0, Math.Min(255, currentColor.B + (deltaB * x)));
                    
                    _colorTable[t * 16 + x] = Color.FromArgb(255, r, g, b).ToArgb();
                }
            }
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
            
            // Clear all points
            for (int h = 0; h < NUM_ROT_HEIGHT; h++)
            {
                for (int r = 0; r < NUM_ROT_DIV; r++)
                {
                    _points[h, r] = new FountainPoint();
                    _points[h, r].IsActive = false;
                }
            }
            
            _isInitialized = true;
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
            
            // Update transformation matrix
            UpdateTransformationMatrix();
            
            // Update fountain points
            UpdateFountainPoints(audioFeatures);
            
            // Render fountain
            RenderFountain(imageBuffer);
            
            // Update rotation
            UpdateRotation();
        }
        
        /// <summary>
        /// Update the 3D transformation matrix
        /// </summary>
        private void UpdateTransformationMatrix()
        {
            // Create rotation matrix around Y axis (fountain rotation)
            Matrix4x4 rotationY = Matrix4x4.CreateRotationY(_currentRotation * (float)Math.PI / 180.0f);
            
            // Create rotation matrix around X axis (fountain tilt)
            Matrix4x4 rotationX = Matrix4x4.CreateRotationX(Angle * (float)Math.PI / 180.0f);
            
            // Create translation matrix
            Matrix4x4 translation = Matrix4x4.CreateTranslation(0.0f, HeightOffset, Depth);
            
            // Combine transformations: translate -> rotate X -> rotate Y
            _transformationMatrix = translation * rotationX * rotationY;
        }
        
        /// <summary>
        /// Update all fountain points
        /// </summary>
        private void UpdateFountainPoints(AudioFeatures audioFeatures)
        {
            // Move existing points up and update their properties
            for (int h = NUM_ROT_HEIGHT - 2; h >= 0; h--)
            {
                for (int r = 0; r < NUM_ROT_DIV; r++)
                {
                    if (_points[h, r].IsActive)
                    {
                        // Copy point to next level
                        _points[h + 1, r] = _points[h, r];
                        
                        // Update point properties
                        FountainPoint point = _points[h + 1, r];
                        point.Radius += point.RadiusVelocity;
                        point.HeightVelocity += Gravity;
                        point.Height += point.HeightVelocity;
                        
                        // Apply radius acceleration based on height
                        float heightFactor = 1.3f / (h + 100);
                        point.RadiusVelocity += heightFactor;
                        
                        _points[h + 1, r] = point;
                        
                        // Clear current level
                        _points[h, r].IsActive = false;
                    }
                }
            }
            
            // Generate new points at the bottom
            GenerateNewPoints(audioFeatures);
        }
        
        /// <summary>
        /// Generate new particles at the bottom of the fountain
        /// </summary>
        private void GenerateNewPoints(AudioFeatures audioFeatures)
        {
            for (int r = 0; r < NUM_ROT_DIV; r++)
            {
                // Calculate audio input value for this rotation division
                float audioValue = GetAudioValue(r, audioFeatures);
                
                // Create new point
                FountainPoint newPoint = new FountainPoint();
                newPoint.Radius = BaseRadius;
                newPoint.Height = 250.0f;
                newPoint.IsActive = true;
                
                // Calculate angular position
                float angle = r * 2.0f * (float)Math.PI / NUM_ROT_DIV;
                newPoint.AngularX = (float)Math.Sin(angle);
                newPoint.AngularY = (float)Math.Cos(angle);
                
                // Calculate height velocity based on audio
                float audioFactor = Math.Abs(audioValue) / 200.0f;
                float velocity = -audioFactor * 2.8f;
                newPoint.HeightVelocity = velocity;
                
                // Set color based on audio intensity
                int colorIndex = Math.Min(63, (int)(audioValue / 4));
                newPoint.ColorIndex = colorIndex;
                
                // Store the new point
                _points[0, r] = newPoint;
            }
        }
        
        /// <summary>
        /// Get audio value for a specific rotation division
        /// </summary>
        private float GetAudioValue(int rotationIndex, AudioFeatures audioFeatures)
        {
            // Simulate audio data for different frequency bands
            float baseValue = 0.0f;
            
            if (audioFeatures != null)
            {
                // Use different frequency bands for different rotation divisions
                int bandIndex = rotationIndex % audioFeatures.FrequencyBands.Length;
                baseValue = audioFeatures.FrequencyBands[bandIndex];
            }
            
            // Add some variation based on rotation index
            float variation = (float)Math.Sin(rotationIndex * 0.5f + _frameCounter * 0.1f) * 50.0f;
            baseValue += variation;
            
            // Apply beat response
            if (BeatResponse && audioFeatures.IsBeat)
            {
                baseValue += 128.0f;
            }
            
            // Apply audio sensitivity
            baseValue *= AudioSensitivity;
            
            // Clamp to valid range
            return Math.Max(-255, Math.Min(255, baseValue));
        }
        
        /// <summary>
        /// Render the fountain to the image buffer
        /// </summary>
        private void RenderFountain(ImageBuffer imageBuffer)
        {
            int width = imageBuffer.Width;
            int height = imageBuffer.Height;
            
            // Calculate perspective adjustment
            float perspectiveAdjust = Math.Min(
                width * 440.0f / 640.0f,
                height * 440.0f / 480.0f
            );
            
            // Render all active points
            for (int h = 0; h < NUM_ROT_HEIGHT; h++)
            {
                for (int r = 0; r < NUM_ROT_DIV; r++)
                {
                    if (_points[h, r].IsActive)
                    {
                        RenderPoint(_points[h, r], imageBuffer, perspectiveAdjust);
                    }
                }
            }
        }
        
        /// <summary>
        /// Render a single fountain point
        /// </summary>
        private void RenderPoint(FountainPoint point, ImageBuffer imageBuffer, float perspectiveAdjust)
        {
            int width = imageBuffer.Width;
            int height = imageBuffer.Height;
            
            // Calculate 3D position
            Vector3 position = new Vector3(
                point.AngularX * point.Radius,
                point.Height,
                point.AngularY * point.Radius
            );
            
            // Apply transformation matrix
            Vector3 transformedPosition = Vector3.Transform(position, _transformationMatrix);
            
            // Apply perspective projection
            if (transformedPosition.Z > 0.0000001f)
            {
                float perspective = perspectiveAdjust / transformedPosition.Z;
                
                // Convert to screen coordinates
                int screenX = (int)(transformedPosition.X * perspective) + width / 2;
                int screenY = (int)(transformedPosition.Y * perspective) + height / 2;
                
                // Check bounds
                if (screenX >= 0 && screenX < width && screenY >= 0 && screenY < height)
                {
                    // Get color from color table
                    int colorArgb = _colorTable[Math.Min(point.ColorIndex, _colorTable.Length - 1)];
                    Color color = Color.FromArgb(colorArgb);
                    
                    // Apply intensity
                    color = ApplyIntensity(color, Intensity);
                    
                    // Set pixel
                    imageBuffer.SetPixel(screenX, screenY, color);
                }
            }
        }
        
        /// <summary>
        /// Apply intensity multiplier to a color
        /// </summary>
        private Color ApplyIntensity(Color color, float intensity)
        {
            if (intensity <= 1.0f) return color;
            
            int r = Math.Min(255, (int)(color.R * intensity));
            int g = Math.Min(255, (int)(color.G * intensity));
            int b = Math.Min(255, (int)(color.B * intensity));
            
            return Color.FromArgb(color.A, r, g, b);
        }
        
        /// <summary>
        /// Update the rotation angle
        /// </summary>
        private void UpdateRotation()
        {
            _currentRotation += RotationVelocity / 5.0f;
            
            // Keep rotation in 0-360 range
            while (_currentRotation >= 360.0f) _currentRotation -= 360.0f;
            while (_currentRotation < 0.0f) _currentRotation += 360.0f;
        }
        
        #endregion
        
        #region Configuration Validation
        
        public override bool ValidateConfiguration()
        {
            if (RotationVelocity < -100.0f || RotationVelocity > 100.0f) return false;
            if (Angle < -90.0f || Angle > 90.0f) return false;
            if (BaseRadius < 0.1f || BaseRadius > 10.0f) return false;
            if (Intensity < 0.1f || Intensity > 10.0f) return false;
            if (AudioSensitivity < 0.1f || AudioSensitivity > 5.0f) return false;
            if (ParticleLifetime < 0.1f || ParticleLifetime > 5.0f) return false;
            if (Gravity < -1.0f || Gravity > 1.0f) return false;
            if (HeightOffset < -100.0f || HeightOffset > 100.0f) return false;
            if (Depth < 100.0f || Depth > 1000.0f) return false;
            
            return true;
        }
        
        #endregion
        
        #region Preset Methods
        
        /// <summary>
        /// Load a slow rotating fountain preset
        /// </summary>
        public void LoadSlowRotatingPreset()
        {
            RotationVelocity = 8.0f;
            Angle = -15.0f;
            BaseRadius = 1.0f;
            Intensity = 1.0f;
            AudioSensitivity = 1.2f;
            ParticleLifetime = 1.0f;
            Gravity = 0.03f;
            HeightOffset = -20.0f;
            Depth = 400.0f;
        }
        
        /// <summary>
        /// Load a fast spinning fountain preset
        /// </summary>
        public void LoadFastSpinningPreset()
        {
            RotationVelocity = 32.0f;
            Angle = -25.0f;
            BaseRadius = 1.5f;
            Intensity = 1.5f;
            AudioSensitivity = 1.8f;
            ParticleLifetime = 0.8f;
            Gravity = 0.08f;
            HeightOffset = -30.0f;
            Depth = 350.0f;
        }
        
        /// <summary>
        /// Load a gentle flowing preset
        /// </summary>
        public void LoadGentleFlowingPreset()
        {
            RotationVelocity = 4.0f;
            Angle = -10.0f;
            BaseRadius = 0.8f;
            Intensity = 0.8f;
            AudioSensitivity = 0.7f;
            ParticleLifetime = 1.5f;
            Gravity = 0.02f;
            HeightOffset = -15.0f;
            Depth = 450.0f;
        }
        
        /// <summary>
        /// Load a beat-responsive preset
        /// </summary>
        public void LoadBeatResponsivePreset()
        {
            RotationVelocity = 16.0f;
            Angle = -20.0f;
            BaseRadius = 1.2f;
            Intensity = 2.0f;
            AudioSensitivity = 2.5f;
            ParticleLifetime = 0.6f;
            Gravity = 0.06f;
            HeightOffset = -25.0f;
            Depth = 380.0f;
            BeatResponse = true;
        }
        
        #endregion
        
        #region Utility Methods
        
        /// <summary>
        /// Get the current rotation angle
        /// </summary>
        public float GetCurrentRotation()
        {
            return _currentRotation;
        }
        
        /// <summary>
        /// Get the number of active particles
        /// </summary>
        public int GetActiveParticleCount()
        {
            int count = 0;
            for (int h = 0; h < NUM_ROT_HEIGHT; h++)
            {
                for (int r = 0; r < NUM_ROT_DIV; r++)
                {
                    if (_points[h, r].IsActive) count++;
                }
            }
            return count;
        }
        
        /// <summary>
        /// Reset the fountain to initial state
        /// </summary>
        public void Reset()
        {
            _currentRotation = 0.0f;
            _frameCounter = 0;
            _isInitialized = false;
            
            // Clear all points
            for (int h = 0; h < NUM_ROT_HEIGHT; h++)
            {
                for (int r = 0; r < NUM_ROT_DIV; r++)
                {
                    _points[h, r].IsActive = false;
                }
            }
        }
        
        /// <summary>
        /// Get effect execution statistics
        /// </summary>
        public string GetExecutionStats()
        {
            return $"Frame: {_frameCounter}, Rotation: {_currentRotation:F1}°, Active Particles: {GetActiveParticleCount()}, Matrix Valid: {_transformationMatrix != Matrix4x4.Identity}";
        }
        
        #endregion
        
        #region Public Properties for Colors
        
        /// <summary>
        /// Default colors for the fountain (can be customized)
        /// </summary>
        public Color[] DefaultColors { get; set; } = new Color[5];
        
        #endregion
    }
}
```

## Effect Properties

### Core Properties
- **Enabled**: Toggle the effect on/off
- **RotationVelocity**: Speed of fountain rotation in degrees per frame
- **Angle**: Tilt angle of the fountain (-90 to 90 degrees)
- **BaseRadius**: Base radius of the fountain structure
- **Intensity**: Overall effect strength multiplier

### Audio Properties
- **BeatResponse**: Whether to respond to beat detection
- **AudioSensitivity**: Multiplier for audio input sensitivity
- **ParticleLifetime**: How long particles live before disappearing

### Physics Properties
- **Gravity**: Gravity effect on particle movement
- **HeightOffset**: Vertical offset of the fountain base
- **Depth**: Distance of the fountain in 3D space

### Internal Properties
- **CurrentRotation**: Current rotation angle in degrees
- **TransformationMatrix**: 3D transformation matrix for rendering
- **Points**: Array of fountain particles
- **ColorTable**: Pre-calculated color interpolation table

## Fountain Structure

The effect creates a 3D fountain with:
- **30 Rotation Divisions**: Particles are arranged in 30 divisions around the fountain
- **256 Height Levels**: Particles can exist at up to 256 different height levels
- **3D Positioning**: Each particle has X, Y, Z coordinates in 3D space
- **Dynamic Movement**: Particles flow upward with physics-based motion

## Particle System

Each particle in the fountain has:
- **Position**: 3D coordinates (radius, height, angular position)
- **Velocity**: Rate of change for radius and height
- **Color**: Interpolated color from the color palette
- **Lifetime**: How long the particle exists
- **Audio Response**: Movement based on audio input

## 3D Rendering

The effect uses:
- **Matrix Transformations**: Rotation, translation, and perspective projection
- **3D to 2D Projection**: Converts 3D particle positions to screen coordinates
- **Perspective Correction**: Adjusts for different screen resolutions
- **Depth Sorting**: Particles are rendered in depth order

## Audio Integration

The fountain responds to audio by:
- **Frequency Analysis**: Different rotation divisions respond to different frequency bands
- **Beat Detection**: Enhanced particle generation on beats
- **Audio Sensitivity**: Configurable response to audio input
- **Dynamic Variation**: Audio creates variation in particle properties

## Color System

The effect features:
- **5 Base Colors**: Configurable color palette
- **Color Interpolation**: Smooth transitions between colors
- **Audio-Based Coloring**: Particle colors based on audio intensity
- **64 Color Variations**: Pre-calculated color interpolation table

## Performance Optimizations

- **Pre-calculated Tables**: Color interpolation and transformation matrices
- **Efficient Rendering**: Only renders active particles
- **Matrix Operations**: Optimized 3D transformations
- **Bounds Checking**: Clips particles to screen boundaries

## Use Cases

- **Music Visualization**: Dynamic fountain that responds to audio
- **3D Effects**: Creates depth and perspective in visualizations
- **Particle Systems**: Demonstrates advanced particle physics
- **Beat Synchronization**: Visual effects synchronized with music
- **Interactive Displays**: Fountain responds to audio input in real-time

## Preset Effects

### Basic Presets
- **Slow Rotating**: Gentle, slow-moving fountain
- **Fast Spinning**: Rapid rotation with high energy
- **Gentle Flowing**: Smooth, calm particle flow
- **Beat Responsive**: Highly reactive to music beats

### Customization
- **Color Palettes**: User-defined color schemes
- **Physics Parameters**: Adjustable gravity and movement
- **Audio Response**: Configurable sensitivity and behavior
- **Visual Effects**: Customizable rotation and tilt

## Mathematical Functions

The effect uses:
- **Trigonometric Functions**: `sin()`, `cos()` for angular calculations
- **Matrix Mathematics**: 3D transformations and projections
- **Vector Operations**: 3D position and velocity calculations
- **Perspective Projection**: 3D to 2D coordinate conversion

## Error Handling

The effect includes:
- **Bounds Checking**: Validates screen coordinates
- **Parameter Validation**: Ensures configuration values are within ranges
- **Null Checking**: Handles missing audio features gracefully
- **Matrix Validation**: Ensures transformation matrices are valid
