'use client';

import { useState } from 'react';

interface Invoice {
  id: string;
  date: string;
  amount: number;
  status: 'paid' | 'pending' | 'failed';
}

export default function BillingPage() {
  const [currentPlan, setCurrentPlan] = useState('professional');
  const [invoices] = useState<Invoice[]>([
    { id: 'INV-001', date: '2024-03-01', amount: 99.00, status: 'paid' },
    { id: 'INV-002', date: '2024-02-01', amount: 99.00, status: 'paid' },
    { id: 'INV-003', date: '2024-01-01', amount: 99.00, status: 'paid' },
  ]);

  const plans = [
    { id: 'starter', name: 'Starter', price: 29, features: ['5 users', '10GB storage', 'Email support'] },
    { id: 'professional', name: 'Professional', price: 99, features: ['25 users', '100GB storage', 'Priority support', 'Analytics'] },
    { id: 'enterprise', name: 'Enterprise', price: 299, features: ['Unlimited users', '1TB storage', '24/7 support', 'Custom integrations'] },
  ];

  return (
    <div className="p-6 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Billing</h1>
        <p className="text-slate-600 dark:text-slate-400">Manage your subscription and billing information</p>
      </div>

      {/* Current Plan */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Current Plan</h2>
        <div className="flex items-center justify-between p-4 bg-primary-50 dark:bg-primary-900/20 rounded-lg">
          <div>
            <p className="text-2xl font-bold text-primary-600 dark:text-primary-400">Professional</p>
            <p className="text-slate-600 dark:text-slate-400">$99/month • Renews on April 1, 2024</p>
          </div>
          <button className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-sm font-medium">
            Upgrade Plan
          </button>
        </div>
      </div>

      {/* Plans */}
      <div>
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Available Plans</h2>
        <div className="grid gap-6 md:grid-cols-3">
          {plans.map((plan) => (
            <div
              key={plan.id}
              className={`bg-white dark:bg-slate-900 rounded-xl border p-6 ${
                currentPlan === plan.id
                  ? 'border-primary-500 ring-2 ring-primary-500/20'
                  : 'border-slate-200 dark:border-slate-800'
              }`}
            >
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{plan.name}</h3>
              <p className="mt-2">
                <span className="text-3xl font-bold text-slate-900 dark:text-white">${plan.price}</span>
                <span className="text-slate-500">/month</span>
              </p>
              <ul className="mt-4 space-y-2">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-center text-sm text-slate-600 dark:text-slate-400">
                    <svg className="w-4 h-4 mr-2 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {feature}
                  </li>
                ))}
              </ul>
              <button
                className={`mt-6 w-full py-2 rounded-lg text-sm font-medium ${
                  currentPlan === plan.id
                    ? 'bg-slate-100 dark:bg-slate-800 text-slate-400 cursor-default'
                    : 'bg-primary-600 hover:bg-primary-700 text-white'
                }`}
                disabled={currentPlan === plan.id}
              >
                {currentPlan === plan.id ? 'Current Plan' : 'Switch Plan'}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Payment Method */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Payment Method</h2>
        <div className="flex items-center justify-between p-4 border border-slate-200 dark:border-slate-700 rounded-lg">
          <div className="flex items-center gap-4">
            <div className="h-12 w-20 bg-gradient-to-r from-blue-600 to-blue-800 rounded flex items-center justify-center">
              <span className="text-white font-bold text-xs">VISA</span>
            </div>
            <div>
              <p className="font-medium text-slate-900 dark:text-white">•••• •••• •••• 4242</p>
              <p className="text-sm text-slate-500">Expires 12/2025</p>
            </div>
          </div>
          <button className="text-primary-600 hover:text-primary-500 text-sm font-medium">Update</button>
        </div>
      </div>

      {/* Invoices */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Invoice History</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-700">
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-500">Invoice</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-500">Date</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-500">Amount</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-500">Status</th>
                <th className="text-right py-3 px-4 text-sm font-medium text-slate-500"></th>
              </tr>
            </thead>
            <tbody>
              {invoices.map((invoice) => (
                <tr key={invoice.id} className="border-b border-slate-100 dark:border-slate-800">
                  <td className="py-3 px-4 text-sm font-medium text-slate-900 dark:text-white">{invoice.id}</td>
                  <td className="py-3 px-4 text-sm text-slate-600 dark:text-slate-400">{invoice.date}</td>
                  <td className="py-3 px-4 text-sm text-slate-900 dark:text-white">${invoice.amount.toFixed(2)}</td>
                  <td className="py-3 px-4">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      invoice.status === 'paid'
                        ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                        : invoice.status === 'pending'
                        ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
                        : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                    }`}>
                      {invoice.status.charAt(0).toUpperCase() + invoice.status.slice(1)}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button className="text-primary-600 hover:text-primary-500 text-sm font-medium">Download</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
