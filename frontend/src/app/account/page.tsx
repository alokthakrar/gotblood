'use client';

import { useState } from 'react';

export default function AccountPage() {
  const [activeTab, setActiveTab] = useState('profile');

  return (
    <div className="min-h-screen bg-off-white py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="heading-1 text-center mb-12">Account Settings</h1>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex flex-wrap gap-4">
            <button
              onClick={() => setActiveTab('profile')}
              className={`px-6 py-2 rounded-full font-semibold transition-colors ${
                activeTab === 'profile'
                  ? 'bg-primary-red text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Profile
            </button>
            <button
              onClick={() => setActiveTab('donations')}
              className={`px-6 py-2 rounded-full font-semibold transition-colors ${
                activeTab === 'donations'
                  ? 'bg-primary-red text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Donation History
            </button>
            <button
              onClick={() => setActiveTab('notifications')}
              className={`px-6 py-2 rounded-full font-semibold transition-colors ${
                activeTab === 'notifications'
                  ? 'bg-primary-red text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Notifications
            </button>
          </div>
        </div>

        {/* Profile Section */}
        {activeTab === 'profile' && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="heading-2 mb-6">Profile Information</h2>
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
                <input
                  type="text"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-red focus:border-transparent"
                  placeholder="John Doe"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                <input
                  type="email"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-red focus:border-transparent"
                  placeholder="john@example.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Blood Type</label>
                <select className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-red focus:border-transparent">
                  <option>A+</option>
                  <option>A-</option>
                  <option>B+</option>
                  <option>B-</option>
                  <option>O+</option>
                  <option>O-</option>
                  <option>AB+</option>
                  <option>AB-</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
                <input
                  type="tel"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-red focus:border-transparent"
                  placeholder="+1 (555) 123-4567"
                />
              </div>
              <button className="btn-primary w-full">
                Save Changes
              </button>
            </div>
          </div>
        )}

        {/* Donation History Section */}
        {activeTab === 'donations' && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="heading-2 mb-6">Donation History</h2>
            <div className="space-y-4">
              <div className="border-b pb-4">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="font-semibold">Whole Blood Donation</h3>
                    <p className="text-gray-600">City Hospital</p>
                  </div>
                  <div className="text-right">
                    <div className="text-primary-red font-semibold">450ml</div>
                    <div className="text-gray-600">March 1, 2024</div>
                  </div>
                </div>
              </div>
              <div className="border-b pb-4">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="font-semibold">Platelet Donation</h3>
                    <p className="text-gray-600">Community Blood Bank</p>
                  </div>
                  <div className="text-right">
                    <div className="text-primary-red font-semibold">1 Unit</div>
                    <div className="text-gray-600">February 15, 2024</div>
                  </div>
                </div>
              </div>
              <div className="pb-4">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="font-semibold">Whole Blood Donation</h3>
                    <p className="text-gray-600">Regional Medical Center</p>
                  </div>
                  <div className="text-right">
                    <div className="text-primary-red font-semibold">450ml</div>
                    <div className="text-gray-600">January 30, 2024</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Notifications Section */}
        {activeTab === 'notifications' && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="heading-2 mb-6">Notification Preferences</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold">Email Notifications</h3>
                  <p className="text-gray-600">Receive updates about blood donation opportunities</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" className="sr-only peer" defaultChecked />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-red/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-red"></div>
                </label>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold">SMS Notifications</h3>
                  <p className="text-gray-600">Get text alerts for urgent blood needs</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" className="sr-only peer" defaultChecked />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-red/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-red"></div>
                </label>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold">Donation Reminders</h3>
                  <p className="text-gray-600">Get notified when you're eligible to donate again</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" className="sr-only peer" defaultChecked />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-red/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-red"></div>
                </label>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 