import React from 'react';
import ChatInterface from './components/ChatInterface';

const App: React.FC = () => {
  return (
    <div className="h-screen w-screen overflow-hidden bg-gray-50">
      <ChatInterface />
    </div>
  );
};

export default App;
