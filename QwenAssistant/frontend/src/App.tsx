import React from 'react';
import ChatInterface from './components/ChatInterface';

const App: React.FC = () => {
  return (
    <div className="h-screen flex flex-col">
      <ChatInterface />
    </div>
  );
};

export default App;