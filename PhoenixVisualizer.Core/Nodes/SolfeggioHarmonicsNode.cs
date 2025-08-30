using System;
using System.Collections.Generic;
using System.Numerics;

namespace PhoenixVisualizer.Core.Nodes;

/// <summary>
/// Solfeggio Harmonics Node - Specialized visualizer for sacred frequencies
/// Implements the exact mathematical relationships from Earth harmonics research
/// </summary>
public class SolfeggioHarmonicsNode : IEffectNode
{
    // Solfeggio frequencies with exact Hz values from research
    private static readonly Dictionary<string, SolfeggioTone> SolfeggioTones = new()
    {
        ["UT"] = new SolfeggioTone { Name = "UT", Hz = 396f, Note = "G#", Meaning = "Liberation from guilt and fear", Helek = 118.8f },
        ["RE"] = new SolfeggioTone { Name = "RE", Hz = 417f, Note = "G#", Meaning = "Undoing situations and facilitating change", Helek = 125.1f },
        ["MI"] = new SolfeggioTone { Name = "MI", Hz = 528f, Note = "C", Meaning = "Transformation and miracles", Helek = 158.4f },
        ["FA"] = new SolfeggioTone { Name = "FA", Hz = 639f, Note = "D#", Meaning = "Connecting relationships", Helek = 191.7f },
        ["SOL"] = new SolfeggioTone { Name = "SOL", Hz = 741f, Note = "F#", Meaning = "Awakening intuition", Helek = 222.3f },
        ["LA"] = new SolfeggioTone { Name = "LA", Hz = 852f, Note = "G#", Meaning = "Spiritual order", Helek = 255.6f }
    };

    // Earth harmonics that generate Solfeggio frequencies
    private static readonly Dictionary<string, EarthHarmonic> EarthHarmonics = new()
    {
        ["B-flat"] = new EarthHarmonic { Note = "Bb", Hz = 14.4f, Description = "Base Earth frequency", Multiplier = 11, Generates = "MI 528" },
        ["F"] = new EarthHarmonic { Note = "F", Hz = 10.8f, Description = "5th harmonic of Earth", Multiplier = 11, Generates = "UT 396" },
        ["F#"] = new EarthHarmonic { Note = "F#", Hz = 11.377f, Description = "3rd harmonic of Earth", Multiplier = 11, Generates = "RE 417" },
        ["E"] = new EarthHarmonic { Note = "E", Hz = 20.222f, Description = "Higher harmonic", Multiplier = 11, Generates = "SOL 741" }
    };

    // Lost Solfeggio frequencies (interpolated)
    private static readonly Dictionary<string, LostSolfeggio> LostTones = new()
    {
        ["E#"] = new LostSolfeggio { Note = "E#", Hz = 83.437037f, Helek = 278, OctaveUp = 333.748f },
        ["Gb#"] = new LostSolfeggio { Note = "Gb#", Hz = 93.8666f, Helek = 313, OctaveUp = 375.466f },
        ["Db#"] = new LostSolfeggio { Note = "Db#", Hz = 140.8f, Helek = 469, OctaveUp = 281.6f },
        ["Ab#"] = new LostSolfeggio { Note = "Ab#", Hz = 105.6f, Helek = 352, OctaveUp = 422.4f }
    };

    // Current visualization state
    private string _selectedTone = "MI";
    private float _customFrequency = 528f;
    private bool _showHarmonicSeries = true;
    private bool _showEarthConnections = true;
    private bool _showLostTones = true;
    private float _patternIntensity = 1.0f;
    private float _animationSpeed = 1.0f;
    private bool _useHelekUnits = false;
    private float _harmonicDepth = 3; // How many harmonics to show
    private float _time = 0f; // For animation

