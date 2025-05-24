import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Area,
  AreaChart,
  ComposedChart,
} from 'recharts';
import {
  Globe,
  Shield,
  AlertTriangle,
  TrendingUp,
  Users,
  Server,
  Eye,
  Settings,
  Download,
  Search,
  Filter,
  RefreshCw,
  ChevronDown,
  ChevronRight,
  ExternalLink,
  Clock,
  Map,
  LogIn,
  LogOut,
  User,
  Mail,
  Lock,
  Calendar,
  FileText,
  PieChart as PieChartIcon,
  BarChart3,
  Activity,
  Bell,
} from 'lucide-react';

// Mock authentication and data
const mockUsers = [
  {
    email: 'admin@example.com',
    password: 'admin123',
    role: 'admin',
    name: 'Admin User',
  },
  {
    email: 'manager@example.com',
    password: 'manager123',
    role: 'manager',
    name: 'Manager User',
  },
];

const mockData = {
  overview: {
    totalWebsites: 12547,
    activeScans: 234,
    violationsToday: 1829,
    successRate: 94.2,
    totalScans: 45621,
    avgViolationsPerSite: 3.4,
    criticalViolations: 89,
    resolvedViolations: 2341,
  },
  violations: [
    {
      name: 'Specific Retention Exceed',
      value: 542,
      color: '#ef4444',
      severity: 'critical',
    },
    {
      name: 'Third-party Undeclared',
      value: 389,
      color: '#f97316',
      severity: 'high',
    },
    {
      name: 'General Purpose Mismatch',
      value: 278,
      color: '#eab308',
      severity: 'medium',
    },
    {
      name: 'Session Cookie Persist',
      value: 256,
      color: '#06b6d4',
      severity: 'medium',
    },
    {
      name: 'Undefined Behavior',
      value: 234,
      color: '#8b5cf6',
      severity: 'high',
    },
    {
      name: 'Cross-site Tracking',
      value: 130,
      color: '#10b981',
      severity: 'low',
    },
  ],
  trends: [
    { date: '2024-05-17', violations: 1245, scans: 3420, compliance: 89.2 },
    { date: '2024-05-18', violations: 1389, scans: 3651, compliance: 87.8 },
    { date: '2024-05-19', violations: 1456, scans: 3892, compliance: 86.5 },
    { date: '2024-05-20', violations: 1523, scans: 4123, compliance: 85.1 },
    { date: '2024-05-21', violations: 1678, scans: 4356, compliance: 83.7 },
    { date: '2024-05-22', violations: 1789, scans: 4587, compliance: 82.3 },
    { date: '2024-05-23', violations: 1829, scans: 4621, compliance: 81.9 },
  ],
  topViolators: [
    {
      domain: 'shopping-giant.com',
      violations: 43,
      severity: 'critical',
      lastScan: '2024-05-23 14:30',
      complianceScore: 45.2,
      violationTypes: [
        'Retention Exceed',
        'Third-party Undeclared',
        'Purpose Mismatch',
      ],
    },
    {
      domain: 'news-portal.net',
      violations: 29,
      severity: 'high',
      lastScan: '2024-05-23 13:45',
      complianceScore: 67.8,
      violationTypes: ['Session Persist', 'Cross-site Tracking'],
    },
    {
      domain: 'social-media.io',
      violations: 27,
      severity: 'high',
      lastScan: '2024-05-23 12:20',
      complianceScore: 71.3,
      violationTypes: ['Third-party Undeclared', 'Undefined Behavior'],
    },
    {
      domain: 'e-commerce.org',
      violations: 25,
      severity: 'medium',
      lastScan: '2024-05-23 11:15',
      complianceScore: 78.9,
      violationTypes: ['Purpose Mismatch', 'Retention Exceed'],
    },
    {
      domain: 'blog-platform.com',
      violations: 22,
      severity: 'medium',
      lastScan: '2024-05-23 10:30',
      complianceScore: 82.1,
      violationTypes: ['Session Persist'],
    },
  ],
  trackers: [
    {
      name: 'Google Analytics',
      websites: 8547,
      violations: 334,
      riskLevel: 'medium',
    },
    {
      name: 'Facebook Pixel',
      websites: 6234,
      violations: 289,
      riskLevel: 'high',
    },
    { name: 'Google Ads', websites: 4521, violations: 256, riskLevel: 'high' },
    {
      name: 'Amazon Associates',
      websites: 3456,
      violations: 198,
      riskLevel: 'medium',
    },
    {
      name: 'Twitter Analytics',
      websites: 2890,
      violations: 167,
      riskLevel: 'low',
    },
    {
      name: 'Adobe Analytics',
      websites: 2345,
      violations: 134,
      riskLevel: 'medium',
    },
  ],
  recentActivity: [
    {
      time: '2 min ago',
      action: 'Critical violation detected',
      website: 'shopping-giant.com',
      type: 'critical',
    },
    {
      time: '5 min ago',
      action: 'Scan completed successfully',
      website: 'test-site.org',
      type: 'success',
    },
    {
      time: '8 min ago',
      action: 'Policy extraction failed',
      website: 'broken-site.net',
      type: 'error',
    },
    {
      time: '12 min ago',
      action: 'New website registered',
      website: 'fresh-site.com',
      type: 'info',
    },
    {
      time: '15 min ago',
      action: 'Violation resolved',
      website: 'fixed-site.com',
      type: 'resolved',
    },
    {
      time: '18 min ago',
      action: 'Compliance check passed',
      website: 'good-site.net',
      type: 'success',
    },
  ],
  complianceHistory: [
    { month: 'Jan', compliant: 78, nonCompliant: 22 },
    { month: 'Feb', compliant: 82, nonCompliant: 18 },
    { month: 'Mar', compliant: 79, nonCompliant: 21 },
    { month: 'Apr', compliant: 85, nonCompliant: 15 },
    { month: 'May', compliant: 81, nonCompliant: 19 },
  ],
};

