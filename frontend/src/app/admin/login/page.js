// filepath: d:\ifpe\Tango\frontend\src\app\admin\login\page.js
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { setCookie } from 'cookies-next';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Shield, Lock, Eye, EyeOff } from 'lucide-react';
import { motion } from 'framer-motion';

export default function AdminLoginPage() {
  const [accessCode, setAccessCode] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const router = useRouter();

  const ADMIN_ACCESS_CODE = 'mango2024';

  const handleLogin = (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    setTimeout(() => {
      if (accessCode === ADMIN_ACCESS_CODE) {
        setCookie('admin_token', 'authenticated', {
          maxAge: 60 * 60 * 2,
          path: '/',
          sameSite: 'strict',
          secure: process.env.NODE_ENV === 'production'
        });
        router.push('/admin');
      } else {
        setError('Código de acesso inválido');
        setIsLoading(false);
      }
    }, 500);
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden">    
      {/* Container com largura fixa para garantir posicionamento */}
      <div className="relative z-10 w-full" style={{ maxWidth: '28rem' }}>
        <div className="mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="w-full"
          >
            <Card className="bg-zinc-900/95 backdrop-blur-sm border-zinc-700/50 shadow-2xl">
              <CardHeader className="text-center space-y-6 pb-6">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.3, duration: 0.5 }}
                  className="flex justify-center"
                >
                  <div className="p-4 bg-gradient-to-r from-orange-500 to-orange-600 rounded-full shadow-lg">
                    <Shield className="w-8 h-8 text-white" />
                  </div>
                </motion.div>
                <div className="space-y-2">
                  <CardTitle className="text-2xl font-bold text-white tracking-tight">
                    Acesso Administrativo
                  </CardTitle>
                  <p className="text-zinc-400 text-sm leading-relaxed">
                    Digite o código de acesso para continuar
                  </p>
                </div>
              </CardHeader>

              <CardContent className="space-y-6 px-6">
                <form onSubmit={handleLogin} className="space-y-6">
                  <div className="space-y-3">
                    <Label htmlFor="accessCode" className="text-zinc-300 text-sm font-medium">
                      Código de Acesso
                    </Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-zinc-400" />
                      <Input
                        id="accessCode"
                        type={showPassword ? "text" : "password"}
                        value={accessCode}
                        onChange={(e) => setAccessCode(e.target.value)}
                        placeholder="Digite o código"
                        className="pl-11 pr-12 h-12 bg-zinc-800/80 border-zinc-600 text-white placeholder:text-zinc-500 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 transition-all duration-200"
                        autoComplete="off"
                        autoFocus
                        required
                      />
                      <button
                        type="button"
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 hover:bg-zinc-700 rounded transition-colors"
                        onClick={() => setShowPassword(!showPassword)}
                      >
                        {showPassword ? (
                          <EyeOff className="h-5 w-5 text-zinc-400" />
                        ) : (
                          <Eye className="h-5 w-5 text-zinc-400" />
                        )}
                      </button>
                    </div>
                  </div>

                  {error && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="p-4 bg-red-900/30 border border-red-700/50 rounded-lg backdrop-blur-sm"
                    >
                      <p className="text-red-300 text-sm font-medium flex items-center gap-2">
                        <span className="w-2 h-2 bg-red-400 rounded-full"></span>
                        {error}
                      </p>
                    </motion.div>
                  )}

                  <Button
                    type="submit"
                    className="w-full h-12 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-medium shadow-lg hover:shadow-orange-500/25 transition-all duration-200"
                    disabled={isLoading || !accessCode.trim()}
                  >
                    {isLoading ? (
                      <div className="flex items-center gap-3">
                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                        <span>Verificando...</span>
                      </div>
                    ) : (
                      <span className="flex items-center gap-2">
                        <Shield className="w-4 h-4" />
                        Acessar Painel
                      </span>
                    )}
                  </Button>
                </form>
              </CardContent>

              <CardFooter className="text-center border-t border-zinc-700/50 pt-6 pb-6">
                <div className="w-full space-y-2">
                  <p className="text-sm font-medium text-white">
                    Painel Administrativo
                  </p>
                  <p className="text-xs text-zinc-500">
                    Mango AI
                  </p>
                </div>
              </CardFooter>
            </Card>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="text-center mt-6"
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-zinc-900/50 backdrop-blur-sm border border-zinc-700/50 rounded-full">
                <div className="w-2 h-2 bg-red-400 rounded-full animate-pulse"></div>
                <p className="text-xs text-zinc-400 font-medium">
                  Área restrita - Acesso monitorado
                </p>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}