    public string Name => "Solfeggio Harmonics";
    public Dictionary<string, EffectParam> Params { get; } = new()
    {
        ["tone"] = new EffectParam {
            Label = "Solfeggio Tone",
            Type = "dropdown",
            StringValue = "MI",
            Options = new() { "UT", "RE", "MI", "FA", "SOL", "LA", "custom" }
        },
        ["customFreq"] = new EffectParam {
            Label = "Custom Frequency (Hz)",
            Type = "slider",
            Min = 1,
            Max = 1000,
            FloatValue = 528f
        },
        ["intensity"] = new EffectParam {
            Label = "Pattern Intensity",
            Type = "slider",
            Min = 0.1f,
            Max = 3f,
            FloatValue = 1f
        },
        ["animation"] = new EffectParam {
            Label = "Animation Speed",
            Type = "slider",
            Min = 0.1f,
            Max = 5f,
            FloatValue = 1f
        },
        ["harmonics"] = new EffectParam {
            Label = "Show Harmonic Series",
            Type = "checkbox",
            BoolValue = true
        },
        ["earthConnections"] = new EffectParam {
            Label = "Show Earth Connections",
            Type = "checkbox",
            BoolValue = true
        },
        ["lostTones"] = new EffectParam {
            Label = "Show Lost Tones",
            Type = "checkbox",
            BoolValue = true
        },
        ["helekUnits"] = new EffectParam {
            Label = "Use Helek Units",
            Type = "checkbox",
            BoolValue = false
        },
        ["harmonicDepth"] = new EffectParam {
            Label = "Harmonic Depth",
            Type = "slider",
            Min = 1,
            Max = 8,
            FloatValue = 3f
        },
        ["baseColor"] = new EffectParam {
            Label = "Base Color",
            Type = "color",
            ColorValue = "#8B00FF"
        }
    };

    public void Render(float[] waveform, float[] spectrum, RenderContext ctx)
    {
        UpdateParameters();
        
        var currentTone = GetCurrentTone();
        var harmonics = GenerateHarmonicSeries(currentTone.Hz);
        var earthConnections = GetEarthConnections(currentTone.Hz);
        
        RenderMainPattern(currentTone, ctx);
        
        if (_showHarmonicSeries)
            RenderHarmonicSeries(harmonics, ctx);
        
        if (_showEarthConnections)
            RenderEarthConnections(earthConnections, ctx);
        
        if (_showLostTones)
            RenderLostTones(ctx);
        
        RenderFrequencyInfo(currentTone, ctx);
    }

    private void UpdateParameters()
    {
        _selectedTone = Params["tone"].StringValue;
        _customFrequency = Params["customFreq"].FloatValue;
        _patternIntensity = Params["intensity"].FloatValue;
        _animationSpeed = Params["animation"].FloatValue;
        _showHarmonicSeries = Params["harmonics"].BoolValue;
        _showEarthConnections = Params["earthConnections"].BoolValue;
        _showLostTones = Params["lostTones"].BoolValue;
        _useHelekUnits = Params["helekUnits"].BoolValue;
        _harmonicDepth = Params["harmonicDepth"].FloatValue;
    }

    private SolfeggioTone GetCurrentTone()
    {
        if (_selectedTone == "custom")
        {
            return new SolfeggioTone
            {
                Name = "Custom",
                Hz = _customFrequency,
                Note = "Custom",
                Meaning = "User-defined frequency",
                Helek = _customFrequency / 3.333f
            };
        }
        
        return SolfeggioTones[_selectedTone];
    }

    private List<Harmonic> GenerateHarmonicSeries(float fundamental)
    {
        var harmonics = new List<Harmonic>();
        
        for (int i = 1; i <= _harmonicDepth; i++)
        {
            float frequency = fundamental * i;
            float wavelength = 343f / frequency; // Speed of sound in air
            
            harmonics.Add(new Harmonic
            {
                Order = i,
                Frequency = frequency,
                Wavelength = wavelength,
                MusicalInterval = GetMusicalInterval(i),
                Color = GetHarmonicColor(i)
            });
        }
        
        return harmonics;
    }

    private string GetMusicalInterval(int harmonic)
    {
        return harmonic switch
        {
            1 => "Fundamental",
            2 => "Octave",
            3 => "Perfect 5th",
            4 => "Octave",
            5 => "Major 3rd",
            6 => "Perfect 5th",
            7 => "Minor 7th",
            8 => "Octave",
            _ => $"Harmonic {harmonic}"
        };
    }

