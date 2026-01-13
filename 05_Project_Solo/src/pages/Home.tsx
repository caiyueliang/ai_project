import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Search, Utensils, Film, ShoppingBag, Coffee, Dumbbell, MoreHorizontal } from 'lucide-react';
import { supabase, Database } from '@/lib/supabase';
import MerchantCard from '@/components/MerchantCard';

type Merchant = Database['public']['Tables']['merchants']['Row'];

export default function Home() {
  const [merchants, setMerchants] = useState<Merchant[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchMerchants();
  }, []);

  const fetchMerchants = async () => {
    try {
      const { data, error } = await supabase
        .from('merchants')
        .select('*')
        .order('avg_rating', { ascending: false })
        .limit(8);

      if (error) throw error;
      if (data) setMerchants(data);
    } catch (error) {
      console.error('Error fetching merchants:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  const categories = [
    { name: '餐饮', icon: Utensils, color: 'bg-orange-100 text-orange-600' },
    { name: '娱乐', icon: Film, color: 'bg-blue-100 text-blue-600' },
    { name: '购物', icon: ShoppingBag, color: 'bg-pink-100 text-pink-600' },
    { name: '咖啡', icon: Coffee, color: 'bg-brown-100 text-amber-700' },
    { name: '健身', icon: Dumbbell, color: 'bg-green-100 text-green-600' },
    { name: '更多', icon: MoreHorizontal, color: 'bg-gray-100 text-gray-600' },
  ];

  return (
    <div>
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-orange-500 to-red-500 text-white py-16">
        <div className="container-custom text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-6">发现城市好去处</h1>
          <p className="text-xl opacity-90 mb-8">寻找美食、娱乐、购物及更多精彩体验</p>
          
          <div className="max-w-2xl mx-auto">
            <form onSubmit={handleSearch} className="relative">
              <input
                type="text"
                placeholder="搜索商家、分类或地点..."
                className="w-full py-4 pl-12 pr-4 rounded-full text-gray-900 focus:outline-none focus:ring-4 focus:ring-orange-300 shadow-lg"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <button 
                type="submit"
                className="absolute right-2 top-2 bottom-2 bg-orange-500 text-white px-6 rounded-full font-medium hover:bg-orange-600 transition-colors"
              >
                搜索
              </button>
            </form>
          </div>
        </div>
      </div>

      {/* Categories */}
      <div className="container-custom py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-8">热门分类</h2>
        <div className="grid grid-cols-3 md:grid-cols-6 gap-6">
          {categories.map((cat) => (
            <Link 
              key={cat.name} 
              to={`/search?category=${cat.name === '更多' ? '' : cat.name}`}
              className="flex flex-col items-center group"
            >
              <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-3 transition-transform group-hover:-translate-y-1 ${cat.color}`}>
                <cat.icon className="w-8 h-8" />
              </div>
              <span className="text-gray-700 font-medium group-hover:text-orange-500 transition-colors">{cat.name}</span>
            </Link>
          ))}
        </div>
      </div>

      {/* Recommended Merchants */}
      <div className="bg-gray-50 py-12 border-t border-gray-100">
        <div className="container-custom">
          <div className="flex justify-between items-end mb-8">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">精选推荐</h2>
              <p className="text-gray-500 mt-1">大家都在去的优质好店</p>
            </div>
            <Link to="/search" className="text-orange-500 hover:text-orange-600 font-medium flex items-center">
              查看全部 <span className="ml-1">→</span>
            </Link>
          </div>

          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="bg-white rounded-lg h-80 animate-pulse">
                  <div className="h-48 bg-gray-200 rounded-t-lg"></div>
                  <div className="p-4 space-y-3">
                    <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                    <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                    <div className="h-4 bg-gray-200 rounded w-full"></div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {merchants.map((merchant) => (
                <MerchantCard key={merchant.id} merchant={merchant} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
