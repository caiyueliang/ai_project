import React, { useState } from 'react';
import { X, Star, Image as ImageIcon } from 'lucide-react';
import { supabase } from '@/lib/supabase';
import toast from 'react-hot-toast';

interface ReviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  merchantId: number;
  onSuccess: () => void;
}

export default function ReviewModal({ isOpen, onClose, merchantId, onSuccess }: ReviewModalProps) {
  const [rating, setRating] = useState(5);
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [hoverRating, setHoverRating] = useState(0);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) {
      toast.error('请输入评价内容');
      return;
    }

    setLoading(true);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error('请先登录');

      const { error } = await supabase.from('reviews').insert({
        merchant_id: merchantId,
        user_id: user.id,
        rating,
        content,
        images: [] // Placeholder for images
      });

      if (error) throw error;

      toast.success('评价发布成功');
      onSuccess();
      onClose();
    } catch (error: any) {
      console.error('Error submitting review:', error);
      toast.error(error.message || '发布失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg overflow-hidden animate-in fade-in zoom-in duration-200">
        <div className="flex justify-between items-center p-4 border-b border-gray-100">
          <h3 className="text-lg font-bold text-gray-900">写评价</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6">
          <div className="mb-6 text-center">
            <div className="text-sm text-gray-500 mb-2">点击星星评分</div>
            <div className="flex justify-center space-x-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  className="focus:outline-none transition-transform hover:scale-110"
                  onMouseEnter={() => setHoverRating(star)}
                  onMouseLeave={() => setHoverRating(0)}
                  onClick={() => setRating(star)}
                >
                  <Star
                    className={`w-8 h-8 ${
                      star <= (hoverRating || rating)
                        ? 'text-orange-400 fill-current'
                        : 'text-gray-200'
                    }`}
                  />
                </button>
              ))}
            </div>
            <div className="text-orange-500 font-medium mt-2">
              {hoverRating || rating} 分
            </div>
          </div>

          <div className="mb-6">
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="分享你的体验感受，帮助更多人发现好店..."
              className="w-full h-32 p-4 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent resize-none transition-shadow"
              required
            />
          </div>

          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg font-medium transition-colors"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-medium shadow-sm shadow-orange-200 transition-all disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {loading ? '发布中...' : '发布评价'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
