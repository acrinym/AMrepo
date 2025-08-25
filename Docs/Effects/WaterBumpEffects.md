# Water Bump Effects

## Overview

The Water Bump effect creates advanced fluid simulation with height-based displacement mapping. It simulates realistic water surface dynamics by maintaining height buffers and applying fluid physics calculations, creating organic wave patterns that respond to audio input and generate depth through sophisticated displacement algorithms.

## C# Implementation

### WaterBumpEffectsNode Class

```csharp
using System;
using System.Collections.Generic;
using System.Drawing;
using PhoenixVisualizer.Core.Effects.Models;
using PhoenixVisualizer.Core.Models;

namespace PhoenixVisualizer.Core.Effects.Nodes.AvsEffects
{
    public class WaterBumpEffectsNode : BaseEffectNode
    {
        #region Properties

        /// <summary>
        /// Enable/disable the water bump effect
        /// </summary>
        public bool Enabled { get; set; } = true;

        /// <summary>
        /// Water density - controls wave damping (2-10)
        /// </summary>
        public int Density { get; set; } = 6;

        /// <summary>
        /// Wave depth - controls displacement intensity (100-2000)
        /// </summary>
        public int Depth { get; set; } = 600;

        /// <summary>
        /// Random drop placement - true for random, false for fixed position
        /// </summary>
        public bool RandomDrop { get; set; } = false;

        /// <summary>
        /// Drop position X - 0=left, 1=center, 2=right
        /// </summary>
        public int DropPositionX { get; set; } = 1;

        /// <summary>
        /// Drop position Y - 0=top, 1=middle, 2=bottom
        /// </summary>
        public int DropPositionY { get; set; } = 1;

        /// <summary>
        /// Drop radius - controls wave source size (10-100)
        /// </summary>
        public int DropRadius { get; set; } = 40;

        /// <summary>
        /// Calculation method - 0=standard, 1=sludge
        /// </summary>
        public int Method { get; set; } = 0;

        #endregion

        #region Private Fields

        private int[,] _heightBuffer1;
        private int[,] _heightBuffer2;
        private int _currentBuffer;
        private int _bufferWidth;
        private int _bufferHeight;
        private Random _random;

        #endregion

        #region Constructor

        public WaterBumpEffectsNode()
        {
            _heightBuffer1 = new int[0, 0];
            _heightBuffer2 = new int[0, 0];
            _currentBuffer = 0;
            _bufferWidth = 0;
            _bufferHeight = 0;
            _random = new Random();
        }

        #endregion

        #region Processing

        public override void ProcessFrame(ImageBuffer imageBuffer, AudioFeatures audioFeatures)
        {
            if (!Enabled) return;

            int width = imageBuffer.Width;
            int height = imageBuffer.Height;

            // Initialize height buffers if dimensions changed
            if (_bufferWidth != width || _bufferHeight != height)
            {
                InitializeBuffers(width, height);
            }

            // Create water drops on beat
            if (audioFeatures.IsBeat)
            {
                CreateWaterDrop();
            }

            // Apply water displacement to image
            ApplyWaterDisplacement(imageBuffer);

            // Calculate next frame water physics
            CalculateWaterPhysics();

            // Swap buffers
            _currentBuffer = 1 - _currentBuffer;
        }

        private void InitializeBuffers(int width, int height)
        {
            _heightBuffer1 = new int[width, height];
            _heightBuffer2 = new int[width, height];
            _bufferWidth = width;
            _bufferHeight = height;
            _currentBuffer = 0;

            // Clear buffers
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    _heightBuffer1[x, y] = 0;
                    _heightBuffer2[x, y] = 0;
                }
            }
        }

        private void CreateWaterDrop()
        {
            int x, y;

            if (RandomDrop)
            {
                // Random placement
                int maxDimension = Math.Max(_bufferWidth, _bufferHeight);
                x = _random.Next(_bufferWidth);
                y = _random.Next(_bufferHeight);
                CreateSineBlob(x, y, DropRadius * maxDimension / 100, -Depth, _currentBuffer);
            }
            else
            {
                // Fixed position based on settings
                switch (DropPositionX)
                {
                    case 0: x = _bufferWidth / 4; break;
                    case 1: x = _bufferWidth / 2; break;
                    case 2: x = _bufferWidth * 3 / 4; break;
                    default: x = _bufferWidth / 2; break;
                }

                switch (DropPositionY)
                {
                    case 0: y = _bufferHeight / 4; break;
                    case 1: y = _bufferHeight / 2; break;
                    case 2: y = _bufferHeight * 3 / 4; break;
                    default: y = _bufferHeight / 2; break;
                }

                CreateSineBlob(x, y, DropRadius, -Depth, _currentBuffer);
            }
        }

        private void CreateSineBlob(int centerX, int centerY, int radius, int height, int bufferIndex)
        {
            var buffer = bufferIndex == 0 ? _heightBuffer1 : _heightBuffer2;

            // Ensure coordinates are within bounds
            if (centerX < 0) centerX = 1 + radius + _random.Next(_bufferWidth - 2 * radius - 1);
            if (centerY < 0) centerY = 1 + radius + _random.Next(_bufferHeight - 2 * radius - 1);

            int radiusSquared = radius * radius;
            double length = (1024.0 / radius) * (1024.0 / radius);

            // Calculate bounds with edge clipping
            int left = Math.Max(-radius, 1 - (centerX - radius));
            int right = Math.Min(radius, _bufferWidth - 1 - (centerX + radius));
            int top = Math.Max(-radius, 1 - (centerY - radius));
            int bottom = Math.Min(radius, _bufferHeight - 1 - (centerY + radius));

            for (int cy = top; cy < bottom; cy++)
            {
                for (int cx = left; cx < right; cx++)
                {
                    int square = cy * cy + cx * cx;
                    if (square < radiusSquared)
                    {
                        double distance = Math.Sqrt(square * length);
                        int bufferX = centerX + cx;
                        int bufferY = centerY + cy;

                        if (bufferX >= 0 && bufferX < _bufferWidth && bufferY >= 0 && bufferY < _bufferHeight)
                        {
                            int heightValue = (int)((Math.Cos(distance) + 1.0) * height) >> 19;
                            buffer[bufferX, bufferY] += heightValue;
                        }
                    }
                }
            }
        }

        private void CreateHeightBlob(int centerX, int centerY, int radius, int height, int bufferIndex)
        {
            var buffer = bufferIndex == 0 ? _heightBuffer1 : _heightBuffer2;

            // Ensure coordinates are within bounds
            if (centerX < 0) centerX = 1 + radius + _random.Next(_bufferWidth - 2 * radius - 1);
            if (centerY < 0) centerY = 1 + radius + _random.Next(_bufferHeight - 2 * radius - 1);

            int radiusSquared = radius * radius;

            // Calculate bounds with edge clipping
            int left = Math.Max(-radius, 1 - (centerX - radius));
            int right = Math.Min(radius, _bufferWidth - 1 - (centerX + radius));
            int top = Math.Max(-radius, 1 - (centerY - radius));
            int bottom = Math.Min(radius, _bufferHeight - 1 - (centerY + radius));

            for (int cy = top; cy < bottom; cy++)
            {
                int cySquared = cy * cy;
                for (int cx = left; cx < right; cx++)
                {
                    if (cx * cx + cySquared < radiusSquared)
                    {
                        int bufferX = centerX + cx;
                        int bufferY = centerY + cy;

                        if (bufferX >= 0 && bufferX < _bufferWidth && bufferY >= 0 && bufferY < _bufferHeight)
                        {
                            buffer[bufferX, bufferY] += height;
                        }
                    }
                }
            }
        }

        private void ApplyWaterDisplacement(ImageBuffer imageBuffer)
        {
            var currentBuffer = _currentBuffer == 0 ? _heightBuffer1 : _heightBuffer2;
            var outputBuffer = new Color[imageBuffer.Width, imageBuffer.Height];

            for (int y = 0; y < imageBuffer.Height; y++)
            {
                for (int x = 0; x < imageBuffer.Width; x++)
                {
                    // Calculate displacement from height differences
                    int dx = 0, dy = 0;

                    if (x < _bufferWidth - 1)
                        dx = currentBuffer[x, y] - currentBuffer[x + 1, y];
                    if (y < _bufferHeight - 1)
                        dy = currentBuffer[x, y] - currentBuffer[x, y + 1];

                    // Apply displacement with scaling
                    int offsetX = x + (dx >> 3);
                    int offsetY = y + (dy >> 3);

                    // Clamp coordinates to image bounds
                    offsetX = Math.Max(0, Math.Min(imageBuffer.Width - 1, offsetX));
                    offsetY = Math.Max(0, Math.Min(imageBuffer.Height - 1, offsetY));

                    // Sample color from displaced position
                    Color sourceColor = imageBuffer.GetPixel(offsetX, offsetY);
                    outputBuffer[x, y] = sourceColor;
                }
            }

            // Update image buffer with water displacement
            for (int y = 0; y < imageBuffer.Height; y++)
            {
                for (int x = 0; x < imageBuffer.Width; x++)
                {
                    imageBuffer.SetPixel(x, y, outputBuffer[x, y]);
                }
            }
        }

        private void CalculateWaterPhysics()
        {
            var currentBuffer = _currentBuffer == 0 ? _heightBuffer1 : _heightBuffer2;
            var nextBuffer = _currentBuffer == 0 ? _heightBuffer2 : _heightBuffer1;

            if (Method == 0)
            {
                CalculateStandardWater(nextBuffer, currentBuffer);
            }
            else
            {
                CalculateSludgeWater(nextBuffer, currentBuffer);
            }
        }

        private void CalculateStandardWater(int[,] newBuffer, int[,] oldBuffer)
        {
            for (int y = 1; y < _bufferHeight - 1; y++)
            {
                for (int x = 1; x < _bufferWidth - 1; x++)
                {
                    // Eight-pixel method for smooth water physics
                    int newHeight = ((oldBuffer[x, y + 1] +      // Below
                                   oldBuffer[x, y - 1] +      // Above
                                   oldBuffer[x + 1, y] +      // Right
                                   oldBuffer[x - 1, y] +      // Left
                                   oldBuffer[x - 1, y - 1] +  // Top-left
                                   oldBuffer[x + 1, y - 1] +  // Top-right
                                   oldBuffer[x - 1, y + 1] +  // Bottom-left
                                   oldBuffer[x + 1, y + 1])   // Bottom-right
                                   >> 2) - newBuffer[x, y];

                    newBuffer[x, y] = newHeight - (newHeight >> Density);
                }
            }
        }

        private void CalculateSludgeWater(int[,] newBuffer, int[,] oldBuffer)
        {
            for (int y = 1; y < _bufferHeight - 1; y++)
            {
                for (int x = 1; x < _bufferWidth - 1; x++)
                {
                    // Sludge method for different water behavior
                    int newHeight = (oldBuffer[x, y] << 2) +
                                   oldBuffer[x - 1, y - 1] +
                                   oldBuffer[x + 1, y - 1] +
                                   oldBuffer[x - 1, y + 1] +
                                   oldBuffer[x + 1, y + 1] +
                                   ((oldBuffer[x - 1, y] +
                                     oldBuffer[x + 1, y] +
                                     oldBuffer[x, y - 1] +
                                     oldBuffer[x, y + 1]) << 1);

                    newBuffer[x, y] = (newHeight - (newHeight >> 6)) >> Density;
                }
            }
        }

        #endregion

        #region Configuration

        public override bool ValidateConfiguration()
        {
            // Validate property ranges
            Density = Math.Max(2, Math.Min(10, Density));
            Depth = Math.Max(100, Math.Min(2000, Depth));
            DropRadius = Math.Max(10, Math.Min(100, DropRadius));
            DropPositionX = Math.Max(0, Math.Min(2, DropPositionX));
            DropPositionY = Math.Max(0, Math.Min(2, DropPositionY));
            Method = Math.Max(0, Math.Min(1, Method));

            return true;
        }

        public override string GetSettingsSummary()
        {
            string positionX = DropPositionX == 0 ? "Left" : DropPositionX == 1 ? "Center" : "Right";
            string positionY = DropPositionY == 0 ? "Top" : DropPositionY == 1 ? "Middle" : "Bottom";
            string method = Method == 0 ? "Standard" : "Sludge";

            return $"Water Bump Effect - Enabled: {Enabled}, Density: {Density}, " +
                   $"Depth: {Depth}, Radius: {DropRadius}, Method: {method}, " +
                   $"Position: {positionX}/{positionY}, Random: {RandomDrop}";
        }

        #endregion
    }
}
```

