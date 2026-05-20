import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getPostsByTag } from '../services/api';
import PostCard from '../components/PostCard';
import LoadingSpinner from '../components/LoadingSpinner';

const TagPage = () => {
  const { slug } = useParams();
  const [posts, setPosts] = useState([]);
  const [tagName, setTagName] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTagPosts();
  }, [slug]);

  const fetchTagPosts = async () => {
    setLoading(true);
    try {
      const response = await getPostsByTag(slug);
      setPosts(response.data || []);
      if (response.data && response.data.length > 0) {
        // Get tag name from first post's tags
        const firstPost = response.data[0];
        const tag = firstPost.tags_detail?.find(t => t.slug === slug);
        if (tag) setTagName(tag.name);
      }
    } catch (error) {
      console.error('Error fetching tag posts:', error);
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
            #{tagName || slug}
          </h1>
          <p className="text-gray-600">
            {posts.length} post{posts.length !== 1 ? 's' : ''} tagged with "{tagName || slug}"
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
            <p className="text-gray-500">No posts found with this tag.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default TagPage;