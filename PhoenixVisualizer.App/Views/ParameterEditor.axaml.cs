using System;
using System.Collections.Generic;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Media;
using PhoenixVisualizer.Core.Nodes;

namespace PhoenixVisualizer.App.Views;

/// <summary>
/// Dynamic parameter editor that generates UI controls based on effect parameters
/// </summary>
public partial class ParameterEditor : UserControl
{
    public static readonly StyledProperty<Dictionary<string, EffectParam>> ParametersProperty =
        AvaloniaProperty.Register<ParameterEditor, Dictionary<string, EffectParam>>(nameof(Parameters));

    public static readonly StyledProperty<string> EffectNameProperty =
        AvaloniaProperty.Register<ParameterEditor, string>(nameof(EffectName));

    public Dictionary<string, EffectParam> Parameters
    {
        get => GetValue(ParametersProperty);
        set => SetValue(ParametersProperty, value);
    }

    public string EffectName
    {
        get => GetValue(EffectNameProperty);
        set => SetValue(EffectNameProperty, value);
    }

    public ParameterEditor()
    {
        InitializeComponent();
        Parameters = new Dictionary<string, EffectParam>();
    }

    protected override void OnPropertyChanged(AvaloniaPropertyChangedEventArgs change)
    {
        base.OnPropertyChanged(change);

        if (change.Property == ParametersProperty || change.Property == EffectNameProperty)
        {
            UpdateParameterControls();
        }
    }

    private void UpdateParameterControls()
    {
        ParametersPanel.Children.Clear();

        if (string.IsNullOrEmpty(EffectName))
        {
            // Show default message
            var defaultText = new TextBlock
            {
                Text = "Select an effect to edit parameters",
                Foreground = Brushes.Gray,
                TextAlignment = TextAlignment.Center,
                Margin = new Thickness(0, 20, 0, 0)
            };
            ParametersPanel.Children.Add(defaultText);
            return;
        }

        // Add effect header
        var header = new Border
        {
            Background = new SolidColorBrush(Color.Parse("#007ACC")),
            BorderBrush = new SolidColorBrush(Color.Parse("#3F3F46")),
            BorderThickness = new Thickness(0, 0, 0, 1),
            Margin = new Thickness(0, 0, 0, 10)
        };

        var headerText = new TextBlock
        {
            Text = $"⚙️ {EffectName}",
            FontSize = 12,
            FontWeight = FontWeight.Bold,
            Foreground = Brushes.White,
            Margin = new Thickness(10, 5)
        };

        header.Child = headerText;
        ParametersPanel.Children.Add(header);

        // Generate controls for each parameter
        foreach (var parameter in Parameters)
        {
            var control = CreateParameterControl(parameter.Key, parameter.Value);
            if (control != null)
            {
                ParametersPanel.Children.Add(control);
            }
        }
    }

    private Control CreateParameterControl(string key, EffectParam param)
    {
        var container = new Border
        {
            Background = new SolidColorBrush(Color.Parse("#2D2D30")),
            BorderBrush = new SolidColorBrush(Color.Parse("#3F3F46")),
            BorderThickness = new Thickness(1),
            CornerRadius = new CornerRadius(3),
            Margin = new Thickness(0, 0, 0, 8)
        };

        var stack = new StackPanel { Margin = new Thickness(8) };

        // Parameter label
        var label = new TextBlock
        {
            Text = param.Label,
            Foreground = Brushes.White,
            FontSize = 11,
            FontWeight = FontWeight.Bold,
            Margin = new Thickness(0, 0, 0, 4)
        };
        stack.Children.Add(label);

        // Parameter control based on type
        Control control = param.Type switch
        {
            "slider" => CreateSliderControl(param),
            "checkbox" => CreateCheckboxControl(param),
            "color" => CreateColorControl(param),
            "dropdown" => CreateDropdownControl(param),
            _ => CreateTextBlock($"Unsupported parameter type: {param.Type}")
        };

        stack.Children.Add(control);

        // Parameter value display
        var valueDisplay = CreateValueDisplay(param);
        stack.Children.Add(valueDisplay);

        container.Child = stack;
        return container;
    }

