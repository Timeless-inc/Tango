export function formatChatHistory(messages) {
    return messages.map(message => ({
      role: message.role,
      content: message.content
    }));
  }
  
  export function extractErrorMessage(error) {
    return error.response?.data?.error || error.message || 'Ocorreu um erro desconhecido';
  }

/**
 * Gera sugestões de perguntas com base na resposta do assistente
 * @param {string} assistantResponse - A resposta do assistente
 * @returns {Promise<string[]>} Array de sugestões
 */
export async function fetchSuggestions(assistantResponse) {
  try {
    const keywords = ['curso', 'matrícula', 'professor', 'aula', 'campus', 'horário', 'inscrição', 'edital'];
    
    const suggestions = [];
    
    // Verifica palavras-chave na resposta
    keywords.forEach(keyword => {
      if (assistantResponse.toLowerCase().includes(keyword.toLowerCase())) {
        switch (keyword) {
          case 'curso':
            suggestions.push('Como faço para me inscrever neste curso?');
            suggestions.push('Quais são os pré-requisitos para este curso?');
            break;
          case 'matrícula':
            suggestions.push('Qual o prazo para matrícula?');
            suggestions.push('Quais documentos são necessários para matrícula?');
            break;
          case 'professor':
            suggestions.push('Como posso contatar este professor?');
            suggestions.push('Qual o horário de atendimento deste professor?');
            break;
          case 'aula':
            suggestions.push('Onde serão realizadas as aulas?');
            suggestions.push('Qual o calendário de aulas?');
            break;
          case 'campus':
            suggestions.push('Como chegar neste campus?');
            suggestions.push('Quais cursos são oferecidos neste campus?');
            break;
          default:
            break;
        }
      }
    });
    
    // Sempre adiciona algumas perguntas gerais
    if (suggestions.length < 2) {
      suggestions.push('Como faço para me inscrever no IFPE?');
      suggestions.push('Quais são os cursos oferecidos?');
    }
    
    // Limita o número de sugestões
    return suggestions.slice(0, 3);
  } catch (error) {
    console.error('Erro ao gerar sugestões:', error);
    return [];
  }
}