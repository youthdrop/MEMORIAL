import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'

// ✅ Import Tailwind stylesheet so it’s included in the Vite build
import './index.css'

createRoot(document.getElementById('root')).render(<App />)
