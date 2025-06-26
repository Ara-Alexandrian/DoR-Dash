<script>
  import { onMount } from 'svelte';
  import { fade, fly, scale } from 'svelte/transition';
  import mermaid from 'mermaid';
  
  // Platform updates/changelog
  const platformUpdates = [
    {
      date: '2025-01-19',
      version: 'v1.5.0',
      title: 'User Experience Improvements',
      changes: [
        'Fixed font readability across all dark themes',
        'Resolved faculty updates visibility issues',
        'Fixed file attachment display for student submissions',
        'Improved dashboard counting logic for admins'
      ],
      type: 'enhancement'
    },
    {
      date: '2025-01-18',
      version: 'v1.4.0',
      title: 'QA System Implementation',
      changes: [
        'Added comprehensive QA validation framework',
        'Implemented LLM text refinement testing suite',
        'Standardized QA report templates',
        'Added automated test endpoints for admins'
      ],
      type: 'feature'
    },
    {
      date: '2025-01-15',
      version: 'v1.3.0',
      title: 'Database Enhancements',
      changes: [
        'Added cascade delete constraints',
        'Fixed transaction handling for user deletion',
        'Improved enum validation for announcements',
        'Enhanced role-based filtering'
      ],
      type: 'enhancement'
    }
  ];

  // Roadmap modal state
  let showModal = false;
  let selectedFeature = null;

  // Roadmap feature details
  const featureDetails = {
    'Faculty Updates System': {
      status: 'completed',
      description: 'System for faculty to submit announcements and updates',
      details: [
        'Faculty can create and submit announcements',
        'Multiple announcement types (general, urgent, project)',
        'Integration with meeting agenda generation',
        'Real-time notifications to students'
      ]
    },
    'Student Submission Portal': {
      status: 'completed',
      description: 'Portal for students to submit research progress updates',
      details: [
        'Research progress tracking and submission',
        'Challenge and obstacle reporting',
        'Goal setting and milestone tracking',
        'File attachment support for documents'
      ]
    },
    'Meeting Agenda Management': {
      status: 'completed',
      description: 'Automated meeting agenda creation and management',
      details: [
        'Automatic agenda compilation from submissions',
        'Meeting scheduling and calendar integration',
        'Printable agenda generation',
        'Historical meeting archive'
      ]
    },
    'File Upload System': {
      status: 'completed',
      description: 'Secure file upload and management system',
      details: [
        'Support for multiple file formats (PDF, DOC, PPT)',
        'Secure file storage and access control',
        'File preview and download capabilities',
        'Integration with student submissions'
      ]
    },
    'QA Validation Framework': {
      status: 'completed',
      description: 'Quality assurance and testing framework',
      details: [
        'Automated testing suite for all features',
        'LLM text refinement validation',
        'Performance monitoring and reporting',
        'Continuous integration workflows'
      ]
    },
    'LLM Text Refinement Testing': {
      status: 'completed',
      description: 'AI-powered text improvement and validation system',
      details: [
        'Grammar and clarity enhancement',
        'Conservative text refinement approach',
        'Quality validation and reporting',
        'Integration with submission workflow'
      ]
    },
    'Presentation Assignment System': {
      status: 'completed',
      description: 'Faculty-driven presentation scheduling with grillometer feedback',
      details: [
        'Faculty can assign presentations to students',
        'Grillometer intensity settings (novelty, methodology, delivery)',
        'Integration with meeting scheduling',
        'Student submission portal for materials'
      ]
    },
    'Profile Picture System': {
      status: 'completed',
      description: 'User profile customization with avatar support',
      details: [
        'Image upload and cropping functionality',
        'Automatic resizing to standard formats',
        'Soft edge and circular crop options',
        'Database storage with Redis caching'
      ]
    },
    'Auto-compiling Agenda': {
      status: 'in_progress',
      description: 'Intelligent agenda compilation from submissions',
      details: [
        'Smart grouping of related submissions',
        'Time allocation optimization',
        'Presenter scheduling automation',
        'Dynamic agenda updates'
      ]
    },
    'Advanced Roster Management': {
      status: 'in_progress',
      description: 'Enhanced user and role management system',
      details: [
        'Bulk user import and export',
        'Advanced permission controls',
        'User activity tracking',
        'Custom role definitions'
      ]
    },
    'LLM Feedback Integration': {
      status: 'future',
      description: 'AI-powered feedback and suggestion system',
      details: [
        'Intelligent progress analysis',
        'Personalized improvement suggestions',
        'Research direction recommendations',
        'Automated milestone tracking'
      ]
    },
    'LLM LoRA Fine-tuning': {
      status: 'future',
      description: 'Custom AI model training for research domain',
      details: [
        'Domain-specific language model training',
        'Research terminology optimization',
        'Custom feedback generation',
        'Improved text analysis accuracy'
      ]
    },
    'LLM-Assisted Agenda Compiler': {
      status: 'future',
      description: 'AI-powered intelligent agenda creation',
      details: [
        'Natural language processing of submissions',
        'Intelligent topic grouping and ordering',
        'Optimal time allocation suggestions',
        'Meeting flow optimization'
      ]
    },
    'Real-time Collaboration': {
      status: 'future',
      description: 'Live collaboration features for research teams',
      details: [
        'Real-time document editing',
        'Live chat and messaging',
        'Collaborative whiteboarding',
        'Video conference integration'
      ]
    },
    'Mobile App Development': {
      status: 'future',
      description: 'Native mobile applications for iOS and Android',
      details: [
        'Native iOS and Android applications',
        'Push notifications for updates',
        'Offline functionality support',
        'Mobile-optimized user interface'
      ]
    },
    'Secretarial Login Layer': {
      status: 'future',
      description: 'Administrative assistant access and workflow support',
      details: [
        'Limited administrative access for support staff',
        'Meeting preparation assistance tools',
        'Document management workflows',
        'Administrative reporting features'
      ]
    }
  };

  function openModal(featureName) {
    selectedFeature = featureDetails[featureName];
    showModal = true;
  }

  function closeModal() {
    showModal = false;
    selectedFeature = null;
  }

  // Format date for display
  function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }

  onMount(async () => {
    // Initialize Mermaid
    mermaid.initialize({ 
      startOnLoad: true,
      theme: 'default',
      themeVariables: {
        primaryColor: '#8b5cf6',
        primaryTextColor: '#fff',
        primaryBorderColor: '#7c3aed',
        lineColor: '#5b21b6',
        secondaryColor: '#f59e0b',
        tertiaryColor: '#10b981',
        background: '#ffffff',
        mainBkg: '#f3f4f6',
        secondBkg: '#e5e7eb',
        tertiaryBkg: '#d1d5db',
        darkMode: false
      }
    });
    
    // Render Mermaid diagrams after component mounts
    setTimeout(() => {
      mermaid.contentLoaded();
    }, 100);
  });