    private uint GetHarmonicColor(int harmonic)
    {
        // Color based on harmonic order
        return harmonic switch
        {
            1 => 0xFF8B00FF, // Purple - fundamental
            2 => 0xFF0000FF, // Blue - octave
            3 => 0xFF00FF00, // Green - 5th
            4 => 0xFFFFFF00, // Yellow - octave
            5 => 0xFFFF8000, // Orange - 3rd
            6 => 0xFFFF0080, // Magenta - 5th
            7 => 0xFF8000FF, // Purple - 7th
            8 => 0xFF00FFFF, // Cyan - octave
            _ => 0xFFFFFFFF  // White - higher harmonics
        };
    }

    private List<EarthConnection> GetEarthConnections(float frequency)
    {
        var connections = new List<EarthConnection>();
        
        // Check if this frequency is an 11th harmonic of Earth frequencies
        foreach (var earth in EarthHarmonics.Values)
        {
            float generatedFreq = earth.Hz * earth.Multiplier;
            if (Math.Abs(generatedFreq - frequency) < 0.1f) // Within 0.1 Hz
            {
                connections.Add(new EarthConnection
                {
                    EarthHarmonic = earth,
                    GeneratedFrequency = generatedFreq,
                    Relationship = $"{earth.Note} {earth.Hz} Hz × {earth.Multiplier} = {generatedFreq} Hz"
                });
            }
        }
        
        return connections;
    }

    private void RenderMainPattern(SolfeggioTone tone, RenderContext ctx)
    {
        if (ctx.Canvas == null) return;
        
        // Clear canvas
        ctx.Canvas.Clear(0xFF000000);
        
        // Calculate center and radius
        float centerX = ctx.Width / 2f;
        float centerY = ctx.Height / 2f;
        float maxRadius = Math.Min(centerX, centerY) * 0.8f;
        
        // Draw sacred geometry pattern based on frequency
        float frequencyRatio = tone.Hz / 174f; // Base frequency
        int sides = Math.Max(3, (int)(frequencyRatio * 8f));
        
        // Draw polygon
        var points = new List<Vector2>();
        for (int i = 0; i < sides; i++)
        {
            float angle = i * 2f * MathF.PI / sides;
            float radius = maxRadius * (0.5f + 0.3f * MathF.Sin(_time * 2f + angle * 3f));
            points.Add(new Vector2(
                centerX + radius * MathF.Cos(angle),
                centerY + radius * MathF.Sin(angle)
            ));
        }
        
        // Draw polygon outline
        for (int i = 0; i < points.Count; i++)
        {
            var p1 = points[i];
            var p2 = points[(i + 1) % points.Count];
            ctx.Canvas.DrawLine(p1.X, p1.Y, p2.X, p2.Y, GetSolfeggioColor(tone.Hz), 2f);
        }
        
        // Draw Chladni plate-style nodal patterns
        DrawChladniPatterns(tone, ctx, centerX, centerY, maxRadius);
        
        // Draw animated wave interference patterns
        DrawWaveInterference(tone, ctx, centerX, centerY, maxRadius);
    }

    private void RenderHarmonicSeries(List<Harmonic> harmonics, RenderContext ctx)
    {
        if (ctx.Canvas == null || harmonics.Count == 0) return;
        
        float centerX = ctx.Width / 2f;
        float centerY = ctx.Height / 2f;
        float maxRadius = Math.Min(centerX, centerY) * 0.6f;
        
        // Draw fundamental frequency circle
        float fundamentalRadius = maxRadius * 0.2f;
        ctx.Canvas.DrawCircle(centerX, centerY, fundamentalRadius, GetSolfeggioColor(harmonics[0].Frequency), 3f);
        
        // Draw harmonic circles
        for (int i = 1; i < harmonics.Count && i < 8; i++)
        {
            float radius = fundamentalRadius * (i + 1);
            float alpha = 1f - (i * 0.1f);
            uint color = GetSolfeggioColor(harmonics[i].Frequency);
            color = ApplyAlpha(color, alpha);
            
            ctx.Canvas.DrawCircle(centerX, centerY, radius, color, 2f);
            
            // Draw frequency label
            string label = $"{harmonics[i].Frequency:F1} Hz";
            // Note: SkiaSharp text rendering would go here
        }
        
        // Draw harmonic bars on the right side
        float barWidth = 20f;
        float barSpacing = 30f;
        float startX = centerX + maxRadius + 50f;
        
        for (int i = 0; i < harmonics.Count && i < 12; i++)
        {
            float barHeight = (harmonics[i].Frequency / harmonics[0].Frequency) * 100f;
            float barY = centerY - barHeight / 2f;
            uint color = GetSolfeggioColor(harmonics[i].Frequency);
            
            ctx.Canvas.FillRectangle(startX + i * barSpacing, barY, barWidth, barHeight, color);
        }
    }

