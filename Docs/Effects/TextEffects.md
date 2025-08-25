# Text Effects

## Overview

The Text effect is a comprehensive text rendering system that displays customizable text with advanced formatting options. It supports multiple text sources, dynamic positioning, beat-responsive behavior, and various visual effects including outlines, shadows, and blending modes. The effect can display static text, dynamic content from audio sources, and supports word-by-word animation.

## C# Implementation

### TextEffectsNode Class

```csharp
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Text;
using PhoenixVisualizer.Core.Effects.Models;
using PhoenixVisualizer.Core.Models;

namespace PhoenixVisualizer.Core.Effects.Nodes.AvsEffects
{
    public class TextEffectsNode : BaseEffectNode
    {
        #region Properties

        /// <summary>
        /// Enable/disable the text effect
        /// </summary>
        public bool Enabled { get; set; } = true;

        /// <summary>
        /// Text color (RGB)
        /// </summary>
        public Color TextColor { get; set; } = Color.White;

        /// <summary>
        /// Blending mode - 0=none, 1=additive, 2=50/50
        /// </summary>
        public int BlendMode { get; set; } = 0;

        /// <summary>
        /// Enable beat-responsive behavior
        /// </summary>
        public bool BeatResponse { get; set; } = false;

        /// <summary>
        /// Insert blank lines between text
        /// </summary>
        public bool InsertBlank { get; set; } = false;

        /// <summary>
        /// Random positioning enabled
        /// </summary>
        public bool RandomPosition { get; set; } = false;

        /// <summary>
        /// Vertical alignment - 0=top, 1=center, 2=bottom
        /// </summary>
        public int VerticalAlignment { get; set; } = 1; // DT_VCENTER

        /// <summary>
        /// Horizontal alignment - 0=left, 1=center, 2=right
        /// </summary>
        public int HorizontalAlignment { get; set; } = 1; // DT_CENTER

        /// <summary>
        /// Speed on beat (frames per word)
        /// </summary>
        public int BeatSpeed { get; set; } = 15;

        /// <summary>
        /// Normal speed (frames per word)
        /// </summary>
        public int NormalSpeed { get; set; } = 15;

        /// <summary>
        /// Text content (semicolon-separated for multiple lines)
        /// </summary>
        public string Text { get; set; } = "Sample Text";

        /// <summary>
        /// Enable text outline
        /// </summary>
        public bool Outline { get; set; } = false;

        /// <summary>
        /// Outline color
        /// </summary>
        public Color OutlineColor { get; set; } = Color.Black;

        /// <summary>
        /// X position shift (-100 to 100)
        /// </summary>
        public int XShift { get; set; } = 0;

        /// <summary>
        /// Y position shift (-100 to 100)
        /// </summary>
        public int YShift { get; set; } = 0;

        /// <summary>
        /// Outline size in pixels
        /// </summary>
        public int OutlineSize { get; set; } = 1;

        /// <summary>
        /// Random word selection
        /// </summary>
        public bool RandomWord { get; set; } = false;

        /// <summary>
        /// Enable text shadow
        /// </summary>
        public bool Shadow { get; set; } = false;

        /// <summary>
        /// Font family name
        /// </summary>
        public string FontFamily { get; set; } = "Arial";

        /// <summary>
        /// Font size in points
        /// </summary>
        public float FontSize { get; set; } = 24.0f;

        /// <summary>
        /// Font style (Bold, Italic, etc.)
        /// </summary>
        public FontStyle FontStyle { get; set; } = FontStyle.Regular;

        #endregion

        #region Private Fields

        private string[] _textWords;
        private int _currentWordIndex;
        private int _frameCounter;
        private int _currentSpeed;
        private Random _random;
        private Font _currentFont;
        private StringFormat _stringFormat;
        private SizeF _textSize;

        #endregion

        #region Constructor

        public TextEffectsNode()
        {
            _textWords = new string[0];
            _currentWordIndex = 0;
            _frameCounter = 0;
            _currentSpeed = 15;
            _random = new Random();
            _currentFont = new Font("Arial", 24.0f);
            _stringFormat = new StringFormat();
            _textSize = SizeF.Empty;

            UpdateStringFormat();
        }

        #endregion

        #region Processing

        public override void ProcessFrame(ImageBuffer imageBuffer, AudioFeatures audioFeatures)
        {
            if (!Enabled || string.IsNullOrEmpty(Text)) return;

            // Initialize text words if needed
            if (_textWords.Length == 0)
            {
                ParseText();
            }

            // Handle beat response
            if (BeatResponse && audioFeatures.IsBeat)
            {
                _currentSpeed = BeatSpeed;
            }
            else
            {
                _currentSpeed = NormalSpeed;
            }

            // Update word display
            if (_frameCounter >= _currentSpeed)
            {
                UpdateWordDisplay();
                _frameCounter = 0;
            }

            // Render current text
            RenderText(imageBuffer);

            _frameCounter++;
        }

        private void ParseText()
        {
            if (string.IsNullOrEmpty(Text))
            {
                _textWords = new string[0];
                return;
            }

            // Split text by semicolons for multiple lines
            _textWords = Text.Split(';');
            
            // Insert blank lines if enabled
            if (InsertBlank)
            {
                var expandedWords = new List<string>();
                foreach (string word in _textWords)
                {
                    if (!string.IsNullOrEmpty(word.Trim()))
                    {
                        expandedWords.Add(word.Trim());
                        expandedWords.Add(""); // Blank line
                    }
                }
                _textWords = expandedWords.ToArray();
            }

            // Remove empty entries
            _textWords = Array.FindAll(_textWords, word => !string.IsNullOrEmpty(word.Trim()));
        }

        private void UpdateWordDisplay()
        {
            if (_textWords.Length == 0) return;

            if (RandomWord)
            {
                _currentWordIndex = _random.Next(_textWords.Length);
            }
            else
            {
                _currentWordIndex = (_currentWordIndex + 1) % _textWords.Length;
            }
        }

        private void RenderText(ImageBuffer imageBuffer)
        {
            if (_textWords.Length == 0 || _currentWordIndex >= _textWords.Length) return;

            string currentText = _textWords[_currentWordIndex];
            if (string.IsNullOrEmpty(currentText)) return;

            // Calculate text position
            Point textPosition = CalculateTextPosition(imageBuffer, currentText);

            // Create graphics path for text
            using (var path = new GraphicsPath())
            {
                path.AddString(currentText, _currentFont.FontFamily, (int)_currentFont.Style, 
                             _currentFont.Size, textPosition, _stringFormat);

                // Render shadow if enabled
                if (Shadow)
                {
                    RenderShadow(imageBuffer, path, textPosition);
                }

                // Render outline if enabled
                if (Outline)
                {
                    RenderOutline(imageBuffer, path);
                }

                // Render main text
                RenderMainText(imageBuffer, path);
            }
        }

        private Point CalculateTextPosition(ImageBuffer imageBuffer, string text)
        {
            // Measure text size
            using (var g = Graphics.FromImage(new Bitmap(1, 1)))
            {
                _textSize = g.MeasureString(text, _currentFont);
            }

            int x, y;

            // Calculate horizontal position
            switch (HorizontalAlignment)
            {
                case 0: // Left
                    x = 10 + XShift;
                    break;
                case 1: // Center
                    x = (imageBuffer.Width / 2) - ((int)_textSize.Width / 2) + XShift;
                    break;
                case 2: // Right
                    x = imageBuffer.Width - 10 - (int)_textSize.Width + XShift;
                    break;
                default:
                    x = (imageBuffer.Width / 2) - ((int)_textSize.Width / 2) + XShift;
                    break;
            }

            // Calculate vertical position
            switch (VerticalAlignment)
            {
                case 0: // Top
                    y = 10 + YShift;
                    break;
                case 1: // Center
                    y = (imageBuffer.Height / 2) - ((int)_textSize.Height / 2) + YShift;
                    break;
                case 2: // Bottom
                    y = imageBuffer.Height - 10 - (int)_textSize.Height + YShift;
                    break;
                default:
                    y = (imageBuffer.Height / 2) - ((int)_textSize.Height / 2) + YShift;
                    break;
            }

            // Apply random positioning if enabled
            if (RandomPosition)
            {
                x = _random.Next(imageBuffer.Width - (int)_textSize.Width);
                y = _random.Next(imageBuffer.Height - (int)_textSize.Height);
            }

            return new Point(x, y);
        }

        private void RenderShadow(ImageBuffer imageBuffer, GraphicsPath path, Point textPosition)
        {
            // Create shadow path
            using (var shadowPath = new GraphicsPath())
            {
                shadowPath.AddString(_textWords[_currentWordIndex], _currentFont.FontFamily, 
                                   (int)_currentFont.Style, _currentFont.Size, 
                                   new Point(textPosition.X + 2, textPosition.Y + 2), _stringFormat);

                // Render shadow with dark color
                using (var brush = new SolidBrush(Color.FromArgb(128, Color.Black)))
                {
                    RenderPathToImage(imageBuffer, shadowPath, brush, BlendMode);
                }
            }
        }

        private void RenderOutline(ImageBuffer imageBuffer, GraphicsPath path)
        {
            // Create outline path
            using (var pen = new Pen(OutlineColor, OutlineSize))
            {
                pen.LineJoin = LineJoin.Round;
                pen.MiterLimit = 0.5f;

                // Render outline
                RenderPathOutlineToImage(imageBuffer, path, pen, BlendMode);
            }
        }

        private void RenderMainText(ImageBuffer imageBuffer, GraphicsPath path)
        {
            using (var brush = new SolidBrush(TextColor))
            {
                RenderPathToImage(imageBuffer, path, brush, BlendMode);
            }
        }

        private void RenderPathToImage(ImageBuffer imageBuffer, GraphicsPath path, Brush brush, int blendMode)
        {
            // Convert path to bitmap for rendering
            using (var bitmap = new Bitmap(imageBuffer.Width, imageBuffer.Height))
            using (var g = Graphics.FromImage(bitmap))
            {
                g.SmoothingMode = SmoothingMode.AntiAlias;
                g.TextRenderingHint = TextRenderingHint.AntiAlias;

                g.FillPath(brush, path);

                // Apply to image buffer with blending
                for (int y = 0; y < imageBuffer.Height; y++)
                {
                    for (int x = 0; x < imageBuffer.Width; x++)
                    {
                        Color sourceColor = bitmap.GetPixel(x, y);
                        if (sourceColor.A > 0)
                        {
                            Color existingColor = imageBuffer.GetPixel(x, y);
                            Color finalColor = BlendColors(existingColor, sourceColor, blendMode);
                            imageBuffer.SetPixel(x, y, finalColor);
                        }
                    }
                }
            }
        }

        private void RenderPathOutlineToImage(ImageBuffer imageBuffer, GraphicsPath path, Pen pen, int blendMode)
        {
            // Convert path outline to bitmap for rendering
            using (var bitmap = new Bitmap(imageBuffer.Width, imageBuffer.Height))
            using (var g = Graphics.FromImage(bitmap))
            {
                g.SmoothingMode = SmoothingMode.AntiAlias;
                g.TextRenderingHint = TextRenderingHint.AntiAlias;

                g.DrawPath(pen, path);

                // Apply to image buffer with blending
                for (int y = 0; y < imageBuffer.Height; y++)
                {
                    for (int x = 0; x < imageBuffer.Width; x++)
                    {
                        Color sourceColor = bitmap.GetPixel(x, y);
                        if (sourceColor.A > 0)
                        {
                            Color existingColor = imageBuffer.GetPixel(x, y);
                            Color finalColor = BlendColors(existingColor, sourceColor, blendMode);
                            imageBuffer.SetPixel(x, y, finalColor);
                        }
                    }
                }
            }
        }

        private Color BlendColors(Color existing, Color source, int blendMode)
        {
            switch (blendMode)
            {
                case 0: // Replace
                    return source;
                case 1: // Additive
                    return Color.FromArgb(
                        Math.Min(255, existing.R + source.R),
                        Math.Min(255, existing.G + source.G),
                        Math.Min(255, existing.B + source.B)
                    );
                case 2: // 50/50
                    return Color.FromArgb(
                        (existing.R + source.R) / 2,
                        (existing.G + source.G) / 2,
                        (existing.B + source.B) / 2
                    );
                default:
                    return source;
            }
        }

        private void UpdateStringFormat()
        {
            _stringFormat.Alignment = HorizontalAlignment switch
            {
                0 => StringAlignment.Near,    // Left
                1 => StringAlignment.Center,   // Center
                2 => StringAlignment.Far,      // Right
                _ => StringAlignment.Center
            };

            _stringFormat.LineAlignment = VerticalAlignment switch
            {
                0 => StringAlignment.Near,    // Top
                1 => StringAlignment.Center,  // Center
                2 => StringAlignment.Far,     // Bottom
                _ => StringAlignment.Center
            };
        }

        #endregion

        #region Configuration

        public override bool ValidateConfiguration()
        {
            // Validate property ranges
            BeatSpeed = Math.Max(1, Math.Min(100, BeatSpeed));
            NormalSpeed = Math.Max(1, Math.Min(100, NormalSpeed));
            XShift = Math.Max(-100, Math.Min(100, XShift));
            YShift = Math.Max(-100, Math.Min(100, YShift));
            OutlineSize = Math.Max(1, Math.Min(10, OutlineSize));
            FontSize = Math.Max(8.0f, Math.Min(72.0f, FontSize));

            // Update font if needed
            if (_currentFont == null || _currentFont.FontFamily.Name != FontFamily || 
                _currentFont.Size != FontSize || _currentFont.Style != FontStyle)
            {
                _currentFont?.Dispose();
                _currentFont = new Font(FontFamily, FontSize, FontStyle);
            }

            UpdateStringFormat();

            return true;
        }

        public override string GetSettingsSummary()
        {
            string blendMode = BlendMode == 0 ? "Replace" : BlendMode == 1 ? "Additive" : "50/50";
            string vAlign = VerticalAlignment == 0 ? "Top" : VerticalAlignment == 1 ? "Center" : "Bottom";
            string hAlign = HorizontalAlignment == 0 ? "Left" : HorizontalAlignment == 1 ? "Center" : "Right";
            string beatResponse = BeatResponse ? "On" : "Off";

            return $"Text Effect - Enabled: {Enabled}, Text: \"{Text}\", " +
                   $"Color: {TextColor.Name}, Font: {FontFamily} {FontSize}pt, " +
                   $"Align: {hAlign}/{vAlign}, Blend: {blendMode}, " +
                   $"Beat: {beatResponse}, Speed: {NormalSpeed}/{BeatSpeed}";
        }

        #endregion

        #region IDisposable

        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
                _currentFont?.Dispose();
                _stringFormat?.Dispose();
            }
            base.Dispose(disposing);
        }

        #endregion
    }
}
```

