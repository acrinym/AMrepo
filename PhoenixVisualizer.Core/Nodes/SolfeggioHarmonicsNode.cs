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
        // TODO: Implement SkiaSharp rendering for the main Solfeggio pattern
        // This would include:
        // - Sacred geometry patterns based on frequency
        // - Chladni plate-style nodal patterns
        // - Color gradients based on frequency ratios
        // - Animated wave interference patterns
    }

    private void RenderHarmonicSeries(List<Harmonic> harmonics, RenderContext ctx)
    {
        // TODO: Render harmonic series visualization
        // Show fundamental and harmonics as concentric circles or bars
        // Display frequency ratios and musical intervals
        // Use harmonic-specific colors
    }

    private void RenderEarthConnections(List<EarthConnection> connections, RenderContext ctx)
    {
        // TODO: Render Earth harmonic connections
        // Show how Earth frequencies generate Solfeggio tones
        // Display mathematical relationships
        // Visualize the x11 multiplication factor
    }

    private void RenderLostTones(RenderContext ctx)
    {
        // TODO: Render lost Solfeggio tones
        // Show interpolated frequencies
        // Display Helek conversions
        // Visualize octave relationships
    }

    private void RenderFrequencyInfo(SolfeggioTone tone, RenderContext ctx)
    {
        // TODO: Render frequency information overlay
        // Display current frequency in Hz and Helek
        // Show musical note and meaning
        // Display mathematical relationships
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
