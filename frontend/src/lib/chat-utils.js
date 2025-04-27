export function formatChatHistory(messages) {
    return messages.map(message => ({
      role: message.role,
      content: message.content
    }));
  }
  
  export function extractErrorMessage(error) {
    return error.response?.data?.error || error.message || 'Ocorreu um erro desconhecido';
  }