import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Filter, ChevronDown, Search as SearchIcon } from 'lucide-react';
import { supabase, Database } from '@/lib/supabase';
import MerchantCard from '@/components/MerchantCard';

type Merchant = Database['public']['Tables']['merchants']['Row'];

export default function Search() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [merchants, setMerchants] = useState<Merchant[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Filter states
  const query = searchParams.get('q') || '';
  const category = searchParams.get('category') || '全部';
  const [sortBy, setSortBy] = useState('rating'); // 'rating' | 'newest' | 'reviews'

  useEffect(() => {
    fetchMerchants();
  }, [query, category, sortBy]);

  const fetchMerchants = async () => {
    setLoading(true);
    try {
      let supabaseQuery = supabase
        .from('merchants')
        .select('*');

      // Apply search filter
      if (query) {
        supabaseQuery = supabaseQuery.ilike('name', `%${query}%`);
      }

      // Apply category filter
      if (category && category !== '全部') {
        supabaseQuery = supabaseQuery.eq('category', category);
      }

      // Apply sorting
      switch (sortBy) {
        case 'rating':
          supabaseQuery = supabaseQuery.order('avg_rating', { ascending: false });
          break;
        case 'newest':
          supabaseQuery = supabaseQuery.order('created_at', { ascending: false });
          break;
        case 'reviews':
          supabaseQuery = supabaseQuery.order('review_count', { ascending: false });
          break;
        default:
          supabaseQuery = supabaseQuery.order('avg_rating', { ascending: false });
      }

      const { data, error } = await supabaseQuery;

      if (error) throw error;
      if (data) setMerchants(data);
    } catch (error) {
      console.error('Error fetching merchants:', error);
    } finally {
      setLoading(false);
    }
  };

  const categories = ['全部', '餐饮', '娱乐', '购物', '咖啡', '健身'];

  const handleCategoryChange = (cat: string) => {
    if (cat === '全部') {
      searchParams.delete('category');
    } else {
      searchParams.set('category', cat);
    }
    setSearchParams(searchParams);
  };

  return (
    <div className="container-custom py-8">
      {/* Header & Filters */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-6">
          {query ? `搜索 "${query}" 的结果` : '发现商家'}
        </h1>

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-4 rounded-lg shadow-sm border border-gray-100">
          {/* Category Filter */}
          <div className="flex items-center space-x-2 overflow-x-auto pb-2 md:pb-0 scrollbar-hide">
            <Filter className="w-5 h-5 text-gray-500 flex-shrink-0" />
            <div className="flex space-x-2">
              {categories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => handleCategoryChange(cat)}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
                    category === cat
                      ? 'bg-orange-500 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          {/* Sort Dropdown */}
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500">排序:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-gray-50 border border-gray-200 text-gray-700 text-sm rounded-lg focus:ring-orange-500 focus:border-orange-500 block p-2"
            >
              <option value="rating">评分最高</option>
              <option value="reviews">评价最多</option>
              <option value="newest">最新收录</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results List */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="bg-white rounded-lg h-64 animate-pulse">
              <div className="h-40 bg-gray-200 rounded-t-lg"></div>
              <div className="p-4 space-y-3">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              </div>
            </div>
          ))}
        </div>
      ) : merchants.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {merchants.map((merchant) => (
            <MerchantCard key={merchant.id} merchant={merchant} />
          ))}
        </div>
      ) : (
        <div className="text-center py-16 bg-white rounded-lg border border-gray-100">
          <div className="bg-gray-50 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <SearchIcon className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">未找到相关商家</h3>
          <p className="text-gray-500">尝试更换搜索关键词或筛选条件</p>
        </div>
      )}
    </div>
  );
}
