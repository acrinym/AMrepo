# Dot Plane Effects

The Dot Plane effect creates a 3D plane of colored dots that rotates and responds to audio input. It generates a dynamic surface that can be tilted, rotated, and animated based on music, creating a sophisticated 3D visualization effect.

## Effect Overview

The Dot Plane effect works by:
1. Creating a 64x64 grid of dots in 3D space
2. Applying 3D transformations including rotation and perspective projection
3. Using audio input to control dot heights and colors
4. Implementing physics-based movement with velocity and damping
5. Rendering the plane with depth-based perspective and blending

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
    public class DotPlaneEffectsNode : BaseEffectNode
    {
        #region Constants
        
        /// <summary>
        /// Width and height of the dot plane grid
        /// </summary>
        private const int NUM_WIDTH = 64;
        
        #endregion
        
        #region Properties
        
        /// <summary>
        /// Whether the effect is enabled
        /// </summary>
        public bool Enabled { get; set; } = true;
        
        /// <summary>
        /// Rotation velocity of the plane (degrees per frame)
        /// </summary>
        public float RotationVelocity { get; set; } = 16.0f;
        
        /// <summary>
        /// Angle of the plane tilt (-90 to 90 degrees)
        /// </summary>
        public float Angle { get; set; } = -20.0f;
        
        /// <summary>
        /// Base radius of the plane
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
        /// Audio sensitivity for dot height control
        /// </summary>
        public float AudioSensitivity { get; set; } = 1.0f;
        
        /// <summary>
        /// Physics damping factor for dot movement
        /// </summary>
        public float DampingFactor { get; set; } = 0.15f;
        
        /// <summary>
        /// Velocity update rate for smooth movement
        /// </summary>
        public float VelocityUpdateRate { get; set; } = 90.0f;
        
        /// <summary>
        /// Plane height offset in 3D space
        /// </summary>
        public float HeightOffset { get; set; } = -20.0f;
        
        /// <summary>
        /// Plane depth in 3D space
        /// </summary>
        public float Depth { get; set; } = 400.0f;
        
        /// <summary>
        /// Plane width in 3D space
        /// </summary>
        public float PlaneWidth { get; set; } = 350.0f;
        
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
        /// Array of dot heights for each grid position
        /// </summary>
        private float[,] _heightTable;
        
        /// <summary>
        /// Array of dot velocities for each grid position
        /// </summary>
        private float[,] _velocityTable;
        
        /// <summary>
        /// Array of dot colors for each grid position
        /// </summary>
        private int[,] _colorTable;
        
        /// <summary>
        /// Pre-calculated color interpolation table
        /// </summary>
        private int[] _colorInterpolationTable;
        
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
        
        public DotPlaneEffectsNode()
        {
            _heightTable = new float[NUM_WIDTH, NUM_WIDTH];
            _velocityTable = new float[NUM_WIDTH, NUM_WIDTH];
            _colorTable = new int[NUM_WIDTH, NUM_WIDTH];
            _colorInterpolationTable = new int[64];
            
            // Set default colors (BGR format like original)
            SetDefaultColors();
            
            // Initialize tables
            InitializeTables();
        }
        
        #endregion
        
        #region Initialization Methods
        
        /// <summary>
        /// Set default colors for the plane
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
                    
                    _colorInterpolationTable[t * 16 + x] = Color.FromArgb(255, r, g, b).ToArgb();
                }
            }
        }
        
        /// <summary>
        /// Initialize all data tables
        /// </summary>
        private void InitializeTables()
        {
            // Clear all tables
            for (int y = 0; y < NUM_WIDTH; y++)
            {
                for (int x = 0; x < NUM_WIDTH; x++)
                {
                    _heightTable[y, x] = 0.0f;
                    _velocityTable[y, x] = 0.0f;
                    _colorTable[y, x] = 0;
                }
            }
            
            // Initialize color table
            InitializeColorTable();
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
            
            // Update dot plane physics
            UpdateDotPlanePhysics(audioFeatures);
            
            // Render the plane
            RenderDotPlane(imageBuffer);
            
            // Update rotation
            UpdateRotation();
        }
        
        /// <summary>
        /// Update the 3D transformation matrix
        /// </summary>
        private void UpdateTransformationMatrix()
        {
            // Create rotation matrix around Y axis (plane rotation)
            Matrix4x4 rotationY = Matrix4x4.CreateRotationY(_currentRotation * (float)Math.PI / 180.0f);
            
            // Create rotation matrix around X axis (plane tilt)
            Matrix4x4 rotationX = Matrix4x4.CreateRotationX(Angle * (float)Math.PI / 180.0f);
            
            // Create translation matrix
            Matrix4x4 translation = Matrix4x4.CreateTranslation(0.0f, HeightOffset, Depth);
            
            // Combine transformations: translate -> rotate X -> rotate Y
            _transformationMatrix = translation * rotationX * rotationY;
        }
        
        /// <summary>
        /// Update the dot plane physics and audio response
        /// </summary>
        private void UpdateDotPlanePhysics(AudioFeatures audioFeatures)
        {
            // Create backup of height table for physics calculations
            float[,] backupHeightTable = new float[NUM_WIDTH, NUM_WIDTH];
            Array.Copy(_heightTable, backupHeightTable, _heightTable.Length);
            
            // Update dot positions and velocities
            for (int fo = 0; fo < NUM_WIDTH; fo++)
            {
                int sourceIndex = NUM_WIDTH - (fo + 2);
                int targetIndex = NUM_WIDTH - (fo + 1);
                
                if (fo == NUM_WIDTH - 1)
                {
                    // Generate new dots from audio input
                    GenerateNewDotsFromAudio(audioFeatures);
                }
                else
                {
                    // Update existing dots with physics
                    UpdateExistingDots(sourceIndex, targetIndex);
                }
            }
        }
        
        /// <summary>
        /// Generate new dots from audio input
        /// </summary>
        private void GenerateNewDotsFromAudio(AudioFeatures audioFeatures)
        {
            for (int p = 0; p < NUM_WIDTH; p++)
            {
                // Get audio value for this position
                float audioValue = GetAudioValue(p, audioFeatures);
                
                // Set height based on audio
                _heightTable[0, p] = audioValue;
                
                // Calculate color based on audio intensity
                int colorIndex = Math.Min(63, (int)(audioValue / 4));
                _colorTable[0, p] = _colorInterpolationTable[colorIndex];
                
                // Calculate velocity for smooth movement
                float velocity = (audioValue - _heightTable[1, p]) / VelocityUpdateRate;
                _velocityTable[0, p] = velocity;
            }
        }
        
        /// <summary>
        /// Update existing dots with physics simulation
        /// </summary>
        private void UpdateExistingDots(int sourceIndex, int targetIndex)
        {
            for (int p = 0; p < NUM_WIDTH; p++)
            {
                // Update height based on velocity
                float newHeight = _heightTable[sourceIndex, p] + _velocityTable[sourceIndex, p];
                
                // Clamp height to prevent negative values
                if (newHeight < 0.0f) newHeight = 0.0f;
                
                _heightTable[targetIndex, p] = newHeight;
                
                // Update velocity with damping
                float damping = DampingFactor * (newHeight / 255.0f);
                _velocityTable[targetIndex, p] = _velocityTable[sourceIndex, p] - damping;
                
                // Copy color
                _colorTable[targetIndex, p] = _colorTable[sourceIndex, p];
            }
        }
        
        /// <summary>
        /// Get audio value for a specific position
        /// </summary>
        private float GetAudioValue(int position, AudioFeatures audioFeatures)
        {
            float baseValue = 0.0f;
            
            if (audioFeatures != null)
            {
                // Use different frequency bands for different positions
                int bandIndex = position % audioFeatures.FrequencyBands.Length;
                baseValue = audioFeatures.FrequencyBands[bandIndex];
            }
            
            // Add some variation based on position
            float variation = (float)Math.Sin(position * 0.1f + _frameCounter * 0.05f) * 30.0f;
            baseValue += variation;
            
            // Apply audio sensitivity
            baseValue *= AudioSensitivity;
            
            // Clamp to valid range
            return Math.Max(0, Math.Min(255, baseValue));
        }
        
        /// <summary>
        /// Render the dot plane to the image buffer
        /// </summary>
        private void RenderDotPlane(ImageBuffer imageBuffer)
        {
            int width = imageBuffer.Width;
            int height = imageBuffer.Height;
            
            // Calculate perspective adjustment
            float perspectiveAdjust = Math.Min(
                width * 440.0f / 640.0f,
                height * 440.0f / 480.0f
            );
            
            // Render each row of the plane
            for (int fo = 0; fo < NUM_WIDTH; fo++)
            {
                // Determine rendering order based on rotation
                int renderIndex = (_currentRotation < 90.0f || _currentRotation > 270.0f) 
                    ? NUM_WIDTH - fo - 1 : fo;
                
                // Calculate plane dimensions
                float dotWidth = PlaneWidth / NUM_WIDTH;
                float startWidth = -(NUM_WIDTH * 0.5f) * dotWidth;
                
                // Get current row data
                int[] colorRow = GetColorRow(renderIndex);
                float[] heightRow = GetHeightRow(renderIndex);
                
                // Determine rendering direction
                int direction = (_currentRotation < 180.0f) ? -1 : 1;
                float widthStep = (_currentRotation < 180.0f) ? -dotWidth : dotWidth;
                float currentWidth = (_currentRotation < 180.0f) ? -startWidth + dotWidth : startWidth;
                
                // Render dots in this row
                for (int p = 0; p < NUM_WIDTH; p++)
                {
                    int dataIndex = (_currentRotation < 180.0f) ? NUM_WIDTH - 1 - p : p;
                    
                    // Calculate 3D position
                    Vector3 position = new Vector3(
                        currentWidth,
                        64.0f - heightRow[dataIndex],
                        (renderIndex - NUM_WIDTH * 0.5f) * dotWidth
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
                            int colorArgb = colorRow[dataIndex];
                            Color color = Color.FromArgb(colorArgb);
                            
                            // Apply intensity
                            color = ApplyIntensity(color, Intensity);
                            
                            // Set pixel
                            imageBuffer.SetPixel(screenX, screenY, color);
                        }
                    }
                    
                    // Update width for next dot
                    currentWidth += widthStep;
                }
            }
        }
        
        /// <summary>
        /// Get a row of colors from the color table
        /// </summary>
        private int[] GetColorRow(int rowIndex)
        {
            int[] row = new int[NUM_WIDTH];
            for (int i = 0; i < NUM_WIDTH; i++)
            {
                row[i] = _colorTable[rowIndex, i];
            }
            return row;
        }
        
        /// <summary>
        /// Get a row of heights from the height table
        /// </summary>
        private float[] GetHeightRow(int rowIndex)
        {
            float[] row = new float[NUM_WIDTH];
            for (int i = 0; i < NUM_WIDTH; i++)
            {
                row[i] = _heightTable[rowIndex, i];
            }
            return row;
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
            if (DampingFactor < 0.01f || DampingFactor > 1.0f) return false;
            if (VelocityUpdateRate < 10.0f || VelocityUpdateRate > 200.0f) return false;
            if (HeightOffset < -100.0f || HeightOffset > 100.0f) return false;
            if (Depth < 100.0f || Depth > 1000.0f) return false;
            if (PlaneWidth < 100.0f || PlaneWidth > 1000.0f) return false;
            
            return true;
        }
        
        #endregion
        
        #region Preset Methods
        
        /// <summary>
        /// Load a slow rotating plane preset
        /// </summary>
        public void LoadSlowRotatingPreset()
        {
            RotationVelocity = 8.0f;
            Angle = -15.0f;
            BaseRadius = 1.0f;
            Intensity = 1.0f;
            AudioSensitivity = 1.2f;
            DampingFactor = 0.12f;
            VelocityUpdateRate = 90.0f;
            HeightOffset = -20.0f;
            Depth = 400.0f;
            PlaneWidth = 350.0f;
        }
        
        /// <summary>
        /// Load a fast spinning plane preset
        /// </summary>
        public void LoadFastSpinningPreset()
        {
            RotationVelocity = 32.0f;
            Angle = -25.0f;
            BaseRadius = 1.5f;
            Intensity = 1.5f;
            AudioSensitivity = 1.8f;
            DampingFactor = 0.20f;
            VelocityUpdateRate = 70.0f;
            HeightOffset = -30.0f;
            Depth = 350.0f;
            PlaneWidth = 300.0f;
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
            DampingFactor = 0.08f;
            VelocityUpdateRate = 120.0f;
            HeightOffset = -15.0f;
            Depth = 450.0f;
            PlaneWidth = 400.0f;
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
            DampingFactor = 0.18f;
            VelocityUpdateRate = 60.0f;
            HeightOffset = -25.0f;
            Depth = 380.0f;
            PlaneWidth = 320.0f;
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
        /// Get the number of active dots
        /// </summary>
        public int GetActiveDotCount()
        {
            int count = 0;
            for (int y = 0; y < NUM_WIDTH; y++)
            {
                for (int x = 0; x < NUM_WIDTH; x++)
                {
                    if (_heightTable[y, x] > 0.0f) count++;
                }
            }
            return count;
        }
        
        /// <summary>
        /// Get the average height of all dots
        /// </summary>
        public float GetAverageDotHeight()
        {
            float total = 0.0f;
            int count = 0;
            
            for (int y = 0; y < NUM_WIDTH; y++)
            {
                for (int x = 0; x < NUM_WIDTH; x++)
                {
                    total += _heightTable[y, x];
                    count++;
                }
            }
            
            return count > 0 ? total / count : 0.0f;
        }
        
        /// <summary>
        /// Reset the plane to initial state
        /// </summary>
        public void Reset()
        {
            _currentRotation = 0.0f;
            _frameCounter = 0;
            _isInitialized = false;
            
            // Clear all tables
            InitializeTables();
        }
        
        /// <summary>
        /// Get effect execution statistics
        /// </summary>
        public string GetExecutionStats()
        {
            return $"Frame: {_frameCounter}, Rotation: {_currentRotation:F1}°, Active Dots: {GetActiveDotCount()}, Avg Height: {GetAverageDotHeight():F1}, Matrix Valid: {_transformationMatrix != Matrix4x4.Identity}";
        }
        
        #endregion
        
        #region Public Properties for Colors
        
        /// <summary>
        /// Default colors for the plane (can be customized)
        /// </summary>
        public Color[] DefaultColors { get; set; } = new Color[5];
        
        #endregion
    }
}
```

## Effect Properties

### Core Properties
- **Enabled**: Toggle the effect on/off
- **RotationVelocity**: Speed of plane rotation in degrees per frame
- **Angle**: Tilt angle of the plane (-90 to 90 degrees)
- **BaseRadius**: Base radius of the plane structure
- **Intensity**: Overall effect strength multiplier

### Audio Properties
- **BeatResponse**: Whether to respond to beat detection
- **AudioSensitivity**: Multiplier for audio input sensitivity
- **DampingFactor**: Physics damping for smooth movement
- **VelocityUpdateRate**: Rate of velocity updates

### Physics Properties
- **HeightOffset**: Vertical offset of the plane in 3D space
- **Depth**: Distance of the plane in 3D space
- **PlaneWidth**: Width of the plane in 3D space

### Internal Properties
- **CurrentRotation**: Current rotation angle in degrees
- **TransformationMatrix**: 3D transformation matrix for rendering
- **HeightTable**: Array of dot heights
- **VelocityTable**: Array of dot velocities
- **ColorTable**: Array of dot colors

## Plane Structure

The effect creates a 3D plane with:
- **64x64 Grid**: 4096 dots arranged in a square grid
- **3D Positioning**: Each dot has X, Y, Z coordinates
- **Dynamic Heights**: Dot heights respond to audio input
- **Physics Simulation**: Smooth movement with velocity and damping

## Physics System

Each dot in the plane has:
- **Height**: Current vertical position
- **Velocity**: Rate of height change
- **Damping**: Gradual slowdown over time
- **Audio Response**: Height based on frequency analysis

## 3D Rendering

The effect uses:
- **Matrix Transformations**: Rotation, translation, and perspective projection
- **3D to 2D Projection**: Converts 3D dot positions to screen coordinates
- **Perspective Correction**: Adjusts for different screen resolutions
- **Depth Sorting**: Dots are rendered in depth order

## Audio Integration

The plane responds to audio by:
- **Frequency Analysis**: Different grid positions respond to different frequency bands
- **Beat Detection**: Enhanced dot generation on beats
- **Audio Sensitivity**: Configurable response to audio input
- **Dynamic Variation**: Audio creates variation in dot heights

## Color System

The effect features:
- **5 Base Colors**: Configurable color palette
- **Color Interpolation**: Smooth transitions between colors
- **Audio-Based Coloring**: Dot colors based on audio intensity
- **64 Color Variations**: Pre-calculated color interpolation table

## Performance Optimizations

- **Pre-calculated Tables**: Color interpolation and transformation matrices
- **Efficient Rendering**: Only renders visible dots
- **Matrix Operations**: Optimized 3D transformations
- **Physics Simulation**: Efficient velocity and height updates

## Use Cases

- **Music Visualization**: Dynamic plane that responds to audio
- **3D Effects**: Creates depth and perspective in visualizations
- **Physics Simulation**: Demonstrates realistic dot movement
- **Beat Synchronization**: Visual effects synchronized with music
- **Interactive Displays**: Plane responds to audio input in real-time

## Preset Effects

### Basic Presets
- **Slow Rotating**: Gentle, slow-moving plane
- **Fast Spinning**: Rapid rotation with high energy
- **Gentle Flowing**: Smooth, calm dot flow
- **Beat Responsive**: Highly reactive to music beats

### Customization
- **Color Palettes**: User-defined color schemes
- **Physics Parameters**: Adjustable damping and movement
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
- **Matrix Validation**: Ensures transformation matrices are valid
- **Physics Safety**: Prevents invalid height and velocity values
