import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import SystemStatus from '../SystemStatus';

// Mock da função fetch global
global.fetch = jest.fn();

const mockFetch = (data: any, ok = true) => {
  (global.fetch as jest.Mock).mockResolvedValueOnce({
    ok: ok,
    json: async () => data,
    status: ok ? 200 : 500,
  });
};

describe('SystemStatus Component', () => {
  beforeEach(() => {
    // Limpa mocks antes de cada teste
    (global.fetch as jest.Mock).mockClear();
  });

  test('deve renderizar o estado de carregamento inicialmente', () => {
    mockFetch({ status: "Operational", timestamp: new Date().toISOString() });
    render(<SystemStatus />);
    expect(screen.getByText(/System Status: Loading.../i)).toBeInTheDocument();
  });

  test('deve renderizar o status operacional após o fetch bem-sucedido', async () => {
    const mockTimestamp = new Date().toISOString();
    mockFetch({ status: "Operational", timestamp: mockTimestamp });

    render(<SystemStatus />);

    await waitFor(() => {
      expect(screen.getByText(/System Status: Operational/i)).toBeInTheDocument();
    });

    // Verifica se o círculo verde está presente (indiretamente pela cor de fundo)
    // Esta é uma forma simplificada. Em um cenário real, você poderia testar o estilo exato
    // ou usar data-testid para selecionar o elemento do círculo.
    const statusIndicator = screen.getByText(/System Status: Operational/i).previousSibling as HTMLElement;
    expect(statusIndicator).toHaveStyle('background-color: green');
  });

  test('deve renderizar o status de erro se o fetch falhar', async () => {
    mockFetch({}, false); // Simula uma resposta de erro da API

    render(<SystemStatus />);

    await waitFor(() => {
      expect(screen.getByText(/System Status: Error/i)).toBeInTheDocument();
    });

    const statusIndicator = screen.getByText(/System Status: Error/i).previousSibling as HTMLElement;
    expect(statusIndicator).toHaveStyle('background-color: red');
  });

  test('deve renderizar um status desconhecido/diferente se a API retornar algo inesperado', async () => {
    const mockTimestamp = new Date().toISOString();
    mockFetch({ status: "Maintenance", timestamp: mockTimestamp });

    render(<SystemStatus />);

    await waitFor(() => {
      expect(screen.getByText(/System Status: Maintenance/i)).toBeInTheDocument();
    });

    const statusIndicator = screen.getByText(/System Status: Maintenance/i).previousSibling as HTMLElement;
    expect(statusIndicator).toHaveStyle('background-color: orange');
  });
});
