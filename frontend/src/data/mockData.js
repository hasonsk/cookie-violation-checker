// src/data/mockData.js
export const mockUsers = [
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

export const mockData = {
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
    // ... các violation khác
  ],
  trends: [
    { date: '2024-05-17', violations: 1245, scans: 3420, compliance: 89.2 },
    { date: '2024-05-18', violations: 1389, scans: 3651, compliance: 87.8 },
    // ... các ngày khác
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
    // ... các violator khác
  ],
  // ... rest of mockData
};
