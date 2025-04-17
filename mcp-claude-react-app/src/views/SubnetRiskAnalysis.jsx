import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

const SubnetRiskAnalysis = () => {
  // Data from our analysis
  const subnetRiskData = [
    {
      subnet: "10.0.1.0/24", 
      averageScore: 2.80, 
      totalScore: 14, 
      critical: 1, 
      high: 2, 
      medium: 2, 
      total: 5,
      riskDensity: 60
    },
    {
      subnet: "10.0.19.0/24", 
      averageScore: 2.80, 
      totalScore: 14, 
      critical: 2, 
      high: 1, 
      medium: 1, 
      total: 5,
      riskDensity: 60
    },
    {
      subnet: "198.51.26.0/24", 
      averageScore: 2.80, 
      totalScore: 14, 
      critical: 2, 
      high: 0, 
      medium: 3, 
      total: 5,
      riskDensity: 40
    },
    {
      subnet: "23.20.1.0/24", 
      averageScore: 2.80, 
      totalScore: 14, 
      critical: 2, 
      high: 0, 
      medium: 3, 
      total: 5,
      riskDensity: 40
    },
    {
      subnet: "10.0.8.0/24", 
      averageScore: 2.60, 
      totalScore: 13, 
      critical: 1, 
      high: 1, 
      medium: 3, 
      total: 5,
      riskDensity: 40
    },
    {
      subnet: "10.0.12.0/24", 
      averageScore: 2.60, 
      totalScore: 13, 
      critical: 1, 
      high: 1, 
      medium: 3, 
      total: 5,
      riskDensity: 40
    },
    {
      subnet: "23.20.4.0/24", 
      averageScore: 2.60, 
      totalScore: 13, 
      critical: 2, 
      high: 0, 
      medium: 2, 
      total: 5,
      riskDensity: 40
    },
    {
      subnet: "10.0.9.0/24", 
      averageScore: 2.40, 
      totalScore: 12, 
      critical: 1, 
      high: 1, 
      medium: 2, 
      total: 5,
      riskDensity: 40
    },
    {
      subnet: "10.0.11.0/24", 
      averageScore: 2.40, 
      totalScore: 12, 
      critical: 0, 
      high: 2, 
      medium: 3, 
      total: 5,
      riskDensity: 40
    },
    {
      subnet: "10.0.16.0/24", 
      averageScore: 2.40, 
      totalScore: 12, 
      critical: 2, 
      high: 0, 
      medium: 2, 
      total: 5,
      riskDensity: 40
    }
  ];

  // Sort by average score for display
  const sortedData = [...subnetRiskData].sort((a, b) => b.averageScore - a.averageScore);

  // Colors for our risk charts
  const criticalColor = "#d32f2f";
  const highColor = "#f57c00";
  const mediumColor = "#fbc02d";

  return (
    <div className="flex flex-col p-4 w-full">
      <h1 className="text-2xl font-bold mb-4">Highest Risk Subnets in runZero Environment</h1>
      
      <p className="mb-4">
        This analysis aggregates risk levels of all assets within each /24 subnet in your runZero environment.
        Risk scores are calculated based on the severity of issues found: Critical (4 points), High (3 points), 
        Medium (2 points), Low (1 point), and Info (0 points).
      </p>
      
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-2">Top 10 Highest Risk Subnets</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border border-gray-300">
            <thead className="bg-gray-100">
              <tr>
                <th className="py-2 px-4 border-b border-gray-300 text-left">Rank</th>
                <th className="py-2 px-4 border-b border-gray-300 text-left">Subnet</th>
                <th className="py-2 px-4 border-b border-gray-300 text-left">Avg Risk</th>
                <th className="py-2 px-4 border-b border-gray-300 text-left">Critical</th>
                <th className="py-2 px-4 border-b border-gray-300 text-left">High</th>
                <th className="py-2 px-4 border-b border-gray-300 text-left">Medium</th>
                <th className="py-2 px-4 border-b border-gray-300 text-left">Total Assets</th>
                <th className="py-2 px-4 border-b border-gray-300 text-left">Risk Density</th>
              </tr>
            </thead>
            <tbody>
              {sortedData.map((item, index) => (
                <tr key={index} className={index % 2 === 0 ? "bg-gray-50" : "bg-white"}>
                  <td className="py-2 px-4 border-b border-gray-300">{index + 1}</td>
                  <td className="py-2 px-4 border-b border-gray-300 font-medium">{item.subnet}</td>
                  <td className="py-2 px-4 border-b border-gray-300">{item.averageScore.toFixed(2)}</td>
                  <td className="py-2 px-4 border-b border-gray-300 text-red-600 font-bold">{item.critical}</td>
                  <td className="py-2 px-4 border-b border-gray-300 text-orange-500 font-bold">{item.high}</td>
                  <td className="py-2 px-4 border-b border-gray-300 text-yellow-500">{item.medium}</td>
                  <td className="py-2 px-4 border-b border-gray-300">{item.total}</td>
                  <td className="py-2 px-4 border-b border-gray-300">{item.riskDensity}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Risk Distribution by Subnet</h2>
        <div className="h-96">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={sortedData}
              layout="vertical"
              margin={{ top: 20, right: 30, left: 100, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" domain={[0, 5]} />
              <YAxis dataKey="subnet" type="category" width={100} />
              <Tooltip 
                formatter={(value, name) => {
                  return [value, name === 'critical' ? 'Critical' : name === 'high' ? 'High' : name === 'medium' ? 'Medium' : 'Low/Info'];
                }}
              />
              <Legend />
              <Bar dataKey="critical" stackId="a" fill={criticalColor} name="Critical" />
              <Bar dataKey="high" stackId="a" fill={highColor} name="High" />
              <Bar dataKey="medium" stackId="a" fill={mediumColor} name="Medium" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-gray-100 p-4 rounded-lg">
        <h2 className="text-lg font-semibold mb-2">Key Findings:</h2>
        <ul className="list-disc ml-5 space-y-1">
          <li><span className="font-medium">10.0.1.0/24 and 10.0.19.0/24</span> are the highest risk subnets with average risk scores of 2.80</li>
          <li>DMZ subnet <span className="font-medium">198.51.26.0/24</span> has 2 critical-risk systems that should be prioritized</li>
          <li>Cloud subnet <span className="font-medium">23.20.1.0/24</span> contains 2 critical assets with multiple internet-exposed services</li>
          <li>Based on risk density (% of high/critical assets), <span className="font-medium">10.0.1.0/24 and 10.0.19.0/24</span> have the highest concentration (60%)</li>
          <li>All top 10 subnets have at least 2 high or critical risk assets, indicating widespread security concerns</li>
        </ul>
      </div>
    </div>
  );
};

export default SubnetRiskAnalysis;