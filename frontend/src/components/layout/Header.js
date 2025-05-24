// src/components/layout/Header.js
import React from 'react';
import {
  Shield,
  RefreshCw,
  User,
  LogOut,
  TrendingUp,
  AlertTriangle,
  BarChart3,
  Globe,
  Server,
  Settings
} from 'lucide-react';

export const Header = ({ user, activeTab, setActiveTab, onLogout, onRefresh, isLoading }) => {
  const tabs = [
    { id: 'overview', label: 'Overview', icon: TrendingUp },
    { id: 'violations', label: 'Violations Report', icon: AlertTriangle },
    { id: 'compliance', label: 'Compliance Analysis', icon: BarChart3 },
    { id: 'websites', label: 'Websites', icon: Globe },
    { id: 'trackers', label: 'Trackers', icon: Shield },
    { id: 'monitoring', label: 'Monitoring', icon: Server },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
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
              onClick={onRefresh}
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
                onClick={onLogout}
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
  );
};
