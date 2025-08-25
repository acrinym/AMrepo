# Bass Spin Effects

The Bass Spin effect creates dynamic spinning visual elements that respond to bass frequencies, generating rotating lines or triangles that expand and contract based on audio input intensity.

## Overview

The Bass Spin effect analyzes bass frequencies from the audio spectrum and creates spinning visual elements that respond to the intensity of low-frequency sounds. It supports both line-based and triangle-based rendering modes, with independent control over left and right channel visualization.

## Properties

### Core Settings
- **Enabled**: Controls whether the Bass Spin effect is active (bit-packed for left/right channels)
- **LeftChannelEnabled**: Enables visualization for the left audio channel
- **RightChannelEnabled**: Enables visualization for the right audio channel
- **Mode**: Rendering mode (0 = Lines, 1 = Triangles)
- **LeftColor**: Color for the left channel visualization
- **RightColor**: Color for the right channel visualization
- **Intensity**: Overall intensity of the effect (0.0 to 1.0)

### Internal State
- **LastAudioLevel**: Previous audio level for smooth transitions
- **LeftPosition/RightPosition**: Current positions for left and right channels
- **LeftVelocity/RightVelocity**: Current velocity for smooth movement
- **LeftRotation/RightRotation**: Current rotation angles for spinning effects
- **LeftDirection/RightDirection**: Direction of rotation for each channel

## Rendering Modes

### Line Mode (Mode = 0)
- Creates spinning line patterns that expand and contract
- Lines radiate from the center point outward
- Symmetrical patterns on both sides of the center
- Smooth line drawing with blending support

### Triangle Mode (Mode = 1)
- Generates spinning triangle shapes that respond to audio
- Triangles expand and contract based on bass intensity
- Filled triangle rendering for solid visual impact
- Efficient triangle rasterization algorithm

## Audio Analysis

### Bass Frequency Processing
- Analyzes the first 44 frequency bands (0-43) from the spectrum data
- Focuses on low-frequency content for bass response
- Provides smooth transitions between audio levels
- Maintains visual continuity during audio changes

### Velocity Calculation
- Combines current and previous audio levels for smooth movement
- Uses weighted averaging (70% current, 30% previous)
- Prevents sudden jumps and provides fluid animation
- Scales rotation speed based on audio intensity

## Implementation Details

### Channel Separation
- Independent processing for left and right audio channels
- Separate color schemes for each channel
- Configurable enable/disable for individual channels
- Synchronized but independent rotation patterns

### Rotation System
- Continuous rotation based on audio intensity
- Configurable rotation direction for each channel
- Smooth angular velocity changes
- Maintains rotation state across frames

### Rendering Optimization
- Efficient line drawing with blending support
- Optimized triangle rasterization algorithm
- Minimal memory allocation during rendering
- Support for different blending modes

## C# Implementation

