# ANPTOP - Reporting Engine Documentation

## Table of Contents
1. [Overview](#overview)
2. [Report Types](#report-types)
3. [Report Templates](#report-templates)
4. [Generation Workflow](#generation-workflow)
5. [Pandoc Integration](#pandoc-integration)
6. [HTML Templates](#html-templates)
7. [PDF Generation](#pdf-generation)
8. [Sample Reports](#sample-reports)

---

## 1. Overview

The ANPTOP Reporting Engine generates comprehensive penetration test reports in both HTML and PDF formats, following industry standards for executive and technical reporting.

### 1.1 Architecture
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Reporting Engine Architecture                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    Report Generation Controller                       │   │
│  │                                                                      │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │ Executive │  │ Technical│  │  NIST    │  │  PCI     │           │   │
│  │  │  Report  │  │  Report  │  │   800-115│  │   DSS    │           │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘           │   │
│  │       │             │             │             │                   │   │
│  └───────┼─────────────┼─────────────┼─────────────┼───────────────────┘   │
│          │             │             │             │                        │
│          ▼             ▼             ▼             ▼                        │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      Markdown Generator                                │   │
│  │                                                                      │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │  Section │  │   Data   │  │   Chart  │  │ Template │           │   │
│  │  │ Builder  │  │  Mapper  │  │ Generator│  │ Engine   │           │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                     │                                        │
│                                     ▼                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    Format Converters                                   │   │
│  │                                                                      │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │   │
│  │  │  Pandoc (MD→HTML)│  │  wkhtmltopdf   │  │   Custom        │    │   │
│  │  │                 │  │  (HTML→PDF)     │  │   Formatters    │    │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Report Generation Flow
```python
def generate_report(engagement_id: str, report_type: str, format: str):
    """
    Generate a comprehensive penetration test report
    """
    # 1. Fetch engagement data
    data = fetch_engagement_data(engagement_id)
    
    # 2. Generate markdown content
    markdown = markdown_generator.generate(
        template=report_type,
        data=data
    )
    
    # 3. Convert to requested format
    if format == 'html':
        output = pandoc.convert(markdown, from='markdown', to='html5')
    elif format == 'pdf':
        html = pandoc.convert(markdown, from='markdown', to='html5')
        output = wkhtmltopdf.convert(html)
    
    # 4. Add branding and styling
    output = apply_branding(output, data.client_name)
    
    # 5. Add digital signature
    output = sign_report(output)
    
    return output
```

---

## 2. Report Types

### 2.1 Executive Report
Designed for management and non-technical stakeholders.

**Contents:**
- Executive Summary
- Scope & Objectives
- Key Findings Overview
- Risk Summary
- Recommendations Summary
- Compliance Status

### 2.2 Technical Report
Designed for technical teams and security engineers.

**Contents:**
- Technical Summary
- Detailed Findings
- Proof of Concepts
- Evidence & Screenshots
- Remediation Steps
- Technical Recommendations

### 2.3 NIST SP 800-115 Report
Compliance-focused report aligned with NIST methodology.

**Contents:**
- NIST SP 800-115 Alignment
- Testing Methodology
- Reconnaissance Results
- Scanning Results
- Exploitation Results
- Post-Exploitation Results

### 2.4 PCI-DSS Report
Payment card industry compliance report.

**Contents:**
- PCI-DSS Requirements Tested
- Findings by Requirement
- Compensating Controls
- Remediation Plan

---

## 3. Report Templates

### 3.1 Executive Report Template

```markdown
---
title: "{{engagement.name}} - Executive Security Assessment"
author: "ANPTOP Platform"
date: "{{report.generation_date}}"
geometry: "margin=1in"
lang: en
---

# Executive Summary

## Overview
{{ engagement.description | default("Security assessment conducted on " + engagement.client_name) }}

## Scope
- **Assessment Type:** {{ engagement.type }}
- **Targets Evaluated:** {{ metrics.hosts_scanned }} hosts
- **Testing Period:** {{ engagement.start_date }} to {{ engagement.end_date }}
- **Methodology:** {{ engagement.methodology }}

## Key Findings Summary

| Risk Level | Count |
|------------|-------|
| Critical | {{ metrics.critical_count }} |
| High | {{ metrics.high_count }} |
| Medium | {{ metrics.medium_count }} |
| Low | {{ metrics.low_count }} |

## Overall Risk Assessment

!!! note "Risk Rating: {{ metrics.overall_risk_score }}/10"

{{ executive_summary.risk_overview }}

# Scope of Work

## Objectives
{{ engagement.objectives | default("Conduct comprehensive security assessment to identify vulnerabilities and provide remediation guidance.") }}

## Methodology
{{ engagement.methodology | default("Black box testing methodology following industry standards.") }}

## Limitations
{{ engagement.limitations | default("No limitations reported.") }}

# Executive Findings

## Critical Findings

{% for finding in findings.critical %}
### {{ finding.title }}
**Severity:** Critical (CVSS: {{ finding.cvss_score }})

{{ finding.summary }}

**Business Impact:** {{ finding.business_impact }}

**Recommendation:** {{ finding.recommendation }}
{% endfor %}

## High Findings

{% for finding in findings.high %}
### {{ finding.title }}
**Severity:** High (CVSS: {{ finding.cvss_score }})

{{ finding.summary }}

**Recommendation:** {{ finding.recommendation }}
{% endfor %}

# Recommendations Summary

## Immediate Actions Required

1. **Critical Vulnerabilities**
   - {{ findings.critical | length }} critical issues require immediate attention
   - Estimated remediation time: {{ remediation.critical_time }}
   
2. **High Priority Issues**
   - {{ findings.high | length }} high-severity issues to address
   - Estimated remediation time: {{ remediation.high_time }}

## Strategic Recommendations

{{ recommendations.strategic }}

# Compliance Status

## NIST SP 800-115 Alignment

| Phase | Status | Notes |
|-------|--------|-------|
| Planning | ✅ Complete | ROE documented and approved |
| Reconnaissance | ✅ Complete | Passive and active reconnaissance conducted |
| Scanning | ✅ Complete | Port and vulnerability scanning performed |
| Exploitation | ⚠️ Controlled | Approved exploitation with documentation |
| Post-Exploitation | ⚠️ Controlled | Session management documented |
| Reporting | 🔄 In Progress | Report generation in progress |

# Conclusion

{{ executive_summary.conclusion }}

---

**Report Generated by:** ANPTOP - Automated Network Penetration Testing Orchestration Platform  
**Report ID:** {{ report.id }}  
**Classification:** {{ engagement.classification | default("Confidential") }}
```

### 3.2 Technical Report Template

```markdown
---
title: "{{engagement.name}} - Technical Security Assessment"
author: "ANPTOP Platform"
date: "{{report.generation_date}}"
geometry: "margin=0.75in"
lang: en
---

# Table of Contents
{:.toc}

1. [Introduction](#1-introduction)
2. [Scope & Methodology](#2-scope--methodology)
3. [Network Infrastructure](#3-network-infrastructure)
4. [Vulnerability Findings](#4-vulnerability-findings)
5. [Exploitation Results](#5-exploitation-results)
6. [Post-Exploitation Activities](#6-post-exploitation-activities)
7. [Evidence Appendix](#7-evidence-appendix)
8. [Remediation](#8-remediation)

---

# 1. Introduction

## 1.1 Purpose
This technical report documents the findings from the security assessment conducted on {{ engagement.client_name }}'s network infrastructure.

## 1.2 Assessment Scope
- **Total Hosts Scanned:** {{ metrics.hosts_scanned }}
- **Total Services Identified:** {{ metrics.services_count }}
- **Total Vulnerabilities Found:** {{ metrics.total_vulnerabilities }}
- **Exploitation Attempts:** {{ metrics.exploitation_attempts }}

## 1.3 Timeline
- **Start Date:** {{ engagement.start_date }}
- **End Date:** {{ engagement.end_date }}
- **Total Duration:** {{ engagement.duration_days }} days

---

# 2. Scope & Methodology

## 2.1 Scope Definition

### In-Scope Assets

| Asset Type | Count | Examples |
|------------|-------|----------|
{% for asset_type, count in scope.in_scope %}
| {{ asset_type }} | {{ count }} | {{ scope.examples[asset_type] }} |
{% endfor %}

### Out-of-Scope Assets
{% for exclusion in scope.exclusions %}
- {{ exclusion }}
{% endfor %}

## 2.2 Testing Methodology

### Reconnaissance
- Passive reconnaissance using OSINT techniques
- Active reconnaissance with DNS enumeration
- Social media and public information gathering

### Scanning & Enumeration
```
Port Scanning:
- Tool: Nmap, Masscan
- Range: 1-65535 (TCP)
- Techniques: SYN scan, Service version detection
```

### Vulnerability Assessment
```
Vulnerability Scanning:
- Tool: OpenVAS
- Scan Types: Full and Fast, Host Discovery
- Credentials: Unauthenticated and authenticated scans
```

### Exploitation
```
Exploitation Framework:
- Tool: Metasploit Pro
- Payloads: Staged and unstaged
- Sessions: Meterpreter, Shell
```

## 2.3 Rules of Engagement
{{ engagement.roe_summary }}

---

# 3. Network Infrastructure

## 3.1 Host Summary

| Host IP | Hostname | OS | Open Ports | Risk Score |
|---------|----------|-----|-----------|------------|
{% for host in hosts %}
| {{ host.ip }} | {{ host.hostname | default("-") }} | {{ host.os_family | default("Unknown") }} | {{ host.port_count }} | {{ host.risk_score }} |
{% endfor %}

## 3.2 Service Distribution

### Services by Port Range

| Port Range | Count | Examples |
|------------|-------|----------|
| Well Known (1-1023) | {{ services.well_known_count }} | HTTP, HTTPS, SSH |
| Registered (1024-49151) | {{ services.registered_count }} | MySQL, PostgreSQL |
| Dynamic (49152-65535) | {{ services.dynamic_count }} | Ephemeral ports |

---

# 4. Vulnerability Findings

## 4.1 Vulnerability Overview

!!! note "Total Vulnerabilities: {{ metrics.total_vulnerabilities }}"

### By Severity

| Severity | Count | Remediated | Open |
|----------|-------|------------|------|
| Critical | {{ vuln.critical.count }} | {{ vuln.critical.remediated }} | {{ vuln.critical.open }} |
| High | {{ vuln.high.count }} | {{ vuln.high.remediated }} | {{ vuln.high.open }} |
| Medium | {{ vuln.medium.count }} | {{ vuln.medium.remediated }} | {{ vuln.medium.open }} |
| Low | {{ vuln.low.count }} | {{ vuln.low.remediated }} | {{ vuln.low.open }} |
| Informational | {{ vuln.info.count }} | {{ vuln.info.remediated }} | {{ vuln.info.open }} |

## 4.2 Detailed Findings

### Finding #{{ finding.index }}: {{ finding.title }}
**CVE:** {{ finding.cves | default("N/A") }}  
**CVSS v3.1 Score:** {{ finding.cvss_score }} ({{ finding.cvss_severity }})  
**CVSS Vector:** `{{ finding.cvss_vector }}`  
**Status:** {{ finding.status }}  

#### Description
{{ finding.description }}

#### Technical Details
- **Affected Component:** {{ finding.component }}
- **Version(s) Affected:** {{ finding.versions }}
- **Attack Vector:** {{ finding.attack_vector }}
- **Attack Complexity:** {{ finding.attack_complexity }}
- **Privileges Required:** {{ finding.privileges_required }}
- **User Interaction:** {{ finding.user_interaction }}

#### Proof of Concept
```{{ finding.poc_language }}
{{ finding.poc_code }}
```

#### Evidence
{% for evidence in finding.evidence %}
![Evidence {{ loop.index }}]({{ evidence.path | relative_path }})
{% endfor %}

#### Remediation
**Solution:** {{ finding.solution }}

**Patch Information:**
- Vendor: {{ finding.vendor_patch }}
- Patch ID: {{ finding.patch_id }}
- Download URL: {{ finding.patch_url }}

**Workaround:** {{ finding.workaround | default("No workaround available") }}

#### References
{% for ref in finding.references %}
- {{ ref }}
{% endfor %}

---

# 5. Exploitation Results

## 5.1 Exploitation Summary

| Metric | Value |
|--------|-------|
| Exploitation Attempts | {{ exploit.attempts }} |
| Successful Exploits | {{ exploit.successful }} |
| Failed Exploits | {{ exploit.failed }} |
| Sessions Established | {{ exploit.sessions }} |

## 5.2 Successful Exploits

### Exploit: {{ exploit.name }}
**Target:** {{ exploit.target_ip }}:{{ exploit.target_port }}  
**Module:** {{ exploit.module }}  
**Session Type:** {{ exploit.session_type }}  
**Session ID:** {{ exploit.session_id }}  

#### Session Details
```
{{ exploit.session_output }}
```

#### Post-Exploitation Actions
{% for action in exploit.post_ex_actions %}
- {{ action.name }}: {{ action.result }}
{% endfor %}

---

# 6. Post-Exploitation Activities

## 6.1 Credential Harvesting

### Credentials Obtained

| Type | Count | Sensitive |
|------|-------|-----------|
| Passwords | {{ cred.passwords }} | High |
| Hashes | {{ cred.hashes }} | High |
| Tokens | {{ cred.tokens }} | Critical |
| Keys | {{ cred.keys }} | Critical |

## 6.2 Lateral Movement

### Movement Path
```
{{ lateral_movement.path }}
```

### Systems Accessed
{% for system in lateral_movement.systems %}
- {{ system.hostname }} ({{ system.ip }})
{% endfor %}

---

# 7. Evidence Appendix

## 7.1 Evidence Index

| ID | Type | Description | Host | Timestamp |
|----|------|-------------|------|-----------|
{% for evidence in evidence_list %}
| {{ evidence.id }} | {{ evidence.type }} | {{ evidence.description }} | {{ evidence.host }} | {{ evidence.timestamp }} |
{% endfor %}

## 7.2 Chain of Custody

All evidence collected during this assessment has been logged with:
- SHA-256 hash verification
- Collection timestamp
- Collector identification
- Storage location

---

# 8. Remediation

## 8.1 Priority Matrix

| Priority | Vulnerabilities | Recommended Timeline |
|----------|-----------------|----------------------|
| P1 (Critical) | {{ remediation.p1_count }} | 24-48 hours |
| P2 (High) | {{ remediation.p2_count }} | 1-2 weeks |
| P3 (Medium) | {{ remediation.p3_count }} | 1 month |
| P4 (Low) | {{ remediation.p4_count }} | 3 months |

## 8.2 Remediation Plan

### Critical & High Priority

{% for finding in findings.critical_high %}
#### {{ finding.title }}

**Actions Required:**
1. {{ finding.remediation_step_1 }}
2. {{ finding.remediation_step_2 }}
3. {{ finding.remediation_step_3 }}

**Verification:**
- Run verification scan: `{{ finding.verification_command }}`
- Expected result: {{ finding.expected_result }}

**Estimated Effort:** {{ finding.estimated_effort }}
{% endfor %}

---

# Appendix A: MITRE ATT&CK Mapping

| Technique ID | Technique Name | Tactic | Findings |
|--------------|----------------|--------|----------|
{% for mapping in mitre_mapping %}
| {{ mapping.technique_id }} | {{ mapping.technique_name }} | {{ mapping.tactic }} | {{ mapping.findings }} |
{% endfor %}

---

# Appendix B: Nmap Scan Results

```nmap
{{ nmap_output }}
```

---

# Appendix C: Tool Versions

| Tool | Version |
|------|---------|
| Nmap | {{ tools.nmap_version }} |
| OpenVAS | {{ tools.openvas_version }} |
| Metasploit | {{ tools.metasploit_version }} |
| ANPTOP | {{ tools.anptop_version }} |

---

**Report Generated:** {{ report.generation_date }}  
**Generated By:** ANPTOP Platform v{{ report.version }}  
**Report ID:** {{ report.id }}  
**Document Classification:** {{ engagement.classification | default("CONFIDENTIAL") }}
```

---

## 4. Report Generation Service

### 4.1 Python Implementation
```python
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json
import markdown
from jinja2 import Environment, FileSystemLoader
import yaml

class ReportGenerator:
    def __init__(self, template_dir: str = "templates/reports"):
        self.template_dir = Path(template_dir)
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            extensions=['markdown.extensions.fenced_code', 'markdown.extensions.tables']
        )
    
    def generate_executive_report(
        self,
        engagement_id: str,
        output_format: str = 'html'
    ) -> bytes:
        """
        Generate executive summary report
        """
        # Fetch data
        data = self._fetch_engagement_data(engagement_id)
        
        # Render markdown
        template = self.env.get_template('executive_report.md')
        markdown_content = template.render(
            engagement=data['engagement'],
            metrics=data['metrics'],
            findings=self._categorize_findings(data['vulnerabilities']),
            recommendations=data['recommendations'],
            report={
                'id': engagement_id,
                'generation_date': datetime.utcnow().strftime('%Y-%m-%d'),
                'version': '1.0'
            }
        )
        
        # Convert to output format
        if output_format == 'html':
            return self._convert_to_html(markdown_content)
        elif output_format == 'pdf':
            return self._convert_to_pdf(markdown_content)
        else:
            return markdown_content.encode('utf-8')
    
    def generate_technical_report(
        self,
        engagement_id: str,
        output_format: str = 'pdf'
    ) -> bytes:
        """
        Generate detailed technical report
        """
        data = self._fetch_engagement_data(engagement_id)
        
        # Prepare detailed data
        detailed_data = self._prepare_technical_data(data)
        
        template = self.env.get_template('technical_report.md')
        markdown_content = template.render(
            **detailed_data,
            report={
                'id': engagement_id,
                'generation_date': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
                'version': '1.0'
            },
            mitre_mapping=self._generate_mitre_mapping(data['exploits'])
        )
        
        if output_format == 'pdf':
            return self._convert_to_pdf(markdown_content)
        else:
            return markdown_content.encode('utf-8')
    
    def _convert_to_html(self, markdown_content: str) -> bytes:
        """
        Convert markdown to HTML using Pandoc
        """
        import pypandoc
        
        html = pypandoc.convert_text(
            markdown_content,
            format='markdown',
            to='html5',
            outputfile=None,
            extra_args=[
                '--standalone',
                '--template=templates/report_template.html',
                '--variable=lang:en',
                '--metadata=title:',
            ]
        )
        
        # Add styling
        styled_html = self._apply_branding(html)
        
        return styled_html.encode('utf-8')
    
    def _convert_to_pdf(self, markdown_content: str) -> bytes:
        """
        Convert markdown to PDF using Pandoc and wkhtmltopdf
        """
        import pypandoc
        
        # Convert to HTML first
        html = pypandoc.convert_text(
            markdown_content,
            format='markdown',
            to='html5',
            outputfile=None,
            extra_args=[
                '--standalone',
                '--template=templates/report_template.html',
                '--variable=lang:en',
            ]
        )
        
        # Add styling
        styled_html = self._apply_branding(html)
        
        # Convert to PDF
        pdf = pypandoc.convert_text(
            styled_html,
            format='html',
            to='pdf',
            outputfile=None,
            extra_args=[
                '--pdf-engine=wkhtmltopdf',
                '--variable=margin-left:1in',
                '--variable=margin-right:1in',
                '--variable=margin-top:1in',
                '--variable=margin-bottom:1in',
            ]
        )
        
        return pdf
    
    def _apply_branding(self, html_content: str) -> str:
        """
        Apply client branding and styling
        """
        branding = {
            'primary_color': '#1d4ed8',
            'secondary_color': '#3b82f6',
            'logo_url': '/static/logos/anptop_logo.png',
            'company_name': 'ANPTOP',
        }
        
        # Inject CSS
        styled_html = html_content.replace(
            '{{ styles }}',
            f"""
            <style>
                :root {{
                    --primary-color: {branding['primary_color']};
                    --secondary-color: {branding['secondary_color']};
                }}
                .header {{ background-color: {branding['primary_color']}; }}
                .footer {{ border-top: 2px solid {branding['primary_color']}; }}
            </style>
            """
        )
        
        return styled_html
    
    def _fetch_engagement_data(self, engagement_id: str) -> Dict[str, Any]:
        """
        Fetch all engagement data for reporting
        """
        # This would call the backend API
        return {
            'engagement': self._get_engagement(engagement_id),
            'hosts': self._get_hosts(engagement_id),
            'vulnerabilities': self._get_vulnerabilities(engagement_id),
            'exploits': self._get_exploits(engagement_id),
            'evidence': self._get_evidence(engagement_id),
        }
    
    def _categorize_findings(self, vulnerabilities: list) -> Dict[str, list]:
        """
        Categorize vulnerabilities by severity
        """
        categorized = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': [],
            'informational': []
        }
        
        for vuln in vulnerabilities:
            severity = vuln.get('risk_rating', 'low').lower()
            if severity in categorized:
                categorized[severity].append(vuln)
        
        return categorized
```

---

## 5. Pandoc Integration

### 5.1 Pandoc Filters
```python
# pandoc_filters.py
from panflute import (
    Element, Para, Span, Str, Code, CodeBlock,
    Header, Link, Image, Table, TableCell, TableRow
)

def emphasis_filter(elem: Element):
    """
    Filter to handle emphasis and special formatting
    """
    if isinstance(elem, Para):
        # Handle warning boxes
        if elem.content and isinstance(elem.content[0], Span):
            if 'class' in elem.content[0].attributes:
                if 'warning' in elem.content[0].attributes['class']:
                    return create_warning_box(elem)
    
    return None

def create_warning_box(elem: Para) -> Table:
    """
    Create a warning table box
    """
    # Implementation for warning box
    pass

def code_highlight_filter(elem: CodeBlock):
    """
    Syntax highlighting for code blocks
    """
    # Get language
    language = elem.classes[0] if elem.classes else 'text'
    
    return {
        'type': 'code',
        'text': elem.text,
        'language': language,
    }

def table_filter(elem: Table):
    """
    Custom table formatting
    """
    # Format tables with proper styling
    return {
        'type': 'styled_table',
        'data': elem
    }

def main(doc=None):
    """
    Run all filters
    """
    return doc.filter(
        emphasis_filter,
        code_highlight_filter,
        table_filter
    )

if __name__ == "__main__":
    main()
```

### 5.2 Pandoc Custom Writer
```python
# custom_writer.py
import panflute as pf

def writer(doc: pf.Doc, output, **kwargs):
    """
    Custom Pandoc writer for HTML5 output
    """
    output.write('<!DOCTYPE html>\n')
    output.write('<html lang="en">\n')
    output.write('<head>\n')
    output.write('<meta charset="UTF-8">\n')
    output.write('<meta name="viewport" content="width=device-width, initial-scale=1.0">\n')
    output.write(f'<title>{pf.stringify(doc.meta.get("title", "Security Report"))}</title>\n')
    
    # Add CSS
    output.write(generate_css())
    
    output.write('</head>\n')
    output.write('<body>\n')
    
    # Write content
    pf.dump(doc, output)
    
    output.write('</body>\n')
    output.write('</html>')
```

---

## 6. HTML Templates

### 6.1 Base Report Template
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>$title$</title>
    <style>
        :root {
            --primary-color: #1e40af;
            --secondary-color: #3b82f6;
            --success-color: #16a34a;
            --warning-color: #ca8a04;
            --danger-color: #dc2626;
            --neutral-color: #6b7280;
            
            --bg-primary: #ffffff;
            --bg-secondary: #f9fafb;
            --text-primary: #111827;
            --text-secondary: #4b5563;
            --border-color: #e5e7eb;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: var(--text-primary);
            background: var(--bg-primary);
        }
        
        /* Layout */
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        /* Typography */
        h1 {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: 1rem;
        }
        
        h2 {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-top: 2rem;
            margin-bottom: 1rem;
            border-bottom: 2px solid var(--primary-color);
            padding-bottom: 0.5rem;
        }
        
        h3 {
            font-size: 1.25rem;
            font-weight: 600;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
        }
        
        p {
            margin-bottom: 1rem;
        }
        
        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            font-size: 0.9rem;
        }
        
        th, td {
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }
        
        th {
            background: var(--bg-secondary);
            font-weight: 600;
            color: var(--text-primary);
        }
        
        tr:hover {
            background: var(--bg-secondary);
        }
        
        /* Code blocks */
        pre {
            background: #1f2937;
            color: #e5e7eb;
            padding: 1rem;
            border-radius: 0.5rem;
            overflow-x: auto;
            margin: 1rem 0;
        }
        
        code {
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            font-size: 0.875rem;
        }
        
        /* Severity badges */
        .severity {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .severity-critical {
            background: #fee2e2;
            color: #991b1b;
        }
        
        .severity-high {
            background: #ffedd5;
            color: #9a3412;
        }
        
        .severity-medium {
            background: #fef9c3;
            color: #854d0e;
        }
        
        .severity-low {
            background: #dcfce7;
            color: #166534;
        }
        
        /* Info boxes */
        .info-box {
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        
        .info-box.note {
            background: #eff6ff;
            border-left: 4px solid var(--secondary-color);
        }
        
        .info-box.warning {
            background: #fef9c3;
            border-left: 4px solid var(--warning-color);
        }
        
        .info-box.danger {
            background: #fee2e2;
            border-left: 4px solid var(--danger-color);
        }
        
        /* Print styles */
        @media print {
            body {
                font-size: 12pt;
            }
            
            .container {
                max-width: 100%;
                padding: 0;
            }
            
            h1, h2, h3 {
                page-break-after: avoid;
            }
            
            table {
                page-break-inside: avoid;
            }
            
            pre {
                page-break-inside: avoid;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        $body$
    </div>
</body>
</html>
```

---

## 7. PDF Generation

### 7.1 wkhtmltopdf Configuration
```yaml
# wkhtmltopdf configuration
pdf_options:
  page_size: A4
  orientation: Portrait
  margin:
    top: 1in
    bottom: 1in
    left: 1in
    right: 1in
    
  header:
    height: 0.5in
    content: |
      <div style="text-align: center; font-size: 10px; color: #666;">
        $title$ - Page $page$ of $pages$
      </div>
      
  footer:
    height: 0.5in
    content: |
      <div style="text-align: center; font-size: 10px; color: #666;">
        Generated by ANPTOP | $date$
      </div>
  
  # Enable JavaScript
  enable_local_file_access: true
  enable_internal_links: true
  
  # Images
  image_dpi: 300
  image_quality: 94
  
  # TOC
  toc:
    enable: true
    toc_depth: 3
    toc_header_text: "Table of Contents"
```

### 7.2 Python PDF Generator
```python
import pdfkit

class PDFGenerator:
    def __init__(self):
        self.options = {
            'page-size': 'A4',
            'orientation': 'Portrait',
            'margin-top': '1in',
            'margin-bottom': '1in',
            'margin-left': '1in',
            'margin-right': '1in',
            'encoding': 'UTF-8',
            'enable-local-file-access': None,
            'enable-internal-links': None,
            'javascript-delay': 1000,
            'no-stop-slow-scripts': None,
            'disable-smart-shrinking': None,
        }
        
        self.header_template = '''
        <div style="text-align: center; font-size: 10px; color: #666; width: 100%;">
            {{ title }} - Page {{ page }} of {{ pages }}
        </div>
        '''
        
        self.footer_template = '''
        <div style="text-align: center; font-size: 10px; color: #666; width: 100%;">
            Generated by ANPTOP Platform | {{ date }}
        </div>
        '''
    
    def generate_pdf(
        self,
        html_content: str,
        output_path: str,
        toc: bool = False
    ) -> str:
        """
        Generate PDF from HTML content
        """
        # Add header and footer
        full_html = self._add_header_footer(html_content)
        
        # Configure options
        options = self.options.copy()
        
        if toc:
            options.update({
                'toc': None,
                'toc-depth': '3',
                'toc-header-text': 'Table of Contents',
            })
        
        # Generate PDF
        pdfkit.from_string(
            full_html,
            output_path,
            options=options,
            cover=None,
            cover_first=False
        )
        
        return output_path
    
    def _add_header_footer(self, html_content: str) -> str:
        """
        Add header and footer to HTML
        """
        # Inject header/footer HTML
        header_html = f'''
        <html>
        <head>
            <style>
                .header {{ 
                    position: fixed; 
                    top: 0; 
                    left: 0; 
                    right: 0; 
                    height: 0.5in;
                    background: #f9fafb;
                    border-bottom: 1px solid #e5e7eb;
                }}
                .footer {{ 
                    position: fixed; 
                    bottom: 0; 
                    left: 0; 
                    right: 0; 
                    height: 0.5in;
                    background: #f9fafb;
                    border-top: 1px solid #e5e7eb;
                }}
                .content {{
                    margin-top: 0.5in;
                    margin-bottom: 0.5in;
                }}
            </style>
        </head>
        <body>
            <div class="header"></div>
            <div class="content">
                {html_content}
            </div>
            <div class="footer"></div>
        </body>
        </html>
        '''
        
        return header_html
```

---

## 8. Sample Reports

### 8.1 Executive Summary Sample

```markdown
# Executive Security Assessment Report
## Client: Acme Corporation
## Date: 2024-02-06

## Overview
A comprehensive security assessment was conducted on Acme Corporation's 
network infrastructure from January 15-28, 2024. The assessment identified 
several vulnerabilities requiring immediate attention.

## Key Findings

| Severity | Count | Status |
|----------|-------|--------|
| Critical | 3 | Remediation Required |
| High | 12 | Remediation Required |
| Medium | 45 | Planned Fixes |
| Low | 128 | Informational |

## Critical Issues
1. **Unpatched Remote Desktop Services** (CVSS: 9.8)
2. **SQL Injection in Customer Portal** (CVSS: 9.1)
3. **Default Credentials on Management Systems** (CVSS: 8.8)

## Risk Rating: HIGH (7.2/10)

The overall security posture requires immediate improvement to address 
critical vulnerabilities that could be exploited by malicious actors.
```

### 8.2 Technical Finding Sample

```markdown
# Finding: CVE-2024-1234 - Critical RCE Vulnerability

## Summary
A remote code execution vulnerability was identified in the 
Acme Corp VPN gateway, allowing unauthenticated attackers to 
execute arbitrary commands with SYSTEM privileges.

## CVSS v3.1 Metrics
- **Base Score:** 9.8 (Critical)
- **Vector:** CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
- **Attack Vector:** Network
- **Attack Complexity:** Low
- **Privileges Required:** None
- **User Interaction:** None

## Affected Systems
- VPN-GW-01 (192.168.1.100)
- VPN-GW-02 (192.168.1.101)

## Technical Details
The vulnerability exists in the web management interface 
of the VPN gateway, which fails to properly sanitize 
user-supplied input in the login form.

## Proof of Concept
```python
import requests

target = "https://vpn.acme.com"
payload = "'; cat /etc/passwd #"

data = {
    "username": payload,
    "password": "test"
}

response = requests.post(f"{target}/login", data=data)
print(response.text)
```

## Remediation
1. Apply vendor patch CVE-2024-1234
2. Implement input validation on login forms
3. Enable rate limiting on authentication endpoints
4. Consider disabling management interface from internet

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-1234
- Vendor Advisory: ACME-2024-001
```

---

**Document Version**: 1.0  
**Last Updated**: 2024-02-06  
**Classification**: Internal Use Only
