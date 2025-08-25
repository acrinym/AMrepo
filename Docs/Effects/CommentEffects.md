# Comment Effects

The Comment effect is a utility effect that allows users to add comments, notes, and documentation to their effect chains without affecting the visual output. It serves as a non-visual placeholder for organizing and documenting complex effect configurations.

## Effect Overview

The Comment effect works by:
1. Storing user-defined comment text
2. Providing a configuration interface for editing comments
3. Not affecting the visual output of the effect chain
4. Serving as a documentation and organization tool

## C# Implementation

```csharp
using System;
using System.ComponentModel;
using System.Drawing;
using PhoenixVisualizer.Core.Effects.Models;
using PhoenixVisualizer.Core.Models;

namespace PhoenixVisualizer.Core.Effects.Nodes.AvsEffects
{
    public class CommentEffectsNode : BaseEffectNode
    {
        #region Properties
        
        /// <summary>
        /// Whether the effect is enabled (always true for comments)
        /// </summary>
        [Browsable(false)]
        public override bool Enabled 
        { 
            get => true; 
            set { } // Comments are always enabled
        }
        
        /// <summary>
        /// The comment text content
        /// </summary>
        [Description("Comment text to display in the effect chain")]
        [Category("Comment")]
        public string CommentText { get; set; } = "";
        
        /// <summary>
        /// Comment author or creator
        /// </summary>
        [Description("Author of the comment")]
        [Category("Comment")]
        public string Author { get; set; } = "";
        
        /// <summary>
        /// Date when the comment was created
        /// </summary>
        [Description("Date when the comment was created")]
        [Category("Comment")]
        public DateTime CreatedDate { get; set; } = DateTime.Now;
        
        /// <summary>
        /// Date when the comment was last modified
        /// </summary>
        [Description("Date when the comment was last modified")]
        [Category("Comment")]
        public DateTime ModifiedDate { get; set; } = DateTime.Now;
        
        /// <summary>
        /// Comment category or type
        /// </summary>
        [Description("Category or type of the comment")]
        [Category("Comment")]
        public string Category { get; set; } = "General";
        
        /// <summary>
        /// Priority level of the comment (1-5, where 5 is highest)
        /// </summary>
        [Description("Priority level of the comment (1-5)")]
        [Category("Comment")]
        public int Priority { get; set; } = 3;
        
        /// <summary>
        /// Whether the comment is visible in the effect chain
        /// </summary>
        [Description("Whether the comment is visible in the effect chain")]
        [Category("Comment")]
        public bool IsVisible { get; set; } = true;
        
        /// <summary>
        /// Comment color for visual identification
        /// </summary>
        [Description("Color for visual identification of the comment")]
        [Category("Comment")]
        public Color CommentColor { get; set; } = Color.LightBlue;
        
        /// <summary>
        /// Whether to show timestamps in the comment
        /// </summary>
        [Description("Whether to show timestamps in the comment")]
        [Category("Comment")]
        public bool ShowTimestamps { get; set; } = false;
        
        /// <summary>
        /// Maximum comment length
        /// </summary>
        [Browsable(false)]
        public int MaxCommentLength { get; set; } = 1000;
        
        #endregion
        
        #region Private Fields
        
        /// <summary>
        /// Internal comment text storage
        /// </summary>
        private string _internalCommentText = "";
        
        /// <summary>
        /// Whether the comment has been modified
        /// </summary>
        private bool _isModified = false;
        
        #endregion
        
        #region Constructor
        
        public CommentEffectsNode()
        {
            CommentText = "";
            Author = Environment.UserName;
            CreatedDate = DateTime.Now;
            ModifiedDate = DateTime.Now;
            Category = "General";
            Priority = 3;
            IsVisible = true;
            CommentColor = Color.LightBlue;
            ShowTimestamps = false;
            MaxCommentLength = 1000;
        }
        
        #endregion
        
        #region Processing Methods
        
        public override void ProcessFrame(ImageBuffer imageBuffer, AudioFeatures audioFeatures)
        {
            // Comments do not affect visual output
            // This method intentionally does nothing
        }
        
        #endregion
        
        #region Configuration Validation
        
        public override bool ValidateConfiguration()
        {
            if (CommentText == null) return false;
            if (CommentText.Length > MaxCommentLength) return false;
            if (Priority < 1 || Priority > 5) return false;
            if (Author == null || Author.Length > 100) return false;
            if (Category == null || Category.Length > 50) return false;
            
            return true;
        }
        
        #endregion
        
        #region Comment Management Methods
        
        /// <summary>
        /// Set the comment text and update modification timestamp
        /// </summary>
        public void SetComment(string comment)
        {
            if (comment == null) comment = "";
            if (comment.Length > MaxCommentLength)
            {
                comment = comment.Substring(0, MaxCommentLength);
            }
            
            CommentText = comment;
            ModifiedDate = DateTime.Now;
            _isModified = true;
        }
        
        /// <summary>
        /// Append text to the existing comment
        /// </summary>
        public void AppendComment(string additionalText)
        {
            if (string.IsNullOrEmpty(additionalText)) return;
            
            string newComment = CommentText + additionalText;
            if (newComment.Length > MaxCommentLength)
            {
                newComment = newComment.Substring(0, MaxCommentLength);
            }
            
            CommentText = newComment;
            ModifiedDate = DateTime.Now;
            _isModified = true;
        }
        
        /// <summary>
        /// Clear the comment text
        /// </summary>
        public void ClearComment()
        {
            CommentText = "";
            ModifiedDate = DateTime.Now;
            _isModified = true;
        }
        
        /// <summary>
        /// Get the full comment with metadata
        /// </summary>
        public string GetFullComment()
        {
            string fullComment = CommentText;
            
            if (ShowTimestamps)
            {
                fullComment += $"\n\nCreated: {CreatedDate:yyyy-MM-dd HH:mm:ss}";
                if (_isModified)
                {
                    fullComment += $"\nModified: {ModifiedDate:yyyy-MM-dd HH:mm:ss}";
                }
            }
            
            if (!string.IsNullOrEmpty(Author))
            {
                fullComment += $"\nAuthor: {Author}";
            }
            
            if (!string.IsNullOrEmpty(Category))
            {
                fullComment += $"\nCategory: {Category}";
            }
            
            fullComment += $"\nPriority: {Priority}";
            
            return fullComment;
        }
        
        /// <summary>
        /// Get a formatted comment for display
        /// </summary>
        public string GetFormattedComment()
        {
            if (string.IsNullOrEmpty(CommentText))
            {
                return "[No comment]";
            }
            
            string formatted = CommentText;
            
            // Add priority indicator
            string priorityIndicator = new string('!', Priority);
            if (Priority >= 4)
            {
                formatted = $"[{priorityIndicator}] {formatted}";
            }
            
            // Add category prefix if not general
            if (!string.IsNullOrEmpty(Category) && Category != "General")
            {
                formatted = $"[{Category}] {formatted}";
            }
            
            return formatted;
        }
        
        #endregion
        
        #region Utility Methods
        
        /// <summary>
        /// Check if the comment has been modified since creation
        /// </summary>
        public bool HasBeenModified()
        {
            return _isModified;
        }
        
        /// <summary>
        /// Get the age of the comment in days
        /// </summary>
        public int GetCommentAge()
        {
            return (int)(DateTime.Now - CreatedDate).TotalDays;
        }
        
        /// <summary>
        /// Get the time since last modification
        /// </summary>
        public TimeSpan GetTimeSinceModification()
        {
            return DateTime.Now - ModifiedDate;
        }
        
        /// <summary>
        /// Check if the comment is empty
        /// </summary>
        public bool IsEmpty()
        {
            return string.IsNullOrWhiteSpace(CommentText);
        }
        
        /// <summary>
        /// Get the comment length
        /// </summary>
        public int GetCommentLength()
        {
            return CommentText?.Length ?? 0;
        }
        
        /// <summary>
        /// Get the remaining character count
        /// </summary>
        public int GetRemainingCharacters()
        {
            return MaxCommentLength - GetCommentLength();
        }
        
        #endregion
        
        #region Preset Methods
        
        /// <summary>
        /// Set comment as a TODO item
        /// </summary>
        public void SetAsTodo(string todoText)
        {
            Category = "TODO";
            Priority = 4;
            CommentText = todoText;
            CommentColor = Color.Orange;
            ModifiedDate = DateTime.Now;
            _isModified = true;
        }
        
        /// <summary>
        /// Set comment as a note
        /// </summary>
        public void SetAsNote(string noteText)
        {
            Category = "Note";
            Priority = 2;
            CommentText = noteText;
            CommentColor = Color.LightBlue;
            ModifiedDate = DateTime.Now;
            _isModified = true;
        }
        
        /// <summary>
        /// Set comment as a warning
        /// </summary>
        public void SetAsWarning(string warningText)
        {
            Category = "Warning";
            Priority = 5;
            CommentText = warningText;
            CommentColor = Color.Yellow;
            ModifiedDate = DateTime.Now;
            _isModified = true;
        }
        
        /// <summary>
        /// Set comment as an information item
        /// </summary>
        public void SetAsInfo(string infoText)
        {
            Category = "Info";
            Priority = 1;
            CommentText = infoText;
            CommentColor = Color.LightGreen;
            ModifiedDate = DateTime.Now;
            _isModified = true;
        }
        
        /// <summary>
        /// Set comment as a bug report
        /// </summary>
        public void SetAsBug(string bugText)
        {
            Category = "Bug";
            Priority = 5;
            CommentText = bugText;
            CommentColor = Color.Red;
            ModifiedDate = DateTime.Now;
            _isModified = true;
        }
        
        #endregion
        
        #region Search and Filter Methods
        
        /// <summary>
        /// Check if the comment contains specific text
        /// </summary>
        public bool ContainsText(string searchText)
        {
            if (string.IsNullOrEmpty(searchText)) return false;
            return CommentText.IndexOf(searchText, StringComparison.OrdinalIgnoreCase) >= 0;
        }
        
        /// <summary>
        /// Check if the comment matches a specific category
        /// </summary>
        public bool MatchesCategory(string category)
        {
            if (string.IsNullOrEmpty(category)) return false;
            return string.Equals(Category, category, StringComparison.OrdinalIgnoreCase);
        }
        
        /// <summary>
        /// Check if the comment has a specific priority level
        /// </summary>
        public bool HasPriority(int priority)
        {
            return Priority == priority;
        }
        
        /// <summary>
        /// Check if the comment has high priority (4-5)
        /// </summary>
        public bool IsHighPriority()
        {
            return Priority >= 4;
        }
        
        /// <summary>
        /// Check if the comment is recent (within specified days)
        /// </summary>
        public bool IsRecent(int days)
        {
            return GetCommentAge() <= days;
        }
        
        #endregion
        
        #region Export and Import Methods
        
        /// <summary>
        /// Export comment data as a formatted string
        /// </summary>
        public string ExportComment()
        {
            return $"Comment: {CommentText}\n" +
                   $"Author: {Author}\n" +
                   $"Category: {Category}\n" +
                   $"Priority: {Priority}\n" +
                   $"Created: {CreatedDate:yyyy-MM-dd HH:mm:ss}\n" +
                   $"Modified: {ModifiedDate:yyyy-MM-dd HH:mm:ss}\n" +
                   $"Color: {CommentColor.Name}";
        }
        
        /// <summary>
        /// Import comment data from a formatted string
        /// </summary>
        public bool ImportComment(string commentData)
        {
            try
            {
                string[] lines = commentData.Split('\n');
                foreach (string line in lines)
                {
                    if (line.StartsWith("Comment: "))
                    {
                        CommentText = line.Substring(9);
                    }
                    else if (line.StartsWith("Author: "))
                    {
                        Author = line.Substring(8);
                    }
                    else if (line.StartsWith("Category: "))
                    {
                        Category = line.Substring(10);
                    }
                    else if (line.StartsWith("Priority: "))
                    {
                        if (int.TryParse(line.Substring(10), out int priority))
                        {
                            Priority = priority;
                        }
                    }
                }
                
                ModifiedDate = DateTime.Now;
                _isModified = true;
                return true;
            }
            catch
            {
                return false;
            }
        }
        
        #endregion
    }
}
```