```csharp
using System;
using System.Drawing;
using PhoenixVisualizer.Core.Effects.Models;
using PhoenixVisualizer.Core.Models;

namespace PhoenixVisualizer.Core.Effects.Nodes.AvsEffects
{
    public class BassSpinEffectsNode : BaseEffectNode
    {
        #region Properties

        /// <summary>
        /// Controls whether the Bass Spin effect is active
        /// </summary>
        public bool Enabled { get; set; } = true;

        /// <summary>
        /// Enables visualization for the left audio channel
        /// </summary>
        public bool LeftChannelEnabled { get; set; } = true;

        /// <summary>
        /// Enables visualization for the right audio channel
        /// </summary>
        public bool RightChannelEnabled { get; set; } = true;

        /// <summary>
        /// Rendering mode (0 = Lines, 1 = Triangles)
        /// </summary>
        public int Mode { get; set; } = 1;

        /// <summary>
        /// Color for the left channel visualization
        /// </summary>
        public Color LeftColor { get; set; } = Color.White;

        /// <summary>
        /// Color for the right channel visualization
        /// </summary>
        public Color RightColor { get; set; } = Color.White;

        /// <summary>
        /// Overall intensity of the effect (0.0 to 1.0)
        /// </summary>
        public float Intensity { get; set; } = 1.0f;

        #endregion

        #region Private Fields

        private int lastAudioLevel = 0;
        private Point[,] leftPositions = new Point[2, 2];
        private Point[,] rightPositions = new Point[2, 2];
        private double leftVelocity = 0.0;
        private double rightVelocity = 0.0;
        private double leftRotation = Math.PI;
        private double rightRotation = 0.0;
        private double leftDirection = -1.0;
        private double rightDirection = 1.0;
        private const double RotationStep = Math.PI / 6.0;
        private const int BassBandCount = 44;

        #endregion

        #region Public Methods

        /// <summary>
        /// Processes the current frame with Bass Spin visualization
        /// </summary>
        public override void ProcessFrame(ImageBuffer imageBuffer, AudioFeatures audioFeatures)
        {
            if (!Enabled)
                return;

            int width = imageBuffer.Width;
            int height = imageBuffer.Height;

            // Process left channel if enabled
            if (LeftChannelEnabled)
            {
                ProcessChannel(imageBuffer, audioFeatures, 0, LeftColor, width, height);
            }

            // Process right channel if enabled
            if (RightChannelEnabled)
            {
                ProcessChannel(imageBuffer, audioFeatures, 1, RightColor, width, height);
            }
        }

        /// <summary>
        /// Sets the rendering mode
        /// </summary>
        public void SetMode(int mode)
        {
            Mode = (mode == 0 || mode == 1) ? mode : 1;
        }

        /// <summary>
        /// Sets the left channel color
        /// </summary>
        public void SetLeftColor(Color color)
        {
            LeftColor = color;
        }

        /// <summary>
        /// Sets the right channel color
        /// </summary>
        public void SetRightColor(Color color)
        {
            RightColor = color;
        }

        /// <summary>
        /// Enables or disables the left channel
        /// </summary>
        public void SetLeftChannelEnabled(bool enabled)
        {
            LeftChannelEnabled = enabled;
        }

        /// <summary>
        /// Enables or disables the right channel
        /// </summary>
        public void SetRightChannelEnabled(bool enabled)
        {
            RightChannelEnabled = enabled;
        }

        #endregion

        #region Private Methods

        private void ProcessChannel(ImageBuffer imageBuffer, AudioFeatures audioFeatures, int channelIndex, Color color, int width, int height)
        {
            // Calculate audio level from bass frequencies
            int audioLevel = CalculateBassLevel(audioFeatures, channelIndex);
            
            // Update velocity with smooth transitions
            double velocity = 0.7 * (Math.Max(audioLevel - 104, 12) / 96.0) + 0.3 * GetChannelVelocity(channelIndex);
            SetChannelVelocity(channelIndex, velocity);

            // Update rotation
            double rotation = GetChannelRotation(channelIndex);
            double direction = GetChannelDirection(channelIndex);
            rotation += RotationStep * velocity * direction;
            SetChannelRotation(channelIndex, rotation);

            // Calculate visual size based on audio level
            int maxSize = Math.Min(height / 2, (width * 3) / 8);
            double size = maxSize * (audioLevel / 256.0);
            
            // Calculate center position
            int centerX = (channelIndex == 0) ? width / 2 - maxSize / 2 : width / 2 + maxSize / 2;
            int centerY = height / 2;

            // Calculate current position
            int xPos = (int)(Math.Cos(rotation) * size);
            int yPos = (int)(Math.Sin(rotation) * size);

            // Render based on mode
            if (Mode == 0)
            {
                RenderLines(imageBuffer, centerX, centerY, xPos, yPos, color, channelIndex, width, height);
            }
            else
            {
                RenderTriangles(imageBuffer, centerX, centerY, xPos, yPos, color, channelIndex, width, height);
            }
        }

        private int CalculateBassLevel(AudioFeatures audioFeatures, int channelIndex)
        {
            // Analyze the first 44 frequency bands for bass content
            int totalLevel = 0;
            var spectrumData = audioFeatures.GetSpectrumData();
            
            if (spectrumData != null && spectrumData.Length > 0)
            {
                int bandCount = Math.Min(BassBandCount, spectrumData.Length);
                for (int i = 0; i < bandCount; i++)
                {
                    totalLevel += (int)spectrumData[i];
                }
            }

            // Calculate relative level compared to previous frame
            int relativeLevel = (totalLevel * 512) / (lastAudioLevel + 30 * 256);
            lastAudioLevel = totalLevel;

            return Math.Min(relativeLevel, 255);
        }

        private void RenderLines(ImageBuffer imageBuffer, int centerX, int centerY, int xPos, int yPos, Color color, int channelIndex, int width, int height)
        {
            var positions = GetChannelPositions(channelIndex);

            // Draw line from center to current position
            if (positions[0, 0] != Point.Empty || positions[0, 1] != Point.Empty)
            {
                DrawLine(imageBuffer, positions[0, 0], positions[0, 1], centerX + xPos, centerY + yPos, color);
            }

            // Draw line from center to current position
            DrawLine(imageBuffer, centerX, centerY, centerX + xPos, centerY + yPos, color);

            // Draw symmetrical line on the opposite side
            if (positions[1, 0] != Point.Empty || positions[1, 1] != Point.Empty)
            {
                DrawLine(imageBuffer, positions[1, 0], positions[1, 1], centerX - xPos, centerY - yPos, color);
            }

            // Draw line from center to opposite position
            DrawLine(imageBuffer, centerX, centerY, centerX - xPos, centerY - yPos, color);

            // Update positions
            UpdateChannelPositions(channelIndex, centerX + xPos, centerY + yPos, centerX - xPos, centerY - yPos);
        }

        private void RenderTriangles(ImageBuffer imageBuffer, int centerX, int centerY, int xPos, int yPos, Color color, int channelIndex, int width, int height)
        {
            var positions = GetChannelPositions(channelIndex);

            // Render triangle from center to previous and current positions
            if (positions[0, 0] != Point.Empty || positions[0, 1] != Point.Empty)
            {
                Point[] triangle1 = { new Point(centerX, centerY), positions[0, 0], new Point(centerX + xPos, centerY + yPos) };
                RenderTriangle(imageBuffer, triangle1, color);
            }

            // Render triangle from center to previous and current opposite positions
            if (positions[1, 0] != Point.Empty || positions[1, 1] != Point.Empty)
            {
                Point[] triangle2 = { new Point(centerX, centerY), positions[1, 0], new Point(centerX - xPos, centerY - yPos) };
                RenderTriangle(imageBuffer, triangle2, color);
            }

            // Update positions
            UpdateChannelPositions(channelIndex, centerX + xPos, centerY + yPos, centerX - xPos, centerY - yPos);
        }

        private void DrawLine(ImageBuffer imageBuffer, Point start, Point end, int x, int y, Color color)
        {
            if (start == Point.Empty)
                return;

            DrawLine(imageBuffer, start.X, start.Y, x, y, color);
        }

        private void DrawLine(ImageBuffer imageBuffer, int x1, int y1, int x2, int y2, Color color)
        {
            // Bresenham line drawing algorithm
            int dx = Math.Abs(x2 - x1);
            int dy = Math.Abs(y2 - y1);
            int sx = x1 < x2 ? 1 : -1;
            int sy = y1 < y2 ? 1 : -1;
            int err = dx - dy;

            int x = x1, y = y1;

            while (true)
            {
                if (x >= 0 && x < imageBuffer.Width && y >= 0 && y < imageBuffer.Height)
                {
                    Color existingColor = imageBuffer.GetPixel(x, y);
                    Color blendedColor = BlendColors(existingColor, color);
                    imageBuffer.SetPixel(x, y, blendedColor);
                }

                if (x == x2 && y == y2) break;

                int e2 = 2 * err;
                if (e2 > -dy)
                {
                    err -= dy;
                    x += sx;
                }
                if (e2 < dx)
                {
                    err += dx;
                    y += sy;
                }
            }
        }

        private void RenderTriangle(ImageBuffer imageBuffer, Point[] points, Color color)
        {
            if (points.Length != 3)
                return;

            // Sort points by Y coordinate for efficient rasterization
            Array.Sort(points, (a, b) => a.Y.CompareTo(b.Y));

            int x1 = points[0].X, y1 = points[0].Y;
            int x2 = points[1].X, y2 = points[1].Y;
            int x3 = points[2].X, y3 = points[2].Y;

            // Calculate slopes for triangle edges
            double slope1 = (y2 - y1) != 0 ? (double)(x2 - x1) / (y2 - y1) : 0;
            double slope2 = (y3 - y1) != 0 ? (double)(x3 - x1) / (y3 - y1) : 0;
            double slope3 = (y3 - y2) != 0 ? (double)(x3 - x2) / (y3 - y2) : 0;

            // Rasterize triangle
            for (int y = y1; y <= y3; y++)
            {
                if (y < 0 || y >= imageBuffer.Height) continue;

                int startX, endX;

                if (y < y2)
                {
                    startX = (int)(x1 + slope1 * (y - y1));
                    endX = (int)(x1 + slope2 * (y - y1));
                }
                else
                {
                    startX = (int)(x2 + slope3 * (y - y2));
                    endX = (int)(x1 + slope2 * (y - y1));
                }

                if (startX > endX)
                {
                    int temp = startX;
                    startX = endX;
                    endX = temp;
                }

                // Draw horizontal line segment
                for (int x = startX; x <= endX; x++)
                {
                    if (x >= 0 && x < imageBuffer.Width)
                    {
                        Color existingColor = imageBuffer.GetPixel(x, y);
                        Color blendedColor = BlendColors(existingColor, color);
                        imageBuffer.SetPixel(x, y, blendedColor);
                    }
                }
            }
        }

        private Color BlendColors(Color existing, Color source)
        {
            // Simple additive blending
            return Color.FromArgb(
                Math.Min(255, existing.A + source.A),
                Math.Min(255, existing.R + source.R),
                Math.Min(255, existing.G + source.G),
                Math.Min(255, existing.B + source.B)
            );
        }

        #region Channel State Management

        private double GetChannelVelocity(int channelIndex)
        {
            return channelIndex == 0 ? leftVelocity : rightVelocity;
        }

        private void SetChannelVelocity(int channelIndex, double velocity)
        {
            if (channelIndex == 0)
                leftVelocity = velocity;
            else
                rightVelocity = velocity;
        }

        private double GetChannelRotation(int channelIndex)
        {
            return channelIndex == 0 ? leftRotation : rightRotation;
        }

        private void SetChannelRotation(int channelIndex, double rotation)
        {
            if (channelIndex == 0)
                leftRotation = rotation;
            else
                rightRotation = rotation;
        }

        private double GetChannelDirection(int channelIndex)
        {
            return channelIndex == 0 ? leftDirection : rightDirection;
        }

        private Point[,] GetChannelPositions(int channelIndex)
        {
            return channelIndex == 0 ? leftPositions : rightPositions;
        }

        private void UpdateChannelPositions(int channelIndex, int x1, int y1, int x2, int y2)
        {
            var positions = GetChannelPositions(channelIndex);
            positions[0, 0] = positions[0, 1];
            positions[0, 1] = new Point(x1, y1);
            positions[1, 0] = positions[1, 1];
            positions[1, 1] = new Point(x2, y2);
        }

        #endregion

        #endregion

        #region Configuration

        /// <summary>
        /// Validates the current configuration
        /// </summary>
        public override bool ValidateConfiguration()
        {
            if (Mode < 0 || Mode > 1)
                Mode = 1;

            if (Intensity < 0.0f || Intensity > 1.0f)
                Intensity = 1.0f;

            return true;
        }

        /// <summary>
        /// Returns a summary of current settings
        /// </summary>
        public override string GetSettingsSummary()
        {
            string channels = "";
            if (LeftChannelEnabled && RightChannelEnabled)
                channels = "Both";
            else if (LeftChannelEnabled)
                channels = "Left";
            else if (RightChannelEnabled)
                channels = "Right";
            else
                channels = "None";

            return $"Bass Spin: {(Enabled ? "Enabled" : "Disabled")}, " +
                   $"Channels: {channels}, " +
                   $"Mode: {(Mode == 0 ? "Lines" : "Triangles")}";
        }

        #endregion

        #region Initialization

        public BassSpinEffectsNode()
        {
            // Initialize positions to empty
            for (int i = 0; i < 2; i++)
            {
                for (int j = 0; j < 2; j++)
                {
                    leftPositions[i, j] = Point.Empty;
                    rightPositions[i, j] = Point.Empty;
                }
            }
        }

        /// <summary>
        /// Resets all positions and rotation states
        /// </summary>
        public void Reset()
        {
            leftRotation = Math.PI;
            rightRotation = 0.0;
            leftVelocity = 0.0;
            rightVelocity = 0.0;
            lastAudioLevel = 0;

            for (int i = 0; i < 2; i++)
            {
                for (int j = 0; j < 2; j++)
                {
                    leftPositions[i, j] = Point.Empty;
                    rightPositions[i, j] = Point.Empty;
                }
            }
        }

        #endregion
    }
}
```

