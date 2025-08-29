using System;
using System.Collections.Generic;

namespace PhoenixVisualizer.Core.Nodes;

/// <summary>
/// Particle Swarm effect node - Creates dynamic particle systems driven by audio frequencies
/// Particles respond to FFT bins with position, size, and color mapping
/// </summary>
public class ParticleSwarmNode : IEffectNode
{
    // Particle data structure
    private class Particle
    {
        public float X, Y;
        public float VX, VY;
        public float Size;
        public float Life;
        public uint Color;
        public int FreqBin; // Which frequency bin this particle responds to
    }

    private readonly List<Particle> _particles = new();
    private readonly Random _random = new();

    public string Name => "Particle Swarm";
    public Dictionary<string, EffectParam> Params { get; } = new()
    {
        ["count"] = new EffectParam {
            Label = "Particle Count",
            Type = "slider",
            Min = 50,
            Max = 1000,
            FloatValue = 200
        },
        ["speed"] = new EffectParam {
            Label = "Movement Speed",
            Type = "slider",
            Min = 0.1f,
            Max = 5f,
            FloatValue = 1f
        },
        ["sizeMin"] = new EffectParam {
            Label = "Min Size",
            Type = "slider",
            Min = 1,
            Max = 10,
            FloatValue = 2f
        },
        ["sizeMax"] = new EffectParam {
            Label = "Max Size",
            Type = "slider",
            Min = 5,
            Max = 20,
            FloatValue = 8f
        },
        ["colorMode"] = new EffectParam {
            Label = "Color Mode",
            Type = "dropdown",
            StringValue = "spectrum",
            Options = new() { "spectrum", "rainbow", "mono", "energy" }
        },
        ["baseColor"] = new EffectParam {
            Label = "Base Color",
            Type = "color",
            ColorValue = "#00FFCC"
        },
        ["trail"] = new EffectParam {
            Label = "Trail Effect",
            Type = "checkbox",
            BoolValue = true
        },
        ["attraction"] = new EffectParam {
            Label = "Center Attraction",
            Type = "slider",
            Min = 0,
            Max = 1,
            FloatValue = 0.3f
        }
    };

    public void Render(float[] waveform, float[] spectrum, RenderContext ctx)
    {
        UpdateParticles(spectrum, ctx);
        RenderParticles(ctx);
    }

    private void UpdateParticles(float[] spectrum, RenderContext ctx)
    {
        int targetCount = (int)Params["count"].FloatValue;
        float speed = Params["speed"].FloatValue;
        float sizeMin = Params["sizeMin"].FloatValue;
        float sizeMax = Params["sizeMax"].FloatValue;
        string colorMode = Params["colorMode"].StringValue;
        string baseColorHex = Params["baseColor"].ColorValue;
        float attraction = Params["attraction"].FloatValue;

        uint baseColor = ParseHexColor(baseColorHex);
        float centerX = ctx.Width * 0.5f;
        float centerY = ctx.Height * 0.5f;

        // Maintain target particle count
        while (_particles.Count < targetCount)
        {
            var particle = new Particle
            {
                X = (float)_random.NextDouble() * ctx.Width,
                Y = (float)_random.NextDouble() * ctx.Height,
                VX = ((float)_random.NextDouble() - 0.5f) * speed * 2,
                VY = ((float)_random.NextDouble() - 0.5f) * speed * 2,
                Size = sizeMin + (float)_random.NextDouble() * (sizeMax - sizeMin),
                Life = 1f,
                FreqBin = _random.Next(Math.Max(1, spectrum.Length))
            };
            _particles.Add(particle);
        }

        while (_particles.Count > targetCount)
        {
            _particles.RemoveAt(_particles.Count - 1);
        }

        // Update existing particles
        for (int i = _particles.Count - 1; i >= 0; i--)
        {
            var particle = _particles[i];

            // Get frequency bin energy
            float energy = 0;
            if (particle.FreqBin < spectrum.Length)
            {
                energy = spectrum[particle.FreqBin];
            }

            // Apply frequency-based forces
            float force = energy * 2f;
            particle.VX += (float)(_random.NextDouble() - 0.5) * force;
            particle.VY += (float)(_random.NextDouble() - 0.5) * force;

            // Apply center attraction
            float dx = centerX - particle.X;
            float dy = centerY - particle.Y;
            float distance = (float)Math.Sqrt(dx * dx + dy * dy);
            if (distance > 0)
            {
                particle.VX += (dx / distance) * attraction * speed * 0.1f;
                particle.VY += (dy / distance) * attraction * speed * 0.1f;
            }

            // Apply damping
            particle.VX *= 0.98f;
            particle.VY *= 0.98f;

            // Limit velocity
            float maxVel = speed * 3f;
            particle.VX = Math.Clamp(particle.VX, -maxVel, maxVel);
            particle.VY = Math.Clamp(particle.VY, -maxVel, maxVel);

            // Update position
            particle.X += particle.VX;
            particle.Y += particle.VY;

            // Wrap around screen edges
            if (particle.X < 0) particle.X = ctx.Width;
            if (particle.X > ctx.Width) particle.X = 0;
            if (particle.Y < 0) particle.Y = ctx.Height;
            if (particle.Y > ctx.Height) particle.Y = 0;

            // Update size based on energy
            particle.Size = sizeMin + energy * (sizeMax - sizeMin);

            // Update color
            particle.Color = CalculateParticleColor(particle, energy, colorMode, baseColor, spectrum);

            // Update life (particles fade over time)
            particle.Life -= 0.005f;
            if (particle.Life <= 0)
            {
                // Respawn particle
                particle.X = (float)_random.NextDouble() * ctx.Width;
                particle.Y = (float)_random.NextDouble() * ctx.Height;
                particle.VX = ((float)_random.NextDouble() - 0.5f) * speed * 2;
                particle.VY = ((float)_random.NextDouble() - 0.5f) * speed * 2;
                particle.Life = 1f;
                particle.FreqBin = _random.Next(Math.Max(1, spectrum.Length));
            }
        }
    }

