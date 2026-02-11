VAULTA VOICE AGENT - MERMAID FLOWCHART DIAGRAMS
================================================

This folder contains 4 Mermaid flowchart diagrams for the Vaulta Voice Agent system.
FILES:
------
1. 1-complete-system-flow.txt
   - Full end-to-end system flow
   - All 12 banking features
   - Security features (fraud, auth)
   - Hybrid data source routing

2. 2-intent-routing-tree.txt
   - Intent classification priority order
   - Fraud detection at highest priority
   - All 12 banking operations
   
3. 3-database-query-flow.txt
   - Hybrid data source strategy
   - Mock customer (0-5ms instant)
   - PostgreSQL queries (50-4000ms)
   
4. 4-security-auth-flow.txt
   - Credential extraction
   - PIN verification with retry
   - PII redaction
   - Account lockout after 3 attempts

HOW TO USE:
-----------
1. Copy the content from any .txt file
2. Paste into any Mermaid renderer:
   - Mermaid Live Editor: https://mermaid.live/
   - GitHub/GitLab markdown files
   - VS Code with Mermaid extension
   - Documentation sites

COLOR CODING:
-------------
Red (#ff6666) - Critical security (fraud, lockout)
Green (#90EE90) - Mock data (instant responses)
Blue (#87CEEB) - Database queries
Yellow (#fff3cd) - Security/PII protection
Light Red (#ffcccc) - Fraud-related operations

SYNTAX:
-------
All diagrams use Mermaid flowchart syntax.
Tested and validated for rendering.
Special characters removed from labels to prevent parse errors.
