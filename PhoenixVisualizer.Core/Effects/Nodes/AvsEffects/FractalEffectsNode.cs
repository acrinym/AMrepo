using System;
using System.Collections.Generic;
using PhoenixVisualizer.Core.Effects.Models;
using PhoenixVisualizer.Core.Models;

namespace PhoenixVisualizer.Core.Effects.Nodes.AvsEffects
{
    public class FractalEffectsNode : BaseEffectNode
    {
        public int FractalType { get; set; } = 0; // 0=Mandelbrot, 1=Julia, 2=Sierpinski
        public int MaxIterations { get; set; } = 100;
        public float Zoom { get; set; } = 1.0f;
        public float CenterX { get; set; } = 0.0f;
        public float CenterY { get; set; } = 0.0f;
        public bool BeatReactive { get; set; } = false;
        public float BeatZoom { get; set; } = 1.5f;

        public FractalEffectsNode()
        {
            Name = "Fractal Effects";
            Description = "Generates mathematical fractals with real-time parameters";
            Category = "AVS Effects";
        }

        protected override void InitializePorts()
        {
            _inputPorts.Add(new EffectPort("Image", typeof(ImageBuffer), true, null, "Input image for fractal overlay"));
            _outputPorts.Add(new EffectPort("Output", typeof(ImageBuffer), false, null, "Fractal output image"));
        }

        protected override object ProcessCore(Dictionary<string, object> inputs, AudioFeatures audioFeatures)
        {
            if (!inputs.TryGetValue("Image", out var input) || input is not ImageBuffer imageBuffer)
                return GetDefaultOutput();

            var output = new ImageBuffer(imageBuffer.Width, imageBuffer.Height);
            float currentZoom = Zoom;
            
            if (BeatReactive && audioFeatures?.IsBeat == true)
            {
                currentZoom *= BeatZoom;
            }

            switch (FractalType)
            {
                case 0:
                    GenerateMandelbrot(output, currentZoom);
                    break;
                case 1:
                    GenerateJulia(output, currentZoom);
                    break;
                case 2:
                    GenerateSierpinski(output, currentZoom);
                    break;
            }

            return output;
        }

        private void GenerateMandelbrot(ImageBuffer output, float zoom)
        {
            float scale = 4.0f / (output.Width * zoom);
            float offsetX = CenterX - (output.Width * scale) / 2;
            float offsetY = CenterY - (output.Height * scale) / 2;

            for (int y = 0; y < output.Height; y++)
            {
                for (int x = 0; x < output.Width; x++)
                {
                    float real = x * scale + offsetX;
                    float imag = y * scale + offsetY;
                    int iterations = CalculateMandelbrot(real, imag);
                    int color = GetFractalColor(iterations, MaxIterations);
                    output.SetPixel(x, y, color);
                }
            }
        }

        private void GenerateJulia(ImageBuffer output, float zoom)
        {
            float scale = 4.0f / (output.Width * zoom);
            float offsetX = CenterX - (output.Width * scale) / 2;
            float offsetY = CenterY - (output.Height * scale) / 2;
            float cReal = -0.7f;
            float cImag = 0.27f;

            for (int y = 0; y < output.Height; y++)
            {
                for (int x = 0; x < output.Width; x++)
                {
                    float real = x * scale + offsetX;
                    float imag = y * scale + offsetY;
                    int iterations = CalculateJulia(real, imag, cReal, cImag);
                    int color = GetFractalColor(iterations, MaxIterations);
                    output.SetPixel(x, y, color);
                }
            }
        }

        private void GenerateSierpinski(ImageBuffer output, float zoom)
        {
            int size = (int)(Math.Min(output.Width, output.Height) / zoom);
            int offsetX = (output.Width - size) / 2;
            int offsetY = (output.Height - size) / 2;

            for (int y = 0; y < size; y++)
            {
                for (int x = 0; x < size; x++)
                {
                    if (IsSierpinskiPoint(x, y))
                    {
                        output.SetPixel(offsetX + x, offsetY + y, 0xFFFFFF);
                    }
                }
            }
        }

        private int CalculateMandelbrot(float real, float imag)
        {
            float zReal = 0;
            float zImag = 0;
            int iterations = 0;

            while (zReal * zReal + zImag * zImag < 4.0f && iterations < MaxIterations)
            {
                float temp = zReal * zReal - zImag * zImag + real;
                zImag = 2.0f * zReal * zImag + imag;
                zReal = temp;
                iterations++;
            }

            return iterations;
        }

        private int CalculateJulia(float real, float imag, float cReal, float cImag)
        {
            float zReal = real;
            float zImag = imag;
            int iterations = 0;

            while (zReal * zReal + zImag * zImag < 4.0f && iterations < MaxIterations)
            {
                float temp = zReal * zReal - zImag * zImag + cReal;
                zImag = 2.0f * zReal * zImag + cImag;
                zReal = temp;
                iterations++;
            }

            return iterations;
        }

        private bool IsSierpinskiPoint(int x, int y)
        {
            while (x > 0 || y > 0)
            {
                if (x % 2 == 1 && y % 2 == 1)
                    return false;
                x /= 2;
                y /= 2;
            }
            return true;
        }

        private int GetFractalColor(int iterations, int maxIterations)
        {
            if (iterations >= maxIterations)
                return 0;

            float normalized = (float)iterations / maxIterations;
            int intensity = (int)(normalized * 255);
            return intensity | (intensity << 8) | (intensity << 16);
        }

        protected override object GetDefaultOutput()
        {
            return new ImageBuffer(1, 1);
        }
    }
}
