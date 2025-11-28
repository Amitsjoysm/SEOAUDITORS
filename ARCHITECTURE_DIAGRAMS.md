# 🏗️ ARCHITECTURE DIAGRAMS - SEO Audit Platform

Complete system architecture visualization using Mermaid diagrams.

---

## 1. SYSTEM ARCHITECTURE OVERVIEW

```mermaid
graph TB
    subgraph "Client Layer"
        A[Web Browser]
        B[Mobile App]
    end
    
    subgraph "Frontend - React"
        C[Landing Page]
        D[Dashboard]
        E[Audit Detail]
        F[Competitors]
        G[Content Ideas]
        H[Admin Panel]
        I[API Integrations]
    end
    
    subgraph "Backend - FastAPI"
        J[API Gateway]
        K[Auth Service]
        L[SEO Engine]
        M[Integration Manager]
        N[Report Generator]
        O[AI Orchestrator]
    end
    
    subgraph "Database Layer"
        P[(PostgreSQL/SQLite)]
        Q[(Redis Cache)]
    end
    
    subgraph "External APIs"
        R[Lighthouse CLI]
        S[SerpAPI]
        T[Google Search Console]
        U[Google Analytics]
        V[Google Trends]
        W[Bing Webmaster]
        X[Ahrefs]
        Y[Common Crawl]
        Z[Exa.ai]
    end
    
    subgraph "AI/LLM Services"
        AA[Groq]
        AB[OpenAI]
        AC[Anthropic]
        AD[Gemini]
        AE[Ollama]
    end
    
    A --> C
    A --> D
    A --> E
    A --> F
    A --> G
    A --> H
    A --> I
    B --> C
    
    C --> J
    D --> J
    E --> J
    F --> J
    G --> J
    H --> J
    I --> J
    
    J --> K
    J --> L
    J --> M
    J --> N
    J --> O
    
    K --> P
    L --> P
    M --> P
    N --> P
    O --> P
    
    L --> Q
    M --> Q
    
    M --> R
    M --> S
    M --> T
    M --> U
    M --> V
    M --> W
    M --> X
    M --> Y
    M --> Z
    
    O --> AA
    O --> AB
    O --> AC
    O --> AD
    O --> AE
    
    style A fill:#5B60F0,color:#fff
    style B fill:#5B60F0,color:#fff
    style J fill:#10B981,color:#fff
    style L fill:#F59E0B,color:#fff
    style M fill:#F59E0B,color:#fff
    style O fill:#EF4444,color:#fff
    style P fill:#8B5CF6,color:#fff
```

---

## 2. DATABASE SCHEMA

```mermaid
erDiagram
    User ||--o{ Audit : creates
    User ||--o{ Subscription : has
    User ||--o{ APIToken : owns
    User ||--o{ ChatMessage : sends
    
    Plan ||--o{ Subscription : "subscribed to"
    
    Audit ||--o{ AuditResult : contains
    Audit ||--o{ ChatMessage : "discussed in"
    Audit ||--o{ CompetitorAnalysis : has
    Audit ||--o{ ContentOpportunity : identifies
    Audit ||--o{ AnomalyDetection : detects
    
    APIKeyPool }o--|| User : "managed by"
    APIIntegrationStatus }o--|| APIKeyPool : monitors
    
    User {
        string id PK
        string email UK
        string password_hash
        string full_name
        enum role
        boolean is_active
        datetime created_at
    }
    
    Plan {
        string id PK
        string name UK
        float price
        int max_audits_per_month
        int max_pages_per_audit
        json features
    }
    
    Subscription {
        string id PK
        string user_id FK
        string plan_id FK
        enum status
        datetime current_period_end
        int audits_used_this_month
    }
    
    Audit {
        string id PK
        string user_id FK
        string website_url
        enum status
        int pages_crawled
        float overall_score
        float lighthouse_score
        int serp_position
        int competitor_count
        int opportunities_found
        int anomalies_detected
        datetime created_at
    }
    
    AuditResult {
        string id PK
        string audit_id FK
        string category
        string check_name
        enum status
        int impact_score
        text solution
        json details
    }
    
    CompetitorAnalysis {
        string id PK
        string audit_id FK
        string competitor_url
        float competitor_score
        int keyword_overlap
        int backlink_count
        float domain_authority
        json content_gap_analysis
    }
    
    ContentOpportunity {
        string id PK
        string audit_id FK
        string opportunity_type
        string keyword
        int difficulty_score
        int search_volume
        int current_position
        int potential_traffic
        text content_brief
        json ai_recommendations
    }
    
    AnomalyDetection {
        string id PK
        string audit_id FK
        string anomaly_type
        enum severity
        string metric_name
        float expected_value
        float actual_value
        float deviation_percentage
        text recommended_action
    }
    
    APIKeyPool {
        string id PK
        string service_name
        text api_key
        int quota_limit
        int quota_used
        enum health_status
        int priority
        boolean is_active
        datetime last_used_at
    }
    
    APIIntegrationStatus {
        string id PK
        string service_name UK
        boolean is_healthy
        int success_count
        int failure_count
        float avg_response_time
        text error_message
        datetime last_check_at
    }
    
    APIToken {
        string id PK
        string user_id FK
        string token UK
        string name
        boolean is_active
        datetime last_used_at
    }
    
    ChatMessage {
        string id PK
        string audit_id FK
        string user_id FK
        string role
        text content
        datetime created_at
    }
```

