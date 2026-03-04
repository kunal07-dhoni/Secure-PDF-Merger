import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { historyAPI } from '../api/history';
import {
  Merge,
  History,
  FileStack,
  TrendingUp,
  Calendar,
  ArrowRight,
} from 'lucide-react';
import { formatDate } from '../utils/helpers';

export default function Dashboard() {
  const { user } = useAuth();
  const [recentHistory, setRecentHistory] = useState([]);
  const [stats, setStats] = useState({ total: 0 });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const response = await historyAPI.getHistory(1, 5);
      setRecentHistory(response.data.items);
      setStats({ total: response.data.total });
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Welcome */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold">
          Welcome back, {user?.full_name || user?.username}! 👋
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Here's your PDF merging overview
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-primary-100 dark:bg-primary-900/50 rounded-xl">
              <FileStack className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{user?.merge_count || 0}</p>
              <p className="text-sm text-gray-500">Total Merges</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-100 dark:bg-green-900/50 rounded-xl">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.total}</p>
              <p className="text-sm text-gray-500">History Records</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-purple-100 dark:bg-purple-900/50 rounded-xl">
              <Calendar className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">
                {user?.created_at ? formatDate(user.created_at).split(',')[0] : 'N/A'}
              </p>
              <p className="text-sm text-gray-500">Member Since</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <Link
          to="/merge"
          className="card hover:shadow-lg transition-all group border-2 border-transparent hover:border-primary-300 dark:hover:border-primary-700"
        >
          <div className="flex items-center gap-4">
            <div className="p-4 bg-primary-100 dark:bg-primary-900/50 rounded-xl group-hover:scale-110 transition-transform">
              <Merge className="w-8 h-8 text-primary-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-lg">Merge PDFs</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Upload and merge multiple PDF files
              </p>
            </div>
            <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-primary-600 group-hover:translate-x-1 transition-all" />
          </div>
        </Link>

        <Link
          to="/history"
          className="card hover:shadow-lg transition-all group border-2 border-transparent hover:border-primary-300 dark:hover:border-primary-700"
        >
          <div className="flex items-center gap-4">
            <div className="p-4 bg-green-100 dark:bg-green-900/50 rounded-xl group-hover:scale-110 transition-transform">
              <History className="w-8 h-8 text-green-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-lg">View History</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                See past merges and download files
              </p>
            </div>
            <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-green-600 group-hover:translate-x-1 transition-all" />
          </div>
        </Link>
      </div>

      {/* Recent Activity */}
      {recentHistory.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Recent Activity</h2>
            <Link to="/history" className="text-sm text-primary-600 hover:text-primary-700 font-medium">
              View All →
            </Link>
          </div>

          <div className="space-y-2">
            {recentHistory.map((item) => (
              <div key={item.id} className="card py-3">
                <div className="flex items-center gap-3">
                  <FileStack className="w-5 h-5 text-primary-500 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm truncate">{item.output_filename}</p>
                    <p className="text-xs text-gray-500">
                      {item.file_count} files · {item.total_pages} pages · {formatDate(item.created_at)}
                    </p>
                  </div>
                  <span
                    className={`text-xs px-2 py-1 rounded-full ${
                      item.status === 'completed'
                        ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                        : 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
                    }`}
                  >
                    {item.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}