</script>

<svelte:head>
  <title>About DoR-Dash</title>
  <meta name="description" content="Learn about DoR-Dash - A comprehensive research management platform for academic departments" />
</svelte:head>

<div class="min-h-screen py-8">
  <div class="max-w-6xl mx-auto px-4 space-y-12">
    
    <!-- Header -->
    <div class="text-center" in:fade={{duration: 300}}>
      <h1 class="text-4xl font-bold bg-gradient-to-r from-primary-800 to-primary-600 dark:from-primary-400 dark:to-primary-300 bg-clip-text text-transparent mb-4">
        About DoR-Dash
      </h1>
      <p class="text-xl text-[rgb(var(--color-text-secondary))] max-w-3xl mx-auto">
        A comprehensive research management platform designed to streamline academic department workflows, 
        enhance collaboration, and provide intelligent insights for research teams.
      </p>
    </div>

    <!-- System Overview -->
    <div class="space-y-6" in:fly={{y: 20, duration: 400, delay: 100}}>
      <h2 class="text-2xl font-bold text-[rgb(var(--color-text-primary))]">System Architecture Overview</h2>
      
      <div class="card p-8">
        <div class="space-y-8">
          
          <!-- High-Level Architecture -->
          <div>
            <h3 class="text-xl font-semibold text-[rgb(var(--color-text-primary))] mb-4">High-Level Architecture</h3>
            <div class="mermaid bg-white dark:bg-gray-800 p-6 rounded-lg border">
