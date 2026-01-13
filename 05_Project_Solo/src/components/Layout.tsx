import React, { useState, useEffect } from 'react';
import { Link, Outlet, useNavigate } from 'react-router-dom';
import { Search, User, Menu, X, LogOut } from 'lucide-react';
import { supabase } from '@/lib/supabase';
import toast from 'react-hot-toast';

export default function Layout() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [user, setUser] = useState<any>(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
    });

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  const handleLogout = async () => {
    try {
      await supabase.auth.signOut();
      toast.success('已退出登录');
      navigate('/');
    } catch (error) {
      toast.error('退出失败');
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="container-custom mx-auto">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-2">
              <span className="text-2xl font-bold text-orange-500">大众点评Lite</span>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <Link to="/" className="text-gray-600 hover:text-orange-500 font-medium">首页</Link>
              <Link to="/search" className="text-gray-600 hover:text-orange-500 font-medium">商家</Link>
              
              <div className="flex items-center space-x-4">
                <Link to="/search" className="p-2 text-gray-500 hover:text-orange-500">
                  <Search className="w-5 h-5" />
                </Link>
                
                {user ? (
                  <div className="relative group">
                    <button className="flex items-center space-x-2 text-gray-700 hover:text-orange-500">
                      <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center text-orange-500">
                        <User className="w-5 h-5" />
                      </div>
                      <span className="max-w-[100px] truncate">{user.email?.split('@')[0]}</span>
                    </button>
                    
                    {/* Dropdown Menu */}
                    <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 hidden group-hover:block border border-gray-100">
                      <Link to="/profile" className="block px-4 py-2 text-sm text-gray-700 hover:bg-orange-50">个人中心</Link>
                      <button 
                        onClick={handleLogout}
                        className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-orange-50"
                      >
                        退出登录
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center space-x-2">
                    <Link to="/login" className="text-gray-600 hover:text-orange-500 font-medium">登录</Link>
                    <span className="text-gray-300">|</span>
                    <Link to="/register" className="text-gray-600 hover:text-orange-500 font-medium">注册</Link>
                  </div>
                )}
              </div>
            </div>

            {/* Mobile Menu Button */}
            <div className="md:hidden flex items-center">
              <button 
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="p-2 text-gray-600 hover:text-orange-500"
              >
                {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden bg-white border-t border-gray-100">
            <div className="px-4 pt-2 pb-4 space-y-1">
              <Link 
                to="/" 
                className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-orange-500 hover:bg-orange-50"
                onClick={() => setIsMenuOpen(false)}
              >
                首页
              </Link>
              <Link 
                to="/search" 
                className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-orange-500 hover:bg-orange-50"
                onClick={() => setIsMenuOpen(false)}
              >
                发现商家
              </Link>
              
              <div className="border-t border-gray-100 my-2 pt-2">
                {user ? (
                  <>
                    <div className="px-3 py-2 text-sm text-gray-500">
                      已登录: {user.email}
                    </div>
                    <Link 
                      to="/profile" 
                      className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-orange-500 hover:bg-orange-50"
                      onClick={() => setIsMenuOpen(false)}
                    >
                      个人中心
                    </Link>
                    <button 
                      onClick={() => {
                        handleLogout();
                        setIsMenuOpen(false);
                      }}
                      className="block w-full text-left px-3 py-2 rounded-md text-base font-medium text-red-500 hover:bg-red-50"
                    >
                      退出登录
                    </button>
                  </>
                ) : (
                  <div className="grid grid-cols-2 gap-4 px-3">
                    <Link 
                      to="/login" 
                      className="text-center py-2 border border-orange-500 text-orange-500 rounded-md"
                      onClick={() => setIsMenuOpen(false)}
                    >
                      登录
                    </Link>
                    <Link 
                      to="/register" 
                      className="text-center py-2 bg-orange-500 text-white rounded-md"
                      onClick={() => setIsMenuOpen(false)}
                    >
                      注册
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="flex-grow">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-8 mt-12">
        <div className="container-custom mx-auto text-center text-gray-500">
          <p className="mb-2">© 2024 大众点评Lite - 发现身边好店</p>
          <p className="text-sm">仅用于演示目的，不包含真实商业数据</p>
        </div>
      </footer>
    </div>
  );
}
