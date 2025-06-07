import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    const formData = await request.formData();
    
    console.log("Enviando PDF para o backend...");
    
    const response = await fetch('http://localhost:8000/api/upload-pdf', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `API responded with status: ${response.status}`);
    }

    const data = await response.json();
    console.log("Resposta do backend para upload de PDF:", data);
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Erro no proxy de upload de PDF:', error);
    return NextResponse.json(
      { 
        success: false,
        message: 'Falha ao conectar com o serviço de backend',
        error: error.message,
        documents_added: 0
      },
      { status: 500 }
    );
  }
}