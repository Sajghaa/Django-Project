import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { getPost, likePost, incrementView, addComment, getPostComments, deletePost } from '../services/api';
import { format } from 'date-fns';
import ReactMarkdown from 'react-markdown';
import LoadingSpinner from '../components/LoadingSpinner';
import { toast } from 'react-toastify';

const PostDetailPage = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [commentContent, setCommentContent] = useState('');
  const [isLiked, setIsLiked] = useState(false);
  const [likesCount, setLikesCount] = useState(0);

  useEffect(() => {
    fetchPost();
    incrementViewCount();
  }, [slug]);

  const fetchPost = async () => {
    setLoading(true);
    try {
      const response = await getPost(slug);
      setPost(response.data);
      setIsLiked(response.data.is_liked);
      setLikesCount(response.data.likes);
      await fetchComments();
    } catch (error) {
      console.error('Error fetching post:', error);
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  const fetchComments = async () => {
    try {
      const response = await getPostComments(slug);
      setComments(response.data);
    } catch (error) {
      console.error('Error fetching comments:', error);
    }
  };

  const incrementViewCount = async () => {
    try {
      await incrementView(slug);
    } catch (error) {
      console.error('Error incrementing view:', error);
    }
  };

  const handleLike = async () => {
    if (!isAuthenticated) {
      toast.info('Please login to like posts');
      return;
    }
    try {
      const response = await likePost(slug);
      setIsLiked(response.data.liked);
      setLikesCount(response.data.likes_count);
    } catch (error) {
      console.error('Error liking post:', error);
    }
  };

  const handleCommentSubmit = async (e) => {
    e.preventDefault();
    if (!isAuthenticated) {
      toast.info('Please login to comment');
      return;
    }
    if (!commentContent.trim()) return;
    
    try {
      await addComment(slug, { content: commentContent });
      setCommentContent('');
      await fetchComments();
      toast.success('Comment added!');
    } catch (error) {
      console.error('Error adding comment:', error);
    }
  };

  const handleDeletePost = async () => {
    if (window.confirm('Are you sure you want to delete this post?')) {
      try {
        await deletePost(slug);
        toast.success('Post deleted successfully!');
        navigate('/');
      } catch (error) {
        console.error('Error deleting post:', error);
      }
    }
  };

  if (loading) return <LoadingSpinner />;
  if (!post) return null;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        {/* Post Header */}
        <div className="mb-8">
          {/* Category */}
          {post.category && (
            <Link 
              to={`/category/${post.category_detail?.slug}`}
              className="inline-block px-3 py-1 bg-purple-100 text-purple-600 rounded-full text-sm mb-4 hover:bg-purple-200 transition"
            >
              {post.category_detail?.name}
            </Link>
          )}
          
          {/* Title */}
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            {post.title}
          </h1>
          
          {/* Meta Info */}
          <div className="flex flex-wrap items-center gap-4 text-gray-500 mb-6">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
                {post.author_name?.charAt(0).toUpperCase()}
              </div>
              <span className="font-medium text-gray-700">{post.author_name}</span>
            </div>
            <span>•</span>
            <span>{format(new Date(post.published_at), 'MMMM dd, yyyy')}</span>
            <span>•</span>
            <span>{post.reading_time} min read</span>
            <span>•</span>
            <div className="flex items-center space-x-1">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              <span>{post.views}</span>
            </div>
          </div>
          
          {/* Tags */}
          {post.tags_detail && post.tags_detail.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-6">
              {post.tags_detail.map(tag => (
                <Link key={tag.id} to={`/tag/${tag.slug}`} className="text-sm text-gray-500 hover:text-purple-600">
                  #{tag.name}
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Featured Image */}
        {post.featured_image && (
          <div className="mb-8">
            <img src={post.featured_image} alt={post.title} className="w-full rounded-lg shadow-lg" />
          </div>
        )}

        {/* Post Content */}
        <div className="prose prose-lg max-w-none mb-8">
          <ReactMarkdown>{post.content}</ReactMarkdown>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-between border-t border-b py-4 mb-8">
          <button
            onClick={handleLike}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition ${
              isLiked ? 'bg-red-50 text-red-600' : 'bg-gray-100 text-gray-700 hover:bg-red-50 hover:text-red-600'
            }`}
          >
            <svg className="w-5 h-5" fill={isLiked ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
            <span>{likesCount} Likes</span>
          </button>
          
          {user?.is_staff && (
            <div className="flex space-x-3">
              <button
                onClick={() => navigate(`/edit-post/${slug}`)}
                className="px-4 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 transition"
              >
                Edit Post
              </button>
              <button
                onClick={handleDeletePost}
                className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition"
              >
                Delete Post
              </button>
            </div>
          )}
        </div>

        {/* Comments Section */}
        <div>
          <h3 className="text-2xl font-bold mb-6">Comments ({comments.length})</h3>
          
          {/* Comment Form */}
          {isAuthenticated ? (
            <form onSubmit={handleCommentSubmit} className="mb-8">
              <textarea
                value={commentContent}
                onChange={(e) => setCommentContent(e.target.value)}
                placeholder="Write a comment..."
                rows="4"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500"
                required
              />
              <button
                type="submit"
                className="mt-3 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
              >
                Post Comment
              </button>
            </form>
          ) : (
            <div className="bg-gray-100 rounded-lg p-4 text-center mb-8">
              <p className="text-gray-600">
                <Link to="/login" className="text-purple-600 hover:underline">Login</Link> to leave a comment
              </p>
            </div>
          )}
          
          {/* Comments List */}
          <div className="space-y-6">
            {comments.map(comment => (
              <div key={comment.id} className="border-b pb-4">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center text-sm font-bold">
                    {comment.author_name?.charAt(0).toUpperCase()}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="font-semibold text-gray-900">{comment.author_name}</span>
                      <span className="text-xs text-gray-500">{format(new Date(comment.created_at), 'MMM dd, yyyy')}</span>
                    </div>
                    <p className="text-gray-700">{comment.content}</p>
                  </div>
                </div>
              </div>
            ))}
            
            {comments.length === 0 && (
              <p className="text-gray-500 text-center py-8">No comments yet. Be the first to comment!</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PostDetailPage;