graph TB
    subgraph "Frontend Layer"
        UI[SvelteKit UI]
        PWA[Progressive Web App]
        Mobile[Mobile Responsive]
    end
    
    subgraph "API Layer"
        FastAPI[FastAPI Backend]
        Auth[Authentication]
        RBAC[Role-Based Access]
    end
    
    subgraph "Business Logic"
        Users[User Management]
        Updates[Progress Updates]
        Meetings[Meeting Management]
        Presentations[Presentation System]
        Files[File Management]
    end
    
    subgraph "Data Layer"
        PostgreSQL[(PostgreSQL)]
        Redis[(Redis Cache)]
        FileStore[File Storage]
    end
    
    subgraph "AI/ML Services"
        Ollama[Ollama LLM Server]
        TextRefine[Text Refinement]
        Analytics[Progress Analytics]
    end
    
    UI --> FastAPI
    PWA --> FastAPI
    Mobile --> FastAPI
    
    FastAPI --> Auth
    FastAPI --> RBAC
    
    Auth --> Users
    FastAPI --> Updates
    FastAPI --> Meetings
    FastAPI --> Presentations
    FastAPI --> Files
    
    Users --> PostgreSQL
    Updates --> PostgreSQL
    Meetings --> PostgreSQL
    Presentations --> PostgreSQL
    Files --> PostgreSQL
    Files --> FileStore
    
    FastAPI --> Redis
    TextRefine --> Ollama
    Analytics --> Ollama
            </div>
          </div>

          <!-- User Flow -->
          <div>
            <h3 class="text-xl font-semibold text-[rgb(var(--color-text-primary))] mb-4">User Workflow</h3>
            <div class="mermaid bg-white dark:bg-gray-800 p-6 rounded-lg border">
graph LR
    Login[User Login] --> Dashboard[Dashboard View]
    Dashboard --> Choice["User Role?"]
    
    Choice -->|Student| StudentFlow[Student Workflow]
    Choice -->|Faculty| FacultyFlow[Faculty Workflow]
    Choice -->|Admin| AdminFlow[Admin Workflow]
    
    subgraph "Student Actions"
        StudentFlow --> Submit[Submit Progress Update]
        Submit --> AttachFiles[Attach Supporting Files]
        AttachFiles --> ViewAssignments[View Presentation Assignments]
        ViewAssignments --> SubmitMaterials[Submit Presentation Materials]
    end
    
    subgraph "Faculty Actions"
        FacultyFlow --> CreateAnnouncement[Create Announcements]
        CreateAnnouncement --> AssignPresentation[Assign Presentations]
        AssignPresentation --> SetGrillometer[Configure Grillometer Settings]
        SetGrillometer --> ReviewSubmissions[Review Student Submissions]
    end
    
    subgraph "Admin Actions"
        AdminFlow --> ManageUsers[Manage Users & Roles]
        ManageUsers --> ScheduleMeetings[Schedule Meetings]
        ScheduleMeetings --> GenerateAgenda[Generate Meeting Agendas]
        GenerateAgenda --> SystemConfig[System Configuration]
    end
            </div>
          </div>

          <!-- Data Flow -->
          <div>
            <h3 class="text-xl font-semibold text-[rgb(var(--color-text-primary))] mb-4">Data Flow & Processing</h3>
            <div class="mermaid bg-white dark:bg-gray-800 p-6 rounded-lg border">
