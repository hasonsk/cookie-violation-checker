// src/components/auth/LoginForm.js
import React, { useState } from 'react';
import { Mail, Lock, Shield } from 'lucide-react';
import { Card } from '../ui/Card';
import { mockUsers } from '../../data/mockData';

export const LoginForm = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async e => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    // Simulate API call
    setTimeout(() => {
      const user = mockUsers.find(
        u => u.email === email && u.password === password
      );
      if (user) {
        onLogin(user);
      } else {
        setError('Invalid email or password');
      }
      setIsLoading(false);
    }, 1000);
  };

  return (
    <div className='min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-6'>
      <Card className='w-full max-w-md p-8'>
        <div className='text-center mb-8'>
          <div className='w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center mx-auto mb-4'>
            <Shield className='text-white' size={32} />
          </div>
          <h1 className='text-2xl font-bold text-gray-900'>
            Cookie Policy Monitor
          </h1>
          <p className='text-gray-500 mt-2'>
            Sign in to access admin dashboard
          </p>
        </div>

        <form onSubmit={handleSubmit} className='space-y-4'>
          <div>
            <label className='block text-sm font-medium text-gray-700 mb-2'>
              Email
            </label>
            <div className='relative'>
              <Mail size={18} className='absolute left-3 top-3 text-gray-400' />
              <input
                type='email'
                value={email}
                onChange={e => setEmail(e.target.value)}
                className='w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
                placeholder='Enter your email'
                required
              />
            </div>
          </div>

          <div>
            <label className='block text-sm font-medium text-gray-700 mb-2'>
              Password
            </label>
            <div className='relative'>
              <Lock size={18} className='absolute left-3 top-3 text-gray-400' />
              <input
                type='password'
                value={password}
                onChange={e => setPassword(e.target.value)}
                className='w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
                placeholder='Enter your password'
                required
              />
            </div>
          </div>

          {error && (
            <div className='bg-red-50 border border-red-200 rounded-lg p-3'>
              <p className='text-red-600 text-sm'>{error}</p>
            </div>
          )}

          <button
            type='submit'
            disabled={isLoading}
            className={`w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors ${
              isLoading ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            {isLoading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className='mt-6 p-4 bg-gray-50 rounded-lg'>
          <p className='text-sm text-gray-600 mb-2'>Demo credentials:</p>
          <p className='text-xs text-gray-500'>
            Admin: admin@example.com / admin123
          </p>
          <p className='text-xs text-gray-500'>
            Manager: manager@example.com / manager123
          </p>
        </div>
      </Card>
    </div>
  );
};
