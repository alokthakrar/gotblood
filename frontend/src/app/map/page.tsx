'use client';

import { useState } from 'react';

export default function MapPage() {
  const [selectedFilter, setSelectedFilter] = useState('all');

  return (
    <div className="min-h-screen bg-off-white py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="heading-1 text-center mb-12">Interactive Blood Bank Map</h1>
        
        {/* Filters */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex flex-wrap gap-4">
            <button
              onClick={() => setSelectedFilter('all')}
              className={`px-6 py-2 rounded-full font-semibold transition-colors ${
                selectedFilter === 'all'
                  ? 'bg-primary-red text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              All Locations
            </button>
            <button
              onClick={() => setSelectedFilter('hospitals')}
              className={`px-6 py-2 rounded-full font-semibold transition-colors ${
                selectedFilter === 'hospitals'
                  ? 'bg-primary-red text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Hospitals
            </button>
            <button
              onClick={() => setSelectedFilter('donation')}
              className={`px-6 py-2 rounded-full font-semibold transition-colors ${
                selectedFilter === 'donation'
                  ? 'bg-primary-red text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Donation Centers
            </button>
            <button
              onClick={() => setSelectedFilter('urgent')}
              className={`px-6 py-2 rounded-full font-semibold transition-colors ${
                selectedFilter === 'urgent'
                  ? 'bg-primary-red text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Urgent Needs
            </button>
          </div>
        </div>

        {/* Map Container */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="aspect-video bg-gray-100 rounded-lg flex items-center justify-center">
            <div className="text-center">
              <div className="text-4xl mb-4">🗺️</div>
              <p className="text-xl text-gray-600">Interactive Map Coming Soon</p>
              <p className="text-gray-500">We're working on integrating a real-time map view</p>
            </div>
          </div>
        </div>

        {/* Legend */}
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h2 className="heading-3 mb-4">Map Legend</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="flex items-center">
              <div className="w-4 h-4 bg-primary-red rounded-full mr-2"></div>
              <span className="text-gray-700">Hospitals</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-4 bg-secondary-red rounded-full mr-2"></div>
              <span className="text-gray-700">Donation Centers</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-4 bg-accent-red rounded-full mr-2"></div>
              <span className="text-gray-700">Urgent Needs</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-4 bg-gray-400 rounded-full mr-2"></div>
              <span className="text-gray-700">Inactive</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 