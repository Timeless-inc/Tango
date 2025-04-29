'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardHeader, CardContent, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { setCookie } from 'cookies-next';

export default function AdminLoginPage() {
  const [accessCode, setAccessCode] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  // Código de acesso (na prática, isso deveria estar no backend)
  const ADMIN_ACCESS_CODE = 'mango2024'; 

  const handleLogin = (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    // Simula uma verificação de autenticação
    setTimeout(() => {
      if (accessCode === ADMIN_ACCESS_CODE) {
        // Armazena o token de autenticação em cookie por 2 horas
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
    <div className="min-h-screen bg-black text-white flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader>
            <CardTitle className="text-xl text-center">Acesso Administrativo</CardTitle>
          </CardHeader>
          
          <CardContent>
            <form onSubmit={handleLogin} className="space-y-4">
              {error && (
                <div className="bg-red-900/50 text-red-300 p-3 rounded-md text-sm">
                  {error}
                </div>
              )}
              
              <div className="space-y-2">
                <Input
                  type="password"
                  placeholder="Digite o código de acesso"
                  value={accessCode}
                  onChange={(e) => setAccessCode(e.target.value)}
                  className="bg-zinc-800 border-zinc-700"
                  autoComplete="off"
                  required
                />
              </div>
              
              <Button 
                type="submit"
                className="w-full"
                disabled={isLoading || !accessCode}
              >
                {isLoading ? 'Verificando...' : 'Acessar'}
              </Button>
            </form>
          </CardContent>
          
          <CardFooter className="flex justify-center border-t border-zinc-800 text-xs text-zinc-500 py-4">
            Painel administrativo - Mango AI
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}