const Card = ({ children, className = '', hover = false }) => (
  <div
    className={`bg-white rounded-xl shadow-lg border border-gray-100 ${
      hover ? 'hover:shadow-xl hover:scale-105' : ''
    } transition-all duration-300 ${className}`}
  >
    {children}
  </div>
);

const MetricCard = ({
  icon: Icon,
  title,
  value,
  change,
  color = 'blue',
  subtitle,
}) => {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600 border-blue-200',
    green: 'bg-green-50 text-green-600 border-green-200',
    red: 'bg-red-50 text-red-600 border-red-200',
    purple: 'bg-purple-50 text-purple-600 border-purple-200',
    yellow: 'bg-yellow-50 text-yellow-600 border-yellow-200',
  };

  return (
    <Card hover className='p-6'>
      <div className='flex items-center justify-between'>
        <div className={`p-3 rounded-xl border-2 ${colorClasses[color]}`}>
          <Icon size={24} />
        </div>
        <div className='text-right'>
          <p className='text-2xl font-bold text-gray-900'>
            {typeof value === 'number' ? value.toLocaleString() : value}
          </p>
          <p className='text-sm text-gray-500'>{title}</p>
          {subtitle && <p className='text-xs text-gray-400 mt-1'>{subtitle}</p>}
          {change && (
            <p
              className={`text-xs mt-1 ${
                change > 0 ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {change > 0 ? '+' : ''}
              {change}% vs yesterday
            </p>
          )}
        </div>
      </div>
    </Card>
  );
};

const LoginForm = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async e => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    // Simulate API call
    setTimeout(() => {
      const user = mockUsers.find(
        u => u.email === email && u.password === password
      );
      if (user) {
        onLogin(user);
      } else {
        setError('Invalid email or password');
      }
      setIsLoading(false);
    }, 1000);
  };

  return (
    <div className='min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-6'>
      <Card className='w-full max-w-md p-8'>
        <div className='text-center mb-8'>
          <div className='w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center mx-auto mb-4'>
            <Shield className='text-white' size={32} />
          </div>
          <h1 className='text-2xl font-bold text-gray-900'>
            Cookie Policy Monitor
          </h1>
          <p className='text-gray-500 mt-2'>
            Sign in to access admin dashboard
          </p>
        </div>

        <form onSubmit={handleSubmit} className='space-y-4'>
          <div>
            <label className='block text-sm font-medium text-gray-700 mb-2'>
              Email
            </label>
            <div className='relative'>
              <Mail size={18} className='absolute left-3 top-3 text-gray-400' />
              <input
                type='email'
                value={email}
                onChange={e => setEmail(e.target.value)}
                className='w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
                placeholder='Enter your email'
                required
              />
            </div>
          </div>

          <div>
            <label className='block text-sm font-medium text-gray-700 mb-2'>
              Password
            </label>
            <div className='relative'>
              <Lock size={18} className='absolute left-3 top-3 text-gray-400' />
              <input
                type='password'
                value={password}
                onChange={e => setPassword(e.target.value)}
                className='w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
                placeholder='Enter your password'
                required
              />
            </div>
          </div>

          {error && (
            <div className='bg-red-50 border border-red-200 rounded-lg p-3'>
              <p className='text-red-600 text-sm'>{error}</p>
            </div>
          )}

          <button
            type='submit'
            disabled={isLoading}
            className={`w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors ${
              isLoading ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            {isLoading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className='mt-6 p-4 bg-gray-50 rounded-lg'>
          <p className='text-sm text-gray-600 mb-2'>Demo credentials:</p>
          <p className='text-xs text-gray-500'>
            Admin: admin@example.com / admin123
          </p>
          <p className='text-xs text-gray-500'>
            Manager: manager@example.com / manager123
          </p>
        </div>
      </Card>
    </div>
  );
};

const ViolationTable = () => {
  const [selectedSeverity, setSelectedSeverity] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const filteredViolators = mockData.topViolators.filter(site => {
    const matchesSeverity =
      selectedSeverity === 'all' || site.severity === selectedSeverity;
    const matchesSearch = site.domain
      .toLowerCase()
      .includes(searchTerm.toLowerCase());
    return matchesSeverity && matchesSearch;
  });

  return (
    <Card className='p-6'>
      <div className='flex items-center justify-between mb-6'>
        <h3 className='text-lg font-semibold text-gray-900'>
          Top Violating Websites
        </h3>
        <div className='flex gap-2'>
          <div className='relative'>
            <Search
              size={16}
              className='absolute left-3 top-2.5 text-gray-400'
            />
            <input
              type='text'
              placeholder='Search domain...'
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className='pl-9 pr-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            />
          </div>
          <select
            value={selectedSeverity}
            onChange={e => setSelectedSeverity(e.target.value)}
            className='px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent'
          >
            <option value='all'>All Severity</option>
            <option value='critical'>Critical</option>
            <option value='high'>High</option>
            <option value='medium'>Medium</option>
            <option value='low'>Low</option>
          </select>
          <button className='p-2 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors'>
            <RefreshCw size={16} className='text-blue-600' />
          </button>
        </div>
      </div>

      <div className='overflow-x-auto'>
        <table className='w-full'>
          <thead>
            <tr className='border-b border-gray-200'>
              <th className='text-left py-3 px-4 font-medium text-gray-700'>
                Domain
              </th>
              <th className='text-left py-3 px-4 font-medium text-gray-700'>
                Violations
              </th>
              <th className='text-left py-3 px-4 font-medium text-gray-700'>
                Compliance Score
              </th>
              <th className='text-left py-3 px-4 font-medium text-gray-700'>
                Severity
              </th>
              <th className='text-left py-3 px-4 font-medium text-gray-700'>
                Last Scan
              </th>
              <th className='text-left py-3 px-4 font-medium text-gray-700'>
                Actions
              </th>
            </tr>
          </thead>
          <tbody>
            {filteredViolators.map((site, i) => (
              <tr
                key={i}
                className='border-b border-gray-100 hover:bg-gray-50 transition-colors'
              >
                <td className='py-3 px-4'>
                  <div className='flex items-center gap-2'>
                    <Globe size={16} className='text-gray-400' />
                    <div>
                      <span className='font-medium text-gray-900'>
                        {site.domain}
                      </span>
                      <div className='flex flex-wrap gap-1 mt-1'>
                        {site.violationTypes.slice(0, 2).map((type, idx) => (
                          <span
                            key={idx}
                            className='text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded'
                          >
                            {type}
                          </span>
                        ))}
                        {site.violationTypes.length > 2 && (
                          <span className='text-xs text-gray-500'>
                            +{site.violationTypes.length - 2} more
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </td>
                <td className='py-3 px-4'>
                  <span className='bg-red-100 text-red-800 px-2 py-1 rounded-full text-sm font-medium'>
                    {site.violations}
                  </span>
                </td>
                <td className='py-3 px-4'>
                  <div className='flex items-center gap-2'>
                    <div className='w-16 bg-gray-200 rounded-full h-2'>
                      <div
                        className={`h-2 rounded-full transition-all duration-500 ${
                          site.complianceScore >= 80
                            ? 'bg-green-500'
                            : site.complianceScore >= 60
                            ? 'bg-yellow-500'
                            : 'bg-red-500'
                        }`}
                        style={{ width: `${site.complianceScore}%` }}
                      />
                    </div>
                    <span className='text-sm text-gray-700'>
                      {site.complianceScore}%
                    </span>
                  </div>
                </td>
                <td className='py-3 px-4'>
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-medium ${
                      site.severity === 'critical'
                        ? 'bg-red-100 text-red-800'
                        : site.severity === 'high'
                        ? 'bg-orange-100 text-orange-800'
                        : site.severity === 'medium'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-green-100 text-green-800'
                    }`}
                  >
                    {site.severity.toUpperCase()}
                  </span>
                </td>
                <td className='py-3 px-4'>
                  <span className='text-sm text-gray-600'>{site.lastScan}</span>
                </td>
                <td className='py-3 px-4'>
                  <div className='flex gap-2'>
                    <button
                      className='p-1 hover:bg-blue-100 rounded transition-colors'
                      title='View Details'
                    >
                      <Eye size={14} className='text-blue-600' />
                    </button>
                    <button
                      className='p-1 hover:bg-gray-100 rounded transition-colors'
                      title='Visit Site'
                    >
                      <ExternalLink size={14} className='text-gray-600' />
                    </button>
                    <button
                      className='p-1 hover:bg-green-100 rounded transition-colors'
                      title='Rescan'
                    >
                      <RefreshCw size={14} className='text-green-600' />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
};

const ActivityFeed = () => (
  <Card className='p-6'>
    <div className='flex items-center justify-between mb-4'>
      <h3 className='text-lg font-semibold text-gray-900'>
        Real-time Activity
      </h3>
      <Bell size={20} className='text-gray-400' />
    </div>
    <div className='space-y-4'>
      {mockData.recentActivity.map((activity, i) => (
        <div
          key={i}
          className='flex items-start gap-3 p-3 hover:bg-gray-50 rounded-lg transition-colors'
        >
          <div
            className={`w-2 h-2 rounded-full mt-2 ${
              activity.type === 'critical'
                ? 'bg-red-500 animate-pulse'
                : activity.type === 'error'
                ? 'bg-red-500'
                : activity.type === 'success'
                ? 'bg-green-500'
                : activity.type === 'resolved'
                ? 'bg-blue-500'
                : activity.type === 'info'
                ? 'bg-blue-500'
                : 'bg-yellow-500'
            }`}
          />
          <div className='flex-1'>
            <p className='text-sm font-medium text-gray-900'>
              {activity.action}
            </p>
            <p className='text-xs text-gray-500'>{activity.website}</p>
          </div>
          <span className='text-xs text-gray-400'>{activity.time}</span>
        </div>
      ))}
    </div>
  </Card>
);

const TrackersAnalysis = () => (
  <Card className='p-6'>
    <h3 className='text-lg font-semibold text-gray-900 mb-4'>
      Third-party Trackers Analysis
    </h3>
    <div className='space-y-3'>
      {mockData.trackers.map((tracker, i) => (
        <div
          key={i}
          className='flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition-colors'
        >
          <div>
            <p className='font-medium text-gray-900'>{tracker.name}</p>
            <p className='text-sm text-gray-500'>
              {tracker.websites.toLocaleString()} websites
            </p>
            <span
              className={`text-xs px-2 py-0.5 rounded-full ${
                tracker.riskLevel === 'high'
                  ? 'bg-red-100 text-red-800'
                  : tracker.riskLevel === 'medium'
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-green-100 text-green-800'
              }`}
            >
              {tracker.riskLevel} risk
            </span>
          </div>
          <div className='text-right'>
            <p className='text-sm font-medium text-red-600'>
              {tracker.violations} violations
            </p>
            <div className='w-20 bg-gray-200 rounded-full h-2 mt-1'>
              <div
                className='bg-red-500 h-2 rounded-full transition-all duration-500'
                style={{
                  width: `${Math.min((tracker.violations / 400) * 100, 100)}%`,
                }}
              />
            </div>
          </div>
        </div>
      ))}
    </div>
  </Card>
);

const ComplianceChart = () => (
  <Card className='p-6'>
    <h3 className='text-lg font-semibold text-gray-900 mb-4'>
      Compliance Trends
    </h3>
    <ResponsiveContainer width='100%' height={300}>
      <ComposedChart data={mockData.complianceHistory}>
        <CartesianGrid strokeDasharray='3 3' stroke='#f1f5f9' />
        <XAxis dataKey='month' tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip
          contentStyle={{
            backgroundColor: 'white',
            border: '1px solid #e2e8f0',
            borderRadius: '8px',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
          }}
        />
        <Bar dataKey='compliant' stackId='a' fill='#10b981' name='Compliant' />
        <Bar
          dataKey='nonCompliant'
          stackId='a'
          fill='#ef4444'
          name='Non-Compliant'
        />
        <Line
          type='monotone'
          dataKey='compliant'
          stroke='#059669'
          strokeWidth={3}
          name='Compliance Trend'
        />
      </ComposedChart>
    </ResponsiveContainer>
  </Card>
);

const ViolationDetailsChart = () => (
  <Card className='p-6'>
    <h3 className='text-lg font-semibold text-gray-900 mb-4'>
      Violation Types Distribution
    </h3>
    <ResponsiveContainer width='100%' height={400}>
      <BarChart
        data={mockData.violations}
        margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
      >
        <CartesianGrid strokeDasharray='3 3' stroke='#f1f5f9' />
        <XAxis
          dataKey='name'
          tick={{ fontSize: 10 }}
          angle={-45}
          textAnchor='end'
          height={80}
        />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip
          contentStyle={{
            backgroundColor: 'white',
            border: '1px solid #e2e8f0',
            borderRadius: '8px',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
          }}
        />
        <Bar dataKey='value' fill='#8884d8'>
          {mockData.violations.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  </Card>
);

export function CookieAdminDashboard() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [isLoading, setIsLoading] = useState(false);

  const tabs = [
    { id: 'overview', label: 'Overview', icon: TrendingUp },
    { id: 'violations', label: 'Violations Report', icon: AlertTriangle },
    { id: 'compliance', label: 'Compliance Analysis', icon: BarChart3 },
    { id: 'websites', label: 'Websites', icon: Globe },
    { id: 'trackers', label: 'Trackers', icon: Shield },
    { id: 'monitoring', label: 'Monitoring', icon: Server },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  const handleLogin = userData => {
    setUser(userData);
  };

  const handleLogout = () => {
    setUser(null);
    setActiveTab('overview');
  };

  const handleRefresh = () => {
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 1000);
  };

  if (!user) {
    return <LoginForm onLogin={handleLogin} />;
  }

  return (
    <div className='min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50'>
      {/* Header */}
      <div className='bg-white shadow-sm border-b border-gray-200'>
        <div className='max-w-7xl mx-auto px-6 py-4'>
          <div className='flex items-center justify-between'>
            <div className='flex items-center gap-3'>
              <div className='w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center'>
                <Shield className='text-white' size={20} />
              </div>
              <div>
                <h1 className='text-2xl font-bold text-gray-900'>
                  Cookie Policy Monitor
                </h1>
                <p className='text-sm text-gray-500'>
                  Advanced Compliance Dashboard
                </p>
              </div>
            </div>

            <div className='flex items-center gap-4'>
              <button
                onClick={handleRefresh}
                className={`flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-all duration-200 ${
                  isLoading ? 'animate-pulse' : ''
                }`}
              >
                <RefreshCw
                  size={16}
                  className={isLoading ? 'animate-spin' : ''}
                />
                Refresh
              </button>

              <div className='flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg'>
                <div className='w-2 h-2 bg-green-500 rounded-full animate-pulse' />
                <span className='text-sm text-gray-700'>Live</span>
              </div>

              <div className='flex items-center gap-3'>
                <div className='flex items-center gap-2 px-3 py-2 bg-blue-50 rounded-lg'>
                  <User size={16} className='text-blue-600' />
                  <span className='text-sm text-gray-700'>{user.name}</span>
                  <span className='text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full'>
                    {user.role}
                  </span>
                </div>
                <button
                  onClick={handleLogout}
                  className='p-2 hover:bg-red-50 rounded-lg transition-colors'
                  title='Logout'
                >
                  <LogOut size={16} className='text-red-600' />
                </button>
              </div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className='flex gap-1 mt-6 overflow-x-auto'>
            {tabs.map(tab => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200 whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'bg-blue-100 text-blue-700 border-2 border-blue-200'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <Icon size={16} />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className='max-w-7xl mx-auto px-6 py-8'>
        {activeTab === 'overview' && (
          <div className='space-y-8'>
            {/* Enhanced Metrics Grid */}
            <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6'>
              <MetricCard
                icon={Globe}
                title='Total Websites'
                value={mockData.overview.totalWebsites}
                change={12}
                color='blue'
                subtitle='Under monitoring'
              />
              <MetricCard
                icon={Users}
                title='Active Scans'
                value={mockData.overview.activeScans}
                change={8}
                color='green'
                subtitle='Currently running'
              />
              <MetricCard
                icon={AlertTriangle}
                title='Violations Today'
                value={mockData.overview.violationsToday}
                change={-5}
                color='red'
                // subtitle="Critical: "  mockData.overview.criticalViolations
              />
              <MetricCard
                icon={TrendingUp}
                title='Success Rate'
                value={mockData.overview.successRate + '%'}
                change={2.1}
                color='purple'
                subtitle='Compliance score'
              />
            </div>

            {/* Additional Metrics Row */}
            <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6'>
              <MetricCard
                icon={Server}
                title='Total Scans'
                value={mockData.overview.totalScans}
                change={15}
                color='blue'
                subtitle='This month'
              />
              <MetricCard
                icon={PieChartIcon}
                title='Avg Violations/Site'
                value={mockData.overview.avgViolationsPerSite}
                change={-8}
                color='yellow'
                subtitle='Per website'
              />
              <MetricCard
                icon={Shield}
                title='Critical Issues'
                value={mockData.overview.criticalViolations}
                change={-12}
                color='red'
                subtitle='Requires attention'
              />
              <MetricCard
                icon={Activity}
                title='Resolved Issues'
                value={mockData.overview.resolvedViolations}
                change={25}
                color='green'
                subtitle='This month'
              />
            </div>

            {/* Charts Row */}
            <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
              {/* Violations Trend */}
              <Card className='p-6'>
                <h3 className='text-lg font-semibold text-gray-900 mb-4'>
                  Violations & Compliance Trend
                </h3>
                <ResponsiveContainer width='100%' height={300}>
                  <ComposedChart data={mockData.trends}>
                    <defs>
                      <linearGradient
                        id='violationsGradient'
                        x1='0'
                        y1='0'
                        x2='0'
                        y2='1'
                      >
                        <stop
                          offset='5%'
                          stopColor='#ef4444'
                          stopOpacity={0.3}
                        />
                        <stop
                          offset='95%'
                          stopColor='#ef4444'
                          stopOpacity={0}
                        />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray='3 3' stroke='#f1f5f9' />
                    <XAxis dataKey='date' tick={{ fontSize: 10 }} />
                    <YAxis yAxisId='left' tick={{ fontSize: 12 }} />
                    <YAxis
                      yAxisId='right'
                      orientation='right'
                      tick={{ fontSize: 12 }}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'white',
                        border: '1px solid #e2e8f0',
                        borderRadius: '8px',
                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                      }}
                    />
                    <Area
                      yAxisId='left'
                      type='monotone'
                      dataKey='violations'
                      stroke='#ef4444'
                      fillOpacity={1}
                      fill='url(#violationsGradient)'
                      strokeWidth={2}
                      name='Violations'
                    />
                    <Line
                      yAxisId='right'
                      type='monotone'
                      dataKey='compliance'
                      stroke='#10b981'
                      strokeWidth={3}
                      name='Compliance %'
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              </Card>

              {/* Violations Distribution */}
              <Card className='p-6'>
                <h3 className='text-lg font-semibold text-gray-900 mb-4'>
                  Violation Types Distribution
                </h3>
                <ResponsiveContainer width='100%' height={300}>
                  <PieChart>
                    <Pie
                      data={mockData.violations}
                      cx='50%'
                      cy='50%'
                      innerRadius={60}
                      outerRadius={120}
                      paddingAngle={5}
                      dataKey='value'
                    >
                      {mockData.violations.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
                <div className='grid grid-cols-2 gap-2 mt-4'>
                  {mockData.violations.map((item, i) => (
                    <div key={i} className='flex items-center gap-2'>
                      <div
                        className='w-3 h-3 rounded-full'
                        style={{ backgroundColor: item.color }}
                      />
                      <span className='text-xs text-gray-600'>{item.name}</span>
                    </div>
                  ))}
                </div>
              </Card>
            </div>

            {/* Bottom Section */}
            <div className='grid grid-cols-1 lg:grid-cols-3 gap-6'>
              <div className='lg:col-span-2'>
                <ViolationTable />
              </div>
              <div className='space-y-6'>
                <ActivityFeed />
                <TrackersAnalysis />
              </div>
            </div>
          </div>
        )}

        {activeTab === 'violations' && (
          <div className='space-y-8'>
            <div className='flex items-center justify-between'>
              <div>
                <h2 className='text-2xl font-bold text-gray-900'>
                  Violations Report
                </h2>
                <p className='text-gray-600 mt-1'>
                  Detailed analysis of cookie policy violations
                </p>
              </div>
              <div className='flex gap-3'>
                <button className='flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors'>
                  <Download size={16} />
                  Export Report
                </button>
                <button className='flex items-center gap-2 px-4 py-2 border border-gray-300 hover:bg-gray-50 rounded-lg transition-colors'>
                  <Calendar size={16} />
                  Date Range
                </button>
              </div>
            </div>

            <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
              <ViolationDetailsChart />
              <Card className='p-6'>
                <h3 className='text-lg font-semibold text-gray-900 mb-4'>
                  Severity Breakdown
                </h3>
                <div className='space-y-4'>
                  {[
                    {
                      level: 'Critical',
                      count: 89,
                      color: 'bg-red-500',
                      percentage: 23,
                    },
                    {
                      level: 'High',
                      count: 234,
                      color: 'bg-orange-500',
                      percentage: 35,
                    },
                    {
                      level: 'Medium',
                      count: 189,
                      color: 'bg-yellow-500',
                      percentage: 28,
                    },
                    {
                      level: 'Low',
                      count: 98,
                      color: 'bg-green-500',
                      percentage: 14,
                    },
                  ].map((item, i) => (
                    <div key={i} className='flex items-center justify-between'>
                      <div className='flex items-center gap-3'>
                        <div className={`w-4 h-4 rounded-full ${item.color}`} />
                        <span className='font-medium text-gray-900'>
                          {item.level}
                        </span>
                      </div>
                      <div className='flex items-center gap-4'>
                        <div className='w-32 bg-gray-200 rounded-full h-2'>
                          <div
                            className={`h-2 rounded-full ${item.color} transition-all duration-500`}
                            style={{ width: `${item.percentage}%` }}
                          />
                        </div>
                        <span className='text-sm font-medium text-gray-900 w-12 text-right'>
                          {item.count}
                        </span>
                        <span className='text-sm text-gray-500 w-12 text-right'>
                          {item.percentage}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>

            <ViolationTable />
          </div>
        )}

        {activeTab === 'compliance' && (
          <div className='space-y-8'>
            <div className='flex items-center justify-between'>
              <div>
                <h2 className='text-2xl font-bold text-gray-900'>
                  Compliance Analysis
                </h2>
                <p className='text-gray-600 mt-1'>
                  Monitor compliance trends and performance metrics
                </p>
              </div>
              <div className='flex gap-3'>
                <button className='flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors'>
                  <FileText size={16} />
                  Generate Report
                </button>
              </div>
            </div>

            <div className='grid grid-cols-1 md:grid-cols-3 gap-6'>
              <MetricCard
                icon={Shield}
                title='Overall Compliance'
                value='81.9%'
                change={-2.3}
                color='blue'
                subtitle='Current month'
              />
              <MetricCard
                icon={TrendingUp}
                title='Improvement Rate'
                value='12.4%'
                change={8.7}
                color='green'
                subtitle='Month over month'
              />
              <MetricCard
                icon={AlertTriangle}
                title='At-Risk Sites'
                value={156}
                change={-15}
                color='red'
                subtitle='Below 60% compliance'
              />
            </div>

            <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
              <ComplianceChart />
              <Card className='p-6'>
                <h3 className='text-lg font-semibold text-gray-900 mb-4'>
                  Compliance Score Distribution
                </h3>
                <ResponsiveContainer width='100%' height={300}>
                  <BarChart
                    data={[
                      { range: '90-100%', count: 2341, color: '#10b981' },
                      { range: '80-89%', count: 3456, color: '#59d15c' },
                      { range: '70-79%', count: 2890, color: '#eab308' },
                      { range: '60-69%', count: 1987, color: '#f97316' },
                      { range: '0-59%', count: 1873, color: '#ef4444' },
                    ]}
                  >
                    <CartesianGrid strokeDasharray='3 3' stroke='#f1f5f9' />
                    <XAxis dataKey='range' tick={{ fontSize: 12 }} />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip />
                    <Bar dataKey='count' fill='#8884d8'>
                      {[
                        { range: '90-100%', count: 2341, color: '#10b981' },
                        { range: '80-89%', count: 3456, color: '#59d15c' },
                        { range: '70-79%', count: 2890, color: '#eab308' },
                        { range: '60-69%', count: 1987, color: '#f97316' },
                        { range: '0-59%', count: 1873, color: '#ef4444' },
                      ].map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </div>

            <Card className='p-6'>
              <h3 className='text-lg font-semibold text-gray-900 mb-4'>
                Compliance Improvement Recommendations
              </h3>
              <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
                <div className='space-y-4'>
                  <h4 className='font-medium text-gray-900'>
                    Priority Actions
                  </h4>
                  {[
                    {
                      action:
                        'Review retention periods for 89 critical violations',
                      priority: 'High',
                      impact: 'Major',
                    },
                    {
                      action: 'Update third-party tracker declarations',
                      priority: 'High',
                      impact: 'Major',
                    },
                    {
                      action: 'Implement proper cookie categorization',
                      priority: 'Medium',
                      impact: 'Moderate',
                    },
                    {
                      action: 'Enhance user consent mechanisms',
                      priority: 'Medium',
                      impact: 'Moderate',
                    },
                  ].map((item, i) => (
                    <div
                      key={i}
                      className='flex items-center justify-between p-3 bg-gray-50 rounded-lg'
                    >
                      <div>
                        <p className='text-sm font-medium text-gray-900'>
                          {item.action}
                        </p>
                        <div className='flex gap-2 mt-1'>
                          <span
                            className={`text-xs px-2 py-0.5 rounded-full ${
                              item.priority === 'High'
                                ? 'bg-red-100 text-red-800'
                                : 'bg-yellow-100 text-yellow-800'
                            }`}
                          >
                            {item.priority} Priority
                          </span>
                          <span className='text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-800'>
                            {item.impact} Impact
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className='space-y-4'>
                  <h4 className='font-medium text-gray-900'>Quick Wins</h4>
                  {[
                    'Enable automatic cookie scanning for 234 pending sites',
                    'Set up violation alerts for critical issues',
                    'Configure compliance thresholds per domain',
                    'Automate policy extraction for new websites',
                  ].map((item, i) => (
                    <div
                      key={i}
                      className='flex items-center gap-3 p-3 bg-green-50 rounded-lg'
                    >
                      <div className='w-2 h-2 bg-green-500 rounded-full' />
                      <p className='text-sm text-gray-900'>{item}</p>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'trackers' && (
          <div className='space-y-8'>
            <div className='flex items-center justify-between'>
              <div>
                <h2 className='text-2xl font-bold text-gray-900'>
                  Third-party Trackers
                </h2>
                <p className='text-gray-600 mt-1'>
                  Analysis of tracking technologies and their compliance impact
                </p>
              </div>
            </div>

            <div className='grid grid-cols-1 md:grid-cols-3 gap-6'>
              <MetricCard
                icon={Shield}
                title='Tracked Services'
                value={mockData.trackers.length}
                color='blue'
                subtitle='Major tracking platforms'
              />
              <MetricCard
                icon={Globe}
                title='Affected Websites'
                value={mockData.trackers.reduce(
                  (sum, t) => sum + t.websites,
                  0
                )}
                color='purple'
                subtitle='Using these trackers'
              />
              <MetricCard
                icon={AlertTriangle}
                title='Total Violations'
                value={mockData.trackers.reduce(
                  (sum, t) => sum + t.violations,
                  0
                )}
                color='red'
                subtitle='From tracking services'
              />
            </div>

            <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
              <Card className='p-6'>
                <h3 className='text-lg font-semibold text-gray-900 mb-4'>
                  Tracker Usage Distribution
                </h3>
                <ResponsiveContainer width='100%' height={300}>
                  <BarChart data={mockData.trackers} margin={{ bottom: 60 }}>
                    <CartesianGrid strokeDasharray='3 3' stroke='#f1f5f9' />
                    <XAxis
                      dataKey='name'
                      tick={{ fontSize: 10 }}
                      angle={-45}
                      textAnchor='end'
                      height={80}
                    />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip />
                    <Bar
                      dataKey='websites'
                      fill='#3b82f6'
                      name='Websites Using'
                    />
                  </BarChart>
                </ResponsiveContainer>
              </Card>

              <Card className='p-6'>
                <h3 className='text-lg font-semibold text-gray-900 mb-4'>
                  Violation Rate by Tracker
                </h3>
                <ResponsiveContainer width='100%' height={300}>
                  <BarChart
                    data={mockData.trackers.map(t => ({
                      ...t,
                      violationRate: (
                        (t.violations / t.websites) *
                        100
                      ).toFixed(1),
                    }))}
                  >
                    <CartesianGrid strokeDasharray='3 3' stroke='#f1f5f9' />
                    <XAxis
                      dataKey='name'
                      tick={{ fontSize: 10 }}
                      angle={-45}
                      textAnchor='end'
                      height={80}
                    />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip
                      formatter={value => [`${value}%`, 'Violation Rate']}
                    />
                    <Bar
                      dataKey='violationRate'
                      fill='#ef4444'
                      name='Violation Rate %'
                    />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </div>

            <TrackersAnalysis />
          </div>
        )}

        {(activeTab === 'websites' ||
          activeTab === 'monitoring' ||
          activeTab === 'settings') && (
          <Card className='p-12 text-center'>
            <div className='w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4'>
              <Settings size={24} className='text-blue-600' />
            </div>
            <h3 className='text-xl font-semibold text-gray-900 mb-2'>
              {tabs.find(t => t.id === activeTab)?.label} Section
            </h3>
            <p className='text-gray-500 mb-6'>
              This section is under development. Advanced features will be
              available soon.
            </p>
            <button className='px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors'>
              Coming Soon
            </button>
          </Card>
        )}
      </div>
    </div>
  );
}
