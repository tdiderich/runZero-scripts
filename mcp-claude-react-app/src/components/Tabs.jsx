import React from "react";

const Tabs = ({ tabs, activeTab, onTabClick }) => (
  <div className="border-b border-brand">
    <nav className="-mb-px flex space-x-8">
      {tabs.map((tab) => (
        <button
          key={tab.name}
          onClick={() => onTabClick(tab.name)}
          className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
            activeTab === tab.name
              ? "border-brand text-brand-dark"
              : "border-transparent text-gray-500 hover:text-brand-dark hover:border-brand"
          }`}
        >
          {tab.name}
        </button>
      ))}
    </nav>
  </div>
);

export default Tabs;