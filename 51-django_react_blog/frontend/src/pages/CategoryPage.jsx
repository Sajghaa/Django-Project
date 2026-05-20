import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getPostsByCategory } from '../services/api';
import PostCard from '../components/PostCard';
import LoadingSpinner from '../components/LoadingSpinner';

const CategoryPage = () => {
  const { slug } = useParams();
  const [posts, setPosts] = useState([]);
  const [categoryName, setCategoryName] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCategoryPosts();
  }, [slug]);

  const fetchCategoryPosts = async () => {
    setLoading(true);
    try {
      const response = await getPostsByCategory(slug);
      setPosts(response.data || []);
      if (response.data && response.data.length > 0) {
        setCategoryName(response.data[0].category_name);
      }
    } catch (error) {
      console.error('Error fetching category posts:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Category: {categoryName || slug}
          </h1>
          <p className="text-gray-600">
            {posts.length} post{posts.length !== 1 ? 's' : ''} found
          </p>
        </div>

        {posts.length > 0 ? (
          <div className="space-y-6">
            {posts.map(post => (
              <PostCard key={post.id} post={post} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500">No posts found in this category.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default CategoryPage;