graph TD
    Input[User Input] --> Validation[Data Validation]
    Validation --> Processing[Business Logic Processing]
    
    Processing --> Cache["Cache Available?"]
    Cache -->|Yes| ServeCache[Serve from Redis]
    Cache -->|No| Database[Query PostgreSQL]
    
    Database --> UpdateCache[Update Redis Cache]
    UpdateCache --> Response[Send Response]
    ServeCache --> Response
    
    Processing --> LLM["Text Refinement?"]
    LLM -->|Yes| Ollama[Process with Ollama]
    LLM -->|No| Direct[Direct Processing]
    
    Ollama --> Enhanced[Enhanced Content]
    Direct --> Enhanced
    Enhanced --> Database
    
    subgraph "File Processing"
        FileUpload[File Upload] --> FileValidation[Validate File Type/Size]
        FileValidation --> FileStorage[Store in Database/FileSystem]
        FileStorage --> FileCache[Cache File Metadata]
    end
            </div>
          </div>

          <!-- Key Components -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div class="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-slate-800 dark:to-slate-700 dracula:from-gray-800 dracula:to-gray-700 mbp:from-gray-900 mbp:to-gray-800 lsu:from-purple-950 lsu:to-purple-900 border border-blue-200 dark:border-blue-800 dracula:border-gray-600 mbp:border-red-900 lsu:border-purple-800 rounded-lg p-6">
              <h4 class="font-semibold text-blue-800 dark:text-blue-100 dracula:text-cyan-300 mbp:text-red-300 lsu:text-purple-300 mb-3">Frontend (SvelteKit)</h4>
              <ul class="text-sm text-blue-700 dark:text-blue-200 dracula:text-gray-300 mbp:text-gray-300 lsu:text-gray-300 space-y-1">
                <li>• Reactive user interfaces</li>
                <li>• Server-side rendering</li>
                <li>• Progressive enhancement</li>
                <li>• Mobile-first design</li>
                <li>• Dark mode support</li>
              </ul>
            </div>
            
            <div class="bg-gradient-to-br from-green-50 to-green-100 dark:from-slate-800 dark:to-slate-700 dracula:from-gray-800 dracula:to-gray-700 mbp:from-gray-900 mbp:to-gray-800 lsu:from-purple-950 lsu:to-purple-900 border border-green-200 dark:border-green-800 dracula:border-gray-600 mbp:border-red-900 lsu:border-purple-800 rounded-lg p-6">
              <h4 class="font-semibold text-green-800 dark:text-green-100 dracula:text-cyan-300 mbp:text-red-300 lsu:text-purple-300 mb-3">Backend (FastAPI)</h4>
              <ul class="text-sm text-green-700 dark:text-green-200 dracula:text-gray-300 mbp:text-gray-300 lsu:text-gray-300 space-y-1">
                <li>• RESTful API design</li>
                <li>• Automatic API documentation</li>
                <li>• JWT authentication</li>
                <li>• Role-based access control</li>
                <li>• Async request handling</li>
              </ul>
            </div>
            
            <div class="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-slate-800 dark:to-slate-700 dracula:from-gray-800 dracula:to-gray-700 mbp:from-gray-900 mbp:to-gray-800 lsu:from-purple-950 lsu:to-purple-900 border border-purple-200 dark:border-purple-800 dracula:border-gray-600 mbp:border-red-900 lsu:border-purple-800 rounded-lg p-6">
              <h4 class="font-semibold text-purple-800 dark:text-purple-100 dracula:text-cyan-300 mbp:text-red-300 lsu:text-purple-300 mb-3">Database (PostgreSQL)</h4>
              <ul class="text-sm text-purple-700 dark:text-purple-200 dracula:text-gray-300 mbp:text-gray-300 lsu:text-gray-300 space-y-1">
                <li>• Relational data modeling</li>
                <li>• ACID compliance</li>
                <li>• Advanced querying</li>
                <li>• Data integrity constraints</li>
                <li>• Performance optimization</li>
              </ul>
            </div>
            
            <div class="bg-gradient-to-br from-red-50 to-red-100 dark:from-slate-800 dark:to-slate-700 dracula:from-gray-800 dracula:to-gray-700 mbp:from-gray-900 mbp:to-gray-800 lsu:from-purple-950 lsu:to-purple-900 border border-red-200 dark:border-red-800 dracula:border-gray-600 mbp:border-red-900 lsu:border-purple-800 rounded-lg p-6">
              <h4 class="font-semibold text-red-800 dark:text-red-100 dracula:text-cyan-300 mbp:text-red-300 lsu:text-purple-300 mb-3">Caching (Redis)</h4>
              <ul class="text-sm text-red-700 dark:text-red-200 dracula:text-gray-300 mbp:text-gray-300 lsu:text-gray-300 space-y-1">
                <li>• Session management</li>
                <li>• Query result caching</li>
                <li>• Real-time data storage</li>
                <li>• Performance optimization</li>
                <li>• TTL-based expiration</li>
              </ul>
            </div>
            
            <div class="bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-slate-800 dark:to-slate-700 dracula:from-gray-800 dracula:to-gray-700 mbp:from-gray-900 mbp:to-gray-800 lsu:from-purple-950 lsu:to-purple-900 border border-yellow-200 dark:border-yellow-800 dracula:border-gray-600 mbp:border-red-900 lsu:border-purple-800 rounded-lg p-6">
              <h4 class="font-semibold text-yellow-800 dark:text-yellow-100 dracula:text-cyan-300 mbp:text-red-300 lsu:text-purple-300 mb-3">AI/ML (Ollama)</h4>
              <ul class="text-sm text-yellow-700 dark:text-yellow-200 dracula:text-gray-300 mbp:text-gray-300 lsu:text-gray-300 space-y-1">
                <li>• Local LLM inference</li>
                <li>• Text refinement</li>
                <li>• Grammar correction</li>
                <li>• Content enhancement</li>
                <li>• Conservative approach</li>
              </ul>
            </div>
            
            <div class="bg-gradient-to-br from-indigo-50 to-indigo-100 dark:from-slate-800 dark:to-slate-700 dracula:from-gray-800 dracula:to-gray-700 mbp:from-gray-900 mbp:to-gray-800 lsu:from-purple-950 lsu:to-purple-900 border border-indigo-200 dark:border-indigo-800 dracula:border-gray-600 mbp:border-red-900 lsu:border-purple-800 rounded-lg p-6">
              <h4 class="font-semibold text-indigo-800 dark:text-indigo-100 dracula:text-cyan-300 mbp:text-red-300 lsu:text-purple-300 mb-3">Security</h4>
              <ul class="text-sm text-indigo-700 dark:text-indigo-200 dracula:text-gray-300 mbp:text-gray-300 lsu:text-gray-300 space-y-1">
                <li>• JWT token authentication</li>
                <li>• Role-based permissions</li>
                <li>• Input validation</li>
                <li>• HTTPS enforcement</li>
                <li>• Secure file handling</li>
              </ul>
            </div>
          </div>

          <!-- Installation Reference -->
          <div class="bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
            <h4 class="font-semibold text-gray-800 dark:text-gray-200 mb-3 flex items-center">
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              Installation & Setup
            </h4>
            <p class="text-gray-700 dark:text-gray-300 mb-3">
              For detailed installation instructions, deployment guides, and development setup, please refer to our comprehensive documentation on GitHub.
            </p>
            <a 
              href="https://github.com/Ara-Alexandrian/DoR-Dash" 
              target="_blank"
              rel="noopener noreferrer"
              class="inline-flex items-center px-4 py-2 bg-gray-800 dark:bg-gray-700 text-white rounded-lg hover:bg-gray-900 dark:hover:bg-gray-600 transition-colors"
            >
              <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
              </svg>
              View on GitHub
            </a>
          </div>

        </div>
      </div>
    </div>

    <!-- Development Roadmap -->
    <div class="space-y-6" in:fly={{y: 20, duration: 400, delay: 200}}>
      <h2 class="text-2xl font-bold text-[rgb(var(--color-text-primary))]">Development Roadmap</h2>
      <div class="card p-8">
        <div class="space-y-8">
          <!-- Completed Section -->
          <div>
            <h3 class="text-lg font-semibold text-green-600 dark:text-green-400 mb-4 flex items-center">
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              Completed Features
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {#each Object.entries(featureDetails).filter(([_, feature]) => feature.status === 'completed') as [name, feature]}
                <button 
                  on:click={() => openModal(name)}
                  class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors cursor-pointer w-full text-left"
                >
                  <div class="flex items-center text-green-700 dark:text-green-300 font-medium">
                    <div class="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                    {name}
                  </div>
                </button>
              {/each}
            </div>
          </div>

          <!-- In Progress Section -->
          <div>
            <h3 class="text-lg font-semibold text-blue-600 dark:text-blue-400 mb-4 flex items-center">
              <svg class="w-5 h-5 mr-2 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              In Progress
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {#each Object.entries(featureDetails).filter(([_, feature]) => feature.status === 'in_progress') as [name, feature]}
                <button 
                  on:click={() => openModal(name)}
                  class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors cursor-pointer w-full text-left"
                >
                  <div class="flex items-center text-blue-700 dark:text-blue-300 font-medium">
                    <div class="w-2 h-2 bg-blue-500 rounded-full mr-2 animate-pulse"></div>
                    {name}
                  </div>
                </button>
              {/each}
            </div>
          </div>

          <!-- Future Features Section -->
          <div>
            <h3 class="text-lg font-semibold text-purple-600 dark:text-purple-400 mb-4 flex items-center">
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
              </svg>
              Future Features
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {#each Object.entries(featureDetails).filter(([_, feature]) => feature.status === 'future') as [name, feature]}
                <button 
                  on:click={() => openModal(name)}
                  class="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4 hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors cursor-pointer w-full text-left"
                >
                  <div class="flex items-center text-purple-700 dark:text-purple-300 font-medium">
                    <div class="w-2 h-2 bg-purple-500 rounded-full mr-2"></div>
                    {name}
                  </div>
                </button>
              {/each}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Platform Updates -->
    <div class="space-y-6" in:fly={{y: 20, duration: 400, delay: 300}}>
      <h2 class="text-2xl font-bold text-[rgb(var(--color-text-primary))]">Recent Platform Updates</h2>
      <div class="card p-8">
        <div class="space-y-6">
          {#each platformUpdates as update, i}
            <div class="group relative bg-[rgb(var(--color-bg-secondary))] rounded-xl p-6 hover:shadow-lg transition-all duration-300 border border-[rgb(var(--color-border))] hover:border-purple-300 dark:hover:border-purple-600" in:scale={{duration: 300, delay: i * 100}}>
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center gap-3 mb-3">
                    <span class="text-lg font-bold text-purple-600 dark:text-purple-400">
                      {update.version}
                    </span>
                    <span class="text-sm text-gray-500 dark:text-gray-400">
                      {formatDate(update.date)}
                    </span>
                    {#if update.type === 'feature'}
                      <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300">
                        New Feature
                      </span>
                    {:else if update.type === 'enhancement'}
                      <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                        Enhancement
                      </span>
                    {:else if update.type === 'bugfix'}
                      <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300">
                        Bug Fix
                      </span>
                    {/if}
                  </div>
                  <h3 class="text-xl font-semibold text-[rgb(var(--color-text-primary))] mb-3">
                    {update.title}
                  </h3>
                  <ul class="space-y-2">
                    {#each update.changes as change}
                      <li class="flex items-start text-[rgb(var(--color-text-secondary))]">
                        <svg class="h-5 w-5 text-purple-500 mr-3 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span>{change}</span>
                      </li>
                    {/each}
                  </ul>
                </div>
              </div>
            </div>
          {/each}
          
          <div class="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
            <div class="flex items-center justify-between">
              <p class="text-[rgb(var(--color-text-secondary))]">
                View complete changelog and release notes on GitHub
              </p>
              <a 
                href="https://github.com/Ara-Alexandrian/DoR-Dash/releases" 
                target="_blank"
                rel="noopener noreferrer"
                class="inline-flex items-center text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 font-medium group"
              >
                <svg class="h-5 w-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                GitHub Releases
                <svg class="ml-1 h-4 w-4 transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</div>

<!-- Roadmap Feature Modal -->
{#if showModal && selectedFeature}
  <div class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" on:click={closeModal}></div>

      <!-- This element is to trick the browser into centering the modal contents. -->
      <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

      <!-- Modal panel -->
      <div class="inline-block align-bottom bg-white dark:bg-slate-800 rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
        <div class="absolute top-0 right-0 pt-4 pr-4">
          <button type="button" class="bg-white dark:bg-slate-800 rounded-md text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500" on:click={closeModal}>
            <span class="sr-only">Close</span>
            <!-- Heroicon name: outline/x -->
            <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="sm:flex sm:items-start">
          <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
            <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white mb-4" id="modal-title">
              {Object.keys(featureDetails).find(key => featureDetails[key] === selectedFeature)}
            </h3>
            
            <!-- Status badge -->
            <div class="mb-4">
              {#if selectedFeature.status === 'completed'}
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  Completed
                </span>
              {:else if selectedFeature.status === 'in_progress'}
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                  <svg class="w-4 h-4 mr-1 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                  </svg>
                  In Progress
                </span>
              {:else}
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                  </svg>
                  Future
                </span>
              {/if}
            </div>
            
            <!-- Description -->
            <p class="text-sm text-gray-600 dark:text-gray-300 mb-4">
              {selectedFeature.description}
            </p>
            
            <!-- Details list -->
            <div class="space-y-2">
              <h4 class="text-sm font-medium text-gray-900 dark:text-white">Key Features:</h4>
              <ul class="space-y-2">
                {#each selectedFeature.details as detail}
                  <li class="flex items-start text-sm text-gray-600 dark:text-gray-300">
                    <svg class="h-4 w-4 text-primary-500 mr-2 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>{detail}</span>
                  </li>
                {/each}
              </ul>
            </div>
          </div>
        </div>
        <div class="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
          <button type="button" class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-primary-600 text-base font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:ml-3 sm:w-auto sm:text-sm" on:click={closeModal}>
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}

<style>
  /* Mermaid diagram styling */
  .mermaid {
    text-align: center;
  }
  
  :global(.dark) .mermaid {
    filter: invert(0.9) hue-rotate(180deg);
  }
</style>