'use client';

import { useState } from 'react';
import styles from './page.module.css';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [response, setResponse] = useState<any>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isPolling, setIsPolling] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const pollStatus = async (id: string) => {
    setIsPolling(true);

    const check = async () => {
      try{
        const res = await fetch(`http://localhost:3000/audio/status/${id}`);
        const data = await res.json()

        setResponse(data);

        if (data.status === 'completed') {
          setIsPolling(false);
        } else {
          setTimeout(check, 2000);
        }
      }
      catch (error) {
        console.error('Polling failed:', error);
        setIsPolling(false);
      }
    };
    check();
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setIsUploading(true);
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://localhost:3000/audio/verify', {
        method: 'POST',
        body: formData,
      });
      
      const data = await res.json();
      setResponse(data);

      if (data.trackingId){
        console.log(data.trackingId)
        pollStatus(data.trackingId)
      }

    } catch (error) {
      console.error('Upload failed:', error);
      setResponse({ error: 'Failed to connect to the API' });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <main className={styles.main}>
      <div className={styles.card}>
        <h1 className={styles.title}>
          Who changed my mix?
        </h1>
        
        <form onSubmit={handleUpload} className={styles.form}>
          <input
            type="file"
            accept="audio/*"
            onChange={handleFileChange}
            className={styles.fileInput}
            disabled={isUploading || isPolling}
          />
          
          <button
            type="submit"
            disabled={!file || isUploading || isPolling}
            className={styles.submitBtn}
          >
            {/* 4. Dynamic button text based on what phase we are in */}
            {isUploading ? 'Uploading to Server...' : 
             isPolling ? 'AI is Analyzing...' : 
             'Verify Audio'}
          </button>
        </form>

        {response && (
          <div className={styles.responseBox}>
            <h3 className={styles.responseTitle}>System Status:</h3>
            <pre className={styles.responsePre}>
              {JSON.stringify(response, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </main>
  );
}