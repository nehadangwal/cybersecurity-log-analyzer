import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';
import { getAnalysis, AnalysisResult } from '../../utils/api';
import LogTable from '../../components/LogTable';
import TimelineChart from '../../components/TimelineChart';
import AnomalyCard from '../../components/AnomalyCard';

export default function Results() {
  const router = useRouter();
  const { id } = router.query;
  
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'summary' | 'anomalies' | 'timeline' | 'logs'>('summary');

  useEffect(() => {
    if (id) {
      loadResults();
    }
  }, [id]);

  const loadResults = async () => {
    try {
      const data = await getAnalysis(Number(id));
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load results');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">🔄 Loading results...</div>
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center px-4">
        <div className="bg-red-500/20 border border-red-500 rounded-lg p-6 max-w-md">
          <div className="text-red-200">❌ {error || 'Analysis not found'}</div>
          <button
            onClick={() => router.push('/')}
            className="mt-4 text-blue-400 hover:text-blue-300"
          >
            ← Back to Home
          </button>
        </div>
      </div>
    );
  }

  const { analysis, anomalies, timeline, log_entries } = result;
  const severityCounts = {
    critical: anomalies.filter(a => a.severity === 'critical').length,
    high: anomalies.filter(a => a.severity === 'high').length,
    medium: anomalies.filter(a => a.severity === 'medium').length,
    low: anomalies.filter(a => a.severity === 'low').length,
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 px-4 py-8">
      <div className="container mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.push('/')}
            className="text-blue-400 hover:text-blue-300 mb-4"
          >
            ← Back to Home
          </button>
          <h1 className="text-4xl font-bold text-white mb-2">
            📊 Analysis Results
          </h1>
          <div className="text-gray-300">
            {analysis.filename} • {new Date(analysis.upload_time).toLocaleString()}
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white/10 backdrop-blur-md rounded-lg p-6">
            <div className="text-3xl font-bold text-white mb-1">
              {analysis.total_entries.toLocaleString()}
            </div>
            <div className="text-gray-300">Total Entries</div>
          </div>
          <div className="bg-white/10 backdrop-blur-md rounded-lg p-6">
            <div className="text-3xl font-bold text-red-400 mb-1">
              {analysis.anomaly_count}
            </div>
            <div className="text-gray-300">Anomalies Found</div>
          </div>
          <div className="bg-white/10 backdrop-blur-md rounded-lg p-6">
            <div className="text-3xl font-bold text-orange-400 mb-1">
              {severityCounts.critical + severityCounts.high}
            </div>
            <div className="text-gray-300">High Priority</div>
          </div>
          <div className="bg-white/10 backdrop-blur-md rounded-lg p-6">
            <div className="text-3xl font-bold text-green-400 mb-1">
              {analysis.status === 'completed' ? '✓' : '...'}
            </div>
            <div className="text-gray-300">Status</div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white/10 backdrop-blur-md rounded-t-lg">
          <div className="flex border-b border-white/20">
            <button
              onClick={() => setActiveTab('summary')}
              className={`px-6 py-3 font-semibold transition ${
                activeTab === 'summary'
                  ? 'text-white border-b-2 border-blue-500'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              📋 Summary
            </button>
            <button
              onClick={() => setActiveTab('anomalies')}
              className={`px-6 py-3 font-semibold transition ${
                activeTab === 'anomalies'
                  ? 'text-white border-b-2 border-blue-500'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              🚨 Anomalies ({analysis.anomaly_count})
            </button>
            <button
              onClick={() => setActiveTab('timeline')}
              className={`px-6 py-3 font-semibold transition ${
                activeTab === 'timeline'
                  ? 'text-white border-b-2 border-blue-500'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              📈 Timeline
            </button>
            <button
              onClick={() => setActiveTab('logs')}
              className={`px-6 py-3 font-semibold transition ${
                activeTab === 'logs'
                  ? 'text-white border-b-2 border-blue-500'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              📄 All Logs
            </button>
          </div>
        </div>

        {/* Tab Content */}
        <div className="bg-white/10 backdrop-blur-md rounded-b-lg p-6">
          {activeTab === 'summary' && (
            <div>
              <h2 className="text-2xl font-bold text-white mb-4">Executive Summary</h2>
              <div className="bg-white/5 rounded-lg p-6 mb-6">
                <pre className="text-gray-200 whitespace-pre-wrap font-mono text-sm">
                  {analysis.summary}
                </pre>
              </div>

              <h3 className="text-xl font-bold text-white mb-3">Severity Distribution</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-red-500/20 border border-red-500 rounded-lg p-4 text-center">
                  <div className="text-3xl font-bold text-red-400">{severityCounts.critical}</div>
                  <div className="text-red-200 text-sm">Critical</div>
                </div>
                <div className="bg-orange-500/20 border border-orange-500 rounded-lg p-4 text-center">
                  <div className="text-3xl font-bold text-orange-400">{severityCounts.high}</div>
                  <div className="text-orange-200 text-sm">High</div>
                </div>
                <div className="bg-yellow-500/20 border border-yellow-500 rounded-lg p-4 text-center">
                  <div className="text-3xl font-bold text-yellow-400">{severityCounts.medium}</div>
                  <div className="text-yellow-200 text-sm">Medium</div>
                </div>
                <div className="bg-blue-500/20 border border-blue-500 rounded-lg p-4 text-center">
                  <div className="text-3xl font-bold text-blue-400">{severityCounts.low}</div>
                  <div className="text-blue-200 text-sm">Low</div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'anomalies' && (
            <div>
              <h2 className="text-2xl font-bold text-white mb-4">
                Detected Anomalies ({anomalies.length})
              </h2>
              {anomalies.length === 0 ? (
                <div className="text-center py-12 text-gray-400">
                  ✅ No anomalies detected. System appears normal.
                </div>
              ) : (
                <div className="space-y-4">
                  {anomalies.map((anomaly) => (
                    <AnomalyCard key={anomaly.id} anomaly={anomaly} />
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'timeline' && (
            <div>
              <h2 className="text-2xl font-bold text-white mb-4">Activity Timeline</h2>
              <TimelineChart data={timeline} />
            </div>
          )}

          {activeTab === 'logs' && (
            <div>
              <h2 className="text-2xl font-bold text-white mb-4">
                All Log Entries ({log_entries.length})
              </h2>
              <LogTable logs={log_entries} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}