# health_analysis

A set of tools for analyzing personal health data using lightweight daily tracking methods. Originally developed to support research with Dr. Sameer Dhalla at Johns Hopkins Division of Gastroenterology and Hepatology.

## Overview

This project implements a lightweight health tracking system that monitors daily metrics and analyzes their correlations with treatments. The approach focuses on metrics that are easy to track consistently to ensure long-term compliance.

*A note on tracking bowel movements: While it might seem unusual to track this particular metric, as a scientist investigating gastrointestinal health, you have to follow the data wherever it leads! In fact, this detailed tracking proved invaluable - it revealed unexpected medication effects that weren't initially considered by healthcare providers. The regression analysis showed that Claritin-D had a significant adverse effect (coefficient: 1.237, p=0.001) on abnormal bowel movements in the 3-day window, while Nexium showed significant improvement (coefficient: -0.702, p=0.002). 

One of the most surprising findings was the strong positive effect of Nexium. While primarily prescribed as a proton pump inhibitor for acid reduction, our analysis showed it had significant benefits beyond its intended use. Further research revealed this may be due to Nexium's documented anti-inflammatory properties - proton pump inhibitors have been shown to reduce inflammatory cytokines and affect neutrophil function, suggesting a broader therapeutic role than just acid suppression. This finding demonstrates how systematic data collection can uncover unexpected treatment benefits and point to underlying mechanisms.

When doctors suggested reducing Librax to address symptoms, the regression analysis showed this would likely worsen outcomes (Librax showed positive correlation with improved HQI, coefficient: 0.066, p=0.028) - a prediction that proved correct when tested. The data tracking achieved >99% compliance over the study period, demonstrating that even "awkward" metrics can be tracked consistently when the methodology is properly streamlined. Sometimes the most important insights come from tracking metrics we don't normally discuss in polite conversation, but the data speaks for itself: this rigorous tracking enabled evidence-based decisions that ultimately led to better treatment outcomes.*

## Tracked Metrics

- **Bowel Movements (BMs)**
  - Time of occurrence
  - Bristol Stool Scale classification
  - Tracked via Android app "Bowel Move"

- **Health Quality Index (HQI)**
  - Scale: 1-4
  - Tracked AM/PM daily
  - Definitions:
    1. Requires urgent medical attention (e.g., ED visit)
    2. Prevents completing daily activities
    3. Symptoms present but manageable
    4. No symptoms present

- **Other Metrics**
  - Medications (type and dosage)
  - Body weight
  - Cardiovascular exercise duration

## Analysis Tools

`health_analysis.py` is the main analysis script that:
- Processes raw tracking data
- Performs regression analysis
- Evaluates treatment efficacy
- Generates visualization plots
- Outputs results to the `output` directory

## Data Collection

- BM data collected through Android app
- Other metrics tracked via Google Sheets
- High compliance rate (>99% in study)
- Minimal daily time investment

## Statistical Analysis

- Ordinary least squares regression
- Analysis of treatment effects on:
  - HQI means (3-day and 7-day windows)
  - Abnormal event frequency
  - Symptom patterns

## Usage

1. Collect data using recommended tools
2. Run analysis:
```bash
python health_analysis.py
```
3. Review generated plots in `output` directory

## Results

The tools have successfully:
- Identified effective treatments
- Quantified medication impacts
- Tracked improvement patterns
- Supported evidence-based treatment decisions

## Publication

This work formed the basis of research conducted with Johns Hopkins Medicine on lightweight methodologies for tracking treatment efficacy.

## Contact

Email: isaac.gerg@gergltd.com
