using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;

namespace PhoenixVisualizer.Core.Nodes;

/// <summary>
/// Core interface for all effect nodes in the Phoenix system
/// Supports both AVS-ported effects and Phoenix originals
/// </summary>
public interface IEffectNode
{
    string Name { get; }
    Dictionary<string, EffectParam> Params { get; }
    void Render(float[] waveform, float[] spectrum, RenderContext ctx);
}

/// <summary>
/// Parameter definition for effect node properties
/// Supports sliders, checkboxes, color pickers, and more
/// </summary>
public class EffectParam
{
    public string Label { get; set; } = "";
    public string Type { get; set; } = "slider"; // slider, checkbox, color, dropdown
    public float FloatValue { get; set; }
    public bool BoolValue { get; set; }
    public string StringValue { get; set; } = "";
    public string ColorValue { get; set; } = "#FFFFFF";
    public float Min { get; set; } = 0;
    public float Max { get; set; } = 1;
    public List<string> Options { get; set; } = new(); // For dropdown types
}

/// <summary>
/// Rendering context passed to effect nodes
/// Contains surface information and audio data
/// </summary>
public class RenderContext
{
    public int Width { get; set; }
    public int Height { get; set; }
    public float[] Waveform { get; set; } = Array.Empty<float>();
    public float[] Spectrum { get; set; } = Array.Empty<float>();
    public float Time { get; set; }
    public bool Beat { get; set; }
    public float Volume { get; set; }
    // TODO: Add SkiaSharp canvas handle
}

/// <summary>
/// Automatic effect node registry
/// Discovers and manages all IEffectNode implementations
/// </summary>
public static class EffectRegistry
{
    private static readonly List<Type> _effectTypes = new();

    static EffectRegistry()
    {
        var iface = typeof(IEffectNode);
        _effectTypes = Assembly.GetExecutingAssembly()
            .GetTypes()
            .Where(t => iface.IsAssignableFrom(t) && !t.IsInterface && !t.IsAbstract)
            .ToList();
    }

    /// <summary>
    /// Get all registered effect nodes
    /// </summary>
    public static IEnumerable<IEffectNode> GetAll()
    {
        foreach (var type in _effectTypes)
        {
            if (Activator.CreateInstance(type) is IEffectNode node)
                yield return node;
        }
    }

    /// <summary>
    /// Create an effect node by name
    /// </summary>
    public static IEffectNode? CreateByName(string name)
    {
        var type = _effectTypes.FirstOrDefault(t =>
        {
            var tmp = (IEffectNode?)Activator.CreateInstance(t);
            return tmp?.Name == name;
        });
        return type != null ? (IEffectNode?)Activator.CreateInstance(type) : null;
    }

    /// <summary>
    /// Get effect names for UI dropdowns
    /// </summary>
    public static IEnumerable<string> GetEffectNames()
    {
        return _effectTypes.Select(t =>
        {
            var tmp = (IEffectNode?)Activator.CreateInstance(t);
            return tmp?.Name ?? "Unknown";
        }).OrderBy(name => name);
    }
}
