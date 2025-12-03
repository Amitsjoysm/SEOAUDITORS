import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from '@/api/axios';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchActiveTheme();
  }, []);

  const fetchActiveTheme = async () => {
    try {
      const response = await axios.get('/themes/active');
      setTheme(response.data);
      applyTheme(response.data);
    } catch (error) {
      console.error('Failed to fetch theme:', error);
      // Use default Apollo.io light theme
      const defaultTheme = {
        primary_color: '#6366f1',
        secondary_color: '#8b5cf6',
        accent_color: '#06b6d4',
        background_color: '#f9fafb',
        surface_color: '#ffffff',
        text_primary: '#111827',
        text_secondary: '#6b7280',
        border_radius: '0.75rem',
        font_family: 'Inter, system-ui, sans-serif'
      };
      setTheme(defaultTheme);
      applyTheme(defaultTheme);
    } finally {
      setLoading(false);
    }
  };

  const applyTheme = (themeData) => {
    if (!themeData) return;

    const root = document.documentElement;
    root.style.setProperty('--color-primary', themeData.primary_color);
    root.style.setProperty('--color-secondary', themeData.secondary_color);
    root.style.setProperty('--color-accent', themeData.accent_color);
    root.style.setProperty('--color-background', themeData.background_color);
    root.style.setProperty('--color-surface', themeData.surface_color);
    root.style.setProperty('--color-text-primary', themeData.text_primary);
    root.style.setProperty('--color-text-secondary', themeData.text_secondary);
    root.style.setProperty('--border-radius', themeData.border_radius);
    root.style.setProperty('--font-family', themeData.font_family);

    // Detect if it's a light theme based on background color
    const isLight = themeData.background_color && 
      (themeData.background_color.toLowerCase() === '#ffffff' || 
       themeData.background_color.toLowerCase() === '#fff' ||
       themeData.background_color.toLowerCase().startsWith('#f'));
    
    // Add data attribute for CSS to detect theme type
    root.setAttribute('data-theme', isLight ? 'light' : 'dark');
    
    // IMPORTANT: Don't apply body background on admin/integrations routes
    const isAdminRoute = window.location.pathname.startsWith('/admin');
    
    if (!isAdminRoute) {
      // Only apply theme background on non-admin pages
      document.body.style.backgroundColor = themeData.background_color;
      document.body.style.color = themeData.text_primary;
    } else {
      // Force light background on admin pages
      document.body.style.backgroundColor = '#f9fafb';
      document.body.style.color = '#111827';
    }

    // Apply custom CSS if present
    if (themeData.custom_css) {
      let styleEl = document.getElementById('custom-theme-css');
      if (!styleEl) {
        styleEl = document.createElement('style');
        styleEl.id = 'custom-theme-css';
        document.head.appendChild(styleEl);
      }
      styleEl.textContent = themeData.custom_css;
    }
  };

  const refreshTheme = async () => {
    await fetchActiveTheme();
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: 'var(--color-background, #0f172a)' }}>
        <div style={{ color: 'var(--color-text-primary, #f8fafc)' }} className="text-xl">Loading theme...</div>
      </div>
    );
  }

  return (
    <ThemeContext.Provider value={{ theme, refreshTheme, applyTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
