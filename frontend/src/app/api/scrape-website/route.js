import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    const body = await request.json();
    console.log("Enviando requisição de scraping para o backend:", body);
    
    const response = await fetch('http://localhost:8000/api/scrape-website', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `API responded with status: ${response.status}`);
    }

    const data = await response.json();
    console.log("Resposta do backend para scraping:", data);
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Erro no proxy de web scraping:', error);
    return NextResponse.json(
      { 
        success: false,
        message: 'Falha ao conectar com o serviço de backend',
        error: error.message,
        documents_added: 0,
        failed_urls: [],
        scraped_urls: []
      },
      { status: 500 }
    );
  }
}