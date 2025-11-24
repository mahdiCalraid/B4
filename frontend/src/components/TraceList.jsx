import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Clock, Terminal } from 'lucide-react';

const TraceList = ({ onSelectTrace, selectedTraceId, traces: propTraces }) => {
  const [traces, setTraces] = useState([]);
  const [error, setError] = useState(null);

  const fetchTraces = async () => {
    if (propTraces) {
      setTraces(propTraces);
      return;
    }
    try {
      const response = await axios.get('http://localhost:8080/api/traces');
      console.log("Fetched traces:", response.data);
      setTraces(response.data.traces);
      setError(null);
    } catch (error) {
      console.error("Failed to fetch traces", error);
      setError(error.message);
    }
  };

  useEffect(() => {
    fetchTraces();
    if (!propTraces) {
      const interval = setInterval(fetchTraces, 5000); // Poll every 5s
      return () => clearInterval(interval);
    }
  }, [propTraces]);

  return (
    <div className="w-64 bg-gray-50 border-r border-gray-200 h-screen overflow-y-auto flex flex-col">
      <div className="p-4 border-b border-gray-200 bg-white">
        <h2 className="font-semibold text-gray-700 flex items-center gap-2">
          <Terminal size={18} />
          Executions
        </h2>
      </div>
      <div className="flex-1">
        {error && (
          <div className="p-4 text-red-500 text-sm bg-red-50 border-b border-red-100">
            Error: {error}
          </div>
        )}
        {traces.length === 0 && !error ? (
          <div className="p-4 text-gray-400 text-sm text-center">
            No traces found. Run a request to see it here.
          </div>
        ) : (
          traces.map((trace) => (
            <div
              key={trace.trace_id}
              onClick={() => onSelectTrace(trace.trace_id)}
              className={`p-4 border-b border-gray-100 cursor-pointer transition-all duration-200 group ${selectedTraceId === trace.trace_id
                  ? 'bg-blue-50 border-l-4 border-l-blue-500 shadow-inner'
                  : 'hover:bg-gray-50 border-l-4 border-l-transparent'
                }`}
            >
              <div className={`text-sm font-semibold truncate mb-1 ${selectedTraceId === trace.trace_id ? 'text-blue-700' : 'text-gray-700 group-hover:text-gray-900'
                }`}>
                {trace.input_preview || "No Input"}
              </div>
              <div className="flex items-center justify-between mt-2">
                <div className="flex items-center text-xs text-gray-400 gap-1.5 font-mono">
                  <Clock size={12} />
                  {new Date(trace.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wide ${selectedTraceId === trace.trace_id ? 'bg-blue-200 text-blue-700' : 'bg-gray-100 text-gray-500'
                  }`}>
                  {trace.step_count} steps
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default TraceList;
