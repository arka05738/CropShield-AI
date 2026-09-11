import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Suppress noisy third-party browser extension and PerformanceObserver errors
window.addEventListener('error', (event) => {
  if (
    event.message?.includes('startTime') ||
    event.message?.includes('message channel closed') ||
    event.filename?.includes('chrome-extension://') ||
    !event.filename
  ) {
    if (event.message?.includes('startTime')) {
      event.stopImmediatePropagation();
      event.preventDefault();
    }
  }
});

window.addEventListener('unhandledrejection', (event) => {
  const msg = String(event.reason?.message || event.reason || '');
  if (msg.includes('message channel closed') || msg.includes('asynchronous response')) {
    event.stopImmediatePropagation();
    event.preventDefault();
  }
});

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
