import React, { useEffect, useRef } from 'react';
import { Terminal, Clock } from 'lucide-react';

const ExecutionLog = ({ logs = [] }) => {
    const endRef = useRef(null);

    useEffect(() => {
        endRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [logs]);

    return (
        <div className="w-80 bg-slate-900 border-l border-slate-700 flex flex-col h-full">
            <div className="p-4 border-b border-slate-700 flex items-center gap-2">
                <Terminal size={16} className="text-blue-400" />
                <h2 className="text-slate-100 font-semibold">Execution Log</h2>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-3 font-mono text-sm">
                {logs.length === 0 ? (
                    <div className="text-slate-500 italic text-center mt-10">
                        Ready to execute...
                    </div>
                ) : (
                    logs.map((log, index) => (
                        <div key={index} className="flex gap-3 animate-in fade-in slide-in-from-bottom-2 duration-300">
                            <div className="text-slate-500 text-xs pt-0.5 min-w-[60px]">
                                {new Date(log.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                            </div>
                            <div className="flex-1">
                                <div className="text-slate-200 break-words">{log.message}</div>
                                {log.details && (
                                    <pre className="text-xs text-slate-500 mt-1 overflow-x-auto">
                                        {JSON.stringify(log.details, null, 2)}
                                    </pre>
                                )}
                            </div>
                        </div>
                    ))
                )}
                <div ref={endRef} />
            </div>
        </div>
    );
};

export default ExecutionLog;