    private void RenderParticles(RenderContext ctx)
    {
        bool trail = Params["trail"].BoolValue;

        foreach (var particle in _particles)
        {
            // Draw particle
            // TODO: Replace with SkiaSharp drawing
            // ctx.Canvas.FillCircle(particle.X, particle.Y, particle.Size, particle.Color);

            if (trail)
            {
                // Draw trail
                float trailX = particle.X - particle.VX * 3;
                float trailY = particle.Y - particle.VY * 3;
                uint trailColor = (particle.Color & 0x00FFFFFF) | 0x40u << 24;

                // TODO: Draw trail line
                // ctx.Canvas.DrawLine(particle.X, particle.Y, trailX, trailY, trailColor, particle.Size * 0.3f);
            }
        }
    }

    private uint CalculateParticleColor(Particle particle, float energy, string colorMode, uint baseColor, float[] spectrum)
    {
        switch (colorMode)
        {
            case "spectrum":
                // Map frequency bin to color
                if (spectrum.Length > 0)
                {
                    float freqRatio = particle.FreqBin / (float)spectrum.Length;
                    return SpectrumToColor(freqRatio, energy);
                }
                return baseColor;

            case "rainbow":
                // Rainbow based on frequency
                float hue = particle.FreqBin / 32f; // Assuming typical 32-bin spectrum
                return HsvToRgb(hue, 0.8f, 0.6f + energy * 0.4f);

            case "mono":
                // Monochrome with intensity based on energy
                float intensity = 0.3f + energy * 0.7f;
                byte gray = (byte)(intensity * 255);
                return 0xFF000000 | ((uint)gray << 16) | ((uint)gray << 8) | gray;

            case "energy":
                // Energy-based color intensity
                float r = energy * 255;
                float g = (1f - energy) * 255;
                float b = energy * energy * 255;
                return 0xFF000000 | ((uint)r << 16) | ((uint)g << 8) | (uint)b;

            default:
                return baseColor;
        }
    }

    private uint SpectrumToColor(float freqRatio, float intensity)
    {
        // Map frequency ratio to visible spectrum colors
        float hue = freqRatio * 0.8f; // 0-0.8 for visible spectrum
        return HsvToRgb(hue, 1f, 0.4f + intensity * 0.6f);
    }

    private uint HsvToRgb(float hue, float saturation, float brightness)
    {
        float c = brightness * saturation;
        float x = c * (1 - Math.Abs((hue * 6) % 2 - 1));
        float m = brightness - c;

        float r, g, b;
        if (hue < 1f/6f)
        {
            r = c; g = x; b = 0;
        }
        else if (hue < 2f/6f)
        {
            r = x; g = c; b = 0;
        }
        else if (hue < 3f/6f)
        {
            r = 0; g = c; b = x;
        }
        else if (hue < 4f/6f)
        {
            r = 0; g = x; b = c;
        }
        else if (hue < 5f/6f)
        {
            r = x; g = 0; b = c;
        }
        else
        {
            r = c; g = 0; b = x;
        }

        byte red = (byte)((r + m) * 255);
        byte green = (byte)((g + m) * 255);
        byte blue = (byte)((b + m) * 255);

        return 0xFF000000 | ((uint)red << 16) | ((uint)green << 8) | blue;
    }

    private uint ParseHexColor(string hexColor)
    {
        if (string.IsNullOrEmpty(hexColor) || !hexColor.StartsWith("#"))
            return 0xFFFFFFFF;

        try
        {
            string hex = hexColor.Substring(1);
            if (hex.Length == 6)
            {
                uint r = Convert.ToUInt32(hex.Substring(0, 2), 16);
                uint g = Convert.ToUInt32(hex.Substring(2, 2), 16);
                uint b = Convert.ToUInt32(hex.Substring(4, 2), 16);
                return 0xFF000000 | (r << 16) | (g << 8) | b;
            }
        }
        catch
        {
            // Fall back to white on parsing error
        }

        return 0xFFFFFFFF;
    }
}
