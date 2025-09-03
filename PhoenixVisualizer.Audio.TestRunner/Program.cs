using System;
using System.Threading;
using System.Linq;
using PhoenixVisualizer.Audio;

namespace PhoenixVisualizer.Audio.TestRunner;

public static class Program
{
    public static void Main(string[] args)
    {
        Console.WriteLine("🎵 Phoenix Visualizer - VLC Audio Integration Test");
        Console.WriteLine("==================================================");

        TestVlcBasicFunctionality();

        Console.WriteLine("\nPress any key to exit...");
        Console.ReadKey();
    }

    private static void TestVlcBasicFunctionality()
    {
        Console.WriteLine("🔧 Testing basic VLC functionality...");

        try
        {
            // Test 1: Initialize VLC
            var audioService = new VlcAudioService();
            Console.WriteLine("✅ VLC Audio Service created");

            // Test 2: Try to load and play a file
            string testFile = @"libs_etc/come home amanda (1).mp3";
            Console.WriteLine($"🎵 Attempting to play: {testFile}");

            // Try Play method
            audioService.Play(testFile);
            Console.WriteLine("✅ Play method called");

            // Wait a bit for playback to start
            Thread.Sleep(3000);

            // Check status
            Console.WriteLine($"📊 IsPlaying: {audioService.IsPlaying}");
            Console.WriteLine($"📊 Current position: {audioService.GetPositionSeconds():F2}s");
            Console.WriteLine($"📊 Status: {audioService.GetStatus()}");

            // Test multiple data retrievals to simulate real-time usage
            for (int i = 0; i < 3; i++)
            {
                // Try to get audio data
                var waveformData = audioService.GetWaveformData();
                var spectrumData = audioService.GetSpectrumData();

                if (waveformData != null && spectrumData != null)
                {
                    Console.WriteLine($"✅ Audio data retrieved (iteration {i + 1})");
                    Console.WriteLine($"   Waveform Length: {waveformData.Length}");
                    Console.WriteLine($"   Spectrum Length: {spectrumData.Length}");
                    Console.WriteLine($"   Sample values: {string.Join(", ", waveformData.Take(5).Select(x => x.ToString("F4", System.Globalization.CultureInfo.InvariantCulture)))}");
                    Console.WriteLine($"   Spectrum values: {string.Join(", ", spectrumData.Take(5).Select(x => x.ToString("F4", System.Globalization.CultureInfo.InvariantCulture)))}");
                }
                else
                {
                    Console.WriteLine($"❌ No audio data available (iteration {i + 1})");
                    Console.WriteLine($"   Waveform data: {(waveformData != null ? "Available" : "Null")}");
                    Console.WriteLine($"   Spectrum data: {(spectrumData != null ? "Available" : "Null")}");
                }

                Thread.Sleep(500); // Wait between samples
            }

            // Stop playback
            audioService.Stop();
            Console.WriteLine("✅ Playback stopped");

        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Error during VLC test: {ex.Message}");
            Console.WriteLine($"   Stack trace: {ex.StackTrace}");
        }
    }

}
