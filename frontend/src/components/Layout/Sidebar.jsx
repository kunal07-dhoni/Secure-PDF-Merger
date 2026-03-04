import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Merge,
  History,
  Settings,
  HelpCircle,
  FileText,
} from 'lucide-react';
import clsx from 'clsx';

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/merge', label: 'Merge PDFs', icon: Merge },
  { to: '/history', label: 'History', icon: History },
];

export default function Sidebar({ isOpen = true, onClose }) {
  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={clsx(
          'fixed top-16 left-0 bottom-0 w-64 bg-white dark:bg-gray-800',
          'border-r border-gray-200 dark:border-gray-700 z-40',
          'transform transition-transform duration-300 ease-in-out',
          'lg:translate-x-0',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex flex-col h-full">
          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3 px-3">
              Main
            </p>
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={onClose}
                className={({ isActive }) =>
                  clsx(
                    'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium',
                    'transition-all duration-150',
                    isActive
                      ? 'bg-primary-100 dark:bg-primary-900/50 text-primary-700 dark:text-primary-300'
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700/50'
                  )
                }
              >
                <item.icon className="w-5 h-5 shrink-0" />
                <span>{item.label}</span>
              </NavLink>
            ))}
          </nav>

          {/* Bottom section */}
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <div className="bg-primary-50 dark:bg-primary-900/30 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <FileText className="w-5 h-5 text-primary-600" />
                <span className="font-semibold text-sm text-primary-700 dark:text-primary-300">
                  Pro Tip
                </span>
              </div>
              <p className="text-xs text-primary-600 dark:text-primary-400">
                Drag and drop files to reorder them before merging. You can also
                select specific page ranges for each file.
              </p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}