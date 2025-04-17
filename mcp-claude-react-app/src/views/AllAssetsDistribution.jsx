import React from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const AllAssetsDistribution = () => {
  // OS Family distribution data
  const osFamilyData = [
    { name: 'Linux', count: 56, percentage: 42 },
    { name: 'Windows', count: 29, percentage: 22 },
    { name: 'Network Devices', count: 26, percentage: 20 },
    { name: 'IoT/Industrial', count: 12, percentage: 9 },
    { name: 'Apple', count: 5, percentage: 4 },
    { name: 'Other', count: 5, percentage: 4 }
  ];

  // Device Type distribution data
  const deviceTypeData = [
    { name: 'Servers', count: 55, percentage: 41 },
    { name: 'Network Devices', count: 43, percentage: 32 },
    { name: 'IoT/Industrial', count: 15, percentage: 11 },
    { name: 'Endpoints', count: 13, percentage: 10 },
    { name: 'Other', count: 7, percentage: 5 }
  ];

  // OS details data
  const osDetailsData = [
    { name: 'Ubuntu Linux', count: 36 },
    { name: 'Windows 10', count: 12 },
    { name: 'Windows (unspecified)', count: 11 },
    { name: 'Generic Linux', count: 9 },
    { name: 'Windows Server 2019', count: 8 },
    { name: 'CentOS Linux', count: 6 },
    { name: 'Cisco IOS', count: 6 },
    { name: 'Windows Server (23H2)', count: 2 },
    { name: 'Debian Linux', count: 2 },
    { name: 'Apple macOS', count: 3 },
    { name: 'Other', count: 38 }
  ];

  // Colors for the charts
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc658', '#d53e4f', '#8c564b', '#e377c2', '#7f7f7f'];

  return (
    <div className="flex flex-col w-full space-y-8 p-4">
      <h1 className="text-2xl font-bold text-center">Active Assets in runZero Environment</h1>
      <div className="text-center text-lg">Total Assets: 133</div>
      
      <div className="w-full flex flex-col md:flex-row md:space-x-4">
        <div className="w-full md:w-1/2">
          <h2 className="text-xl font-semibold mb-4 text-center">Distribution by OS Family</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={osFamilyData}
                  cx="50%"
                  cy="50%"
                  labelLine={true}
                  label={({ name, percentage }) => `${name} (${percentage}%)`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {osFamilyData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value, name) => [`${value} assets`, name]} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="w-full md:w-1/2">
          <h2 className="text-xl font-semibold mb-4 text-center">Distribution by Device Type</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={deviceTypeData}
                  cx="50%"
                  cy="50%"
                  labelLine={true}
                  label={({ name, percentage }) => `${name} (${percentage}%)`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {deviceTypeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value, name) => [`${value} assets`, name]} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="w-full">
        <h2 className="text-xl font-semibold mb-4 text-center">Top Operating Systems</h2>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={osDetailsData}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              layout="vertical"
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis type="category" dataKey="name" width={150} />
              <Tooltip formatter={(value) => [`${value} assets`, 'Count']} />
              <Legend />
              <Bar dataKey="count" name="Number of Assets" fill="#0088FE" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="border-t pt-4">
        <h2 className="text-xl font-semibold mb-2">Key Insights:</h2>
        <ul className="list-disc pl-6 space-y-2">
          <li>Linux is the dominant OS family in your environment (42%), with Ubuntu being the most common Linux distribution</li>
          <li>Windows accounts for 22% of your assets, with Windows 10 being the most common Windows version</li>
          <li>Servers make up the largest device category (41%), followed by network devices (32%)</li>
          <li>You have a significant number of IoT and industrial control devices (11%) in your environment</li>
          <li>There are several devices with end-of-life operating systems that should be reviewed for potential upgrade or replacement</li>
        </ul>
      </div>

      <div className="border-t pt-4 text-sm text-gray-600">
        <h3 className="font-semibold">Network Topology Insights:</h3>
        <p>Your network appears to be segmented into multiple subnets including internal networks (10.0.x.x), DMZ networks (198.51.x.x), and cloud infrastructure (23.20.x.x). This indicates good network segmentation practices.</p>
      </div>
    </div>
  );
};

export default AllAssetsDistribution;