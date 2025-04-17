import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const CriticalAssetAnalysis = () => {
  // Data from our analysis
  const serviceFrequency = [
    { name: "HTTP", count: 26, percentage: 90 },
    { name: "SSH", count: 24, percentage: 83 },
    { name: "Telnet", count: 21, percentage: 72 },
    { name: "SMTP", count: 13, percentage: 45 },
    { name: "RDP", count: 13, percentage: 45 },
    { name: "SMB", count: 12, percentage: 41 },
    { name: "MySQL", count: 12, percentage: 41 },
    { name: "FTP", count: 11, percentage: 38 },
    { name: "DNS", count: 11, percentage: 38 },
    { name: "TFTP", count: 11, percentage: 38 }
  ];

  const deviceTypeData = [
    { name: "Server", count: 18, percentage: 62 },
    { name: "Router", count: 10, percentage: 34 },
    { name: "Laptop", count: 1, percentage: 3 }
  ];

  const osDistribution = [
    { name: "Ubuntu Linux", count: 17, percentage: 59 },
    { name: "Cisco IOS", count: 10, percentage: 34 },
    { name: "Windows Server", count: 1, percentage: 3 },
    { name: "macOS", count: 1, percentage: 3 }
  ];

  const networkLocation = [
    { name: "Internal", count: 17, percentage: 59 },
    { name: "Cloud", count: 8, percentage: 28 },
    { name: "DMZ", count: 4, percentage: 14 }
  ];

  const riskyCombinations = [
    { name: "Telnet + HTTP", count: 21, percentage: 72 },
    { name: "SSH + Telnet", count: 21, percentage: 72 },
    { name: "RDP + SMB", count: 13, percentage: 45 },
    { name: "MySQL + HTTP", count: 12, percentage: 41 },
    { name: "FTP + HTTP", count: 11, percentage: 38 },
    { name: "VNC + SSH", count: 11, percentage: 38 }
  ];

  const internetExposedServices = [
    { name: "RDP", count: 7, percentage: 58 },
    { name: "SMB", count: 6, percentage: 50 },
    { name: "VNC", count: 6, percentage: 50 },
    { name: "Telnet", count: 5, percentage: 42 },
    { name: "FTP", count: 5, percentage: 42 }
  ];

  // Colors for the charts
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc658', '#d53e4f', '#8c564b', '#e377c2'];
  
  // Danger level colors
  const HIGH_RISK = '#d32f2f';
  const MEDIUM_RISK = '#ff9800';
  const LOW_RISK = '#2196f3';

  return (
    <div className="flex flex-col p-4 w-full">
      <h1 className="text-2xl font-bold mb-2">Critical Asset Service Analysis</h1>
      <p className="text-gray-600 mb-4">Analysis of 29 critical-risk assets and their exposed services</p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        <div>
          <h2 className="text-xl font-semibold mb-4">Common Services on Critical Assets</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={serviceFrequency}
                layout="vertical"
                margin={{ top: 5, right: 30, left: 90, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" domain={[0, 100]} />
                <YAxis type="category" dataKey="name" width={80} />
                <Tooltip 
                  formatter={(value) => [`${value}%`, 'Percentage']}
                  labelFormatter={(value) => `${value} Service`}
                />
                <Bar dataKey="percentage" name="Percentage of Assets" fill="#0088FE" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div>
          <h2 className="text-xl font-semibold mb-4">Risky Service Combinations</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={riskyCombinations}
                layout="vertical"
                margin={{ top: 5, right: 30, left: 120, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" domain={[0, 100]} />
                <YAxis type="category" dataKey="name" width={100} />
                <Tooltip 
                  formatter={(value) => [`${value}%`, 'Percentage']}
                  labelFormatter={(value) => `${value}`}
                />
                <Bar dataKey="percentage" name="% of Critical Assets" fill={HIGH_RISK} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div>
          <h2 className="text-lg font-semibold mb-3">Device Type Distribution</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={deviceTypeData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {deviceTypeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value, name) => [`${value} assets`, name]} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div>
          <h2 className="text-lg font-semibold mb-3">OS Distribution</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={osDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {osDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value, name) => [`${value} assets`, name]} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div>
          <h2 className="text-lg font-semibold mb-3">Network Location</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={networkLocation}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {networkLocation.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value, name) => [`${value} assets`, name]} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Internet-Exposed Vulnerable Services</h2>
        <p className="text-gray-600 mb-4">Services running on critical assets in DMZ or Cloud environments</p>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={internetExposedServices}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(value, name) => [`${value} assets`, name]} />
              <Legend />
              <Bar dataKey="count" name="Internet-Exposed Assets" fill={HIGH_RISK} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      <div className="bg-gray-100 p-6 rounded-lg">
        <h2 className="text-xl font-semibold mb-3">Key Findings from Service Analysis</h2>
        <ul className="list-disc space-y-2 pl-5">
          <li>
            <span className="font-semibold">Widespread obsolete protocols:</span> 72% of critical assets use <span className="text-red-600 font-medium">Telnet</span>, an unencrypted protocol that transmits credentials in plaintext
          </li>
          <li>
            <span className="font-semibold">High-risk service combinations:</span> 45% of critical assets run both <span className="text-red-600 font-medium">RDP and SMB</span> services, a combination targeted in recent ransomware attacks
          </li>
          <li>
            <span className="font-semibold">Internet-exposed vulnerabilities:</span> 7 critical assets expose <span className="text-red-600 font-medium">RDP directly to DMZ or cloud environments</span>, creating significant attack vectors
          </li>
          <li>
            <span className="font-semibold">Server risk concentration:</span> 62% of critical assets are servers, with Ubuntu Linux systems accounting for 59% of all critical assets
          </li>
          <li>
            <span className="font-semibold">Multi-protocol exposure:</span> The average critical asset runs 8+ network services, creating a large potential attack surface
          </li>
          <li>
            <span className="font-semibold">Legacy file transfer services:</span> 38% of critical assets run <span className="text-red-600 font-medium">FTP</span>, with 5 instances directly exposed to internet-adjacent networks
          </li>
        </ul>
        
        <h3 className="text-lg font-semibold mt-6 mb-2">Recommended Priority Actions</h3>
        <ol className="list-decimal space-y-2 pl-5">
          <li>Replace Telnet with SSH across all systems</li>
          <li>Implement RDP Gateway/VPN for all remote access</li>
          <li>Disable SMBv1 across all systems</li>
          <li>Add network segmentation to isolate DMZ services</li>
          <li>Implement enhanced logging for all database servers</li>
        </ol>
      </div>
    </div>
  );
};

export default CriticalAssetAnalysis;