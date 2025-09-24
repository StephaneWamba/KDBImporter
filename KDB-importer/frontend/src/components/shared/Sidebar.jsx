import { NavLink } from 'react-router-dom';

export default function Sidebar() {
  const baseLink =
    'block px-4 py-3 rounded transition font-medium text-gray-700';

  const activeLink = 'bg-blue-600 text-white';
  const hoverLink = 'hover:bg-blue-500 hover:text-white';

  const navItems = [
    { label: 'Import', path: '/' },
    { label: 'Dashboard', path: '/dashboard' },
    { label: 'History', path: '/history' },
    { label: 'Assistant', path: '/assistant' },
  ];

  return (
    <aside className="w-64 h-full bg-gray-100 border-r flex flex-col">
      <div className="p-4 text-xl font-bold border-b">arXiv Platform</div>
      <nav className="p-4 space-y-2">
        {navItems.map(({ label, path }) => (
          <NavLink
            key={path}
            to={path}
            end={path === '/'}
            className={({ isActive }) =>
              `${baseLink} ${hoverLink} ${isActive ? activeLink : ''}`
            }
          >
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
