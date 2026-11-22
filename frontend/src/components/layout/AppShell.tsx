import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Sidebar } from './Sidebar';

export function AppShell() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="h-screen w-screen flex bg-factory-dark text-slate-100 overflow-hidden">
      <Sidebar mobileOpen={mobileOpen} onCloseMobile={() => setMobileOpen(false)} />

      <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
        <Header onOpenMobileMenu={() => setMobileOpen(true)} />
        <main className="flex-1 overflow-y-auto bg-factory-dark bg-grid-tech p-4 sm:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
