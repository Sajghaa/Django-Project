import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getPost, updatePost, getCategories, getTags } from '../services/api';
import { toast } from 'react-toastify';
import ReactMarkdown from 'react-markdown';
import LoadingSpinner from '../components/LoadingSpinner';

const EditPostPage = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [previewMode, setPreviewMode] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    category: '',
    content: '',
    excerpt: '',
    featured_image: null,
    status: 'draft',
    tags_input: '',
  });
  const [categories, setCategories] = useState([]);
  const [tags, setTags] = useState([]);

  useEffect(() => {
    fetchPost();
    fetchCategoriesAndTags();
  }, [slug]);

  const fetchPost = async () => {
    try {
      const response = await getPost(slug);
      const post = response.data;
      setFormData({
        title: post.title,
        category: post.category || '',
        content: post.content,
        excerpt: post.excerpt || '',
        status: post.status,
        tags_input: post.tags_detail?.map(t => t.name).join(', ') || '',
        featured_image: null,
      });
    } catch (error) {
      console.error('Error fetching post:', error);
      toast.error('Post not found');
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const fetchCategoriesAndTags = async () => {
    try {
      const [categoriesRes, tagsRes] = await Promise.all([
        getCategories(),
        getTags()
      ]);
      setCategories(categoriesRes.data.results || []);
      setTags(tagsRes.data.results || []);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    if (name === 'featured_image') {
      setFormData({ ...formData, [name]: files[0] });
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    
    const data = new FormData();
    data.append('title', formData.title);
    data.append('category', formData.category);
    data.append('content', formData.content);
    data.append('excerpt', formData.excerpt);
    data.append('status', formData.status);
    data.append('tags_input', formData.tags_input);
    if (formData.featured_image) {
      data.append('featured_image', formData.featured_image);
    }

    try {
      await updatePost(slug, data);
      toast.success('Post updated successfully!');
      navigate(`/post/${slug}`);
    } catch (error) {
      console.error('Error updating post:', error);
      toast.error('Error updating post');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Edit Post</h1>
        
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="border-b border-gray-200">
            <div className="flex">
              <button
                onClick={() => setPreviewMode(false)}
                className={`px-6 py-3 text-sm font-medium ${!previewMode ? 'bg-purple-600 text-white' : 'text-gray-600 hover:text-gray-900'}`}
              >
                Write
              </button>
              <button
                onClick={() => setPreviewMode(true)}
                className={`px-6 py-3 text-sm font-medium ${previewMode ? 'bg-purple-600 text-white' : 'text-gray-600 hover:text-gray-900'}`}
              >
                Preview
              </button>
            </div>
          </div>
          
          <form onSubmit={handleSubmit} className="p-6">
            {!previewMode ? (
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
                  <input
                    type="text"
                    name="title"
                    value={formData.title}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500"
                    required
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                    <select
                      name="category"
                      value={formData.category}
                      onChange={handleChange}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500"
                    >
                      <option value="">Select Category</option>
                      {categories.map(cat => (
                        <option key={cat.id} value={cat.id}>{cat.name}</option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                    <select
                      name="status"
                      value={formData.status}
                      onChange={handleChange}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500"
                    >
                      <option value="draft">Draft</option>
                      <option value="published">Published</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Tags (comma separated)</label>
                  <input
                    type="text"
                    name="tags_input"
                    value={formData.tags_input}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500"
                    placeholder="python, django, react"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Update Featured Image</label>
                  <input
                    type="file"
                    name="featured_image"
                    onChange={handleChange}
                    accept="image/*"
                    className="w-full"
                  />
                  <p className="text-xs text-gray-500 mt-1">Leave empty to keep current image</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Excerpt</label>
                  <textarea
                    name="excerpt"
                    value={formData.excerpt}
                    onChange={handleChange}
                    rows="3"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Content *</label>
                  <textarea
                    name="content"
                    value={formData.content}
                    onChange={handleChange}
                    rows="15"
                    className="w-full px-4 py-2 font-mono text-sm border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500"
                    required
                  />
                </div>
              </div>
            ) : (
              <div className="prose prose-lg max-w-none">
                <ReactMarkdown>{formData.content || '*No content to preview*'}</ReactMarkdown>
              </div>
            )}
            
            <div className="flex justify-end space-x-3 mt-6 pt-6 border-t">
              <button
                type="button"
                onClick={() => navigate('/dashboard')}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="px-6 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition disabled:opacity-50"
              >
                {submitting ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default EditPostPage;