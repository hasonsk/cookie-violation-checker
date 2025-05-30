import React from 'react';
import {
  TrendingUp,
} from 'lucide-react';

const MetricCard = ({ title, value, icon: Icon, trend = null, bgColor = "bg-blue-50", iconColor = "text-blue-600" }) => (
  <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
    <div className="flex justify-between items-start">
      <div className="flex-1">
        <p className="text-sm text-gray-600 mb-2">{title}</p>
        <p className="text-3xl font-bold text-gray-900">{value}</p>
        {trend && (
          <div className="flex items-center mt-2">
            <TrendingUp className="w-4 h-4 text-red-500" />
            <span className="text-sm text-red-500 ml-1">{trend}</span>
          </div>
        )}
      </div>
      <div className={`${bgColor} p-3 rounded-lg`}>
        <Icon className={`w-6 h-6 ${iconColor}`} />
      </div>
    </div>
  </div>
);

export default MetricCard;