---

## 3. API INTEGRATION FLOW

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant IntegrationManager
    participant APIKeyPool
    participant Redis
    participant ExternalAPI
    
    User->>Frontend: Request Audit
    Frontend->>Backend: POST /audits
    Backend->>IntegrationManager: Start Audit
    
    IntegrationManager->>APIKeyPool: Get Active Key
    APIKeyPool-->>IntegrationManager: Return Key
    
    IntegrationManager->>Redis: Check Cache
    alt Cache Hit
        Redis-->>IntegrationManager: Return Cached Data
    else Cache Miss
        IntegrationManager->>ExternalAPI: API Request
        alt Success
            ExternalAPI-->>IntegrationManager: API Response
            IntegrationManager->>Redis: Cache Response
            IntegrationManager->>APIKeyPool: Update Usage Stats
        else Rate Limit
            ExternalAPI-->>IntegrationManager: 429 Error
            IntegrationManager->>APIKeyPool: Mark Key as Exhausted
            IntegrationManager->>APIKeyPool: Get Next Key
            IntegrationManager->>ExternalAPI: Retry with New Key
        else Error
            ExternalAPI-->>IntegrationManager: Error Response
            IntegrationManager->>APIIntegrationStatus: Log Error
            IntegrationManager->>Backend: Return Error
        end
    end
    
    IntegrationManager-->>Backend: Return Data
    Backend-->>Frontend: Audit Results
    Frontend-->>User: Display Results
```

---

## 4. SEO AUDIT PROCESSING FLOW

```mermaid
flowchart TD
    A[Start Audit] --> B{Website Accessible?}
    B -->|No| C[Return Error]
    B -->|Yes| D[Crawl Website]
    
    D --> E[Extract Metadata]
    E --> F[Run Lighthouse]
    F --> G[Fetch SerpAPI Data]
    G --> H[Fetch GSC Data]
    H --> I[Fetch Analytics Data]
    I --> J[Fetch Trends Data]
    
    J --> K[Run 135 SEO Checks]
    K --> L[Identify Competitors]
    L --> M[Analyze Competitors]
    M --> N[Find Content Opportunities]
    N --> O[Detect Anomalies]
    
    O --> P[Generate AI Analysis]
    P --> Q[Calculate Overall Score]
    Q --> R[Store Results in DB]
    R --> S[Generate Reports PDF/DOCX]
    S --> T[Send Notifications]
    T --> U[Update Audit Status]
    U --> V[End]
    
    style A fill:#10B981,color:#fff
    style V fill:#10B981,color:#fff
    style C fill:#EF4444,color:#fff
    style P fill:#8B5CF6,color:#fff
