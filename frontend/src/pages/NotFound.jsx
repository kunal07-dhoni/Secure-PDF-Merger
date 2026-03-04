import React from 'react';
import { Link } from 'react-router-dom';
import { Home, ArrowLeft, FileQuestion } from 'lucide-react';
import Button from '../components/UI/Button';

export default function NotFound() {
  return (
    <div className="min-h-[calc(100vh-200px)] flex items-center justify-center px-4">
      <div className="text-center max-w-md">
        <div className="inline-flex p-4 bg-gray-100 dark:bg-gray-800 rounded-full mb-6">
          <FileQuestion className="w-16 h-16 text-gray-400" />
        </div>

        <h1 className="text-6xl font-bold text-gray-200 dark:text-gray-700 mb-2">
          404
        </h1>

        <h2 className="text-2xl font-bold mb-2">Page Not Found</h2>

        <p className="text-gray-500 dark:text-gray-400 mb-8">
          The page you're looking for doesn't exist or has been moved.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link to="/">
            <Button variant="primary">
              <Home className="w-4 h-4" />
              Go Home
            </Button>
          </Link>

          <Button variant="secondary" onClick={() => window.history.back()}>
            <ArrowLeft className="w-4 h-4" />
            Go Back
          </Button>
        </div>
      </div>
    </div>
  );
}