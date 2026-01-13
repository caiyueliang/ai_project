import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { User, Mail, Camera, Save, Loader2, Star, Calendar } from 'lucide-react';
import { supabase, Database } from '@/lib/supabase';
import toast from 'react-hot-toast';
import { format } from 'date-fns';

type Profile = Database['public']['Tables']['users']['Row'];
type ReviewWithMerchant = Database['public']['Tables']['reviews']['Row'] & {
  merchants: {
    id: number;
    name: string;
    cover_image: string | null;
  } | null;
};

export default function Profile() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [reviews, setReviews] = useState<ReviewWithMerchant[]>([]);
  const navigate = useNavigate();

  // Form states
  const [nickname, setNickname] = useState('');
  const [avatarUrl, setAvatarUrl] = useState('');

  useEffect(() => {
    getProfile();
  }, []);

  const getProfile = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();

      if (!user) {
        navigate('/login');
        return;
      }

      // Fetch profile
      let { data: profileData, error: profileError } = await supabase
        .from('users')
        .select('*')
        .eq('id', user.id)
        .single();

      if (profileError && profileError.code === 'PGRST116') {
        // Profile might not exist if trigger failed or pre-existing user
        // Create one if missing? Or just handle gracefully.
        // For now, assume trigger worked or handle null
      }

      if (profileData) {
        setProfile(profileData);
        setNickname(profileData.nickname || '');
        setAvatarUrl(profileData.avatar_url || '');
      } else {
        // Fallback if no profile record found (should happen rarely with trigger)
        setNickname(user.email?.split('@')[0] || '');
      }

      // Fetch user reviews
      const { data: reviewsData, error: reviewsError } = await supabase
        .from('reviews')
        .select(`
          *,
          merchants (
            id,
            name,
            cover_image
          )
        `)
        .eq('user_id', user.id)
        .order('created_at', { ascending: false });

      if (reviewsError) throw reviewsError;
      setReviews(reviewsData as any);

    } catch (error) {
      console.error('Error loading profile:', error);
      toast.error('加载个人信息失败');
    } finally {
      setLoading(false);
    }
  };

  const updateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error('No user');

      const updates = {
        id: user.id,
        nickname,
        avatar_url: avatarUrl,
        updated_at: new Date().toISOString(),
      };

      const { error } = await supabase
        .from('users')
        .upsert(updates);

      if (error) throw error;
      toast.success('个人信息已更新');
    } catch (error) {
      console.error('Error updating profile:', error);
      toast.error('更新失败');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[50vh]">
        <Loader2 className="w-8 h-8 animate-spin text-orange-500" />
      </div>
    );
  }

  return (
    <div className="container-custom py-8">
      <h1 className="text-2xl font-bold mb-8">个人中心</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Profile Sidebar */}
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h2 className="text-lg font-bold mb-6">基本信息</h2>
            
            <div className="flex flex-col items-center mb-6">
              <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center overflow-hidden mb-4 border-4 border-white shadow-md">
                {avatarUrl ? (
                  <img src={avatarUrl} alt="avatar" className="w-full h-full object-cover" />
                ) : (
                  <User className="w-10 h-10 text-gray-400" />
                )}
              </div>
              <div className="text-sm text-gray-500">{profile?.email}</div>
            </div>

            <form onSubmit={updateProfile} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">昵称</label>
                <input
                  type="text"
                  value={nickname}
                  onChange={(e) => setNickname(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-orange-500 focus:border-orange-500"
                  placeholder="设置昵称"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">头像链接</label>
                <input
                  type="text"
                  value={avatarUrl}
                  onChange={(e) => setAvatarUrl(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-orange-500 focus:border-orange-500"
                  placeholder="https://example.com/avatar.jpg"
                />
                <p className="text-xs text-gray-500 mt-1">支持外部图片链接</p>
              </div>

              <button
                type="submit"
                disabled={saving}
                className="w-full flex items-center justify-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-orange-500 hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 disabled:opacity-70"
              >
                {saving ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    保存中...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    保存修改
                  </>
                )}
              </button>
            </form>
          </div>
        </div>

        {/* Reviews List */}
        <div className="md:col-span-2">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 min-h-[500px]">
            <h2 className="text-lg font-bold mb-6 flex items-center">
              <Star className="w-5 h-5 mr-2 text-orange-500" />
              我的评价 ({reviews.length})
            </h2>

            <div className="space-y-6">
              {reviews.length > 0 ? (
                reviews.map((review) => (
                  <div key={review.id} className="border-b border-gray-100 pb-6 last:border-0 last:pb-0">
                    <div className="flex justify-between items-start mb-2">
                      <Link 
                        to={`/merchant/${review.merchant_id}`}
                        className="font-medium text-lg text-gray-900 hover:text-orange-500 transition-colors"
                      >
                        {review.merchants?.name || '未知商家'}
                      </Link>
                      <div className="text-xs text-gray-500 flex items-center">
                        <Calendar className="w-3 h-3 mr-1" />
                        {format(new Date(review.created_at), 'yyyy-MM-dd')}
                      </div>
                    </div>

                    <div className="flex items-center mb-3">
                      <div className="flex text-orange-400 mr-2">
                        {[...Array(5)].map((_, i) => (
                          <Star 
                            key={i} 
                            className={`w-4 h-4 ${i < Math.floor(review.rating) ? 'fill-current' : 'text-gray-300'}`} 
                          />
                        ))}
                      </div>
                    </div>

                    <p className="text-gray-600 mb-3 bg-gray-50 p-3 rounded-lg">
                      {review.content}
                    </p>

                    {review.images && review.images.length > 0 && (
                      <div className="flex gap-2">
                        {review.images.map((img, idx) => (
                          <img 
                            key={idx} 
                            src={img} 
                            alt="review" 
                            className="w-16 h-16 object-cover rounded-lg"
                          />
                        ))}
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Star className="w-8 h-8 text-gray-300" />
                  </div>
                  <p>您还没有发表过评价</p>
                  <Link to="/" className="text-orange-500 hover:underline mt-2 inline-block">
                    去发现好店
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
