using System.Runtime.InteropServices;
using System.Text;
using PhoenixVisualizer.Core.Diagnostics;

namespace PhoenixVisualizer.Core.Avs;

public enum AvsRoute
{
    NotAvs,
    NativeAvs,  // Windows + vis_avs.dll present (to be implemented)
    PhoenixAvs, // Use Phoenix native C# implementation
    Unsupported // Show message, list missing deps
}

public sealed class AvsRouteResult
{
    public AvsRoute Route { get; init; }
    public AvsPresetInfo Info { get; init; } = new();
    public string? Message { get; init; }
}

public static class AvsPresetRouter
{
    /// <summary>
    /// Decides what to do with a dropped/loaded blob. Does not throw.
    /// </summary>
    public static AvsRouteResult Decide(byte[] blob, string? fileName = null, string? nativeAvsPath = null)
    {
        try
        {
            var info = AvsPresetDetector.Analyze(blob);
            if (!info.IsNullsoftAvs)
                return new AvsRouteResult { Route = AvsRoute.NotAvs, Info = info };

            // Windows-only native path
            if (!RuntimeInformation.IsOSPlatform(OSPlatform.Windows))
            {
                return new AvsRouteResult
                {
                    Route = AvsRoute.Unsupported,
                    Info = info,
                    Message = "❌ AVS preset detected, but native AVS runtime is Windows-only. Run on Windows or convert this preset."
                };
            }

            // Check DLL presence if user provided a location; allow PATH fallback
            var dll = nativeAvsPath ?? "vis_avs.dll";
            var canLoad = NativeLibrary.TryLoad(dll, out var handle);
            if (canLoad && handle != IntPtr.Zero)
            {
                NativeLibrary.Free(handle);
                return new AvsRouteResult { Route = AvsRoute.NativeAvs, Info = info, Message = $"✅ AVS preset detected{(fileName is null ? "" : $" ({fileName})")} — using native AVS runtime." };
            }

            // Native runtime not available - try Phoenix implementation
            try
            {
                // Check if Phoenix can handle this preset
                var phoenixCompatible = CheckPhoenixCompatibility(info);
                if (phoenixCompatible)
                {
                    return new AvsRouteResult 
                    { 
                        Route = AvsRoute.PhoenixAvs, 
                        Info = info, 
                        Message = $"✅ AVS preset detected{(fileName is null ? "" : $" ({fileName})")} — using Phoenix C# implementation." 
                    };
                }
            }
            catch (Exception ex)
            {
                Log.Error("Phoenix AVS compatibility check failed", ex);
            }

            // We don't have any working implementation; construct a helpful message.
            var sb = new StringBuilder();
            sb.AppendLine("❌ AVS preset detected, but neither native nor Phoenix runtime could handle it.");
            sb.AppendLine();
            if (!string.IsNullOrWhiteSpace(info.Title)) sb.AppendLine($"• Title: {info.Title}");
            if (!string.IsNullOrWhiteSpace(info.Author)) sb.AppendLine($"• Author/Ref: {info.Author}");
            if (info.ProbableComponents.Count > 0)
            {
                sb.AppendLine("• Probable components used:");
                foreach (var c in info.ProbableComponents.OrderBy(x => x))
                    sb.AppendLine($"   - {c}");
            }
            sb.AppendLine();
            sb.AppendLine("💡 Options:");
            sb.AppendLine("   • Place vis_avs.dll next to the executable for native support");
            sb.AppendLine("   • Or try a simpler AVS preset for Phoenix compatibility");

            return new AvsRouteResult
            {
                Route = AvsRoute.Unsupported,
                Info = info,
                Message = sb.ToString()
            };
        }
        catch (Exception ex)
        {
            Log.Error("AVS routing failed", ex);
            return new AvsRouteResult
            {
                Route = AvsRoute.Unsupported,
                Info = new AvsPresetInfo { IsNullsoftAvs = false },
                Message = $"❌ AVS preset check failed: {ex.Message}"
            };
        }
    }
    
    /// <summary>
    /// Check if Phoenix implementation can handle this AVS preset
    /// </summary>
    private static bool CheckPhoenixCompatibility(AvsPresetInfo info)
    {
        // For now, assume Phoenix can handle any valid AVS preset
        // In the future, we could add more sophisticated checking based on 
        // the probable components and known Phoenix capabilities
        if (!info.IsNullsoftAvs) return false;
        
        // Phoenix supports most basic AVS functionality
        // Complex APE modules might not be supported yet
        var unsupportedComponents = new[] 
        {
            "DynamicMovement",  // Advanced APE
            "Texer",           // Complex texture operations
            "Trans",           // Advanced transitions (some may work)
            // Add more as we discover limitations
        };
        
        // Check if any unsupported components are detected
        foreach (var component in info.ProbableComponents)
        {
            if (unsupportedComponents.Contains(component, StringComparer.OrdinalIgnoreCase))
            {
                // For now, still try Phoenix even with advanced components
                // We'll show a warning in the message if needed
            }
        }
        
        // Phoenix can at least attempt to load any AVS preset
        return true;
    }
}
