import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {
  return (
    <footer className="bg-gray-800 text-white mt-12">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* About */}
          <div>
            <h3 className="text-lg font-bold mb-3">About ReactBlog</h3>
            <p className="text-gray-400 text-sm">
              A modern blog platform built with Django REST API and React. Share your stories and connect with readers.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-lg font-bold mb-3">Quick Links</h3>
            <ul className="space-y-2 text-sm">
              <li><Link to="/" className="text-gray-400 hover:text-white transition">Home</Link></li>
              <li><Link to="/dashboard" className="text-gray-400 hover:text-white transition">Dashboard</Link></li>
              <li><Link to="/create-post" className="text-gray-400 hover:text-white transition">Write a Post</Link></li>
            </ul>
          </div>

          {/* Categories */}
          <div>
            <h3 className="text-lg font-bold mb-3">Categories</h3>
            <ul className="space-y-2 text-sm">
              <li><Link to="/category/technology" className="text-gray-400 hover:text-white transition">Technology</Link></li>
              <li><Link to="/category/programming" className="text-gray-400 hover:text-white transition">Programming</Link></li>
              <li><Link to="/category/lifestyle" className="text-gray-400 hover:text-white transition">Lifestyle</Link></li>
            </ul>
          </div>

          {/* Connect */}
          <div>
            <h3 className="text-lg font-bold mb-3">Connect</h3>
            <div className="flex space-x-4">
              <a href="#" className="text-gray-400 hover:text-white transition">
                <i className="fab fa-twitter text-xl"></i>
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition">
                <i className="fab fa-github text-xl"></i>
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition">
                <i className="fab fa-linkedin text-xl"></i>
              </a>
            </div>
            <p className="text-gray-400 text-sm mt-4">
              contact@reactblog.com
            </p>
          </div>
        </div>
        
        <div className="border-t border-gray-700 mt-8 pt-6 text-center text-gray-400 text-sm">
          &copy; {new Date().getFullYear()} ReactBlog. All rights reserved.
        </div>
      </div>
    </footer>
  );
};

export default Footer;