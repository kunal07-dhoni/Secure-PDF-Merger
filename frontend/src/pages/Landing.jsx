import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import {
  Shield,
  Zap,
  Lock,
  FileText,
  ArrowRight,
  CheckCircle2,
  Merge,
} from 'lucide-react';

export default function Landing() {
  const { user } = useAuth();

  const features = [
    {
      icon: Shield,
      title: 'Privacy First',
      description: 'Files auto-delete after processing. We never store your documents permanently.',
    },
    {
      icon: Zap,
      title: 'Lightning Fast',
      description: 'Merge multiple PDFs in seconds with our optimized processing engine.',
    },
    {
      icon: Lock,
      title: 'Bank-Level Security',
      description: 'End-to-end encryption, secure headers, and strict input validation.',
    },
    {
      icon: Merge,
      title: 'Smart Merging',
      description: 'Drag to reorder, select page ranges, add watermarks, and compress output.',
    },
  ];

  const steps = [
    'Upload your PDF files (drag & drop supported)',
    'Reorder files by dragging them',
    'Set options: page ranges, watermark, compression',
    'Click merge and download your result',
  ];

  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-32">
          <div className="text-center max-w-3xl mx-auto">
            <div className="inline-flex items-center gap-2 bg-primary-100 dark:bg-primary-900/50 text-primary-700 dark:text-primary-300 px-4 py-2 rounded-full text-sm font-medium mb-6">
              <Shield className="w-4 h-4" />
              Privacy-Focused PDF Processing
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight">
              Merge PDFs{' '}
              <span className="text-primary-600">Securely</span>
              <br />
              in Seconds
            </h1>

            <p className="mt-6 text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              Fast, private, and powerful PDF merging platform. Upload multiple PDFs,
              reorder them, set page ranges, and download your merged document.
              Files are automatically deleted after processing.
            </p>

            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                to={user ? '/merge' : '/register'}
                className="btn-primary text-base py-3 px-8 flex items-center gap-2"
              >
                {user ? 'Start Merging' : 'Get Started Free'}
                <ArrowRight className="w-5 h-5" />
              </Link>
              {!user && (
                <Link
                  to="/login"
                  className="btn-secondary text-base py-3 px-8"
                >
                  Sign In
                </Link>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 bg-white dark:bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold">Why Choose Secure PDF Merger?</h2>
            <p className="mt-4 text-gray-600 dark:text-gray-400">
              Built with security and privacy as core principles
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, idx) => (
              <div key={idx} className="card hover:shadow-lg transition-shadow text-center">
                <div className="inline-flex p-3 bg-primary-100 dark:bg-primary-900/50 rounded-xl mb-4">
                  <feature.icon className="w-6 h-6 text-primary-600" />
                </div>
                <h3 className="font-semibold text-lg mb-2">{feature.title}</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold">How It Works</h2>
            <p className="mt-4 text-gray-600 dark:text-gray-400">
              Four simple steps to merge your PDFs
            </p>
          </div>

          <div className="max-w-2xl mx-auto space-y-4">
            {steps.map((step, idx) => (
              <div key={idx} className="flex items-start gap-4 card">
                <div className="flex items-center justify-center w-8 h-8 bg-primary-600 text-white rounded-full shrink-0 font-bold text-sm">
                  {idx + 1}
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-green-500 shrink-0" />
                  <p className="text-gray-700 dark:text-gray-300">{step}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-primary-600">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Merge Your PDFs?
          </h2>
          <p className="text-primary-100 mb-8 text-lg">
            Join thousands of users who trust us with their documents.
          </p>
          <Link
            to={user ? '/merge' : '/register'}
            className="inline-flex items-center gap-2 bg-white text-primary-600 font-semibold
                       py-3 px-8 rounded-lg hover:bg-primary-50 transition-colors text-base"
          >
            <FileText className="w-5 h-5" />
            {user ? 'Go to Merger' : 'Create Free Account'}
          </Link>
        </div>
      </section>
    </div>
  );
}