## Effect Behavior

The Text effect provides comprehensive text rendering capabilities by:

1. **Dynamic Text Display**: Shows text word-by-word with configurable timing
2. **Multiple Text Sources**: Supports semicolon-separated text for multiple lines
3. **Advanced Positioning**: Configurable alignment, offsets, and random positioning
4. **Visual Effects**: Outlines, shadows, and multiple blending modes
5. **Beat Synchronization**: Audio-responsive text timing and positioning
6. **Font Customization**: Full font family, size, and style control

## Key Features

- **Word-by-Word Animation**: Progressive text display with configurable speed
- **Multiple Alignment Options**: Left, center, right horizontal and top, center, bottom vertical
- **Visual Enhancement**: Outline, shadow, and blending effects
- **Audio Integration**: Beat-responsive behavior for dynamic text timing
- **Flexible Positioning**: Manual offsets, random positioning, and automatic centering
- **Professional Typography**: Anti-aliased rendering with custom fonts

## Use Cases

- **Music Visualization**: Display song titles, lyrics, or artist information
- **Information Display**: Show status messages, timestamps, or metadata
- **Interactive Interfaces**: Dynamic text overlays for user feedback
- **Presentation Graphics**: Professional text rendering for visual content
- **Gaming Applications**: HUD elements, score displays, and notifications
