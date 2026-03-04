import React, { useEffect, useState, useCallback } from 'react';
import { historyAPI } from '../api/history';
import { useToast } from '../hooks/useToast';
import HistoryTable from '../components/History/HistoryTable';
import Spinner from '../components/UI/Spinner';
import Button from '../components/UI/Button';
import { History as HistoryIcon, ChevronLeft, ChevronRight } from 'lucide-react';

export default function History() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const toast = useToast();

  const loadHistory = useCallback(async () => {
    setLoading(true);
    try {
      const response = await historyAPI.getHistory(page, 15);
      setData(response.data);
    } catch (err) {
      toast.error('Failed to load history');
    } finally {
      setLoading(false);
    }
  }, [page, toast]);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const handleDownload = async (recordId) => {
    try {
      const response = await historyAPI.downloadFile(recordId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'merged.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success('Download started!');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Download failed');
    }
  };

  const handleDelete = async (recordId) => {
    try {
      await historyAPI.deleteRecord(recordId);
      toast.success('Record deleted');
      loadHistory();
    } catch (err) {
      toast.error('Failed to delete record');
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <HistoryIcon className="w-7 h-7 text-primary-600" />
            Merge History
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            View and manage your past PDF merges
          </p>
        </div>

        {data && (
          <p className="text-sm text-gray-500">
            {data.total} total record{data.total !== 1 ? 's' : ''}
          </p>
        )}
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Spinner size="lg" />
        </div>
      ) : (
        <>
          <HistoryTable
            items={data?.items || []}
            onDownload={handleDownload}
            onDelete={handleDelete}
          />

          {/* Pagination */}
          {data && data.total_pages > 1 && (
            <div className="flex items-center justify-center gap-4 mt-8">
              <Button
                variant="secondary"
                size="sm"
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
              >
                <ChevronLeft className="w-4 h-4" />
                Previous
              </Button>

              <span className="text-sm text-gray-500">
                Page {data.page} of {data.total_pages}
              </span>

              <Button
                variant="secondary"
                size="sm"
                disabled={page >= data.total_pages}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}