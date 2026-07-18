'use client';

import React, { useState, useRef } from 'react';
import { uploadService } from '@/services/upload';
import { UploadResponse } from '@/types';
import { motion, AnimatePresence } from 'framer-motion';
import {
  UploadCloud,
  FileSpreadsheet,
  AlertTriangle,
  CheckCircle2,
  Trash2,
  ListRestart,
  History
} from 'lucide-react';

export default function UploadPage() {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [response, setResponse] = useState<UploadResponse | null>(null);
  const [error, setError] = useState('');
  
  const [uploadHistory, setUploadHistory] = useState<UploadResponse[]>(() => [
    {
      success: true,
      message: 'Transaction history synced successfully.',
      fileId: 'file_init_01',
      fileName: 'q1_dine_in_sales.csv',
      rowCount: 1840,
      columnsDetected: ['date', 'time', 'ticket_id', 'total_amount', 'item_count'],
      validationErrors: [],
      uploadedAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString()
    },
    {
      success: true,
      message: 'Supplier order sheets reconciled.',
      fileId: 'file_init_02',
      fileName: 'inventory_safety_margins.xlsx',
      rowCount: 450,
      columnsDetected: ['item_id', 'safety_stock', 'lead_time_days', 'reorder_qty'],
      validationErrors: [],
      uploadedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString()
    }
  ]);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (selectedFile: File) => {
    const ext = selectedFile.name.split('.').pop()?.toLowerCase();
    if (ext !== 'csv' && ext !== 'xlsx' && ext !== 'xls') {
      setError('Unsupported file type. Please upload a valid CSV or Excel spreadsheet.');
      setFile(null);
      return;
    }
    setError('');
    setFile(selectedFile);
    setResponse(null);
    setProgress(0);
  };

  const triggerUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError('');
    setProgress(0);

    try {
      const res = await uploadService.uploadData(file, (p) => {
        setProgress(p);
      });
      setResponse(res);
      if (res.success) {
        setUploadHistory((prev) => [res, ...prev]);
      } else {
        setError(res.message);
      }
    } catch (err: unknown) {
      const errMsg = err instanceof Error ? err.message : (typeof err === 'object' && err !== null && 'message' in err ? String((err as Record<string, unknown>).message) : 'An error occurred during file upload transmission.');
      setError(errMsg);
    } finally {
      setUploading(false);
    }
  };

  const clearFile = () => {
    setFile(null);
    setResponse(null);
    setProgress(0);
    setError('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="space-y-8 font-sans">
      
      {/* Top Header */}
      <div>
        <h1 className="text-3xl font-extrabold font-outfit text-foreground tracking-tight">Data Ingestion Center</h1>
        <p className="text-muted text-xs mt-1">
          Drop restaurant transaction logs, inventories, and shift metrics here to rebuild node relationships.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        
        {/* Upload Zone & Previews */}
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-card p-6 rounded-2xl">
            
            {/* Drag Zone */}
            {!file ? (
              <div
                onDragEnter={handleDrag}
                onDragOver={handleDrag}
                onDragLeave={handleDrag}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`border-2 border-dashed rounded-2xl p-10 text-center flex flex-col items-center justify-center cursor-pointer transition-all duration-200 min-h-64 ${
                  dragActive
                    ? 'border-blue-500 bg-blue-500/5'
                    : 'border-edge bg-surface/10 hover:border-edge-strong hover:bg-surface/30'
                }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  onChange={handleFileChange}
                  accept=".csv, .xlsx, .xls"
                  className="hidden"
                />
                
                <div className="p-4 rounded-full bg-blue-500/10 border border-blue-500/10 text-blue-400 mb-4 animate-bounce">
                  <UploadCloud className="h-7 w-7" />
                </div>
                
                <h3 className="text-base font-bold text-strong font-outfit">Select CSV or Excel logs</h3>
                <p className="text-xs text-faint mt-1.5 max-w-sm leading-relaxed">
                  Drag and drop local sheets or browse your files. Supported formats: .csv, .xls, .xlsx
                </p>
              </div>
            ) : (
              /* Selected file state */
              <div className="border border-edge bg-surface-deep/20 rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-3 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/15">
                      <FileSpreadsheet className="h-6 w-6" />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-strong truncate max-w-xs">{file.name}</h4>
                      <p className="text-xs text-faint">{(file.size / 1024).toFixed(1)} KB</p>
                    </div>
                  </div>

                  {!uploading && (
                    <button
                      onClick={clearFile}
                      className="p-2 rounded-lg hover:bg-red-500/10 text-faint hover:text-red-400 border border-transparent hover:border-red-500/20 transition-colors"
                      aria-label="Remove file"
                    >
                      <Trash2 className="h-4.5 w-4.5" />
                    </button>
                  )}
                </div>

                {/* Progress bar */}
                {uploading && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs font-semibold">
                      <span className="text-muted">Transmitting packets...</span>
                      <span className="text-blue-400">{progress}%</span>
                    </div>
                    <div className="h-2 w-full bg-surface-deep rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-blue-500 to-cyan-400 rounded-full transition-all duration-150" style={{ width: `${progress}%` }} />
                    </div>
                  </div>
                )}

                {/* Action button */}
                {!uploading && !response && (
                  <button
                    onClick={triggerUpload}
                    className="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs shadow-md shadow-blue-500/10 cursor-pointer flex items-center justify-center gap-1.5"
                  >
                    <ListRestart className="h-4 w-4" />
                    <span>Upload and Validate Schema</span>
                  </button>
                )}
              </div>
            )}

            {/* Error notifications */}
            {error && (
              <div className="mt-4 p-4 rounded-xl border border-red-500/20 bg-red-500/5 flex gap-3 text-xs leading-relaxed text-red-400">
                <AlertTriangle className="h-4.5 w-4.5 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-bold mb-1 uppercase tracking-wide">Validation Error</h4>
                  <p>{error}</p>
                </div>
              </div>
            )}
          </div>

          {/* Success Validation Table Response */}
          <AnimatePresence>
            {response && response.success && (
              <motion.div
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 15 }}
                className="glass-card p-6 rounded-2xl space-y-6"
              >
                <div className="flex items-center gap-2 text-emerald-400">
                  <CheckCircle2 className="h-5 w-5" />
                  <h3 className="text-base font-bold font-outfit text-foreground">Validation Success</h3>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 rounded-xl bg-surface-deep/40 border border-edge">
                  <div>
                    <span className="text-[10px] text-faint font-semibold uppercase tracking-wider block">Rows Decoded</span>
                    <span className="text-base font-bold text-strong">{response.rowCount.toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-faint font-semibold uppercase tracking-wider block">Columns Detected</span>
                    <span className="text-base font-bold text-strong">{response.columnsDetected.length}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-faint font-semibold uppercase tracking-wider block">Errors Blocked</span>
                    <span className="text-base font-bold text-emerald-400">0</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-faint font-semibold uppercase tracking-wider block">Sync Status</span>
                    <span className="text-base font-bold text-blue-400">Pending Merge</span>
                  </div>
                </div>

                {/* Detected columns previews */}
                <div>
                  <h4 className="text-xs font-bold text-muted mb-2 uppercase tracking-wide">Headers Detected</h4>
                  <div className="flex flex-wrap gap-1.5">
                    {response.columnsDetected.map((col, idx) => (
                      <span key={idx} className="px-2.5 py-1 text-xs rounded-lg border border-edge bg-surface/60 text-strong font-mono">
                        {col}
                      </span>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}

            {/* Failed validation list */}
            {response && !response.success && response.validationErrors.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 15 }}
                className="glass-card p-6 rounded-2xl space-y-4"
              >
                <div className="flex items-center gap-2 text-red-400">
                  <AlertTriangle className="h-5 w-5" />
                  <h3 className="text-base font-bold font-outfit text-foreground">Validation Summary</h3>
                </div>

                <ul className="space-y-2 max-h-48 overflow-y-auto pr-2">
                  {response.validationErrors.map((err, idx) => (
                    <li key={idx} className="p-2.5 rounded-lg border border-red-500/10 bg-red-500/5 text-xs text-red-400 leading-normal flex gap-2">
                      <span className="font-bold">{idx + 1}.</span>
                      <span>{err}</span>
                    </li>
                  ))}
                </ul>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Upload History side ledger */}
        <div className="glass-card p-6 rounded-2xl space-y-6">
          <div className="flex items-center gap-2 border-b border-edge/80 pb-4">
            <History className="h-4.5 w-4.5 text-muted" />
            <h3 className="text-sm font-bold font-outfit text-foreground uppercase tracking-wider">Ingestion Log</h3>
          </div>

          <div className="space-y-4 max-h-[350px] overflow-y-auto pr-1">
            {uploadHistory.map((hist) => (
              <div key={hist.fileId} className="p-3 rounded-lg border border-edge/80 bg-surface/30 text-xs space-y-2">
                <div className="flex justify-between items-start gap-2">
                  <span className="font-bold text-strong truncate max-w-[150px]">{hist.fileName}</span>
                  <span className="text-[10px] text-faint whitespace-nowrap">
                    {new Date(hist.uploadedAt).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  </span>
                </div>
                <div className="flex justify-between text-muted">
                  <span>{hist.rowCount} records</span>
                  <span className="text-emerald-400 font-medium">Synced</span>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
