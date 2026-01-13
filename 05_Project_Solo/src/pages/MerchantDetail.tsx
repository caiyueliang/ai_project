import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { MapPin, Clock, Phone, Star, User, Image as ImageIcon } from 'lucide-react';
import { supabase, Database } from '@/lib/supabase';
import { format } from 'date-fns';
import ReviewModal from '@/components/ReviewModal';

type Merchant = Database['public']['Tables']['merchants']['Row'];
type Review = Database['public']['Tables']['reviews']['Row'] & {
  users: {
    nickname: string | null;
    avatar_url: string | null;
  } | null;
};

export default function MerchantDetail() {
  const { id } = useParams<{ id: string }>();
  const [merchant, setMerchant] = useState<Merchant | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<any>(null);
  const [isReviewModalOpen, setIsReviewModalOpen] = useState(false);

  useEffect(() => {
    // Get current user
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
    });

    if (id) {
      fetchMerchantData(id);
    }
  }, [id]);

  const fetchMerchantData = async (merchantId: string) => {
    try {
      // Fetch merchant details
      const { data: merchantData, error: merchantError } = await supabase
        .from('merchants')
        .select('*')
        .eq('id', merchantId)
        .single();

      if (merchantError) throw merchantError;
      setMerchant(merchantData);

      // Fetch reviews with user profiles
      const { data: reviewsData, error: reviewsError } = await supabase
        .from('reviews')
        .select(`
          *,
          users (
            nickname,
            avatar_url
          )
        `)
        .eq('merchant_id', merchantId)
        .order('created_at', { ascending: false });

      if (reviewsError) throw reviewsError;
      setReviews(reviewsData as any);
    } catch (error) {
      console.error('Error fetching merchant details:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleReviewSuccess = () => {
    if (id) fetchMerchantData(id);
  };

  if (loading) {
    return (
      <div className="container-custom py-8 animate-pulse">
        <div className="h-64 bg-gray-200 rounded-lg mb-8"></div>
        <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="h-4 bg-gray-200 rounded w-1/2 mb-8"></div>
        <div className="space-y-4">
          <div className="h-24 bg-gray-200 rounded"></div>
          <div className="h-24 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (!merchant) {
    return <div className="container-custom py-8 text-center">未找到商家信息</div>;
  }

  return (
    <div>
      {/* Hero Header */}
      <div className="relative h-[300px] md:h-[400px]">
        <img 
          src={merchant.cover_image || 'https://images.unsplash.com/photo-1514933651103-005eec06c04b?w=1600&auto=format&fit=crop&q=80'} 
          alt={merchant.name}
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent"></div>
        <div className="absolute bottom-0 left-0 right-0 p-6 md:p-10 text-white container-custom">
          <h1 className="text-3xl md:text-4xl font-bold mb-2">{merchant.name}</h1>
          <div className="flex items-center space-x-4 mb-4">
            <div className="flex items-center">
              <div className="flex text-orange-400 mr-2">
                {[...Array(5)].map((_, i) => (
                  <Star 
                    key={i} 
                    className={`w-5 h-5 ${i < Math.floor(merchant.avg_rating) ? 'fill-current' : 'text-gray-400'}`} 
                  />
                ))}
              </div>
              <span className="text-lg font-medium">{merchant.avg_rating.toFixed(1)}分</span>
            </div>
            <span>{merchant.review_count}条评价</span>
            <span className="px-2 py-0.5 bg-white/20 rounded text-sm">{merchant.category}</span>
          </div>
        </div>
      </div>

      <div className="container-custom py-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Info & Reviews */}
        <div className="lg:col-span-2 space-y-8">
          {/* Info Card */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h2 className="text-xl font-bold mb-4">商家信息</h2>
            <div className="space-y-4 text-gray-600">
              <div className="flex items-start">
                <MapPin className="w-5 h-5 mt-0.5 mr-3 text-gray-400" />
                <span>{merchant.address}</span>
              </div>
              <div className="flex items-center">
                <Clock className="w-5 h-5 mr-3 text-gray-400" />
                <span>营业时间：{merchant.business_hours || '暂无信息'}</span>
              </div>
              <div className="flex items-center">
                <Phone className="w-5 h-5 mr-3 text-gray-400" />
                <span>联系电话：{merchant.phone || '暂无信息'}</span>
              </div>
              {merchant.description && (
                <div className="pt-4 border-t border-gray-100 mt-4">
                  <p>{merchant.description}</p>
                </div>
              )}
            </div>
          </div>

          {/* Reviews Section */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold">用户评价 ({merchant.review_count})</h2>
              {user ? (
                <button 
                  onClick={() => {/* Open review modal */}}
                  className="btn-primary"
                >
                  写评价
                </button>
              ) : (
                <Link to={`/login?redirect=/merchant/${merchant.id}`} className="text-orange-500 hover:underline">
                  登录后评价
                </Link>
              )}
            </div>

            <div className="space-y-6">
              {reviews.length > 0 ? (
                reviews.map((review) => (
                  <div key={review.id} className="border-b border-gray-100 pb-6 last:border-0 last:pb-0">
                    <div className="flex items-center mb-3">
                      <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center mr-3 overflow-hidden">
                        {review.users?.avatar_url ? (
                          <img src={review.users.avatar_url} alt="avatar" className="w-full h-full object-cover" />
                        ) : (
                          <User className="w-5 h-5 text-gray-400" />
                        )}
                      </div>
                      <div>
                        <div className="font-medium text-gray-900">
                          {review.users?.nickname || '匿名用户'}
                        </div>
                        <div className="flex items-center text-xs text-gray-500">
                          <div className="flex text-orange-400 mr-2">
                            {[...Array(5)].map((_, i) => (
                              <Star 
                                key={i} 
                                className={`w-3 h-3 ${i < Math.floor(review.rating) ? 'fill-current' : 'text-gray-300'}`} 
                              />
                            ))}
                          </div>
                          <span>{format(new Date(review.created_at), 'yyyy-MM-dd HH:mm')}</span>
                        </div>
                      </div>
                    </div>
                    
                    <p className="text-gray-700 mb-3">{review.content}</p>
                    
                    {review.images && review.images.length > 0 && (
                      <div className="flex gap-2 overflow-x-auto pb-2">
                        {review.images.map((img, idx) => (
                          <img 
                            key={idx} 
                            src={img} 
                            alt="review" 
                            className="w-24 h-24 object-cover rounded-lg flex-shrink-0"
                          />
                        ))}
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  暂无评价，快来抢沙发吧！
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Sidebar (Map placeholder, etc) */}
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 className="font-bold mb-4">位置</h3>
            <div className="bg-gray-100 h-48 rounded-lg flex items-center justify-center text-gray-400">
              <div className="text-center">
                <MapPin className="w-8 h-8 mx-auto mb-2" />
                <span className="text-sm">地图组件占位</span>
              </div>
            </div>
            <p className="mt-3 text-sm text-gray-600">{merchant.address}</p>
          </div>
        </div>
      </div>

      <ReviewModal 
        isOpen={isReviewModalOpen} 
        onClose={() => setIsReviewModalOpen(false)} 
        merchantId={merchant.id}
        onSuccess={handleReviewSuccess}
      />
    </div>
  );
}