```

---

## 5. USER FLOW DIAGRAM

```mermaid
journey
    title User Journey - Creating and Analyzing SEO Audit
    section Registration
      Visit Landing Page: 5: User
      Click Sign Up: 5: User
      Enter Details: 4: User
      Choose Plan: 4: User
      Complete Payment: 3: User
    section Dashboard
      View Dashboard: 5: User
      See Metrics: 4: User
      Click Create Audit: 5: User
    section Audit Creation
      Enter Website URL: 5: User
      Start Audit: 5: User
      Wait for Results: 3: User
    section Results Analysis
      View Overall Score: 5: User
      Check Technical SEO: 4: User
      Check Performance: 4: User
      View Competitors: 5: User
      See Content Ideas: 5: User
      Detect Anomalies: 4: User
    section Actions
      Download PDF: 5: User
      Download DOCX: 5: User
      Chat with AI: 5: User
      Implement Fixes: 4: User
    section Follow-up
      Re-run Audit: 5: User
      Compare Results: 5: User
      Track Progress: 5: User
```

---

## 6. ADMIN PANEL STRUCTURE

```mermaid
graph TD
    A[Admin Dashboard] --> B[Overview Tab]
    A --> C[Users Tab]
    A --> D[Plans Tab]
    A --> E[Themes Tab]
    A --> F[LLM Settings Tab]
    A --> G[Environment Keys Tab]
    A --> H[API Key Pools Tab]
    A --> I[Integrations Tab]
    A --> J[Audits Tab]
    A --> K[Content Opportunities Tab]
    A --> L[Anomalies Tab]
    A --> M[Analytics Tab]
    
    B --> B1[Key Metrics]
    B --> B2[Recent Activity]
    B --> B3[System Health]
    
    C --> C1[User List]
    C --> C2[Add User]
    C --> C3[Edit User]
    C --> C4[Delete User]
    
    D --> D1[Plan List]
    D --> D2[Create Plan]
    D --> D3[Edit Plan]
    D --> D4[Stripe Price IDs]
    
    E --> E1[Theme List]
    E --> E2[Create Theme]
    E --> E3[Edit Colors]
    E --> E4[Activate Theme]
    
    F --> F1[LLM List]
    F --> F2[Add LLM]
    F --> F3[Configure LLM]
    F --> F4[Activate LLM]
    
    G --> G1[Environment Keys List]
    G --> G2[Add Key]
    G --> G3[Edit Key]
    G --> G4[Toggle Active]
    
    H --> H1[API Key Pools by Service]
    H --> H2[Add API Key]
    H --> H3[Test Connection]
    H --> H4[View Usage Stats]
    H --> H5[Key Rotation Settings]
    
    I --> I1[Integration Health Status]
    I --> I2[Uptime Monitoring]
    I --> I3[Error Logs]
    I --> I4[Usage Statistics]
    I --> I5[Cost Tracking]
    
    J --> J1[All Audits List]
    J --> J2[Filter by User]
    J --> J3[Filter by Status]
    J --> J4[Bulk Actions]
    
    K --> K1[Global Opportunities]
    K --> K2[Trend Analysis]
    K --> K3[AI Usage Stats]
    
    L --> L1[System Anomalies]
    L --> L2[Alert Configuration]
    L --> L3[Resolution Tracking]
    
    M --> M1[User Activity]
    M --> M2[Feature Usage]
    M --> M3[Cost Analytics]
    M --> M4[Performance Metrics]
    
    style A fill:#5B60F0,color:#fff
    style H fill:#F59E0B,color:#fff
    style I fill:#F59E0B,color:#fff
    style K fill:#10B981,color:#fff
    style L fill:#EF4444,color:#fff
