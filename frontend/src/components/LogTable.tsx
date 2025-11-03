import { useState } from 'react';
import { LogEntry } from '../utils/api';

interface LogTableProps {
  logs: LogEntry[];
}

export default function LogTable({ logs }: LogTableProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const logsPerPage = 50;

  // Filter logs
  const filteredLogs = logs.filter(log => 
    log.source_ip?.includes(searchTerm) ||
    log.url?.includes(searchTerm) ||
    log.status_code?.includes(searchTerm)
  );

  // Pagination
  const indexOfLastLog = currentPage * logsPerPage;
  const indexOfFirstLog = indexOfLastLog - logsPerPage;
  const currentLogs = filteredLogs.slice(indexOfFirstLog, indexOfLastLog);
  const totalPages = Math.ceil(filteredLogs.length / logsPerPage);

  return (
    <div>
      {/* Search */}
      <div className="mb-4">
        <input
          type="text"
          placeholder="🔍 Search by IP, URL, or status code..."
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setCurrentPage(1);
          }}
          className="w-full px-4 py-2 rounded-lg bg-white/10 border border-white/30 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-white/20">
              <th className="text-left text-white font-semibold p-3">Timestamp</th>
              <th className="text-left text-white font-semibold p-3">Source IP</th>
              <th className="text-left text-white font-semibold p-3">URL</th>
              <th className="text-left text-white font-semibold p-3">Action</th>
              <th className="text-left text-white font-semibold p-3">Status</th>
              <th className="text-left text-white font-semibold p-3">Bytes</th>
            </tr>
          </thead>
          <tbody>
            {currentLogs.map((log, idx) => (
              <tr
                key={log.id}
                className={`border-b border-white/10 hover:bg-white/5 transition ${
                  idx % 2 === 0 ? 'bg-white/5' : ''
                }`}
              >
                <td className="p-3 text-gray-300 font-mono text-xs">
                  {log.timestamp || '-'}
                </td>
                <td className="p-3 text-blue-300 font-mono">
                  {log.source_ip || '-'}
                </td>
                <td className="p-3 text-gray-300 truncate max-w-xs" title={log.url || ''}>
                  {log.url ? (
                    <span className="text-xs">{log.url.substring(0, 50)}{log.url.length > 50 ? '...' : ''}</span>
                  ) : '-'}
                </td>
                <td className="p-3 text-gray-300">
                  {log.action || '-'}
                </td>
                <td className="p-3">
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    log.status_code?.startsWith('2') ? 'bg-green-500/20 text-green-300' :
                    log.status_code?.startsWith('4') ? 'bg-yellow-500/20 text-yellow-300' :
                    log.status_code?.startsWith('5') ? 'bg-red-500/20 text-red-300' :
                    'bg-gray-500/20 text-gray-300'
                  }`}>
                    {log.status_code || '-'}
                  </span>
                </td>
                <td className="p-3 text-gray-400 text-xs">
                  {log.bytes_sent ? log.bytes_sent.toLocaleString() : '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-4 flex justify-between items-center">
          <div className="text-gray-400 text-sm">
            Showing {indexOfFirstLog + 1}-{Math.min(indexOfLastLog, filteredLogs.length)} of {filteredLogs.length}
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 bg-white/10 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-white/20 transition"
            >
              ← Prev
            </button>
            <div className="px-3 py-1 bg-blue-600 text-white rounded">
              {currentPage} / {totalPages}
            </div>
            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="px-3 py-1 bg-white/10 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-white/20 transition"
            >
              Next →
            </button>
          </div>
        </div>
      )}

      {filteredLogs.length === 0 && (
        <div className="text-center py-12 text-gray-400">
          No logs found matching your search.
        </div>
      )}
    </div>
  );
}