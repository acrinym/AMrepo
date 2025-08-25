using System;
using System.Collections.Generic;
using PhoenixVisualizer.Core.Effects.Models;
using PhoenixVisualizer.Core.Models;

namespace PhoenixVisualizer.Core.Effects.Nodes.AvsEffects
{
    public class NoiseEffectsNode : BaseEffectNode
    {
        public int NoiseType { get; set; } = 0; // 0=Random, 1=Perlin, 2=Simplex
        public float NoiseIntensity { get; set; } = 0.5f;
        public float NoiseScale { get; set; } = 1.0f;
        public bool BeatReactive { get; set; } = false;
        public float BeatNoiseIntensity { get; set; } = 2.0f;
        public int Seed { get; set; } = 42;
        private readonly Random random;

        public NoiseEffectsNode()
        {
            Name = "Noise Effects";
            Description = "Generates various types of noise patterns";
            Category = "AVS Effects";
            random = new Random(Seed);
        }

        protected override void InitializePorts()
        {
            _inputPorts.Add(new EffectPort("Image", typeof(ImageBuffer), true, null, "Input image for noise overlay"));
            _outputPorts.Add(new EffectPort("Output", typeof(ImageBuffer), false, null, "Noise output image"));
        }

        protected override object ProcessCore(Dictionary<string, object> inputs, AudioFeatures audioFeatures)
        {
            if (!inputs.TryGetValue("Image", out var input) || input is not ImageBuffer imageBuffer)
                return GetDefaultOutput();

            var output = new ImageBuffer(imageBuffer.Width, imageBuffer.Height);
            float currentIntensity = NoiseIntensity;
            
            if (BeatReactive && audioFeatures?.IsBeat == true)
            {
                currentIntensity *= BeatNoiseIntensity;
            }

            switch (NoiseType)
            {
                case 0:
                    GenerateRandomNoise(output, currentIntensity);
                    break;
                case 1:
                    GeneratePerlinNoise(output, currentIntensity);
                    break;
                case 2:
                    GenerateSimplexNoise(output, currentIntensity);
                    break;
            }

            return output;
        }

        private void GenerateRandomNoise(ImageBuffer output, float intensity)
        {
            for (int y = 0; y < output.Height; y++)
            {
                for (int x = 0; x < output.Width; x++)
                {
                    float noise = (float)random.NextDouble();
                    int noiseValue = (int)(noise * intensity * 255);
                    int pixel = output.GetPixel(x, y);
                    
                    int r = Math.Clamp((pixel & 0xFF) + noiseValue, 0, 255);
                    int g = Math.Clamp(((pixel >> 8) & 0xFF) + noiseValue, 0, 255);
                    int b = Math.Clamp(((pixel >> 16) & 0xFF) + noiseValue, 0, 255);
                    
                    output.SetPixel(x, y, r | (g << 8) | (b << 16));
                }
            }
        }

        private void GeneratePerlinNoise(ImageBuffer output, float intensity)
        {
            for (int y = 0; y < output.Height; y++)
            {
                for (int x = 0; x < output.Width; x++)
                {
                    float noise = PerlinNoise(x * NoiseScale * 0.01f, y * NoiseScale * 0.01f);
                    int noiseValue = (int)(noise * intensity * 255);
                    int pixel = output.GetPixel(x, y);
                    
                    int r = Math.Clamp((pixel & 0xFF) + noiseValue, 0, 255);
                    int g = Math.Clamp(((pixel >> 8) & 0xFF) + noiseValue, 0, 255);
                    int b = Math.Clamp(((pixel >> 16) & 0xFF) + noiseValue, 0, 255);
                    
                    output.SetPixel(x, y, r | (g << 8) | (b << 16));
                }
            }
        }

        private void GenerateSimplexNoise(ImageBuffer output, float intensity)
        {
            for (int y = 0; y < output.Height; y++)
            {
                for (int x = 0; x < output.Width; x++)
                {
                    float noise = SimplexNoise(x * NoiseScale * 0.01f, y * NoiseScale * 0.01f);
                    int noiseValue = (int)(noise * intensity * 255);
                    int pixel = output.GetPixel(x, y);
                    
                    int r = Math.Clamp((pixel & 0xFF) + noiseValue, 0, 255);
                    int g = Math.Clamp(((pixel >> 8) & 0xFF) + noiseValue, 0, 255);
                    int b = Math.Clamp(((pixel >> 16) & 0xFF) + noiseValue, 0, 255);
                    
                    output.SetPixel(x, y, r | (g << 8) | (b << 16));
                }
            }
        }

        private float PerlinNoise(float x, float y)
        {
            // Simplified Perlin noise implementation
            int xi = (int)Math.Floor(x) & 255;
            int yi = (int)Math.Floor(y) & 255;
            float xf = x - (float)Math.Floor(x);
            float yf = y - (float)Math.Floor(y);
            
            float u = Fade(xf);
            float v = Fade(yf);
            
            float a = Grad(xi, yi, xf, yf);
            float b = Grad(xi + 1, yi, xf - 1, yf);
            float c = Grad(xi, yi + 1, xf, yf - 1);
            float d = Grad(xi + 1, yi + 1, xf - 1, yf - 1);
            
            float x1 = Lerp(a, b, u);
            float x2 = Lerp(c, d, u);
            
            return Lerp(x1, x2, v);
        }

        private float SimplexNoise(float x, float y)
        {
            // Simplified Simplex noise implementation
            float n0, n1, n2;
            float F2 = 0.5f * (Math.Sqrt(3.0f) - 1.0f);
            float G2 = (3.0f - Math.Sqrt(3.0f)) / 6.0f;
            
            float s = (x + y) * F2;
            int i = (int)Math.Floor(x + s);
            int j = (int)Math.Floor(y + s);
            
            float t = (i + j) * G2;
            float X0 = i - t;
            float Y0 = j - t;
            float x0 = x - X0;
            float y0 = y - Y0;
            
            return (float)random.NextDouble() * 2.0f - 1.0f;
        }

        private float Fade(float t)
        {
            return t * t * t * (t * (t * 6.0f - 15.0f) + 10.0f);
        }

        private float Lerp(float a, float b, float t)
        {
            return a + t * (b - a);
        }

        private float Grad(int hash, float x, float y)
        {
            int h = hash & 15;
            float u = h < 8 ? x : y;
            float v = h < 4 ? y : h == 12 || h == 14 ? x : 0;
            return ((h & 1) == 0 ? u : -u) + ((h & 2) == 0 ? v : -v);
        }

        protected override object GetDefaultOutput()
        {
            return new ImageBuffer(1, 1);
        }
    }
}
