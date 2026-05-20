import React from 'react';
import { Link } from 'react-router-dom';
import { format } from 'date-fns';

const PostCard = ({ post, featured = false }) => {
  return (
    <article className={`bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition ${featured ? 'border-l-4 border-purple-500' : ''}`}>
      {post.featured_image && (
        <Link to={`/post/${post.slug}`}>
          <img 
            src={post.featured_image} 
            alt={post.title} 
            className="w-full h-48 object-cover hover:opacity-90 transition"
          />
        </Link>
      )}
      
      <div className="p-5">
        {/* Category Badge */}
        {post.category && (
          <Link 
            to={`/category/${post.category_slug}`}
            className="inline-block px-2 py-1 bg-purple-100 text-purple-600 text-xs rounded-full mb-3 hover:bg-purple-200 transition"
          >
            {post.category_name}
          </Link>
        )}
        
        {/* Title */}
        <Link to={`/post/${post.slug}`}>
          <h3 className={`font-bold hover:text-purple-600 transition line-clamp-2 ${featured ? 'text-2xl' : 'text-xl'}`}>
            {post.title}
          </h3>
        </Link>
        
        {/* Meta Info */}
        <div className="flex items-center space-x-3 text-sm text-gray-500 mt-2">
          <span>By {post.author_name}</span>
          <span>•</span>
          <span>{format(new Date(post.published_at), 'MMM dd, yyyy')}</span>
          <span>•</span>
          <span className="flex items-center">
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            {post.views}
          </span>
          <span>•</span>
          <span className="flex items-center">
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
            {post.likes}
          </span>
        </div>
        
        {/* Tags */}
        {post.tags_list && post.tags_list.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-3">
            {post.tags_list.slice(0, 3).map(tag => (
              <Link 
                key={tag.id}
                to={`/tag/${tag.slug}`}
                className="text-xs text-gray-500 hover:text-purple-600"
              >
                #{tag.name}
              </Link>
            ))}
          </div>
        )}
        
        {/* Excerpt */}
        <p className="text-gray-600 mt-3 line-clamp-3">
          {post.excerpt}
        </p>
        
        {/* Read More Button */}
        <Link 
          to={`/post/${post.slug}`}
          className="inline-block mt-4 text-purple-600 font-medium hover:text-purple-700 transition"
        >
          Read More →
        </Link>
      </div>
    </article>
  );
};

export default PostCard;