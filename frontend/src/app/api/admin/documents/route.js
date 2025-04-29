import { NextResponse } from 'next/server';

// GET - Obter todos os documentos
export async function GET() {
  try {
    // Em um cenário real, faríamos uma chamada para o backend
    // Neste caso, como o backend não tem um endpoint específico para listar,
    // você pode implementar isso depois
    
    const response = await fetch('http://localhost:8000/api/documents/list', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      // Fallback temporário se o endpoint não existir
      return NextResponse.json(
        { documents: [] },
        { status: 200 }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Erro ao buscar documentos:', error);
    return NextResponse.json(
      { error: 'Falha ao buscar documentos' },
      { status: 500 }
    );
  }
}

// POST - Adicionar documentos
export async function POST(request) {
  try {
    const body = await request.json();
    
    if (!body.documents || !Array.isArray(body.documents)) {
      return NextResponse.json(
        { error: 'Formato inválido. Esperado: { documents: [string] }' },
        { status: 400 }
      );
    }
    
    const response = await fetch('http://localhost:8000/api/documents', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        documents: body.documents 
      }),
    });

    if (!response.ok) {
      throw new Error(`API respondeu com status: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Erro ao adicionar documentos:', error);
    return NextResponse.json(
      { error: 'Falha ao adicionar documentos' },
      { status: 500 }
    );
  }
}

// DELETE - Remover documentos
export async function DELETE(request) {
  try {
    const body = await request.json();
    
    if (!body.ids || !Array.isArray(body.ids)) {
      return NextResponse.json(
        { error: 'Formato inválido. Esperado: { ids: [number] }' },
        { status: 400 }
      );
    }
    
    const response = await fetch('http://localhost:8000/api/documents', {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ ids: body.ids }),
    });

    if (!response.ok) {
      throw new Error(`API respondeu com status: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Erro ao excluir documentos:', error);
    return NextResponse.json(
      { error: 'Falha ao excluir documentos' },
      { status: 500 }
    );
  }
}