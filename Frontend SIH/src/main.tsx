import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Suppress noisy third-party browser extension and PerformanceObserver errors
window.addEventListener('error', (event) => {
  const msg = String(event.message || '');
  const file = String(event.filename || '');
  if (
    msg.includes('startTime') ||
    msg.includes('message channel closed') ||
    msg.includes('asynchronous response') ||
    file.includes('chrome-extension://') ||
    file.includes('moz-extension://') ||
    !file
  ) {
    event.stopImmediatePropagation();
    event.preventDefault();
  }
}, true);

window.addEventListener('unhandledrejection', (event) => {
  const msg = String(event.reason?.message || event.reason || '');
  if (
    msg.includes('startTime') ||
    msg.includes('message channel closed') ||
    msg.includes('asynchronous response') ||
    msg.includes('chrome-extension://')
  ) {
    event.stopImmediatePropagation();
    event.preventDefault();
  }
}, true);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
