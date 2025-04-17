
import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const SecurityToolGaps = () => {
  // Data from our analysis
  const missingToolsData = [
    { name: 'AzureAD', count: 6, criticalHigh: 2 },
    { name: 'Nessus', count: 6, criticalHigh: 2 },
    { name: 'Qualys', count: 6, criticalHigh: 6 },
    { name: 'CrowdStrike', count: 5, criticalHigh: 1 },
    { name: 'Wiz', count: 1, criticalHigh: 0 }
  ];

  const networkSegmentData = [
    { name: 'Internal', count: 6 },
    { name: 'DMZ', count: 3 },
    { name: 'Cloud', count: 5 }
  ];

  const criticalAssetsMissingTools = [
    { name: 'RZDC-SERVER-153', tools: ['Nessus', 'Qualys'], type: 'Server', os: 'Ubuntu Linux' },
    { name: 'RZDMZ-SERVER-262', tools: ['Qualys'], type: 'Server', os: 'Ubuntu Linux' },
    { name: 'RZDMZ-SERVER-284', tools: ['Qualys'], type: 'Server', os: 'Ubuntu Linux' },
    { name: 'RZCLOUD-SERVER-15', tools: ['AzureAD'], type: 'Server', os: 'Windows Server 2019' },
    { name: 'RZCLOUD-SERVER-03', tools: ['Qualys'], type: 'Server', os: 'Ubuntu Linux' },
    { name: 'RZCLOUD-SERVER-42', tools: ['Qualys'], type: 'Server', os: 'Ubuntu Linux' },
    { name: 'RZHQ-IP-CAMERA-43', tools: ['CrowdStrike', 'AzureAD', 'Nessus', 'Qualys'], type: 'IP Camera', os: 'Windows CE' }
  ];

  const qualysGapsByType = [
    { name: 'Servers', count: 5 },
    { name: 'IP Cameras', count: 1 }
  ];

  const azureADGapsByType = [
    { name: 'Servers', count: 3 },
    { name: 'Firewalls', count: 1 },
    { name: 'IP Cameras', count: 1 },
    { name: 'Desktops', count: 1 }
  ];

  // Colors for the charts
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];
  
  // Danger level colors
  const HIGH_RISK = '#d32f2f';
  const MEDIUM_RISK = '#ff9800';
  const LOW_RISK = '#2196f3';

  return (
    <div className="flex flex-col p-4 w-full">
      <h1 className="text-2xl font-bold mb-2">Security Tool Coverage Gaps Analysis</h1>
      <p className="text-gray-600 mb-4">Analysis of assets missing expected security monitoring tools</p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        <div>
          <h2 className="text-xl font-semibold mb-4">Missing Security Tools Overview</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={missingToolsData}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" name="Total Assets" fill={MEDIUM_RISK} />
                <Bar dataKey="criticalHigh" name="Critical/High Risk" fill={HIGH_RISK} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div>
          <h2 className="text-xl font-semibold mb-4">Missing Coverage by Network Segment</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={networkSegmentData}
                  cx="50%"
                  cy="50%"
                  labelLine={true}
                  label={({ name, percent, value }) => `${name}: ${value} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {networkSegmentData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [`${value} assets`, 'Missing Tools']} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Critical/High Risk Assets Missing Security Tools</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border border-gray-300">
            <thead className="bg-gray-100">
              <tr>
                <th className="py-2 px-4 border-b border-gray-300 text-left">Asset</th>
                <th className="py-2 px-4 border-b border-gray-300 text-left">Type</th>
                <th className="py-2 px-4 border-b border-gray-300 text-left">OS</th>
                <th className="py-2 px-4 border-b border-gray-300 text-left">Missing Tools</th>
              </tr>
            </thead>
            <tbody>
              {criticalAssetsMissingTools.map((asset, index) => (
                <tr key={index} className={index % 2 === 0 ? "bg-gray-50" : "bg-white"}>
                  <td className="py-2 px-4 border-b border-gray-300 font-medium">{asset.name}</td>
                  <td className="py-2 px-4 border-b border-gray-300">{asset.type}</td>
                  <td className="py-2 px-4 border-b border-gray-300">{asset.os}</td>
                  <td className="py-2 px-4 border-b border-gray-300">
                    {asset.tools.map((tool, idx) => (
                      <span key={idx} className="inline-block bg-red-100 text-red-800 px-2 py-1 text-xs font-semibold rounded-full mr-1 mb-1">
                        {tool}
                      </span>
                    ))}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        <div>
          <h2 className="text-lg font-semibold mb-3">Qualys Coverage Gaps by Device Type</h2>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={qualysGapsByType}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={60}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {qualysGapsByType.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-2 text-sm text-gray-600">
            <p>Qualys has 100% of missing coverage on critical/high risk assets</p>
          </div>
        </div>
        
        <div>
          <h2 className="text-lg font-semibold mb-3">AzureAD Coverage Gaps by Device Type</h2>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={azureADGapsByType}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={60}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {azureADGapsByType.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
      <div className="bg-gray-100 p-6 rounded-lg">
        <h2 className="text-xl font-semibold mb-3">Key Findings</h2>
        <ul className="list-disc space-y-2 pl-5">
          <li>
            <span className="font-semibold">Critical Qualys gap:</span> All 6 assets missing Qualys are critical/high risk, representing a significant vulnerability coverage gap
          </li>
          <li>
            <span className="font-semibold">Windows systems missing endpoint protection:</span> 5 Windows systems lack CrowdStrike, including 1 high-risk IP camera
          </li>
          <li>
            <span className="font-semibold">Cloud security monitoring gap:</span> 1 CentOS cloud server is missing all cloud security monitoring (Wiz)
          </li>
          <li>
            <span className="font-semibold">Multiple tool gaps in critical systems:</span> RZDC-SERVER-153 is missing both vulnerability scanning tools despite being a critical-risk asset
          </li>
          <li>
            <span className="font-semibold">Complete security gap:</span> The Windows CE IP camera (RZHQ-IP-CAMERA-43) is missing all 4 security tools despite its high-risk rating
          </li>
        </ul>
        
        <h3 className="text-lg font-semibold mt-6 mb-2">Recommended Actions</h3>
        <ol className="list-decimal space-y-2 pl-5">
          <li>Deploy Qualys to all critical/high-risk Ubuntu servers (6 systems)</li>
          <li>Install CrowdStrike on all Windows systems currently lacking endpoint protection (5 systems)</li>
          <li>Enroll missing Windows servers in AzureAD for identity management (3 servers)</li>
          <li>Deploy Wiz to the cloud CentOS server for cloud security monitoring</li>
          <li>Prioritize security tool deployment for the IP camera due to multiple missing controls</li>
        </ol>
      </div>
    </div>
  );
};

export default SecurityToolGaps;