## Usage Examples

### Basic Bass Spin with Lines
```csharp
var bassSpinNode = new BassSpinEffectsNode();
bassSpinNode.Enabled = true;
bassSpinNode.Mode = 0; // Lines mode
bassSpinNode.LeftChannelEnabled = true;
bassSpinNode.RightChannelEnabled = true;
```

### Triangle Mode with Custom Colors
```csharp
var bassSpinNode = new BassSpinEffectsNode();
bassSpinNode.Enabled = true;
bassSpinNode.Mode = 1; // Triangle mode
bassSpinNode.SetLeftColor(Color.Blue);
bassSpinNode.SetRightColor(Color.Red);
```

### Single Channel Configuration
```csharp
var bassSpinNode = new BassSpinEffectsNode();
bassSpinNode.Enabled = true;
bassSpinNode.SetLeftChannelEnabled(true);
bassSpinNode.SetRightChannelEnabled(false);
bassSpinNode.Mode = 1;
```

### High-Intensity Bass Response
```csharp
var bassSpinNode = new BassSpinEffectsNode();
bassSpinNode.Enabled = true;
bassSpinNode.Mode = 1;
bassSpinNode.Intensity = 1.0f;
bassSpinNode.SetLeftColor(Color.Yellow);
bassSpinNode.SetRightColor(Color.Orange);
```

## Performance Notes

- Line mode is more efficient than triangle mode
- Bass frequency analysis is optimized for the first 44 bands
- Position updates are minimal and efficient
- Rendering scales linearly with audio intensity

## Limitations

- Bass analysis is limited to the first 44 frequency bands
- Rotation speed is capped by audio level calculations
- Triangle rendering may be computationally intensive at high resolutions
- Channel separation requires stereo audio input

## Future Enhancements

- Configurable frequency band ranges for bass analysis
- Additional rendering modes (circles, polygons, etc.)
- Custom rotation patterns and animations
- Advanced blending modes and effects
- Real-time parameter modulation
- MIDI synchronization for rotation control
