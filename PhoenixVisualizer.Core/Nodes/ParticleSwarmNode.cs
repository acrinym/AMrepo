using System;
using System.Collections.Generic;
using System.Numerics;

namespace PhoenixVisualizer.Core.Nodes;

public class ParticleSwarmNode : IEffectNode
{
    public string Name => "Particle Swarm";
    public Dictionary<string, EffectParam> Params { get; } = new()
    {
        ["count"] = new EffectParam{ Label="Particle Count", Type="slider", Min=100, Max=2000, FloatValue=300 },
        ["speed"] = new EffectParam{ Label="Speed", Type="slider", Min=0.1f, Max=3f, FloatValue=1f },
        ["color"] = new EffectParam{ Label="Color", Type="color", ColorValue="#00FFCC" },
        ["size"] = new EffectParam{ Label="Particle Size", Type="slider", Min=1f, Max=5f, FloatValue=2f },
        ["fftReactivity"] = new EffectParam{ Label="FFT Reactivity", Type="slider", Min=0, Max=2f, FloatValue=1f }
    };

    private float _time = 0f;
    private List<Particle> _particles = new();
    private bool _initialized = false;

    public void Render(float[] waveform, float[] spectrum, RenderContext ctx)
    {
        if (ctx.Canvas == null) return;

        _time += 0.016f * Params["speed"].FloatValue;

        // Initialize particles if needed
        if (!_initialized)
        {
            InitializeParticles(ctx);
            _initialized = true;
        }

        // Clear canvas
        ctx.Canvas.Clear(0xFF000000);

        // Get parameters
        float particleSize = Params["size"].FloatValue;
        float fftReactivity = Params["fftReactivity"].FloatValue;
        uint baseColor = ParseColor(Params["color"].ColorValue);

        // Update and render particles
        UpdateParticles(ctx, waveform, spectrum, fftReactivity);
        RenderParticles(ctx, baseColor, particleSize);
    }

    private void InitializeParticles(RenderContext ctx)
    {
        int count = (int)Params["count"].FloatValue;
        _particles.Clear();

        for (int i = 0; i < count; i++)
        {
            _particles.Add(new Particle
            {
                X = Random.Shared.NextSingle() * ctx.Width,
                Y = Random.Shared.NextSingle() * ctx.Height,
                VX = (Random.Shared.NextSingle() - 0.5f) * 2f,
                VY = (Random.Shared.NextSingle() - 0.5f) * 2f,
                Life = Random.Shared.NextSingle(),
                Size = Random.Shared.NextSingle() * 2f + 1f
            });
        }
    }

    private void UpdateParticles(RenderContext ctx, float[] waveform, float[] spectrum, float fftReactivity)
    {
        float centerX = ctx.Width / 2f;
        float centerY = ctx.Height / 2f;

        // Calculate audio energy
        float audioEnergy = 0f;
        if (spectrum.Length > 0)
        {
            for (int i = 0; i < Math.Min(spectrum.Length, 50); i++)
            {
                audioEnergy += spectrum[i];
            }
            audioEnergy /= Math.Min(spectrum.Length, 50);
        }

        foreach (var particle in _particles)
        {
            // Apply center attraction
            float dx = centerX - particle.X;
            float dy = centerY - particle.Y;
            float distance = MathF.Sqrt(dx * dx + dy * dy);
            if (distance > 0)
            {
                particle.VX += (dx / distance) * 0.1f;
                particle.VY += (dy / distance) * 0.1f;
            }

            // Apply audio-driven forces
            if (audioEnergy > 0.1f)
            {
                particle.VX += (Random.Shared.NextSingle() - 0.5f) * audioEnergy * fftReactivity;
                particle.VY += (Random.Shared.NextSingle() - 0.5f) * audioEnergy * fftReactivity;
            }

            // Apply damping
            particle.VX *= 0.98f;
            particle.VY *= 0.98f;

            // Limit velocity
            float maxVel = 3f;
            particle.VX = Math.Max(-maxVel, Math.Min(maxVel, particle.VX));
            particle.VY = Math.Max(-maxVel, Math.Min(maxVel, particle.VY));

            // Update position
            particle.X += particle.VX;
            particle.Y += particle.VY;

            // Wrap around screen edges
            if (particle.X < 0) particle.X = ctx.Width;
            if (particle.X > ctx.Width) particle.X = 0;
            if (particle.Y < 0) particle.Y = ctx.Height;
            if (particle.Y > ctx.Height) particle.Y = 0;

            // Update life cycle
            particle.Life += 0.01f;
            if (particle.Life > 1f) particle.Life = 0f;
        }
    }

    private void RenderParticles(RenderContext ctx, uint baseColor, float particleSize)
    {
        foreach (var particle in _particles)
        {
            // Calculate particle color based on life
            uint particleColor = CalculateParticleColor(baseColor, particle.Life);
            float size = particle.Size * particleSize;
            
            // Draw particle
            ctx.Canvas!.FillCircle(particle.X, particle.Y, size, particleColor);
            
            // Add glow effect
            uint glowColor = ApplyAlpha(particleColor, 0.3f);
            ctx.Canvas.DrawCircle(particle.X, particle.Y, size * 2f, glowColor, false);
        }
    }

    private uint CalculateParticleColor(uint baseColor, float life)
    {
        // Create color variation based on particle life
        byte r = (byte)(baseColor >> 16);
        byte g = (byte)(baseColor >> 8);
        byte b = (byte)baseColor;

        // Add life-based variation
        float lifeFactor = 0.5f + 0.5f * MathF.Sin(life * MathF.PI * 2f);
        r = (byte)(r * (0.7f + lifeFactor * 0.3f));
        g = (byte)(g * (0.7f + lifeFactor * 0.3f));
        b = (byte)(b * (0.7f + lifeFactor * 0.3f));

        return (uint)((255 << 24) | (r << 16) | (g << 8) | b);
    }

    private uint ApplyAlpha(uint color, float alpha)
    {
        byte r = (byte)(color >> 16);
        byte g = (byte)(color >> 8);
        byte b = (byte)color;
        byte a = (byte)(alpha * 255);
        
        return (uint)((a << 24) | (r << 16) | (g << 8) | b);
    }

    private uint ParseColor(string colorString)
    {
        // Simple hex color parser
        if (colorString.StartsWith("#") && colorString.Length == 7)
        {
            string hex = colorString.Substring(1);
            if (uint.TryParse(hex, System.Globalization.NumberStyles.HexNumber, null, out uint color))
            {
                return 0xFF000000 | color; // Add full alpha
            }
        }
        return 0xFF00FFCC; // Default cyan
    }

    private class Particle
    {
        public float X { get; set; }
        public float Y { get; set; }
        public float VX { get; set; }
        public float VY { get; set; }
        public float Life { get; set; }
        public float Size { get; set; }
    }
}