    private Control CreateSliderControl(EffectParam param)
    {
        var slider = new Slider
        {
            Minimum = (double)param.Min,
            Maximum = (double)param.Max,
            Value = (double)param.FloatValue,
            Margin = new Thickness(0, 0, 0, 4),
            Height = 20
        };

        slider.PropertyChanged += (sender, args) =>
        {
            if (args.Property.Name == nameof(Slider.Value))
            {
                param.FloatValue = (float)slider.Value;
            }
        };

        return slider;
    }

    private Control CreateCheckboxControl(EffectParam param)
    {
        var checkbox = new CheckBox
        {
            Content = param.Label,
            IsChecked = param.BoolValue,
            Foreground = Brushes.White,
            Margin = new Thickness(0, 0, 0, 4)
        };

        checkbox.PropertyChanged += (sender, args) =>
        {
            if (args.Property.Name == nameof(CheckBox.IsChecked))
            {
                param.BoolValue = checkbox.IsChecked ?? false;
            }
        };

        return checkbox;
    }

    private Control CreateColorControl(EffectParam param)
    {
        var colorButton = new Button
        {
            Content = "🎨 Pick Color",
            Background = new SolidColorBrush(Color.Parse(param.ColorValue)),
            Foreground = Brushes.White,
            Margin = new Thickness(0, 0, 0, 4),
            Height = 25
        };

        colorButton.Click += async (sender, args) =>
        {
            // TODO: Implement color picker dialog
            // For now, cycle through some colors
            var colors = new[] { "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF", "#FFFFFF" };
            var currentIndex = Array.IndexOf(colors, param.ColorValue);
            var nextIndex = (currentIndex + 1) % colors.Length;
            param.ColorValue = colors[nextIndex];
            colorButton.Background = new SolidColorBrush(Color.Parse(param.ColorValue));
        };

        return colorButton;
    }

    private Control CreateDropdownControl(EffectParam param)
    {
        var comboBox = new ComboBox
        {
            ItemsSource = param.Options,
            SelectedItem = param.StringValue,
            Margin = new Thickness(0, 0, 0, 4),
            Height = 25
        };

        comboBox.SelectionChanged += (sender, args) =>
        {
            if (comboBox.SelectedItem is string selectedValue)
            {
                param.StringValue = selectedValue;
            }
        };

        return comboBox;
    }

    private Control CreateValueDisplay(EffectParam param)
    {
        var valueText = new TextBlock
        {
            FontSize = 10,
            Foreground = new SolidColorBrush(Color.Parse("#CCCCCC")),
            HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Right
        };

        // Bind to parameter value changes
        UpdateValueDisplay(valueText, param);

        // Set up property change monitoring (simplified)
        // In a real implementation, you'd use proper data binding
        var timer = new System.Timers.Timer(100); // Check every 100ms
        timer.Elapsed += (sender, args) =>
        {
            Avalonia.Threading.Dispatcher.UIThread.InvokeAsync(() =>
                UpdateValueDisplay(valueText, param));
        };
        timer.Start();

        return valueText;
    }

    private void UpdateValueDisplay(TextBlock textBlock, EffectParam param)
    {
        string value = param.Type switch
        {
            "slider" => $"{param.FloatValue:F3}",
            "checkbox" => param.BoolValue ? "ON" : "OFF",
            "color" => param.ColorValue,
            "dropdown" => param.StringValue,
            _ => "N/A"
        };

        textBlock.Text = $"Value: {value}";
    }

    private TextBlock CreateTextBlock(string text)
    {
        return new TextBlock
        {
            Text = text,
            Foreground = new SolidColorBrush(Color.Parse("#FF9800")),
            FontSize = 11,
            Margin = new Thickness(0, 0, 0, 4)
        };
    }

    // Method to update parameters externally
    public void UpdateParameters(string effectName, Dictionary<string, EffectParam> parameters)
    {
        EffectName = effectName;
        Parameters = parameters ?? new Dictionary<string, EffectParam>();
    }
}
