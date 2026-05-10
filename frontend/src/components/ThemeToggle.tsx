import React from 'react';
import { useMintabStore } from '../store';

export const ThemeToggle: React.FC = () => {
  const [dark, setDark] = React.useState<boolean>(false);

  React.useEffect(() => {
    const root = document.documentElement;
    if (dark) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [dark]);

  return (
    <button
      className="btn btn-ghost btn-sm"
      onClick={() => setDark(!dark)}
    >
      {dark ? '🌙 Dark' : '☀️ Light'}
    </button>
  );
};