## Effect Behavior

The Water Bump effect creates advanced fluid simulation by:

1. **Height Buffer Management**: Maintains dual height buffers for smooth physics calculations
2. **Sine Blob Generation**: Creates organic wave sources using sine-based height mapping
3. **Fluid Physics**: Applies realistic water surface tension and wave propagation
4. **Beat Response**: Generates water drops on audio beats for dynamic interaction
5. **Displacement Mapping**: Uses height differences to create pixel displacement
6. **Dual Calculation Methods**: Supports both standard and sludge water physics

## Key Features

- **Height-Based Simulation**: Realistic fluid dynamics using height buffers
- **Multiple Wave Sources**: Configurable drop positions and random placement
- **Advanced Physics**: Eight-pixel sampling for smooth wave propagation
- **Beat Synchronization**: Audio-responsive water drop generation
- **Configurable Parameters**: Adjustable density, depth, radius, and calculation method
- **Edge Clipping**: Proper boundary handling for seamless edge effects

## Use Cases

- **Advanced Music Visualization**: Sophisticated water effects that respond to audio
- **Fluid Simulation**: Realistic water surface dynamics and wave propagation
- **Interactive Environments**: Dynamic water surfaces that react to user input
- **Cinematic Effects**: Professional-grade water displacement for visual effects
- **Gaming Applications**: Real-time fluid simulation for interactive experiences
