import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    const body = await request.json();
    console.log("Enviando consulta para o backend:", body.query);
    
    const response = await fetch('http://localhost:8000/api/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: body.query,
        conversation_history: body.conversation_history
      }),
    });

    if (!response.ok) {
      throw new Error(`API responded with status: ${response.status}`);
    }

    const data = await response.json();
    console.log("Resposta do backend:", data);
    
    // Mapeia os campos do backend para o formato esperado pelo frontend
    const mappedResponse = {
      // Se o backend retornar 'response', use-o como 'answer'
      answer: data.response || data.answer || "Não foi possível obter uma resposta.",
      // Mantém quaisquer outros campos que possam ser úteis
      sources: data.sources || [],
      // Adicione outros mapeamentos conforme necessário
    };
    
    console.log("Resposta mapeada para o frontend:", mappedResponse);
    return NextResponse.json(mappedResponse);
  } catch (error) {
    console.error('Error proxying to backend:', error);
    return NextResponse.json(
      { 
        error: 'Failed to connect to backend service',
        details: error.message 
      },
      { status: 500 }
    );
  }
}