```

---

## 7. COMPONENT HIERARCHY (Frontend)

```mermaid
graph TD
    A[App.js] --> B[Router]
    
    B --> C[Public Routes]
    B --> D[Protected Routes]
    B --> E[Admin Routes]
    
    C --> C1[Landing]
    C --> C2[Login]
    C --> C3[Register]
    C --> C4[Plans]
    
    D --> D1[TopNavigation]
    D --> D2[Dashboard]
    D --> D3[AuditDetail]
    D --> D4[Competitors]
    D --> D5[ContentIdeas]
    D --> D6[Integrations]
    D --> D7[Settings]
    D --> D8[APITokens]
    D --> D9[Chat]
    
    E --> E1[AdminDashboard]
    
    D1 --> D1A[Logo]
    D1 --> D1B[NavLinks]
    D1 --> D1C[SearchBar]
    D1 --> D1D[NotificationBell]
    D1 --> D1E[UserDropdown]
    
    D2 --> D2A[MetricCards]
    D2 --> D2B[TabNavigation]
    D2 --> D2C[AuditList]
    D2 --> D2D[Charts]
    
    D2A --> D2A1[MetricCard - Total Audits]
    D2A --> D2A2[MetricCard - Avg Score]
    D2A --> D2A3[MetricCard - Issues]
    D2A --> D2A4[MetricCard - Opportunities]
    
    D3 --> D3A[AuditHeader]
    D3 --> D3B[ScoreCards]
    D3 --> D3C[TabNavigation]
    D3 --> D3D[CheckResults]
    D3 --> D3E[CompetitorSection]
    D3 --> D3F[OpportunitiesSection]
    
    D3B --> D3B1[TechnicalSEOCard]
    D3B --> D3B2[PerformanceCard]
    D3B --> D3B3[OnPageCard]
    D3B --> D3B4[ContentCard]
    
    D3D --> D3D1[CheckCard]
    D3D1 --> D3D1A[StatusIcon]
    D3D1 --> D3D1B[CheckName]
    D3D1 --> D3D1C[ImpactBadge]
    D3D1 --> D3D1D[ExpandableDetails]
    
    E1 --> E1A[AdminTabs]
    E1 --> E1B[OverviewTab]
    E1 --> E1C[UsersTab]
    E1 --> E1D[APIKeyPoolsTab]
    E1 --> E1E[IntegrationsTab]
    
    E1D --> E1D1[ServiceSelector]
    E1D --> E1D2[KeyList]
    E1D --> E1D3[AddKeyModal]
    E1D --> E1D4[UsageCharts]
    
    E1E --> E1E1[IntegrationCards]
    E1E --> E1E2[HealthIndicators]
    E1E --> E1E3[ErrorLogViewer]
    E1E --> E1E4[UsageStats]
    
    style A fill:#5B60F0,color:#fff
    style D1 fill:#10B981,color:#fff
    style D2 fill:#F59E0B,color:#fff
    style D3 fill:#F59E0B,color:#fff
    style E1 fill:#EF4444,color:#fff
```

---

## 8. API INTEGRATION MANAGER

```mermaid
graph LR
    A[Integration Manager] --> B[Lighthouse Service]
    A --> C[SerpAPI Service]
    A --> D[GSC Service]
    A --> E[Analytics Service]
    A --> F[Trends Service]
    A --> G[Bing Service]
    A --> H[Ahrefs Service]
    A --> I[Common Crawl Service]
    A --> J[Exa.ai Service]
    
    B --> B1[Performance Scores]
    B --> B2[Core Web Vitals]
    B --> B3[Accessibility]
    
    C --> C1[SERP Rankings]
    C --> C2[Competitors]
    C --> C3[Featured Snippets]
    C --> C4[PAA Questions]
    
    D --> D1[Keyword Data]
    D --> D2[CTR Data]
    D --> D3[Index Coverage]
    D --> D4[Mobile Usability]
    
    E --> E1[Traffic Data]
    E --> E2[User Behavior]
    E --> E3[Conversion Data]
    
    F --> F1[Trend Data]
    F --> F2[Related Queries]
    F --> F3[Regional Interest]
    
    G --> G1[Bing Rankings]
    G --> G2[Index Stats]
    G --> G3[Crawl Errors]
    
    H --> H1[Backlinks]
    H --> H2[Domain Rating]
    H --> H3[Referring Domains]
    
    I --> I1[Historical Data]
    I --> I2[Old Backlinks]
    I --> I3[Content Changes]
    
    J --> J1[Research Data]
    J --> J2[Competitor Analysis]
    J --> J3[Content Discovery]
    
    A --> K[Key Pool Manager]
    K --> K1[Key Selection]
    K --> K2[Load Balancing]
    K --> K3[Failover Logic]
    
    A --> L[Cache Layer]
    L --> L1[Redis Cache]
    L --> L2[TTL Management]
    
    A --> M[Rate Limiter]
    M --> M1[Request Queue]
    M --> M2[Exponential Backoff]
    
    style A fill:#5B60F0,color:#fff
    style K fill:#F59E0B,color:#fff
    style L fill:#10B981,color:#fff
    style M fill:#EF4444,color:#fff
