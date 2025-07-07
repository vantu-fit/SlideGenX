"use client";

import { useState } from "react";
import { DashboardLayout } from "@/components/dashboard-layout";
import { SlidesTab } from "@/components/slides-tab";
import { TemplatesTab } from "@/components/templates-tab";
import { SettingsTab } from "@/components/settings-tab";
import { ProtectedRoute } from "@/components/protected-route";

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState("slides");

  const renderContent = () => {
    switch (activeTab) {
      case "slides":
        return <SlidesTab />;
      case "templates":
        return <TemplatesTab />;
      case "settings":
        return <SettingsTab />;
      default:
        return <SlidesTab />;
    }
  };

  return (
    <ProtectedRoute>
      <DashboardLayout activeTab={activeTab} onTabChange={setActiveTab}>
        {renderContent()}
      </DashboardLayout>
    </ProtectedRoute>
  );
}