## Effect Properties

### Core Properties
- **CommentText**: The main comment text content
- **Author**: Author or creator of the comment
- **CreatedDate**: Date when the comment was created
- **ModifiedDate**: Date when the comment was last modified
- **Category**: Category or type of the comment

### Display Properties
- **IsVisible**: Whether the comment is visible in the effect chain
- **CommentColor**: Color for visual identification of the comment
- **ShowTimestamps**: Whether to show timestamps in the comment
- **Priority**: Priority level of the comment (1-5, where 5 is highest)

### Internal Properties
- **MaxCommentLength**: Maximum allowed comment length
- **IsModified**: Whether the comment has been modified since creation

## Comment Categories

The effect supports various comment categories for organization:

- **General**: Default category for general comments
- **TODO**: Items that need to be completed
- **Note**: Informational notes
- **Warning**: Important warnings or cautions
- **Info**: General information
- **Bug**: Bug reports or issues

## Priority System

Comments use a 5-level priority system:

- **Priority 1**: Low priority, informational
- **Priority 2**: Low-medium priority
- **Priority 3**: Medium priority (default)
- **Priority 4**: High priority
- **Priority 5**: Critical priority

## Comment Management

### Text Operations
- **SetComment**: Set the complete comment text
- **AppendComment**: Add text to existing comment
- **ClearComment**: Remove all comment text
- **GetFullComment**: Get comment with all metadata
- **GetFormattedComment**: Get formatted comment for display