```

---

## 9. CONTENT OPPORTUNITY ENGINE

```mermaid
flowchart TD
    A[Content Opportunity Engine] --> B[Keyword Research]
    A --> C[Competitor Analysis]
    A --> D[Trend Analysis]
    A --> E[AI Content Generator]
    
    B --> B1[SerpAPI: Search Volume]
    B --> B2[GSC: Current Rankings]
    B --> B3[Trends: Seasonality]
    B --> B4[Calculate Difficulty Score]
    
    C --> C1[Identify Top Competitors]
    C --> C2[Extract Their Keywords]
    C --> C3[Find Keyword Gaps]
    C --> C4[Analyze Content Quality]
    
    D --> D1[Google Trends: Rising Topics]
    D --> D2[Exa.ai: Industry Trends]
    D --> D3[Seasonal Patterns]
    D --> D4[Predict Best Timing]
    
    E --> E1[LLM: Generate Brief]
    E --> E2[LLM: Title Suggestions]
    E --> E3[LLM: Outline Creation]
    E --> E4[LLM: Optimization Tips]
    
    B4 --> F[Score Opportunities]
    C4 --> F
    D4 --> F
    
    F --> G{Priority?}
    G -->|High| H[Quick Win Opportunities]
    G -->|Medium| I[Long-term Opportunities]
    G -->|Low| J[Future Opportunities]
    
    H --> K[Store in Database]
    I --> K
    J --> K
    
    K --> L[Display to User]
    L --> M[Generate Content Brief]
    M --> E
    
    style A fill:#5B60F0,color:#fff
    style E fill:#8B5CF6,color:#fff
    style F fill:#F59E0B,color:#fff
    style H fill:#10B981,color:#fff
```

---

## 10. ANOMALY DETECTION SYSTEM

```mermaid
flowchart TD
    A[Anomaly Detection System] --> B[Data Collection]
    
    B --> C[Current Audit Data]
    B --> D[Historical Data]
    
    C --> E[Current Traffic]
    C --> F[Current Rankings]
    C --> G[Current Performance]
    C --> H[Current Index Status]
    
    D --> I[Historical Traffic]
    D --> J[Historical Rankings]
    D --> K[Historical Performance]
    D --> L[Historical Index Status]
    
    E --> M[Compare]
    I --> M
    F --> N[Compare]
    J --> N
    G --> O[Compare]
    K --> O
    H --> P[Compare]
    L --> P
    
    M --> Q{Deviation > 2σ?}
    N --> Q
    O --> Q
    P --> Q
    
    Q -->|Yes| R[Classify Anomaly]
    Q -->|No| S[No Anomaly]
    
    R --> T{Severity?}
    T -->|Critical| U[Traffic Drop > 50%]
    T -->|High| V[Ranking Drop > 10 positions]
    T -->|Medium| W[Performance Drop > 20%]
    T -->|Low| X[Minor Issues]
    
    U --> Y[Send Alert]
    V --> Y
    W --> Y
    X --> Z[Log Only]
    
    Y --> AA[Store in Database]
    Z --> AA
    
    AA --> AB[Display in Dashboard]
    AB --> AC[Recommend Action]
    
    AC --> AD[AI Analysis]
    AD --> AE[Root Cause]
    AD --> AF[Solution Steps]
    
    style A fill:#5B60F0,color:#fff
    style Q fill:#F59E0B,color:#fff
    style U fill:#EF4444,color:#fff
    style V fill:#EF4444,color:#fff
    style Y fill:#EF4444,color:#fff
    style AD fill:#8B5CF6,color:#fff
