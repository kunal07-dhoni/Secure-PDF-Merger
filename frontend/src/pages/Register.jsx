import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useToast } from '../hooks/useToast';
import RegisterForm from '../components/Auth/RegisterForm';
import { FileText } from 'lucide-react';

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();
  const [loading, setLoading] = useState(false);

  const handleRegister = async (data) => {
    setLoading(true);
    try {
      await register(data);
      toast.success('Account created successfully!');
      navigate('/dashboard');
    } catch (error) {
      const msg = error.response?.data?.detail || 'Registration failed';
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-200px)] flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex p-3 bg-primary-100 dark:bg-primary-900 rounded-xl mb-4">
            <FileText className="w-8 h-8 text-primary-600" />
          </div>
          <h1 className="text-2xl font-bold">Create Account</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Start merging PDFs securely
          </p>
        </div>

        <div className="card">
          <RegisterForm onSubmit={handleRegister} loading={loading} />
        </div>
      </div>
    </div>
  );
}