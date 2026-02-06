# ANPTOP - React Frontend Documentation

## Table of Contents
1. [Project Structure](#project-structure)
2. [Component Architecture](#component-architecture)
3. [Page Layouts](#page-layouts)
4. [State Management](#state-management)
5. [API Integration](#api-integration)
6. [UI Components](#ui-components)
7. [Theming & Styling](#theming--styling)

---

## 1. Project Structure

```
frontend/
├── public/
│   ├── index.html
│   ├── manifest.json
│   └── robots.txt
│
├── src/
│   ├── assets/                   # Static assets
│   │   ├── images/
│   │   ├── icons/
│   │   └── fonts/
│   │
│   ├── components/               # Reusable components
│   │   ├── common/
│   │   │   ├── Button/
│   │   │   ├── Card/
│   │   │   ├── Modal/
│   │   │   ├── Input/
│   │   │   ├── Select/
│   │   │   ├── Checkbox/
│   │   │   ├── Radio/
│   │   │   ├── Table/
│   │   │   ├── Pagination/
│   │   │   ├── Loading/
│   │   │   ├── Alert/
│   │   │   ├── Badge/
│   │   │   ├── Chip/
│   │   │   ├── Tooltip/
│   │   │   ├── Dropdown/
│   │   │   └── Tabs/
│   │   │
│   │   ├── layout/
│   │   │   ├── Header/
│   │   │   ├── Sidebar/
│   │   │   ├── Footer/
│   │   │   ├── MainLayout/
│   │   │   └── AuthLayout/
│   │   │
│   │   ├── forms/
│   │   │   ├── Form/
│   │   │   ├── FormField/
│   │   │   ├── ValidationError/
│   │   │   └── DynamicField/
│   │   │
│   │   ├── data/
│   │   │   ├── DataTable/
│   │   │   ├── FilterBar/
│   │   │   ├── SearchBar/
│   │   │   ├── ColumnSelector/
│   │   │   └── ExportButton/
│   │   │
│   │   ├── charts/
│   │   │   ├── VulnerabilityChart/
│   │   │   ├── HostChart/
│   │   │   ├── TimelineChart/
│   │   │   └── RiskGauge/
│   │   │
│   │   ├── security/
│   │   │   ├── ApprovalDialog/
│   │   │   ├── WarningModal/
│   │   │   ├── ConfirmationDialog/
│   │   │   └── KillSwitch/
│   │   │
│   │   ├── engagement/
│   │   │   ├── ScopeEditor/
│   │   │   ├── HostCard/
│   │   │   ├── PortCard/
│   │   │   ├── ServiceCard/
│   │   │   └── VulnerabilityCard/
│   │   │
│   │   ├── evidence/
│   │   │   ├── EvidenceBrowser/
│   │   │   ├── EvidencePreview/
│   │   │   ├── EvidenceUploader/
│   │   │   └── ChainOfCustody/
│   │   │
│   │   └── feedback/
│   │       ├── Toast/
│   │       ├── NotificationCenter/
│   │       └── ProgressBar/
│   │
│   ├── pages/                    # Page components
│   │   ├── Auth/
│   │   │   ├── Login/
│   │   │   ├── Logout/
│   │   │   ├── Register/
│   │   │   ├── ForgotPassword/
│   │   │   ├── ResetPassword/
│   │   │   └── MFALogin/
│   │   │
│   │   ├── Dashboard/
│   │   │   ├── Dashboard/
│   │   │   ├── Statistics/
│   │   │   └── ActivityFeed/
│   │   │
│   │   ├── Engagements/
│   │   │   ├── EngagementList/
│   │   │   ├── EngagementDetail/
│   │   │   ├── EngagementCreate/
│   │   │   ├── EngagementEdit/
│   │   │   └── EngagementSettings/
│   │   │
│   │   ├── Scans/
│   │   │   ├── ScanProgress/
│   │   │   ├── ScanResults/
│   │   │   ├── ScanHistory/
│   │   │   └── ScanConfig/
│   │   │
│   │   ├── Hosts/
│   │   │   ├── HostList/
│   │   │   ├── HostDetail/
│   │   │   └── HostTimeline/
│   │   │
│   │   ├── Vulnerabilities/
│   │   │   ├── VulnerabilityList/
│   │   │   ├── VulnerabilityDetail/
│   │   │   └── VulnerabilityTimeline/
│   │   │
│   │   ├── Exploitation/
│   │   │   ├── ExploitationDashboard/
│   │   │   ├── ApprovalQueue/
│   │   │   ├── ApprovalDetail/
│   │   │   ├── ExploitResult/
│   │   │   └── SessionManager/
│   │   │
│   │   ├── PostExploitation/
│   │   │   ├── PostExDashboard/
│   │   │   ├── CredentialHarvester/
│   │   │   └── DataCollector/
│   │   │
│   │   ├── LateralMovement/
│   │   │   ├── LateralDashboard/
│   │   │   ├── TargetSelector/
│   │   │   └── MovementTracker/
│   │   │
│   │   ├── Evidence/
│   │   │   ├── EvidenceBrowser/
│   │   │   ├── EvidenceViewer/
│   │   │   └── EvidenceSearch/
│   │   │
│   │   ├── Reports/
│   │   │   ├── ReportList/
│   │   │   ├── ReportGenerator/
│   │   │   ├── ExecutiveReport/
│   │   │   ├── TechnicalReport/
│   │   │   └── ReportPreview/
│   │   │
│   │   ├── Audit/
│   │   │   ├── AuditLog/
│   │   │   ├── AuditDetail/
│   │   │   └── ComplianceReport/
│   │   │
│   │   ├── Settings/
│   │   │   ├── Profile/
│   │   │   ├── Security/
│   │   │   ├── Notifications/
│   │   │   ├── Team/
│   │   │   └── Integrations/
│   │   │
│   │   └── Admin/
│   │       ├── UserManagement/
│   │       ├── RoleManagement/
│   │       ├── SystemConfig/
│   │       └── Analytics/
│   │
│   ├── hooks/                    # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useEngagement.ts
│   │   ├── useScan.ts
│   │   ├── useVulnerability.ts
│   │   ├── useApproval.ts
│   │   ├── useEvidence.ts
│   │   ├── useReport.ts
│   │   ├── useWebSocket.ts
│   │   ├── useDebounce.ts
│   │   ├── useIntersectionObserver.ts
│   │   └── useLocalStorage.ts
│   │
│   ├── services/                 # API services
│   │   ├── api.ts
│   │   ├── auth.service.ts
│   │   ├── engagement.service.ts
│   │   ├── host.service.ts
│   │   ├── port.service.ts
│   │   ├── service.service.ts
│   │   ├── vulnerability.service.ts
│   │   ├── exploit.service.ts
│   │   ├── approval.service.ts
│   │   ├── evidence.service.ts
│   │   ├── report.service.ts
│   │   ├── audit.service.ts
│   │   ├── notification.service.ts
│   │   └── webhook.service.ts
│   │
│   ├── store/                    # State management
│   │   ├── index.ts
│   │   ├── auth/
│   │   ├── engagements/
│   │   ├── scans/
│   │   ├── vulnerabilities/
│   │   ├── approvals/
│   │   ├── evidence/
│   │   ├── notifications/
│   │   └── ui/
│   │
│   ├── types/                    # TypeScript types
│   │   ├── user.ts
│   │   ├── engagement.ts
│   │   ├── host.ts
│   │   ├── port.ts
│   │   ├── service.ts
│   │   ├── vulnerability.ts
│   │   ├── exploit.ts
│   │   ├── evidence.ts
│   │   ├── approval.ts
│   │   ├── report.ts
│   │   ├── audit.ts
│   │   └── common.ts
│   │
│   ├── utils/                    # Utility functions
│   │   ├── format.ts
│   │   ├── validation.ts
│   │   ├── helpers.ts
│   │   ├── constants.ts
│   │   ├── formatters.ts
│   │   └── crypto.ts
│   │
│   ├── styles/                   # Global styles
│   │   ├── main.css
│   │   ├── tailwind.css
│   │   └── variables.css
│   │
│   ├── locales/                  # i18n
│   │   ├── en/
│   │   │   └── translation.json
│   │   └── i18n.ts
│   │
│   ├── App.tsx
│   ├── index.tsx
│   └── react-app-env.d.ts
│
├── .env
├── .env.development
├── .env.production
├── .eslintrc.js
├── .prettierrc
├── tailwind.config.js
├── tsconfig.json
├── package.json
└── README.md
```

---

## 2. Component Architecture

### 2.1 Component Hierarchy
```
App.tsx
├── Providers
│   ├── AuthProvider
│   ├── ThemeProvider
│   ├── ToastProvider
│   └── QueryClientProvider
│
├── Router
│   ├── Public Routes
│   │   ├── Login
│   │   ├── ForgotPassword
│   │   └── Register
│   │
│   └── Private Routes
│       ├── MainLayout
│       │   ├── Header
│       │   ├── Sidebar
│       │   │
│       │   └── Page Content
│       │       ├── Dashboard
│       │       ├── Engagements
│       │       ├── Scans
│       │       ├── Hosts
│       │       ├── Vulnerabilities
│       │       ├── Exploitation
│       │       ├── Evidence
│       │       ├── Reports
│       │       ├── Audit
│       │       └── Settings
│       │
│       └── AuthLayout
│           ├── Login
│           └── MFA Login
```

### 2.2 Reusable Components

#### Button Component
```tsx
// src/components/common/Button/Button.tsx
import React from 'react';
import { cn } from '@/utils/cn';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'warning' | 'success' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  leftIcon,
  rightIcon,
  fullWidth = false,
  className,
  disabled,
  ...props
}) => {
  const baseStyles = `
    inline-flex items-center justify-center font-medium rounded-lg
    transition-all duration-200 ease-in-out
    focus:outline-none focus:ring-2 focus:ring-offset-2
    disabled:opacity-50 disabled:cursor-not-allowed
  `;

  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
    warning: 'bg-yellow-500 text-white hover:bg-yellow-600 focus:ring-yellow-500',
    success: 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-500',
    ghost: 'bg-transparent text-gray-700 hover:bg-gray-100 focus:ring-gray-500',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  return (
    <button
      className={cn(
        baseStyles,
        variants[variant],
        sizes[size],
        fullWidth && 'w-full',
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      ) : leftIcon ? (
        <span className="mr-2">{leftIcon}</span>
      ) : null}
      {children}
      {rightIcon && !loading && <span className="ml-2">{rightIcon}</span>}
    </button>
  );
};
```

#### Modal Component
```tsx
// src/components/common/Modal/Modal.tsx
import React, { useEffect } from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';
import { cn } from '@/utils/cn';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  showCloseButton?: boolean;
  closeOnOverlay?: boolean;
  closeOnEscape?: boolean;
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  showCloseButton = true,
  closeOnOverlay = true,
  closeOnEscape = true,
}) => {
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && closeOnEscape) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, closeOnEscape, onClose]);

  if (!isOpen) return null;

  const sizes = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    full: 'max-w-4xl',
  };

  const modalContent = (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={closeOnOverlay ? onClose : undefined}
      />

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div
          className={cn(
            'relative w-full bg-white rounded-lg shadow-xl transform transition-all',
            sizes[size]
          )}
        >
          {/* Header */}
          {(title || showCloseButton) && (
            <div className="flex items-center justify-between p-4 border-b">
              {title && (
                <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
              )}
              {showCloseButton && (
                <button
                  onClick={onClose}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              )}
            </div>
          )}

          {/* Content */}
          <div className="p-4">{children}</div>
        </div>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
};
```

---

## 3. Page Layouts

### 3.1 Main Layout
```tsx
// src/components/layout/MainLayout/MainLayout.tsx
import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Header } from '../Header';
import { Sidebar } from '../Sidebar';
import { ToastContainer } from '@/components/feedback/Toast';
import { NotificationCenter } from '@/components/feedback/NotificationCenter';

export const MainLayout: React.FC = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [sidebarMobileOpen, setSidebarMobileOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar overlay */}
      {sidebarMobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setSidebarMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <Sidebar
        collapsed={sidebarCollapsed}
        mobileOpen={sidebarMobileOpen}
        onMobileClose={() => setSidebarMobileOpen(false)}
      />

      {/* Main content area */}
      <div
        className={cn(
          'min-h-screen transition-all duration-300',
          sidebarCollapsed ? 'lg:pl-20' : 'lg:pl-64'
        )}
      >
        {/* Header */}
        <Header
          onMenuClick={() => setSidebarMobileOpen(true)}
          onCollapseClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          sidebarCollapsed={sidebarCollapsed}
        />

        {/* Page content */}
        <main className="p-6">
          <Outlet />
        </main>
      </div>

      {/* Toast notifications */}
      <ToastContainer />
      <NotificationCenter />
    </div>
  );
};
```

### 3.2 Dashboard Page
```tsx
// src/pages/Dashboard/Dashboard.tsx
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  Bug, 
  Shield, 
  AlertTriangle, 
  CheckCircle,
  Activity,
  Users,
  Clock,
  TrendingUp
} from 'lucide-react';
import { EngagementService } from '@/services/engagement.service';
import { VulnerabilityChart } from '@/components/charts/VulnerabilityChart';
import { RiskGauge } from '@/components/charts/RiskGauge';
import { RecentActivity } from '@/components/Dashboard/RecentActivity';
import { StatisticsCard } from '@/components/Dashboard/StatisticsCard';
import { EngagementProgress } from '@/components/Dashboard/EngagementProgress';

export const Dashboard: React.FC = () => {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboardStats'],
    queryFn: () => EngagementService.getDashboardStats(),
  });

  if (isLoading) {
    return <DashboardSkeleton />;
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500">Overview of your security assessment activities</p>
      </div>

      {/* Statistics grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatisticsCard
          title="Active Engagements"
          value={stats?.activeEngagements || 0}
          icon={Activity}
          color="blue"
          trend={{ value: 12, direction: 'up' }}
        />
        <StatisticsCard
          title="Critical Vulnerabilities"
          value={stats?.criticalCount || 0}
          icon={AlertTriangle}
          color="red"
          trend={{ value: 5, direction: 'down' }}
        />
        <StatisticsCard
          title="Hosts Scanned"
          value={stats?.hostsScanned || 0}
          icon={Shield}
          color="green"
        />
        <StatisticsCard
          title="Pending Approvals"
          value={stats?.pendingApprovals || 0}
          icon={Clock}
          color="yellow"
          alert={stats?.pendingApprovals > 0}
        />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Vulnerability distribution */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Vulnerability Distribution
          </h2>
          <VulnerabilityChart
            data={stats?.vulnerabilityDistribution}
            height={300}
          />
        </div>

        {/* Risk gauge */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Overall Risk Score
          </h2>
          <RiskGauge
            score={stats?.overallRiskScore || 0}
            size={300}
            showDetails
          />
        </div>
      </div>

      {/* Engagement progress */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Active Engagements Progress
        </h2>
        <EngagementProgress engagements={stats?.activeEngagementDetails || []} />
      </div>

      {/* Recent activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Recent Activity
          </h2>
          <RecentActivity activities={stats?.recentActivity || []} />
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Team Activity
          </h2>
          <TeamActivity activity={stats?.teamActivity || []} />
        </div>
      </div>
    </div>
  );
};
```

### 3.3 Engagement Detail Page
```tsx
// src/pages/Engagements/EngagementDetail.tsx
import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  ArrowLeft,
  Play,
  Pause,
  Download,
  Settings,
  Users,
  Calendar,
  Target,
  Shield,
  Bug,
  Activity,
} from 'lucide-react';
import { EngagementService } from '@/services/engagement.service';
import { Button } from '@/components/common/Button';
import { Tabs } from '@/components/common/Tabs';
import { ProgressBar } from '@/components/feedback/ProgressBar';
import { HostCard } from '@/components/engagement/HostCard';
import { VulnerabilityCard } from '@/components/engagement/VulnerabilityCard';

export const EngagementDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');

  const { data: engagement, isLoading } = useQuery({
    queryKey: ['engagement', id],
    queryFn: () => EngagementService.getEngagement(id!),
    enabled: !!id,
  });

  const startMutation = useMutation({
    mutationFn: () => EngagementService.startEngagement(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['engagement', id] });
    },
  });

  const pauseMutation = useMutation({
    mutationFn: () => EngagementService.pauseEngagement(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['engagement', id] });
    },
  });

  if (isLoading) {
    return <EngagementDetailSkeleton />;
  }

  if (!engagement) {
    return <NotFound />;
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'hosts', label: 'Hosts', icon: Target },
    { id: 'vulnerabilities', label: 'Vulnerabilities', icon: Bug },
    { id: 'scans', label: 'Scans', icon: Shield },
    { id: 'timeline', label: 'Timeline', icon: Calendar },
    { id: 'team', label: 'Team', icon: Users },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/engagements')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{engagement.name}</h1>
            <p className="text-gray-500">{engagement.client_name}</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {engagement.status === 'approved' && (
            <Button
              variant="primary"
              leftIcon={<Play className="w-4 h-4" />}
              onClick={() => startMutation.mutate()}
              loading={startMutation.isPending}
            >
              Start Engagement
            </Button>
          )}
          {engagement.status === 'in_progress' && (
            <Button
              variant="warning"
              leftIcon={<Pause className="w-4 h-4" />}
              onClick={() => pauseMutation.mutate()}
              loading={pauseMutation.isPending}
            >
              Pause
            </Button>
          )}
          <Button
            variant="secondary"
            leftIcon={<Download className="w-4 h-4" />}
          >
            Export
          </Button>
          <Button
            variant="ghost"
            leftIcon={<Settings className="w-4 h-4" />}
          >
            Settings
          </Button>
        </div>
      </div>

      {/* Status and progress */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <EngagementStatusBadge status={engagement.status} />
            {engagement.status === 'in_progress' && (
              <ProgressBar
                progress={engagement.progress}
                size="sm"
                showLabel
              />
            )}
          </div>
          <div className="text-sm text-gray-500">
            Started: {formatDate(engagement.start_date)}
          </div>
        </div>

        {/* Stats grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatItem label="Hosts" value={engagement.host_count} icon={Target} />
          <StatItem
            label="Critical"
            value={engagement.critical_count}
            icon={AlertTriangle}
            color="red"
          />
          <StatItem label="High" value={engagement.high_count} icon={Bug} color="orange" />
          <StatItem
            label="Medium"
            value={engagement.medium_count}
            icon={Shield}
            color="yellow"
          />
        </div>
      </div>

      {/* Tabs */}
      <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab}>
        {activeTab === 'overview' && (
          <EngagementOverviewTab engagement={engagement} />
        )}
        {activeTab === 'hosts' && (
          <HostsTab engagementId={engagement.id} />
        )}
        {activeTab === 'vulnerabilities' && (
          <VulnerabilitiesTab engagementId={engagement.id} />
        )}
        {activeTab === 'scans' && (
          <ScansTab engagementId={engagement.id} />
        )}
        {activeTab === 'timeline' && (
          <TimelineTab engagementId={engagement.id} />
        )}
        {activeTab === 'team' && (
          <TeamTab engagement={engagement} />
        )}
      </Tabs>
    </div>
  );
};
```

---

## 4. State Management

### 4.1 Zustand Store Setup
```tsx
// src/store/index.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { authStore } from './auth';
import { engagementStore } from './engagements';
import { scanStore } from './scans';
import { vulnerabilityStore } from './vulnerabilities';
import { approvalStore } from './approvals';
import { evidenceStore } from './evidence';
import { notificationStore } from './notifications';
import { uiStore } from './ui';

export const useAppStore = create<
  typeof authStore &
  typeof engagementStore &
  typeof scanStore &
  typeof vulnerabilityStore &
  typeof approvalStore &
  typeof evidenceStore &
  typeof notificationStore &
  typeof uiStore
>()((...args) => ({
  ...authStore(...args),
  ...engagementStore(...args),
  ...scanStore(...args),
  ...vulnerabilityStore(...args),
  ...approvalStore(...args),
  ...evidenceStore(...args),
  ...notificationStore(...args),
  ...uiStore(...args),
}));

// Root store type
export type AppStore = ReturnType<typeof useAppStore>;
```

### 4.2 Engagement Store
```tsx
// src/store/engagements/index.ts
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { EngagementService } from '@/services/engagement.service';
import { Engagement, EngagementFilters } from '@/types';

interface EngagementState {
  // Data
  engagements: Engagement[];
  currentEngagement: Engagement | null;
  
  // Pagination
  total: number;
  skip: number;
  limit: number;
  
  // Filters
  filters: EngagementFilters;
  
  // UI State
  isLoading: boolean;
  error: string | null;
  
  // Actions
  fetchEngagements: (filters?: EngagementFilters) => Promise<void>;
  fetchEngagement: (id: string) => Promise<void>;
  createEngagement: (data: Partial<Engagement>) => Promise<Engagement>;
  updateEngagement: (id: string, data: Partial<Engagement>) => Promise<void>;
  deleteEngagement: (id: string) => Promise<void>;
  setFilters: (filters: Partial<EngagementFilters>) => void;
  clearError: () => void;
}

export const engagementStore = create<EngagementState>()(
  devtools(
    (set, get) => ({
      // Initial state
      engagements: [],
      currentEngagement: null,
      total: 0,
      skip: 0,
      limit: 20,
      filters: {},
      isLoading: false,
      error: null,

      // Actions
      fetchEngagements: async (filters = {}) => {
        set({ isLoading: true, error: null });
        try {
          const { filters: currentFilters, skip, limit } = get();
          const response = await EngagementService.listEngagements({
            ...currentFilters,
            ...filters,
            skip,
            limit,
          });
          set({
            engagements: response.data,
            total: response.total,
            isLoading: false,
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch engagements',
            isLoading: false,
          });
        }
      },

      fetchEngagement: async (id: string) => {
        set({ isLoading: true, error: null });
        try {
          const engagement = await EngagementService.getEngagement(id);
          set({ currentEngagement: engagement, isLoading: false });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch engagement',
            isLoading: false,
          });
        }
      },

      createEngagement: async (data: Partial<Engagement>) => {
        set({ isLoading: true, error: null });
        try {
          const engagement = await EngagementService.createEngagement(data);
          set((state) => ({
            engagements: [engagement, ...state.engagements],
            total: state.total + 1,
            isLoading: false,
          }));
          return engagement;
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to create engagement',
            isLoading: false,
          });
          throw error;
        }
      },

      updateEngagement: async (id: string, data: Partial<Engagement>) => {
        set({ isLoading: true, error: null });
        try {
          const updated = await EngagementService.updateEngagement(id, data);
          set((state) => ({
            engagements: state.engagements.map((e) =>
              e.id === id ? updated : e
            ),
            currentEngagement:
              state.currentEngagement?.id === id
                ? updated
                : state.currentEngagement,
            isLoading: false,
          }));
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to update engagement',
            isLoading: false,
          });
          throw error;
        }
      },

      deleteEngagement: async (id: string) => {
        set({ isLoading: true, error: null });
        try {
          await EngagementService.deleteEngagement(id);
          set((state) => ({
            engagements: state.engagements.filter((e) => e.id !== id),
            total: state.total - 1,
            currentEngagement:
              state.currentEngagement?.id === id ? null : state.currentEngagement,
            isLoading: false,
          }));
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to delete engagement',
            isLoading: false,
          });
          throw error;
        }
      },

      setFilters: (filters: Partial<EngagementFilters>) => {
        set((state) => ({
          filters: { ...state.filters, ...filters },
        }));
        get().fetchEngagements();
      },

      clearError: () => {
        set({ error: null });
      },
    }),
    { name: 'engagement-store' }
  )
);
```

---

## 5. API Integration

### 5.1 API Client Setup
```tsx
// src/services/api.ts
import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '@/store/auth';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = useAuthStore.getState().accessToken;
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error: AxiosError) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

        // Handle 401 Unauthorized
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = useAuthStore.getState().refreshToken;
            if (refreshToken) {
              const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
                refresh_token: refreshToken,
              });

              const { access_token, refresh_token } = response.data;
              useAuthStore.getState().setTokens(access_token, refresh_token);

              originalRequest.headers.Authorization = `Bearer ${access_token}`;
              return this.client(originalRequest);
            }
          } catch (refreshError) {
            useAuthStore.getState().logout();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        // Handle other errors
        const errorMessage =
          (error.response?.data as any)?.detail ||
          error.message ||
          'An unexpected error occurred';

        return Promise.reject(new Error(errorMessage));
      }
    );
  }

  // HTTP methods
  async get<T>(url: string, params?: object): Promise<T> {
    const response = await this.client.get<T>(url, { params });
    return response.data;
  }

  async post<T>(url: string, data?: object): Promise<T> {
    const response = await this.client.post<T>(url, data);
    return response.data;
  }

  async put<T>(url: string, data?: object): Promise<T> {
    const response = await this.client.put<T>(url, data);
    return response.data;
  }

  async patch<T>(url: string, data?: object): Promise<T> {
    const response = await this.client.patch<T>(url, data);
    return response.data;
  }

  async delete<T>(url: string): Promise<T> {
    const response = await this.client.delete<T>(url);
    return response.data;
  }

  // File upload
  async upload<T>(url: string, file: File, onProgress?: (progress: number) => void): Promise<T> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post<T>(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });

    return response.data;
  }
}

export const api = new ApiClient();
```

### 5.2 Engagement Service
```tsx
// src/services/engagement.service.ts
import { api } from './api';
import {
  Engagement,
  EngagementCreate,
  EngagementUpdate,
  EngagementFilters,
  PaginatedResponse,
} from '@/types';

const ENGAGEMENTS_ENDPOINT = '/engagements';

export const EngagementService = {
  async listEngagements(
    filters?: EngagementFilters
  ): Promise<PaginatedResponse<Engagement>> {
    return api.get<PaginatedResponse<Engagement>>(ENGAGEMENTS_ENDPOINT, {
      skip: filters?.skip || 0,
      limit: filters?.limit || 20,
      status: filters?.status,
      client_name: filters?.clientName,
    });
  },

  async getEngagement(id: string): Promise<Engagement> {
    return api.get<Engagement>(`${ENGAGEMENTS_ENDPOINT}/${id}`);
  },

  async createEngagement(data: EngagementCreate): Promise<Engagement> {
    return api.post<Engagement>(ENGAGEMENTS_ENDPOINT, data);
  },

  async updateEngagement(id: string, data: EngagementUpdate): Promise<Engagement> {
    return api.put<Engagement>(`${ENGAGEMENTS_ENDPOINT}/${id}`, data);
  },

  async deleteEngagement(id: string): Promise<void> {
    return api.delete(`${ENGAGEMENTS_ENDPOINT}/${id}`);
  },

  async startEngagement(id: string): Promise<void> {
    return api.post(`${ENGAGEMENTS_ENDPOINT}/${id}/start`);
  },

  async pauseEngagement(id: string, reason: string): Promise<void> {
    return api.post(`${ENGAGEMENTS_ENDPOINT}/${id}/pause`, { reason });
  },

  async resumeEngagement(id: string): Promise<void> {
    return api.post(`${ENGAGEMENTS_ENDPOINT}/${id}/resume`);
  },

  async completeEngagement(id: string): Promise<void> {
    return api.post(`${ENGAGEMENTS_ENDPOINT}/${id}/complete`);
  },

  async getEngagementSummary(id: string): Promise<EngagementSummary> {
    return api.get(`${ENGAGEMENTS_ENDPOINT}/${id}/summary`);
  },

  async getEngagementHosts(
    id: string,
    filters?: { skip?: number; limit?: number; aliveOnly?: boolean }
  ): Promise<PaginatedResponse<Host>> {
    return api.get(`${ENGAGEMENTS_ENDPOINT}/${id}/hosts`, filters);
  },

  async getEngagementVulnerabilities(
    id: string,
    filters?: { skip?: number; limit?: number; severity?: string }
  ): Promise<PaginatedResponse<Vulnerability>> {
    return api.get(`${ENGAGEMENTS_ENDPOINT}/${id}/vulnerabilities`, filters);
  },

  async getEngagementTimeline(id: string): Promise<TimelineEvent[]> {
    return api.get(`${ENGAGEMENTS_ENDPOINT}/${id}/timeline`);
  },

  async getDashboardStats(): Promise<DashboardStats> {
    return api.get('/dashboard/stats');
  },
};
```

---

## 6. UI Components

### 6.1 Approval Dialog
```tsx
// src/components/security/ApprovalDialog.tsx
import React, { useState } from 'react';
import { AlertTriangle, Shield, Lock } from 'lucide-react';
import { Button } from '@/components/common/Button';
import { Modal } from '@/components/common/Modal';
import { Input } from '@/components/common/Input';
import { Textarea } from '@/components/common/Textarea';
import { cn } from '@/utils/cn';

interface ApprovalDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onApprove: (comments: string, justification: string) => void;
  onReject: (reason: string) => void;
  approval: {
    title: string;
    description: string;
    riskLevel: 'low' | 'medium' | 'high' | 'critical';
    requiredApprovers: number;
    currentApprovers: number;
    expiresAt: string;
    target: {
      type: string;
      value: string;
    };
  };
}

export const ApprovalDialog: React.FC<ApprovalDialogProps> = ({
  isOpen,
  onClose,
  onApprove,
  onReject,
  approval,
}) => {
  const [mode, setMode] = useState<'approve' | 'reject'>('approve');
  const [comments, setComments] = useState('');
  const [justification, setJustification] = useState('');
  const [reason, setReason] = useState('');
  const [agreedToWarning, setAgreedToWarning] = useState(false);

  const riskColors = {
    low: 'bg-green-100 text-green-800 border-green-200',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    high: 'bg-orange-100 text-orange-800 border-orange-200',
    critical: 'bg-red-100 text-red-800 border-red-200',
  };

  const riskIcons = {
    low: Shield,
    medium: AlertTriangle,
    high: AlertTriangle,
    critical: Lock,
  };

  const isFormValid =
    mode === 'approve'
      ? comments.length > 0 && justification.length > 0 && agreedToWarning
      : reason.length > 10;

  const handleApprove = () => {
    onApprove(comments, justification);
    setMode('approve');
    setComments('');
    setJustification('');
    setAgreedToWarning(false);
  };

  const handleReject = () => {
    onReject(reason);
    setMode('approve');
    setReason('');
  };

  const RiskIcon = riskIcons[approval.riskLevel];

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Action Approval Required"
      size="lg"
    >
      <div className="space-y-6">
        {/* Risk indicator */}
        <div className={cn(
          'p-4 rounded-lg border flex items-center space-x-3',
          riskColors[approval.riskLevel]
        )}>
          <RiskIcon className="w-6 h-6" />
          <div>
            <p className="font-semibold">
              Risk Level: {approval.riskLevel.toUpperCase()}
            </p>
            <p className="text-sm">
              {approval.riskLevel === 'critical' &&
                'This action requires approval from 2 authorized personnel'}
              {approval.riskLevel === 'high' &&
                'This action requires additional justification'}
            </p>
          </div>
        </div>

        {/* Action details */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-2">{approval.title}</h4>
          <p className="text-gray-600 text-sm mb-3">{approval.description}</p>
          <div className="flex items-center text-sm text-gray-500 space-x-4">
            <span>Target: {approval.target.type}: {approval.target.value}</span>
            <span>Expires: {new Date(approval.expiresAt).toLocaleString()}</span>
          </div>
        </div>

        {/* Mode selection */}
        <div className="flex space-x-3">
          <button
            type="button"
            onClick={() => setMode('approve')}
            className={cn(
              'flex-1 py-3 rounded-lg border-2 font-medium transition-colors',
              mode === 'approve'
                ? 'border-green-500 bg-green-50 text-green-700'
                : 'border-gray-200 hover:border-gray-300'
            )}
          >
            Approve
          </button>
          <button
            type="button"
            onClick={() => setMode('reject')}
            className={cn(
              'flex-1 py-3 rounded-lg border-2 font-medium transition-colors',
              mode === 'reject'
                ? 'border-red-500 bg-red-50 text-red-700'
                : 'border-gray-200 hover:border-gray-300'
            )}
          >
            Reject
          </button>
        </div>

        {/* Approval form */}
        {mode === 'approve' && (
          <div className="space-y-4">
            <Textarea
              label="Operational Notes"
              placeholder="Describe what will be done and expected outcomes..."
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              rows={3}
            />
            <Textarea
              label="Business Justification"
              placeholder="Explain why this action is necessary for the assessment..."
              value={justification}
              onChange={(e) => setJustification(e.target.value)}
              rows={3}
            />
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <label className="flex items-start space-x-3">
                <input
                  type="checkbox"
                  checked={agreedToWarning}
                  onChange={(e) => setAgreedToWarning(e.target.checked)}
                  className="mt-1"
                />
                <span className="text-sm text-yellow-800">
                  I acknowledge that this action may impact system availability
                  and that I have verified the target is within the approved scope.
                  I understand this action is being logged for audit purposes.
                </span>
              </label>
            </div>
          </div>
        )}

        {/* Rejection form */}
        {mode === 'reject' && (
          <div className="space-y-4">
            <Textarea
              label="Rejection Reason"
              placeholder="Provide a detailed reason for rejection..."
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows={4}
            />
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-end space-x-3 pt-4 border-t">
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          {mode === 'approve' ? (
            <Button
              variant="primary"
              onClick={handleApprove}
              disabled={!isFormValid}
              className="bg-green-600 hover:bg-green-700"
            >
              Approve Action
            </Button>
          ) : (
            <Button
              variant="danger"
              onClick={handleReject}
              disabled={!isFormValid}
            >
              Reject Request
            </Button>
          )}
        </div>
      </div>
    </Modal>
  );
};
```

---

## 7. Theming & Styling

### 7.1 Tailwind Configuration
```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Primary colors
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        // Status colors
        success: {
          50: '#f0fdf4',
          500: '#22c55e',
          600: '#16a34a',
        },
        warning: {
          50: '#fefce8',
          500: '#eab308',
          600: '#ca8a04',
        },
        danger: {
          50: '#fef2f2',
          500: '#ef4444',
          600: '#dc2626',
        },
        // Neutral
        gray: {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#111827',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Menlo', 'Monaco', 'monospace'],
      },
      boxShadow: {
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)',
        'card-hover': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 3s linear infinite',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
  ],
};
```

### 7.2 CSS Variables
```css
/* src/styles/variables.css */
:root {
  /* Colors */
  --color-primary-50: #eff6ff;
  --color-primary-500: #3b82f6;
  --color-primary-600: #2563eb;
  --color-primary-700: #1d4ed8;
  
  --color-success-500: #22c55e;
  --color-success-600: #16a34a;
  
  --color-warning-500: #eab308;
  --color-warning-600: #ca8a04;
  
  --color-danger-500: #ef4444;
  --color-danger-600: #dc2626;
  
  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  
  /* Border radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-xl: 0.75rem;
  --radius-full: 9999px;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  
  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-normal: 300ms ease;
  --transition-slow: 500ms ease;
}

.dark {
  --color-bg-primary: #111827;
  --color-bg-secondary: #1f2937;
  --color-bg-tertiary: #374151;
  
  --color-text-primary: #f9fafb;
  --color-text-secondary: #d1d5db;
  --color-text-muted: #9ca3af;
}
```

---

## 8. Custom Hooks

### 8.1 Authentication Hook
```tsx
// src/hooks/useAuth.ts
import { useCallback } from 'react';
import { useAuthStore } from '@/store/auth';
import { useNavigate } from 'react-router-dom';
import { AuthService } from '@/services/auth.service';
import { useToast } from './useToast';

export const useAuth = () => {
  const navigate = useNavigate();
  const { addToast } = useToast();
  
  const {
    user,
    isAuthenticated,
    isLoading,
    accessToken,
    login: storeLogin,
    logout: storeLogout,
    setUser,
  } = useAuthStore();

  const login = useCallback(
    async (credentials: { username: string; password: string }) => {
      try {
        const response = await AuthService.login(credentials);
        
        if (response.mfa_required) {
          navigate('/mfa', {
            state: { mfaToken: response.mfa_token },
          });
          return { mfaRequired: true };
        }
        
        storeLogin(response.access_token, response.refresh_token);
        setUser(response.user);
        
        addToast({
          type: 'success',
          title: 'Login Successful',
          message: `Welcome back, ${response.user.first_name}!`,
        });
        
        navigate('/dashboard');
        return { success: true };
      } catch (error) {
        addToast({
          type: 'error',
          title: 'Login Failed',
          message: error instanceof Error ? error.message : 'Invalid credentials',
        });
        return { success: false, error };
      }
    },
    [navigate, storeLogin, setUser, addToast]
  );

  const logout = useCallback(async () => {
    try {
      await AuthService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    }
    
    storeLogout();
    
    addToast({
      type: 'info',
      title: 'Logged Out',
      message: 'You have been successfully logged out.',
    });
    
    navigate('/login');
  }, [storeLogout, navigate, addToast]);

  const refreshToken = useCallback(async () => {
    try {
      const response = await AuthService.refreshToken();
      storeLogin(response.access_token, response.refresh_token);
      return response.access_token;
    } catch (error) {
      logout();
      throw error;
    }
  }, [storeLogin, logout]);

  return {
    user,
    isAuthenticated,
    isLoading,
    accessToken,
    login,
    logout,
    refreshToken,
  };
};
```

### 8.2 WebSocket Hook
```tsx
// src/hooks/useWebSocket.ts
import { useEffect, useRef, useCallback, useState } from 'react';
import SockJS from 'sockjs-client';
import { Client, IMessage } from '@stomp/stompjs';
import { useAuthStore } from '@/store/auth';

interface UseWebSocketOptions {
  onMessage?: (topic: string, data: any) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: any) => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export const useWebSocket = (options: UseWebSocketOptions = {}) => {
  const {
    onMessage,
    onConnect,
    onDisconnect,
    onError,
    reconnectInterval = 5000,
    maxReconnectAttempts = 5,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  
  const clientRef = useRef<Client | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const subscriptionRef = useRef<any>(null);

  const { accessToken } = useAuthStore();

  const connect = useCallback(() => {
    if (clientRef.current?.connected) {
      return;
    }

    const client = new Client({
      webSocketFactory: () =>
        new SockJS(`${import.meta.env.VITE_WS_URL}/ws`, null, {
          transports: ['websocket'],
        }),
      connectHeaders: {
        Authorization: `Bearer ${accessToken}`,
      },
      reconnectDelay: reconnectInterval,
      heartbeatIncoming: 4000,
      heartbeatOutgoing: 4000,
      onConnect: () => {
        setIsConnected(true);
        setConnectionError(null);
        reconnectAttemptsRef.current = 0;
        onConnect?.();
      },
      onDisconnect: () => {
        setIsConnected(false);
        onDisconnect?.();
      },
      onStompError: (frame) => {
        setConnectionError(frame.headers['message']);
        onError?.(frame);
      },
      onMessage: (message: IMessage) => {
        const topic = message.headers.destination;
        const data = JSON.parse(message.body);
        onMessage?.(topic, data);
      },
    });

    clientRef.current = client;
    client.activate();
  }, [accessToken, reconnectInterval, onConnect, onDisconnect, onError, onMessage]);

  const disconnect = useCallback(() => {
    if (clientRef.current) {
      if (subscriptionRef.current) {
        subscriptionRef.current.unsubscribe();
      }
      clientRef.current.deactivate();
      clientRef.current = null;
    }
  }, []);

  const subscribe = useCallback(
    (topic: string) => {
      if (clientRef.current?.connected) {
        subscriptionRef.current = clientRef.current.subscribe(topic, (message: IMessage) => {
          const data = JSON.parse(message.body);
          onMessage?.(topic, data);
        });
      }
    },
    [onMessage]
  );

  const send = useCallback((destination: string, body: any) => {
    if (clientRef.current?.connected) {
      clientRef.current.publish({
        destination,
        body: JSON.stringify(body),
      });
    }
  }, []);

  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    connectionError,
    connect,
    disconnect,
    subscribe,
    send,
  };
};
```

---

**Document Version**: 1.0  
**Last Updated**: 2024-02-06  
**Classification**: Internal Use Only