```

---

## 11. DEPLOYMENT ARCHITECTURE

```mermaid
graph TB
    subgraph "Client Devices"
        A[Desktop Browser]
        B[Mobile Browser]
        C[Tablet Browser]
    end
    
    subgraph "CDN Layer"
        D[CloudFlare CDN]
    end
    
    subgraph "Load Balancer"
        E[Nginx Load Balancer]
    end
    
    subgraph "Application Servers"
        F[FastAPI Server 1]
        G[FastAPI Server 2]
        H[FastAPI Server 3]
    end
    
    subgraph "Worker Processes"
        I[Celery Worker 1]
        J[Celery Worker 2]
        K[Celery Worker 3]
    end
    
    subgraph "Cache Layer"
        L[(Redis Cluster)]
    end
    
    subgraph "Database Layer"
        M[(PostgreSQL Primary)]
        N[(PostgreSQL Replica 1)]
        O[(PostgreSQL Replica 2)]
    end
    
    subgraph "Message Queue"
        P[RabbitMQ/Redis Queue]
    end
    
    subgraph "Storage"
        Q[S3/Object Storage]
    end
    
    subgraph "Monitoring"
        R[Prometheus]
        S[Grafana]
        T[Sentry]
    end
    
    A --> D
    B --> D
    C --> D
    
    D --> E
    
    E --> F
    E --> G
    E --> H
    
    F --> L
    G --> L
    H --> L
    
    F --> M
    G --> M
    H --> M
    
    F --> P
    G --> P
    H --> P
    
    P --> I
    P --> J
    P --> K
    
    I --> M
    J --> M
    K --> M
    
    M --> N
    M --> O
    
    F --> Q
    G --> Q
    H --> Q
    
    F --> R
    G --> R
    H --> R
    
    R --> S
    F --> T
    G --> T
    H --> T
    
    style D fill:#10B981,color:#fff
    style E fill:#10B981,color:#fff
    style L fill:#F59E0B,color:#fff
    style M fill:#8B5CF6,color:#fff
    style P fill:#F59E0B,color:#fff
    style R fill:#EF4444,color:#fff
```

---

## 12. SECURITY ARCHITECTURE

```mermaid
graph TD
    A[User Request] --> B{HTTPS?}
    B -->|No| C[Redirect to HTTPS]
    B -->|Yes| D[Rate Limiter]
    
    D --> E{Rate Limit OK?}
    E -->|No| F[Return 429]
    E -->|Yes| G[CORS Check]
    
    G --> H{Valid Origin?}
    H -->|No| I[Return 403]
    H -->|Yes| J[JWT Validation]
    
    J --> K{Valid Token?}
    K -->|No| L[Return 401]
    K -->|Yes| M[Role Check]
    
    M --> N{Authorized?}
    N -->|No| O[Return 403]
    N -->|Yes| P[Input Validation]
    
    P --> Q{Valid Input?}
    Q -->|No| R[Return 400]
    Q -->|Yes| S[SQL Injection Check]
    
    S --> T{Safe Query?}
    T -->|No| U[Block Request]
    T -->|Yes| V[XSS Protection]
    
    V --> W{Safe Content?}
    W -->|No| X[Sanitize Input]
    W -->|Yes| Y[Process Request]
    
    Y --> Z[Encrypt Sensitive Data]
    Z --> AA[API Key Rotation]
    AA --> AB[Execute Action]
    
    AB --> AC[Audit Log]
    AC --> AD[Return Response]
    
    style A fill:#5B60F0,color:#fff
    style F fill:#EF4444,color:#fff
    style I fill:#EF4444,color:#fff
    style L fill:#EF4444,color:#fff
    style O fill:#EF4444,color:#fff
    style R fill:#EF4444,color:#fff
    style U fill:#EF4444,color:#fff
    style Z fill:#10B981,color:#fff
    style AC fill:#F59E0B,color:#fff
```

---

## 13. DATA FLOW - AUDIT CREATION TO REPORT

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant BE as Backend
    participant SEO as SEO Engine
    participant IM as Integration Manager
    participant API as External APIs
    participant AI as AI Orchestrator
    participant DB as Database
    participant RG as Report Generator
    
    U->>FE: Click "Create Audit"
    FE->>U: Show URL Input
    U->>FE: Enter URL & Submit
    FE->>BE: POST /audits {url}
    BE->>DB: Create Audit Record (status: pending)
    BE-->>FE: Return Audit ID
    FE-->>U: Show "Audit Started"
    
    BE->>SEO: Start Audit Process
    SEO->>IM: Request Website Crawl
    IM->>API: Fetch Page Content
    API-->>IM: Return HTML
    IM-->>SEO: Return Crawled Data
    
    SEO->>IM: Run Lighthouse
    IM->>API: Execute Lighthouse
    API-->>IM: Performance Scores
    IM-->>SEO: Lighthouse Results
    
    SEO->>IM: Get SERP Data
    IM->>API: SerpAPI Request
    API-->>IM: Rankings & Competitors
    IM-->>SEO: SERP Results
    
    SEO->>IM: Get GSC Data
    IM->>API: GSC API Request
    API-->>IM: Keyword & CTR Data
    IM-->>SEO: GSC Results
    
    SEO->>SEO: Run 135 SEO Checks
    SEO->>SEO: Analyze Competitors
    SEO->>SEO: Find Opportunities
    SEO->>SEO: Detect Anomalies
    
    SEO->>AI: Generate Analysis
    AI-->>SEO: AI Insights
    
    SEO->>DB: Store Results
    SEO->>RG: Generate Reports
    RG->>DB: Save PDF Path
    RG->>DB: Save DOCX Path
    
    SEO->>DB: Update Audit (status: completed)
    DB-->>BE: Audit Updated
    BE-->>FE: Audit Complete Event
    FE->>BE: GET /audits/{id}
    BE->>DB: Fetch Full Results
    DB-->>BE: Audit Data
    BE-->>FE: Return Results
    FE-->>U: Display Results
```

