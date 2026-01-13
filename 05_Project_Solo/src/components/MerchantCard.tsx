import React from 'react';
import { Link } from 'react-router-dom';
import { Star, MapPin } from 'lucide-react';
import { Database } from '@/lib/supabase';

type Merchant = Database['public']['Tables']['merchants']['Row'];

interface MerchantCardProps {
  merchant: Merchant;
}

export default function MerchantCard({ merchant }: MerchantCardProps) {
  return (
    <Link to={`/merchant/${merchant.id}`} className="card group hover:shadow-md transition-shadow block">
      <div className="relative h-48 overflow-hidden">
        <img 
          src={merchant.cover_image || 'https://images.unsplash.com/photo-1514933651103-005eec06c04b?w=800&auto=format&fit=crop&q=60'} 
          alt={merchant.name}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        />
        <div className="absolute top-2 right-2 bg-white/90 backdrop-blur-sm px-2 py-1 rounded text-xs font-medium text-gray-600">
          {merchant.category}
        </div>
      </div>
      <div className="p-4">
        <h3 className="text-lg font-bold text-gray-900 group-hover:text-orange-500 transition-colors mb-1">
          {merchant.name}
        </h3>
        
        <div className="flex items-center mb-2">
          <div className="flex text-orange-400">
            {[...Array(5)].map((_, i) => (
              <Star 
                key={i} 
                className={`w-4 h-4 ${i < Math.floor(merchant.avg_rating) ? 'fill-current' : 'text-gray-300'}`} 
              />
            ))}
          </div>
          <span className="text-sm text-gray-500 ml-2">{merchant.avg_rating.toFixed(1)}分</span>
          {merchant.review_count > 0 && (
            <span className="text-xs text-gray-400 ml-2">({merchant.review_count}条评价)</span>
          )}
        </div>
        
        <div className="flex items-start text-gray-500 text-sm">
          <MapPin className="w-4 h-4 mt-0.5 mr-1 flex-shrink-0" />
          <span className="truncate">{merchant.address}</span>
        </div>
      </div>
    </Link>
  );
}
