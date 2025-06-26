// src/components/Header.tsx

import React from 'react';
import { Link } from 'react-router-dom';
import SystemStatus from './SystemStatus'; // Importando o novo componente

const Header = () => {
  return (
    <header className="bg-black bg-opacity-30 p-4 sticky top-0 z-40 backdrop-blur-sm">
      <nav className="container mx-auto flex justify-between items-center">
        <Link to="/" className="text-xl font-bold text-white">
          AURORA
        </Link>
        <div className="flex items-center space-x-6"> {/* Agrupando os itens da direita e alinhando ao centro */}
          <Link to="/" className="text-gray-300 hover:text-white">Home</Link>
          <Link to="/manifesto" className="text-gray-300 hover:text-white">Manifesto</Link>
          <SystemStatus /> {/* Componente de status integrado */}
        </div>
      </nav>
    </header>
  );
};

export default Header;