---

## 14. APOLLO.IO-INSPIRED UI MOCKUP STRUCTURE

```mermaid
graph TD
    A[Top Navigation Bar - Fixed] --> A1[Logo]
    A --> A2[Dashboard]
    A --> A3[Audits]
    A --> A4[Competitors]
    A --> A5[Content Ideas]
    A --> A6[Integrations]
    A --> A7[Search]
    A --> A8[Notifications]
    A --> A9[Profile Menu]
    
    B[Main Content Area] --> C[Hero Metrics Section]
    C --> C1[Card: Total Audits]
    C --> C2[Card: Avg Score]
    C --> C3[Card: Active Issues]
    C --> C4[Card: Opportunities]
    
    B --> D[Tab Navigation]
    D --> D1[Overview Tab]
    D --> D2[Audits Tab]
    D --> D3[Competitors Tab]
    D --> D4[Content Tab]
    D --> D5[Integrations Tab]
    
    D1 --> E[Overview Content]
    E --> E1[Recent Audits - Card Grid]
    E --> E2[Score Trend - Line Chart]
    E --> E3[Category Breakdown - Donut Chart]
    E --> E4[Quick Actions]
    
    D2 --> F[Audits List]
    F --> F1[Filters Bar]
    F --> F2[Audit Cards Grid]
    F2 --> F2A[Audit Card 1]
    F2 --> F2B[Audit Card 2]
    F2 --> F2C[Audit Card 3]
    
    F2A --> G[Card Components]
    G --> G1[Website Thumbnail]
    G --> G2[URL & Title]
    G --> G3[Score Badge]
    G --> G4[Status Badge]
    G --> G5[Date]
    G --> G6[Action Buttons]
    
    style A fill:#5B60F0,color:#fff
    style C fill:#F9FAFB,stroke:#E5E7EB
    style C1 fill:#fff,stroke:#E5E7EB
    style C2 fill:#fff,stroke:#E5E7EB
    style C3 fill:#fff,stroke:#E5E7EB
    style C4 fill:#fff,stroke:#E5E7EB
    style D fill:#fff,stroke:#E5E7EB
    style F2A fill:#fff,stroke:#E5E7EB
```

---

These diagrams provide a complete visual understanding of the system architecture, data flow, and UI structure. They show:

1. ✅ **System Architecture** - Overall technology stack
2. ✅ **Database Schema** - Complete data model with relationships
3. ✅ **API Integration Flow** - How external APIs are called with failover
4. ✅ **SEO Audit Flow** - Step-by-step audit processing
5. ✅ **User Journey** - User experience from registration to results
6. ✅ **Admin Panel** - Complete admin functionality
7. ✅ **Component Hierarchy** - Frontend component structure
8. ✅ **Integration Manager** - How 9 APIs are managed
9. ✅ **Content Opportunity Engine** - AI-powered content recommendations
10. ✅ **Anomaly Detection** - Automated issue detection
11. ✅ **Deployment Architecture** - Production infrastructure
12. ✅ **Security Architecture** - Security layers and validation
13. ✅ **Data Flow** - Complete audit creation flow
14. ✅ **UI Structure** - Apollo.io-inspired interface layout

Ready to start implementation! 🚀
