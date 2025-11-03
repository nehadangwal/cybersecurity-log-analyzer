import { useState, useRef } from 'react';
import { uploadLog } from '../utils/api';
import { useRouter } from 'next/router';

// Define the expected structure for an anomaly
interface Anomaly {
  log_entry: any; // Simplified type for the original log data
  anomaly_type: string;
  description: string;
  confidence_score: number;
  severity: string;
}

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();
  
  // A proper solution would use session/token checking, but for this basic app:
  // We'll rely on the redirect from the login page for now.

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a log file to upload.");
      return;
    }

    setLoading(true);
    setAnomalies([]); // Clear old results

    try {
      // The uploadLog function is defined in your existing `api.ts`
      const result = await uploadLog(file); 
      
      if (result.anomalies) {
        // The backend `anomaly_detector.py` is currently just returning a list of dictionaries.
        setAnomalies(result.anomalies.map((a: any) => ({
            log_entry: a.log_entry || {},
            anomaly_type: a.anomaly_type || 'Unusual Activity', // Using the correct key
            description: a.description || 'Anomaly detected based on defined heuristics.', // Using the correct key
            confidence_score: a.confidence_score || 0.5, // Using the correct key
            severity: (a.confidence_score > 0.8 ? 'high' : 'medium') // Using the correct key
        })));
      }

    } catch (error) {
      alert("Error processing file. Check backend logs and network connection.");
      console.error(error);
    } finally {
      setLoading(false);
      // Reset file input after upload attempt
      if (fileInputRef.current) {
         fileInputRef.current.value = "";
      }
      setFile(null);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white shadow-lg rounded-lg">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">Cybersecurity Log Analyzer</h1>

      {/* Upload Section */}
      <div className="flex items-center space-x-4 mb-8 p-4 border rounded-lg bg-gray-50">
        <input 
          type="file" 
          onChange={handleFileChange} 
          ref={fileInputRef}
          accept=".log, .txt" 
          className="block w-full text-sm text-gray-500
          file:mr-4 file:py-2 file:px-4
          file:rounded-full file:border-0
          file:text-sm file:font-semibold
          file:bg-blue-50 file:text-blue-700
          hover:file:bg-blue-100"
        />
        <button 
          onClick={handleUpload} 
          disabled={!file || loading}
          className={`px-6 py-2 rounded-full text-white font-semibold transition duration-150 ease-in-out 
            ${!file || loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700'}`}
        >
          {loading ? 'Analyzing...' : 'Analyze Log'}
        </button>
      </div>

      {/* Results Section */}
      {anomalies.length > 0 && (
        <div className="mt-8">
          <h2 className="text-2xl font-semibold mb-4 text-red-600">
            🚨 Detected Anomalies ({anomalies.length})
          </h2>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Severity</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Source IP</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Confidence</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {anomalies.map((anomaly, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                        ${anomaly.severity === 'high' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}`}>
                        {anomaly.severity.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{anomaly.log_entry?.source_ip || 'N/A'}</td>
                    <td className="px-6 py-4 text-sm text-gray-500">{anomaly.description}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{(anomaly.confidence_score * 100).toFixed(2)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
      
      {/* No Results Message */}
      {!loading && anomalies.length === 0 && file && (
          <p className="mt-8 text-lg text-green-700 p-4 bg-green-50 border border-green-200 rounded-lg">
              ✅ Analysis complete. No high-confidence anomalies detected.
          </p>
      )}
      {loading && <p className="mt-8 text-center text-blue-500">Analyzing log file...</p>}
    </div>
  );
}