import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Shield, Server, Monitor, Router, AlertTriangle } from 'lucide-react';

const SecurityDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  
  // Data from the document
  const osData = [
    { name: 'Linux', value: 56, percentage: 42 },
    { name: 'Windows', value: 29, percentage: 22 },
    { name: 'Network Devices', value: 26, percentage: 20 },
    { name: 'IoT/Industrial', value: 12, percentage: 9 },
    { name: 'Apple', value: 5, percentage: 4 },
    { name: 'Other', value: 5, percentage: 4 }
  ];
  
  const deviceTypeData = [
    { name: 'Servers', value: 55, percentage: 41 },
    { name: 'Network Devices', value: 43, percentage: 32 },
    { name: 'IoT/Industrial', value: 15, percentage: 11 },
    { name: 'Endpoints', value: 13, percentage: 10 },
    { name: 'Other', value: 7, percentage: 5 }
  ];
  
  const riskData = [
    { name: 'Critical', value: 21, percentage: 16, color: '#ef4444' },
    { name: 'High', value: 14, percentage: 11, color: '#f97316' },
    { name: 'Medium', value: 54, percentage: 41, color: '#eab308' },
    { name: 'Low', value: 18, percentage: 14, color: '#22c55e' },
    { name: 'Info', value: 26, percentage: 20, color: '#3b82f6' }
  ];
  
  const subnetData = [
    { 
      subnet: '10.0.1.0/24', 
      type: 'Internal Network',
      riskScore: 2.80,
      details: 'Contains 1 critical and 2 high-risk assets\nIncludes key internal infrastructure components\n60% of assets in this subnet are high or critical risk'
    },
    { 
      subnet: '10.0.19.0/24', 
      type: 'Internal Network',
      riskScore: 2.80,
      details: 'Contains 2 critical and 1 high-risk assets\nIncludes several operational technology components\n60% of assets in this subnet are high or critical risk'
    },
    { 
      subnet: '198.51.26.0/24', 
      type: 'DMZ Network',
      riskScore: 2.80,
      details: 'Contains 2 critical-risk assets\nDirectly internet-facing systems\nResponsible for customer-facing applications'
    },
    { 
      subnet: '23.20.1.0/24', 
      type: 'Cloud Network',
      riskScore: 2.80,
      details: 'Contains 2 critical-risk assets\nHosts production cloud infrastructure\nAccessible via public internet'
    }
  ];
  
  const eolSystems = [
    { system: 'Ubuntu 16.04', count: 3, eolDate: 'April 2021' },
    { system: 'Debian 9', count: 2, eolDate: 'June 2022' },
    { system: 'Windows CE (IP Cameras)', count: 2, eolDate: 'October 2018' }
  ];
  
  const recommendations = {
    immediate: [
      'Remediate Critical Systems in Internet-Facing Segments',
      'Address End-of-Life Systems',
      'Enhance Network Segmentation'
    ],
    shortTerm: [
      'Comprehensive Vulnerability Management',
      'Asset Lifecycle Management',
      'Update Security Monitoring'
    ],
    longTerm: [
      'Zero Trust Architecture',
      'Cloud Security Posture Management',
      'IoT/OT Security Strategy'
    ]
  };
  
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

  const renderActiveTabContent = () => {
    switch(activeTab) {
      case 'overview':
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">Asset Distribution by OS Family</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={osData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label={({name, percentage}) => `${name}: ${percentage}%`}
                  >
                    {osData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">Asset Distribution by Device Type</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={deviceTypeData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label={({name, percentage}) => `${name}: ${percentage}%`}
                  >
                    {deviceTypeData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow md:col-span-2">
              <h3 className="text-lg font-semibold mb-4">Risk Assessment (133 Total Assets)</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={riskData}
                  margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="value" name="Asset Count">
                    {riskData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
              <div className="mt-4 text-center">
                <p className="text-gray-700">27% of assets (35 systems) are classified as critical or high risk</p>
              </div>
            </div>
          </div>
        );
      
      case 'subnets':
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {subnetData.map((subnet, index) => (
              <div key={index} className="bg-white p-6 rounded-lg shadow">
                <div className="flex justify-between items-start">
                  <h3 className="text-lg font-semibold">{subnet.subnet}</h3>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-md bg-red-100 text-red-800 text-sm font-medium">
                    Risk Score: {subnet.riskScore}
                  </span>
                </div>
                <p className="text-gray-500 mb-4">{subnet.type}</p>
                <div className="mt-2">
                  {subnet.details.split('\n').map((line, i) => (
                    <p key={i} className="text-gray-700 mb-1">{line}</p>
                  ))}
                </div>
              </div>
            ))}
          </div>
        );
      
      case 'eol':
        return (
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">End-of-Life Systems</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">System</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Count</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">EOL Date</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {eolSystems.map((system, index) => (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{system.system}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{system.count}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{system.eolDate}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-md bg-red-100 text-red-800 text-sm font-medium">
                          EOL Passed
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        );
      
      case 'recommendations':
        return (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <span className="inline-block w-3 h-3 bg-red-500 rounded-full mr-2"></span>
                Immediate Actions (0-30 days)
              </h3>
              <ul className="space-y-3">
                {recommendations.immediate.map((rec, index) => (
                  <li key={index} className="flex items-start">
                    <span className="text-red-500 font-bold mr-2">•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <span className="inline-block w-3 h-3 bg-yellow-500 rounded-full mr-2"></span>
                Short-Term Actions (30-90 days)
              </h3>
              <ul className="space-y-3">
                {recommendations.shortTerm.map((rec, index) => (
                  <li key={index} className="flex items-start">
                    <span className="text-yellow-500 font-bold mr-2">•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <span className="inline-block w-3 h-3 bg-green-500 rounded-full mr-2"></span>
                Long-Term Actions (90+ days)
              </h3>
              <ul className="space-y-3">
                {recommendations.longTerm.map((rec, index) => (
                  <li key={index} className="flex items-start">
                    <span className="text-green-500 font-bold mr-2">•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        );
        
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Network Security Posture Assessment</h1>
              <p className="text-gray-500">runZero Asset Inventory Analysis - April 17, 2025</p>
            </div>
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1">
                <Shield className="h-5 w-5 text-red-500" />
                <span className="text-sm font-medium">27% High/Critical Risk</span>
              </div>
              <div className="h-6 border-l border-gray-300"></div>
              <div className="flex items-center space-x-1">
                <Server className="h-5 w-5 text-gray-600" />
                <span className="text-sm font-medium">133 Assets</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="mb-6">
          <nav className="flex space-x-4">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-3 py-2 font-medium text-sm rounded-md ${
                activeTab === 'overview' 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('subnets')}
              className={`px-3 py-2 font-medium text-sm rounded-md ${
                activeTab === 'subnets' 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              High-Risk Subnets
            </button>
            <button
              onClick={() => setActiveTab('eol')}
              className={`px-3 py-2 font-medium text-sm rounded-md ${
                activeTab === 'eol' 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              EOL Systems
            </button>
            <button
              onClick={() => setActiveTab('recommendations')}
              className={`px-3 py-2 font-medium text-sm rounded-md ${
                activeTab === 'recommendations' 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Recommendations
            </button>
          </nav>
        </div>
        
        {renderActiveTabContent()}
        
        <div className="mt-6 bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-2">Key Takeaways</h2>
          <ul className="space-y-2">
            <li className="flex items-start">
              <span className="text-blue-500 font-bold mr-2">•</span>
              <span>The environment consists of 133 active assets with appropriate network segmentation</span>
            </li>
            <li className="flex items-start">
              <span className="text-blue-500 font-bold mr-2">•</span>
              <span>27% of assets (35 systems) are classified as critical or high risk</span>
            </li>
            <li className="flex items-start">
              <span className="text-blue-500 font-bold mr-2">•</span>
              <span>7 systems are running end-of-life software without security patches</span>
            </li>
            <li className="flex items-start">
              <span className="text-blue-500 font-bold mr-2">•</span>
              <span>The most pressing concern is the presence of critical assets in internet-facing segments</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default SecurityDashboard;