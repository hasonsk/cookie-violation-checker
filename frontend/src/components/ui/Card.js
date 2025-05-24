import React from 'react';

export const Card = ({ children, className = '' }) => {
  return (
    <div className={`bg-white shadow-md rounded-xl p-4 ${className}`}>
      {children}
    </div>
  );
};

const MetricCard = ({ title, value, subtitle }) => {
  return (
    <Card className="w-full">
      <h2 className="text-lg font-semibold text-gray-700">{title}</h2>
      <p className="text-2xl font-bold text-blue-600">{value}</p>
      <p className="text-sm text-gray-500">{subtitle}</p>
    </Card>
  );
};

export default MetricCard;
