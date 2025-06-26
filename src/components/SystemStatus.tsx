import React, { useState, useEffect } from 'react';

interface StatusData {
  status: string;
  timestamp: string;
}

const SystemStatus: React.FC = () => {
  const [statusData, setStatusData] = useState<StatusData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchStatus = async () => {
      setIsLoading(true);
      try {
        // Para desenvolvimento, assumimos que a API está em http://localhost:8000
        // Em um ambiente de produção, isso viria de uma variável de ambiente ou configuração.
        const response = await fetch('http://localhost:8000/api/v1/status');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data: StatusData = await response.json();
        setStatusData(data);
        setError(null);
      } catch (err) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError('An unknown error occurred');
        }
        setStatusData(null);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStatus();

    // Opcional: configurar um intervalo para buscar o status periodicamente
    // const intervalId = setInterval(fetchStatus, 30000); // Atualiza a cada 30 segundos
    // return () => clearInterval(intervalId); // Limpa o intervalo quando o componente é desmontado
  }, []);

  if (isLoading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', fontFamily: 'Arial, sans-serif', fontSize: '14px' }}>
        <div style={{
          width: '10px',
          height: '10px',
          borderRadius: '50%',
          backgroundColor: 'gray',
          marginRight: '8px',
          animation: 'pulse 1.5s infinite ease-in-out'
        }}></div>
        System Status: Loading...
        <style>{`
          @keyframes pulse {
            0% { transform: scale(0.8); opacity: 0.7; }
            50% { transform: scale(1); opacity: 1; }
            100% { transform: scale(0.8); opacity: 0.7; }
          }
        `}</style>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', fontFamily: 'Arial, sans-serif', fontSize: '14px' }}>
        <div style={{
          width: '10px',
          height: '10px',
          borderRadius: '50%',
          backgroundColor: 'red',
          marginRight: '8px'
        }}></div>
        System Status: Error ({error})
      </div>
    );
  }

  if (statusData && statusData.status === 'Operational') {
    return (
      <div style={{ display: 'flex', alignItems: 'center', fontFamily: 'Arial, sans-serif', fontSize: '14px' }}>
        <div style={{
          width: '10px',
          height: '10px',
          borderRadius: '50%',
          backgroundColor: 'green',
          marginRight: '8px'
        }}></div>
        System Status: Operational
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', fontFamily: 'Arial, sans-serif', fontSize: '14px' }}>
      <div style={{
        width: '10px',
        height: '10px',
        borderRadius: '50%',
        backgroundColor: 'orange',
        marginRight: '8px'
      }}></div>
      System Status: {statusData?.status || 'Unknown'}
    </div>
  );
};

export default SystemStatus;
