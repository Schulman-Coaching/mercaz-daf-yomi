# Create a comparison table of different YouTube transcript extraction methods
import pandas as pd

# Create comparison data
comparison_data = {
    'Method': [
        'YouTube Native (Manual)',
        'youtube-transcript-api (Python)',
        'YouTube-Transcript.io (Web)',
        'Tactiq.io (Web)',
        'Browser Extensions',
        'Selenium-based Tools',
        'YouTube Data API v3',
        'Third-party APIs'
    ],
    'Ease of Use': [
        'Very Easy',
        'Moderate',
        'Very Easy',
        'Easy',
        'Easy',
        'Moderate',
        'Hard',
        'Easy'
    ],
    'Bulk Processing': [
        'No',
        'Yes',
        'Yes (Limited)',
        'No',
        'No',
        'Yes',
        'Yes',
        'Yes'
    ],
    'Cost': [
        'Free',
        'Free',
        'Free/Paid',
        'Free/Paid',
        'Free',
        'Free',
        'Free (with limits)',
        'Paid'
    ],
    'Rate Limits': [
        'Manual only',
        'Moderate',
        'High',
        'Moderate',
        'Low',
        'Low',
        'High',
        'Variable'
    ],
    'Accuracy': [
        'High',
        'High',
        'High',
        'High',
        'High',
        'High',
        'High',
        'High'
    ],
    'Legal Compliance': [
        'Full',
        'Good',
        'Good',
        'Good',
        'Variable',
        'Variable',
        'Full',
        'Variable'
    ],
    'Technical Skills Required': [
        'None',
        'Python',
        'None',
        'None',
        'Basic',
        'Advanced',
        'Advanced',
        'Basic'
    ],
    'Best For': [
        'Single videos',
        'Bulk processing',
        'Moderate bulk',
        'Single videos',
        'Occasional use',
        'Large scale',
        'Enterprise use',
        'Commercial use'
    ]
}

# Create DataFrame
df = pd.DataFrame(comparison_data)

# Display the comparison table
print("YouTube Transcript Extraction Methods Comparison")
print("=" * 70)
print(df.to_string(index=False))

# Save to CSV
df.to_csv('transcript_methods_comparison.csv', index=False)
print("\nComparison saved to: transcript_methods_comparison.csv")

# Create a detailed pros and cons analysis
pros_cons_data = {
    'Method': [
        'YouTube Native (Manual)',
        'youtube-transcript-api (Python)',
        'YouTube-Transcript.io (Web)',
        'Browser Extensions',
        'Selenium-based Tools'
    ],
    'Pros': [
        'Free; No technical skills; Fully legal; Direct from source',
        'Free; Bulk processing; Programmatic control; Good documentation',
        'Easy to use; Some bulk features; No installation needed',
        'Easy installation; Works in browser; No external sites',
        'Full automation; Can handle any video; Bypass some restrictions'
    ],
    'Cons': [
        'Time-consuming; No bulk processing; Manual copy-paste required',
        'Requires Python knowledge; Rate limiting; May break with YouTube changes',
        'Rate limits; Paid plans for bulk; Privacy concerns with third-party',
        'Limited bulk processing; Depends on extension quality; Privacy concerns',
        'Complex setup; May violate ToS; Requires technical expertise; Unreliable'
    ],
    'Recommended Use Case': [
        'Educational research (1-5 videos)',
        'Academic projects (10-50 videos)',
        'Content creators (5-25 videos)',
        'Personal use (1-10 videos)',
        'Large-scale research (100+ videos) - Use with caution'
    ]
}

pros_cons_df = pd.DataFrame(pros_cons_data)
print("\n\nDetailed Pros and Cons Analysis")
print("=" * 50)
for index, row in pros_cons_df.iterrows():
    print(f"\n{row['Method']}")
    print(f"Pros: {row['Pros']}")
    print(f"Cons: {row['Cons']}")
    print(f"Best for: {row['Recommended Use Case']}")

# Save pros and cons to CSV
pros_cons_df.to_csv('transcript_methods_pros_cons.csv', index=False)
print("\nPros and cons analysis saved to: transcript_methods_pros_cons.csv")