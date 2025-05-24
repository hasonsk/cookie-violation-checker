// src/pages/OverviewPage.js
import React from 'react';
import {
  Globe,
  Users,
  AlertTriangle,
  TrendingUp,
  Server,
  PieChart as PieChartIcon,
  Shield,
  Activity
} from 'lucide-react';
import { MetricCard } from '../components/ui/Card';
import { mockData } from '../data/mockData';

// Import các chart components
// import { ViolationsChart } from '../components/charts/ViolationsChart';
// import { ViolationDistributionChart } from '../components/charts/ViolationDistributionChart';
// import { ViolationTable } from '../components/tables/ViolationTable';
// import { ActivityFeed } from '../components/ActivityFeed';
// import { TrackersAnalysis } from '../components/TrackersAnalysis';

export const OverviewPage = () => {
  return (
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
      {/* <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
        <ViolationsChart />
        <ViolationDistributionChart />
      </div> */}

      {/* Bottom Section */}
      {/* <div className='grid grid-cols-1 lg:grid-cols-3 gap-6'>
        <div className='lg:col-span-2'>
          <ViolationTable />
        </div>
        <div className='space-y-6'>
          <ActivityFeed />
          <TrackersAnalysis />
        </div>
      </div> */}
    </div>
  );
};
