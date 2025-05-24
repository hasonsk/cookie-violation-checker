import React from 'react';
import MetricCard from '../../components/ui/Card';

const mockOverview = {
  totalWebsites: 12547,
  activeScans: 234,
  violationsToday: 1829,
  successRate: '94.2%',
};

const DashboardPage = () => {
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Dashboard Overview</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Websites"
          value={mockOverview.totalWebsites}
          subtitle="Under monitoring"
        />
        <MetricCard
          title="Active Scans"
          value={mockOverview.activeScans}
          subtitle="Currently running"
        />
        <MetricCard
          title="Violations Today"
          value={mockOverview.violationsToday}
          subtitle="Detected today"
        />
        <MetricCard
          title="Success Rate"
          value={mockOverview.successRate}
          subtitle="Compliance percentage"
        />
      </div>
    </div>
  );
};

export default DashboardPage;
