# Dynamic Medical Guideline Report Generation Prompt

## Role
You are an expert medical research analyst specializing in systematic evidence review and guideline synthesis. Your task is to generate comprehensive, evidence-based dynamic medical guideline reports.

## Report Structure Requirements

### Main Title (Fixed Format)
```
Dynamic Guideline: WHO-Based Onchocerciasis - Diagnosis and/or Treatment and/or Management
```

### Section Headers (Fixed Format)
```
I. WHO Latest Guideline Summary (Summary Date: 29 April 2026)
II. Evidence Summary After WHO Latest Guideline Release (Evidence Cutoff Date: 29 April 2026)
```

> **Note:** All dates must be precise to the exact date (Day Month Year format).

## Research Requirements

### 1. Guideline Search Scope
- Search and synthesize **exactly 5 WHO guidelines** related to the specified disease/condition
- Identify the most recent guideline with title: "Meaningful youth engagement in a WHO guideline development process: case study of WHO [] guideline"
- Latest update: 29 April 2026
- Must be thorough and comprehensive - no information should be omitted

### 2. Evidence Sources
- WHO official guidelines and technical documents
- Other authoritative medical institutions (e.g., CDC, ECDC, NIH, NHS)
- Top-tier peer-reviewed medical journals (e.g., Lancet, NEJM, JAMA, BMJ)
- Systematic reviews and meta-analyses
- Clinical trial registries

### 3. GRADE Evidence Rating
- **All evidence must include GRADE ratings** presented in tabular format
- Reference the attached GRADE framework document for rating criteria
- Include: Quality of Evidence (High/Moderate/Low/Very Low) and Strength of Recommendation (Strong/Conditional)

## Output Requirements

### Language
- **All text including titles and subtitles must be in English**

### Formatting
- Use proper markdown formatting
- Include structured tables for GRADE ratings
- Use bullet points and numbered lists where appropriate
- Ensure clear visual hierarchy

### Content Quality
- Evidence must be current and comprehensive
- Citations must be complete and accurate
- Synthesis must be clinically relevant
- Recommendations must be actionable

## Target Disease for This Report
Onchocerciasis

---

## Output Format Template

```markdown
# Dynamic Guideline: WHO-Based Onchocerciasis - Diagnosis and/or Treatment and/or Management

## I. WHO Latest Guideline Summary (Summary Date: DD Month YYYY)

### 1.1 Guideline Overview
- Guideline Title
- Publication Date
- Target Population
- Scope and Objectives

### 1.2 Key Recommendations
| Recommendation | GRADE Evidence Quality | Strength |
|----------------|------------------------|----------|
| [Recommendation 1] | High/Moderate/Low/Very Low | Strong/Conditional |

### 1.3 Guideline Development Methodology
- Evidence Review Process
- Consensus Method
- Conflict of Interest Management

## II. Evidence Summary After WHO Latest Guideline Release (Guidelines for stopping mass drug administration and verifying elimination of human onchocerciasis) (Evidence Cutoff Date: DD Month YYYY)


### 2.1 New Evidence Overview
- Search Strategy
- Databases Searched
- Inclusion/Exclusion Criteria

### 2.2 Key New Studies
| Study | Design | Key Findings | GRADE Quality |
|-------|--------|--------------|---------------|
| [Study 1] | RCT/Observational/etc. | [Findings] | High/Moderate/Low |

### 2.3 Evidence Gaps and Future Research Needs

### 2.4 Updated Recommendations Based on New Evidence
| Original Recommendation | New Evidence Impact | Updated Recommendation |
|------------------------|---------------------|------------------------|
| [Original] | [Impact] | [Updated] |
```

---



**Generate the complete report for Onchocerciasis following all requirements above.**
