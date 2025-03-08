'use client';

import { useState } from 'react';

export default function StatisticsPage() {
  const [timeRange, setTimeRange] = useState('week');

  return (
    <div className="min-h-screen bg-off-white py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="heading-1 text-center mb-12">Blood Management Statistics</h1>

        {/* Time Range Selector */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex flex-wrap gap-4">
            <button
              onClick={() => setTimeRange('day')}
              className={`px-6 py-2 rounded-full font-semibold transition-colors ${
                timeRange === 'day'
                  ? 'bg-primary-red text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Last 24 Hours
            </button>
            <button
              onClick={() => setTimeRange('week')}
              className={`px-6 py-2 rounded-full font-semibold transition-colors ${
                timeRange === 'week'
                  ? 'bg-primary-red text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Last Week
            </button>
            <button
              onClick={() => setTimeRange('month')}
              className={`px-6 py-2 rounded-full font-semibold transition-colors ${
                timeRange === 'month'
                  ? 'bg-primary-red text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Last Month
            </button>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          <div className="card">
            <h3 className="heading-3 text-center">Total Donations</h3>
            <div className="text-4xl font-bold text-primary-red text-center">1,234</div>
            <div className="text-gray-600 text-center mt-2">+12% from last period</div>
          </div>
          <div className="card">
            <h3 className="heading-3 text-center">Blood Units Available</h3>
            <div className="text-4xl font-bold text-primary-red text-center">5,678</div>
            <div className="text-gray-600 text-center mt-2">+8% from last period</div>
          </div>
          <div className="card">
            <h3 className="heading-3 text-center">Urgent Requests</h3>
            <div className="text-4xl font-bold text-primary-red text-center">23</div>
            <div className="text-gray-600 text-center mt-2">-5% from last period</div>
          </div>
        </div>

        {/* Blood Type Distribution */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="heading-2 mb-6">Blood Type Distribution</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary-red">A+</div>
              <div className="text-gray-600">32%</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-primary-red">B+</div>
              <div className="text-gray-600">25%</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-primary-red">O+</div>
              <div className="text-gray-600">28%</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-primary-red">AB+</div>
              <div className="text-gray-600">15%</div>
            </div>
          </div>
        </div>

        {/* Regional Distribution */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="heading-2 mb-6">Regional Blood Distribution</h2>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-1">
                <span className="font-semibold">North Region</span>
                <span className="text-gray-600">75%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-primary-red h-2 rounded-full" style={{ width: '75%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <span className="font-semibold">South Region</span>
                <span className="text-gray-600">60%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-primary-red h-2 rounded-full" style={{ width: '60%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <span className="font-semibold">East Region</span>
                <span className="text-gray-600">85%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-primary-red h-2 rounded-full" style={{ width: '85%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <span className="font-semibold">West Region</span>
                <span className="text-gray-600">45%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-primary-red h-2 rounded-full" style={{ width: '45%' }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 