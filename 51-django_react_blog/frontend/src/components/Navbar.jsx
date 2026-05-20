import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { FiMenu, FiX, FiUser, FiLogOut, FiPlusCircle, FiGrid } from 'react-icons/fi';

const Navbar = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${searchQuery}`);
      setSearchQuery('');
      setIsOpen(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
    setIsOpen(false);
  };

  return (
    <nav className="bg-white shadow-lg sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">B</span>
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              ReactBlog
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-6">
            <Link to="/" className="text-gray-700 hover:text-purple-600 transition">Home</Link>
            
            {/* Search Bar */}
            <form onSubmit={handleSearch} className="flex">
              <input
                type="text"
                placeholder="Search posts..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="px-3 py-1 border border-gray-300 rounded-l-lg focus:outline-none focus:border-purple-500 w-64"
              />
              <button type="submit" className="px-3 py-1 bg-purple-600 text-white rounded-r-lg hover:bg-purple-700 transition">
                Search
              </button>
            </form>
            
            {isAuthenticated ? (
              <>
                {user?.is_staff && (
                  <Link to="/create-post" className="text-gray-700 hover:text-purple-600 transition">
                    <FiPlusCircle className="inline mr-1" /> Write
                  </Link>
                )}
                <Link to="/dashboard" className="text-gray-700 hover:text-purple-600 transition">
                  <FiGrid className="inline mr-1" /> Dashboard
                </Link>
                <div className="relative group">
                  <button className="flex items-center space-x-2 text-gray-700 hover:text-purple-600 transition">
                    <FiUser />
                    <span>{user?.username}</span>
                  </button>
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg hidden group-hover:block">
                    <Link to="/profile" className="block px-4 py-2 text-gray-700 hover:bg-gray-100">Profile</Link>
                    <button onClick={handleLogout} className="block w-full text-left px-4 py-2 text-red-600 hover:bg-gray-100">
                      <FiLogOut className="inline mr-2" /> Logout
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex space-x-4">
                <Link to="/login" className="text-gray-700 hover:text-purple-600 transition">Login</Link>
                <Link to="/register" className="px-4 py-1 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition">
                  Register
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <button onClick={() => setIsOpen(!isOpen)} className="md:hidden text-gray-700">
            {isOpen ? <FiX size={24} /> : <FiMenu size={24} />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <div className="md:hidden py-4 border-t">
            <form onSubmit={handleSearch} className="mb-4">
              <div className="flex">
                <input
                  type="text"
                  placeholder="Search posts..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-l-lg focus:outline-none focus:border-purple-500"
                />
                <button type="submit" className="px-4 py-2 bg-purple-600 text-white rounded-r-lg hover:bg-purple-700 transition">
                  Search
                </button>
              </div>
            </form>
            
            <Link to="/" className="block py-2 text-gray-700 hover:text-purple-600" onClick={() => setIsOpen(false)}>Home</Link>
            
            {isAuthenticated ? (
              <>
                {user?.is_staff && (
                  <Link to="/create-post" className="block py-2 text-gray-700 hover:text-purple-600" onClick={() => setIsOpen(false)}>
                    Write Post
                  </Link>
                )}
                <Link to="/dashboard" className="block py-2 text-gray-700 hover:text-purple-600" onClick={() => setIsOpen(false)}>
                  Dashboard
                </Link>
                <Link to="/profile" className="block py-2 text-gray-700 hover:text-purple-600" onClick={() => setIsOpen(false)}>
                  Profile
                </Link>
                <button onClick={handleLogout} className="block w-full text-left py-2 text-red-600 hover:text-red-700">
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="block py-2 text-gray-700 hover:text-purple-600" onClick={() => setIsOpen(false)}>Login</Link>
                <Link to="/register" className="block py-2 text-gray-700 hover:text-purple-600" onClick={() => setIsOpen(false)}>Register</Link>
              </>
            )}
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;