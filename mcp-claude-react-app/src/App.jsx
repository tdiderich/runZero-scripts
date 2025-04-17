import React, { useState } from 'react';
import Tabs from './components/Tabs';
import AllAssetsDistribution from './views/AllAssetsDistribution';
import SubnetRiskAnalysis from './views/SubnetRiskAnalysis';
import CriticalAssetAnalysis from './views/CriticalAssetAnalysis';
import SecurityDashboard from './views/SecurityDashboard';
import SecurityToolGaps from './views/SecurityToolGaps';

const tabs = [
  { name: 'Executive Overview', Component: SecurityDashboard },
  { name: 'Security Tool Gaps', Component: SecurityToolGaps },
  { name: 'Assets Distribution', Component: AllAssetsDistribution },
  { name: 'Subnet Risk Analysis', Component: SubnetRiskAnalysis },
  { name: 'Critical Asset Analysis', Component: CriticalAssetAnalysis },
];


const App = () => {
  const [activeTab, setActiveTab] = useState(tabs[0].name);
  const ActiveComponent = tabs.find(tab => tab.name === activeTab).Component;

  return (
    <div className='container mx-auto p-4'>
      <Tabs tabs={tabs} activeTab={activeTab} onTabClick={setActiveTab} />
      <div className='mt-4'>
        <ActiveComponent />
      </div>
    </div>
  );
};

export default App;