    private void RenderEarthConnections(List<EarthConnection> connections, RenderContext ctx)
    {
        if (ctx.Canvas == null || connections.Count == 0) return;
        
        float centerX = ctx.Width / 2f;
        float centerY = ctx.Height / 2f;
        float maxRadius = Math.Min(centerX, centerY) * 0.7f;
        
        // Draw Earth at center
        ctx.Canvas.FillCircle(centerX, centerY, 30f, 0xFF4A7C59); // Earth green
        
        // Draw connection lines to generated frequencies
        for (int i = 0; i < connections.Count && i < 8; i++)
        {
            var connection = connections[i];
            float angle = i * 2f * MathF.PI / connections.Count;
            float radius = maxRadius * 0.8f;
            
            float endX = centerX + radius * MathF.Cos(angle);
            float endY = centerY + radius * MathF.Sin(angle);
            
            // Draw connection line
            ctx.Canvas.DrawLine(centerX, centerY, endX, endY, 0xFF8B4513, 2f); // Brown line
            
            // Draw frequency node
            ctx.Canvas.FillCircle(endX, endY, 15f, GetSolfeggioColor(connection.GeneratedFrequency));
            
            // Draw mathematical relationship
            string relationship = $"{connection.EarthHarmonic.Note} × {connection.EarthHarmonic.Multiplier}";
            // Note: SkiaSharp text rendering would go here
        }
    }

    private void RenderLostTones(RenderContext ctx)
    {
        if (ctx.Canvas == null) return;
        
        float centerX = ctx.Width / 2f;
        float centerY = ctx.Height / 2f;
        float maxRadius = Math.Min(centerX, centerY) * 0.5f;
        
        // Draw lost Solfeggio tones as faded circles
        var lostTones = new[]
        {
            new { Note = "C#", Hz = 277.18f, Helek = 0.5f },
            new { Note = "D#", Hz = 311.13f, Helek = 0.5f },
            new { Note = "F#", Hz = 369.99f, Helek = 0.5f },
            new { Note = "G#", Hz = 415.30f, Helek = 0.5f },
            new { Note = "A#", Hz = 466.16f, Helek = 0.5f }
        };
        
        for (int i = 0; i < lostTones.Length; i++)
        {
            float angle = i * 2f * MathF.PI / lostTones.Length;
            float radius = maxRadius * 0.6f;
            
            float x = centerX + radius * MathF.Cos(angle);
            float y = centerY + radius * MathF.Sin(angle);
            
            // Draw faded circle for lost tone
            uint color = GetSolfeggioColor(lostTones[i].Hz);
            color = ApplyAlpha(color, 0.3f);
            ctx.Canvas.DrawCircle(x, y, 25f, color, 2f);
            
            // Draw Helek indicator
            float helekRadius = 8f;
            ctx.Canvas.FillCircle(x, y, helekRadius, 0xFFFF6B6B); // Red for lost
        }
    }

    private void RenderFrequencyInfo(SolfeggioTone tone, RenderContext ctx)
    {
        if (ctx.Canvas == null) return;
        
        // Draw frequency information overlay in top-left corner
        float startX = 20f;
        float startY = 20f;
        float lineHeight = 25f;
        
        // Background rectangle
        ctx.Canvas.FillRectangle(startX - 10f, startY - 10f, 300f, 150f, 0x80000000);
        
        // Frequency info
        string freqText = $"Frequency: {tone.Hz:F2} Hz";
        string noteText = $"Note: {tone.Note}";
        string meaningText = $"Meaning: {tone.Meaning}";
        string helekText = $"Helek: {tone.Helek:F2}";
        
        // Note: SkiaSharp text rendering would go here for all text elements
        // For now, we'll draw colored rectangles to represent the text areas
        
        // Frequency display
        ctx.Canvas.FillRectangle(startX, startY, 280f, 20f, GetSolfeggioColor(tone.Hz));
        
        // Note display
        ctx.Canvas.FillRectangle(startX, startY + lineHeight, 280f, 20f, 0xFF6B6BFF);
        
        // Meaning display
        ctx.Canvas.FillRectangle(startX, startY + lineHeight * 2, 280f, 20f, 0xFF6BFF6B);
        
        // Helek display
        ctx.Canvas.FillRectangle(startX, startY + lineHeight * 3, 280f, 20f, 0xFFFF6BFF);
    }

