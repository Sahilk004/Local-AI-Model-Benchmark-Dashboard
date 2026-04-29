import React, { useState, useEffect, useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, Clock, Cpu, Database } from 'lucide-react';
import api from '../api';

function Dashboard() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await api.get('/history');
      setHistory(res.data);
    } catch (error) {
      console.error("Error fetching history:", error);
    } finally {
      setLoading(false);
    }
  };

  const chartData = useMemo(() => {
    const dataMap = {};

    history.forEach(run => {
      const key = `${run.model_name}-${run.quantization}`;
      if (!dataMap[key]) {
        dataMap[key] = { name: key, count: 0, tpsSum: 0, latSum: 0, ramSum: 0 };
      }
      dataMap[key].count += 1;
      dataMap[key].tpsSum += run.tokens_per_sec || 0;
      dataMap[key].latSum += run.latency_ms || 0;
      dataMap[key].ramSum += run.ram_usage_mb || 0;
    });

    return Object.values(dataMap).map(item => ({
      name: item.name,
      avgTps: Math.round(item.tpsSum / item.count),
      avgLatency: Math.round(item.latSum / item.count),
      avgRam: Math.round(item.ramSum / item.count)
    }));
  }, [history]);

  if (loading) return <div className="p-8">Loading dashboard...</div>;

  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold mb-6">Benchmark Dashboard</h2>

      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <MetricCard title="Total Runs" value={history.length} icon={<Database className="h-6 w-6 text-blue-500" />} />

        <MetricCard
          title="Avg Latency"
          value={`${chartData.length > 0 ? Math.round(chartData.reduce((a, b) => a + b.avgLatency, 0) / chartData.length) : 0} ms`}
          icon={<Clock className="h-6 w-6 text-green-500" />}
        />

        <MetricCard
          title="Avg Speed"
          value={`${chartData.length > 0 ? Math.round(chartData.reduce((a, b) => a + b.avgTps, 0) / chartData.length) : 0} t/s`}
          icon={<Activity className="h-6 w-6 text-purple-500" />}
        />

        <MetricCard
          title="Avg RAM"
          value={`${chartData.length > 0 ? Math.round(chartData.reduce((a, b) => a + b.avgRam, 0) / chartData.length) : 0} MB`}
          icon={<Cpu className="h-6 w-6 text-red-500" />}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">

        {/* Tokens per Second */}
        <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <h3 className="text-lg font-semibold mb-4">Tokens per Second</h3>

          <div className="h-64 w-full flex items-center justify-center">
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="name" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155' }} />
                  <Bar dataKey="avgTps" fill="#6366f1" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-slate-400">No data available</p>
            )}
          </div>
        </div>

        {/* Latency */}
        <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <h3 className="text-lg font-semibold mb-4">Latency (ms)</h3>

          <div className="h-64 w-full flex items-center justify-center">
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="name" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155' }} />
                  <Bar dataKey="avgLatency" fill="#10b981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-slate-400">No data available</p>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}

function MetricCard({ title, value, icon }) {
  return (
    <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm flex items-center">
      <div className="p-3 rounded-full bg-slate-50 dark:bg-slate-800 mr-4">
        {icon}
      </div>
      <div>
        <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{title}</p>
        <p className="text-2xl font-bold">{value}</p>
      </div>
    </div>
  );
}

export default Dashboard;