### Metadata Operations
- **HasBeenModified**: Check if comment was modified
- **GetCommentAge**: Get comment age in days
- **GetTimeSinceModification**: Get time since last change
- **IsEmpty**: Check if comment is empty
- **GetCommentLength**: Get current comment length

## Preset Comment Types

### Quick Setup Methods
- **SetAsTodo**: Configure as a TODO item with high priority
- **SetAsNote**: Configure as a general note
- **SetAsWarning**: Configure as a warning with critical priority
- **SetAsInfo**: Configure as informational content
- **SetAsBug**: Configure as a bug report with critical priority

## Search and Filtering

### Text Search
- **ContainsText**: Check if comment contains specific text
- **MatchesCategory**: Check if comment matches a category
- **HasPriority**: Check if comment has specific priority
- **IsHighPriority**: Check if comment is high priority (4-5)
- **IsRecent**: Check if comment was created recently

## Export and Import

### Data Persistence
- **ExportComment**: Export comment data as formatted string
- **ImportComment**: Import comment data from formatted string

## Use Cases

- **Effect Chain Documentation**: Document complex effect configurations
- **Project Notes**: Keep notes about visualization projects
- **Bug Tracking**: Track issues and problems in effect chains
- **Feature Planning**: Plan future enhancements and features
- **Team Collaboration**: Share information with team members
- **Troubleshooting**: Document solutions to common problems

## Visual Integration

### Effect Chain Display
Comments appear in the effect chain with:
- Color-coded visual identification
- Priority indicators (exclamation marks)
- Category prefixes
- Timestamp information (optional)

### Non-Visual Nature
Comments do not affect the visual output of the effect chain, making them perfect for:
- Documentation purposes
- Organization and categorization
- Project management
- Quality assurance tracking

## Performance Characteristics

- **Zero Processing Overhead**: No visual processing or rendering
- **Minimal Memory Usage**: Only stores text and metadata
- **Instant Execution**: No frame processing delays
- **Efficient Storage**: Optimized string handling and metadata storage
