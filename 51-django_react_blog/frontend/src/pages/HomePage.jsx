import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getPosts, getFeaturedPosts, getPopularPosts, getTrendingPosts, getCategories } from '../services/api';
import PostCard from '../components/PostCard';
import LoadingSpinner from '../components/LoadingSpinner';

const HomePage = () => {
  const [posts, setPosts] = useState([]);
  const [featuredPosts, setFeaturedPosts] = useState([]);
  const [popularPosts, setPopularPosts] = useState([]);
  const [trendingPosts, setTrendingPosts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    fetchAllData();
  }, [currentPage]);

  const fetchAllData = async () => {
    setLoading(true);
    try {
      const [postsRes, featuredRes, popularRes, trendingRes, categoriesRes] = await Promise.all([
        getPosts({ page: currentPage }),
        getFeaturedPosts(),
        getPopularPosts(),
        getTrendingPosts(),
        getCategories()
      ]);
      
      setPosts(postsRes.data.results || []);
      setTotalPages(postsRes.data.total_pages || 1);
      setFeaturedPosts(featuredRes.data || []);
      setPopularPosts(popularRes.data || []);
      setTrendingPosts(trendingRes.data || []);
      setCategories(categoriesRes.data.results || []);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-4">
          Welcome to ReactBlog
        </h1>
        <p className="text-gray-600 text-lg max-w-2xl mx-auto">
          Discover amazing stories, tutorials, and insights from our talented authors
        </p>
      </div>

      {/* Featured Posts Carousel */}
      {featuredPosts.length > 0 && (
        <div className="mb-12">
          <h2 className="text-2xl font-bold mb-6 flex items-center">
            <span className="bg-gradient-to-r from-purple-600 to-pink-600 w-1 h-8 rounded-full mr-3"></span>
            Featured Posts
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {featuredPosts.map(post => (
              <PostCard key={post.id} post={post} featured />
            ))}
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Posts Feed */}
        <div className="lg:col-span-2">
          <h2 className="text-2xl font-bold mb-6">Latest Posts</h2>
          <div className="space-y-6">
            {posts.map(post => (
              <PostCard key={post.id} post={post} />
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center mt-8 space-x-2">
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="px-3 py-1 border rounded-lg disabled:opacity-50 hover:bg-gray-50"
              >
                Previous
              </button>
              <span className="px-3 py-1 text-gray-600">
                Page {currentPage} of {totalPages}
              </span>
              <button
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="px-3 py-1 border rounded-lg disabled:opacity-50 hover:bg-gray-50"
              >
                Next
              </button>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Popular Posts */}
          {popularPosts.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-bold mb-4">🔥 Most Viewed</h3>
              <div className="space-y-3">
                {popularPosts.map(post => (
                  <Link key={post.id} to={`/post/${post.slug}`} className="block group">
                    <div className="flex items-start space-x-3">
                      {post.featured_image && (
                        <img src={post.featured_image} alt={post.title} className="w-12 h-12 rounded object-cover" />
                      )}
                      <div>
                        <h4 className="font-medium group-hover:text-purple-600 transition line-clamp-2">
                          {post.title}
                        </h4>
                        <p className="text-xs text-gray-500">{post.author_name}</p>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )}

          {/* Trending Posts */}
          {trendingPosts.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-bold mb-4">📈 Trending</h3>
              <div className="space-y-3">
                {trendingPosts.map(post => (
                  <Link key={post.id} to={`/post/${post.slug}`} className="block group">
                    <div className="flex justify-between items-center">
                      <span className="group-hover:text-purple-600 transition">{post.title}</span>
                      <span className="text-sm text-gray-500">❤️ {post.likes}</span>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )}

          {/* Categories */}
          {categories.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-bold mb-4">📁 Categories</h3>
              <div className="flex flex-wrap gap-2">
                {categories.map(cat => (
                  <Link
                    key={cat.id}
                    to={`/category/${cat.slug}`}
                    className="px-3 py-1 bg-gray-100 rounded-full text-sm hover:bg-purple-600 hover:text-white transition"
                  >
                    {cat.name} ({cat.post_count})
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default HomePage;