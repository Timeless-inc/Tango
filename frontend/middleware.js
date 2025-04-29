import { NextResponse } from 'next/server';

// Esta função será executada em cada requisição
export function middleware(request) {
  console.log("Middleware executado para:", request.nextUrl.pathname);
  
  // Verifica se estamos em uma rota admin que não seja a página de login
  if (request.nextUrl.pathname.startsWith('/admin') && 
      !request.nextUrl.pathname.includes('/admin/login')) {
    
    console.log("Verificando autenticação para rota protegida:", request.nextUrl.pathname);
    
    // Verifica se o usuário tem o cookie de autenticação
    const adminToken = request.cookies.get('admin_token')?.value;
    console.log("Token encontrado:", adminToken);
    
    // Se não tiver o token, redireciona para login
    if (!adminToken || adminToken !== 'authenticated') {
      console.log("Redirecionando para página de login");
      const loginUrl = new URL('/admin/login', request.url);
      return NextResponse.redirect(loginUrl);
    }
    
    console.log("Usuário autenticado, continuando...");
  }
  
  return NextResponse.next();
}

// Configuração: aplicar o middleware em todas as rotas admin
export const config = {
  matcher: [
    {
      source: '/admin/:path*',
      missing: [
        { type: 'header', key: 'next-router-prefetch' },
        { type: 'header', key: 'purpose', value: 'prefetch' },
      ],
    },
    '/admin',
  ],
};