    private void DrawChladniPatterns(SolfeggioTone tone, RenderContext ctx, float centerX, float centerY, float maxRadius)
    {
        // Draw Chladni plate nodal patterns based on frequency
        float frequency = tone.Hz;
        int nodalLines = Math.Max(3, (int)(frequency / 100f));
        
        for (int i = 0; i < nodalLines; i++)
        {
            float angle = i * 2f * MathF.PI / nodalLines + _time;
            float radius = maxRadius * (0.3f + 0.2f * MathF.Sin(_time * 3f + i));
            
            // Draw nodal line
            float x1 = centerX + radius * MathF.Cos(angle);
            float y1 = centerY + radius * MathF.Sin(angle);
            float x2 = centerX + radius * MathF.Cos(angle + MathF.PI);
            float y2 = centerY + radius * MathF.Sin(angle + MathF.PI);
            
            ctx.Canvas.DrawLine(x1, y1, x2, y2, GetSolfeggioColor(frequency), 1f);
        }
    }

    private void DrawWaveInterference(SolfeggioTone tone, RenderContext ctx, float centerX, float centerY, float maxRadius)
    {
        // Draw animated wave interference patterns
        float frequency = tone.Hz;
        float wavelength = 343f / frequency; // Speed of sound / frequency
        
        for (int i = 0; i < 20; i++)
        {
            float radius = maxRadius * (i / 20f);
            float waveOffset = (_time * 2f + i * 0.5f) % (2f * MathF.PI);
            float amplitude = MathF.Sin(waveOffset) * 10f;
            
            float x = centerX + (radius + amplitude) * MathF.Cos(_time + i * 0.3f);
            float y = centerY + (radius + amplitude) * MathF.Sin(_time + i * 0.3f);
            
            uint color = GetSolfeggioColor(frequency);
            color = ApplyAlpha(color, 0.7f);
            
            ctx.Canvas.FillCircle(x, y, 3f, color);
        }
    }

    private uint GetSolfeggioColor(float frequency)
    {
        // Map frequency to color based on Solfeggio scale
        if (frequency < 200f) return 0xFF6B6BFF;      // Blue (lower frequencies)
        if (frequency < 300f) return 0xFF6BFF6B;      // Green (mid frequencies)
        if (frequency < 400f) return 0xFFFFFF6B;      // Yellow (higher frequencies)
        if (frequency < 500f) return 0xFFFF6B6B;      // Red (highest frequencies)
        return 0xFFFF6BFF;                            // Magenta (ultra high)
    }

    private uint ApplyAlpha(uint color, float alpha)
    {
        byte r = (byte)(color >> 16);
        byte g = (byte)(color >> 8);
        byte b = (byte)color;
        byte a = (byte)(alpha * 255);
        
        return (uint)((a << 24) | (r << 16) | (g << 8) | b);
    }

    // Data structures
    private class SolfeggioTone
    {
        public string Name { get; set; } = "";
        public float Hz { get; set; }
        public string Note { get; set; } = "";
        public string Meaning { get; set; } = "";
        public float Helek { get; set; }
    }

    private class EarthHarmonic
    {
        public string Note { get; set; } = "";
        public float Hz { get; set; }
        public string Description { get; set; } = "";
        public int Multiplier { get; set; }
        public string Generates { get; set; } = "";
    }

    private class LostSolfeggio
    {
        public string Note { get; set; } = "";
        public float Hz { get; set; }
        public float Helek { get; set; }
        public float OctaveUp { get; set; }
    }

    private class Harmonic
    {
        public int Order { get; set; }
        public float Frequency { get; set; }
        public float Wavelength { get; set; }
        public string MusicalInterval { get; set; } = "";
        public uint Color { get; set; }
    }

    private class EarthConnection
    {
        public EarthHarmonic EarthHarmonic { get; set; } = new();
        public float GeneratedFrequency { get; set; }
        public string Relationship { get; set; } = "";
    }
}
