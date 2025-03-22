import pytest
import requests
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Classe para gerenciar notificações
class NotificacaoService:
    def __init__(self, base_url="https://api.inclusao.cps.sp.gov.br"):
        self.base_url = base_url
    
    def obter_notificacoes_usuario(self, usuario_id):
        """
        Recupera notificações de um usuário específico
        
        Args:
            usuario_id: ID do usuário
            
        Returns:
            dict: Resposta da API com status e dados
        """
        url = f"{self.base_url}/notificacoes/usuario/{usuario_id}"
        try:
            response = requests.get(url)
            return {
                "status": response.status_code,
                "data": response.json() if response.status_code == 200 else None,
                "message": response.text if response.status_code != 200 else None
            }
        except Exception as e:
            return {
                "status": 500,
                "data": None,
                "message": f"Erro ao conectar com a API: {str(e)}"
            }

# Função para criar dados simulados
def criar_mock_notificacoes(cenario="com_notificacoes"):
    hoje = datetime.now()
    
    if cenario == "com_notificacoes":
        return MagicMock(
            status_code=200,
            json=lambda: [
                {
                    "id": 101,
                    "titulo": "Atendimento confirmado",
                    "mensagem": "Seu atendimento para amanhã às 14h foi confirmado",
                    "data_criacao": (hoje - timedelta(hours=2)).isoformat(),
                    "prioridade": "alta",
                    "lida": False,
                    "tipo": "confirmacao"
                },
                {
                    "id": 102,
                    "titulo": "Lembrete de atendimento",
                    "mensagem": "Você tem um atendimento agendado para próxima semana",
                    "data_criacao": (hoje - timedelta(days=1)).isoformat(),
                    "prioridade": "media",
                    "lida": False,
                    "tipo": "lembrete"
                },
                {
                    "id": 103,
                    "titulo": "Pesquisa de satisfação",
                    "mensagem": "Gostaríamos de saber sua opinião sobre o último atendimento",
                    "data_criacao": (hoje - timedelta(days=3)).isoformat(),
                    "prioridade": "baixa",
                    "lida": False,
                    "tipo": "feedback"
                }
            ]
        )
    elif cenario == "sem_notificacoes":
        return MagicMock(
            status_code=200,
            json=lambda: []
        )
    elif cenario == "usuario_invalido":
        mock = MagicMock()
        mock.status_code = 404
        mock.text = "Usuário não encontrado"
        return mock
    else:
        mock = MagicMock()
        mock.status_code = 500
        mock.text = "Erro interno no servidor"
        return mock

# Testes
class TestNotificacoes:
    
    @patch('requests.get')
    def test_obter_notificacoes_com_sucesso(self, mock_get):
        # Arrange
        mock_get.return_value = criar_mock_notificacoes("com_notificacoes")
        service = NotificacaoService()
        
        # Act
        resultado = service.obter_notificacoes_usuario(123)
        
        # Assert
        assert resultado["status"] == 200
        assert len(resultado["data"]) == 3
        # Verifica se as notificações estão ordenadas por prioridade
        prioridades = [n["prioridade"] for n in resultado["data"]]
        assert prioridades[0] == "alta"  # Primeira notificação deve ter prioridade alta
        
        print("✅ TESTE APROVADO: Notificações recuperadas com sucesso")
        print(f"Total de notificações: {len(resultado['data'])}")
        print(f"Notificação de maior prioridade: {resultado['data'][0]['titulo']}")
    
    @patch('requests.get')
    def test_obter_notificacoes_usuario_sem_notificacoes(self, mock_get):
        # Arrange
        mock_get.return_value = criar_mock_notificacoes("sem_notificacoes")
        service = NotificacaoService()
        
        # Act
        resultado = service.obter_notificacoes_usuario(456)
        
        # Assert
        assert resultado["status"] == 200
        assert len(resultado["data"]) == 0
        
        print("✅ TESTE APROVADO: Sistema retornou lista vazia corretamente")
        print("Mensagem: Usuário não possui notificações pendentes")
    
    @patch('requests.get')
    def test_obter_notificacoes_usuario_invalido(self, mock_get):
        # Arrange
        mock_get.return_value = criar_mock_notificacoes("usuario_invalido")
        service = NotificacaoService()
        
        # Act
        resultado = service.obter_notificacoes_usuario(999)
        
        # Assert
        assert resultado["status"] == 404
        assert resultado["data"] is None
        assert "Usuário não encontrado" in resultado["message"]
        
        print("✅ TESTE APROVADO: Sistema identificou usuário inválido")
        print(f"Status: {resultado['status']}")
        print(f"Mensagem: {resultado['message']}")

# Função para executar os testes manualmente
def executar_testes():
    print("\n===== INICIANDO TESTES DO MÓDULO DE NOTIFICAÇÕES =====\n")
    
    tester = TestNotificacoes()
    
    # Teste 1: Usuário com notificações
    print("\n----- Teste 1: Usuário com notificações pendentes -----")
    with patch('requests.get', return_value=criar_mock_notificacoes("com_notificacoes")):
        tester.test_obter_notificacoes_com_sucesso(None)
    
    # Teste 2: Usuário sem notificações
    print("\n----- Teste 2: Usuário sem notificações pendentes -----")
    with patch('requests.get', return_value=criar_mock_notificacoes("sem_notificacoes")):
        tester.test_obter_notificacoes_usuario_sem_notificacoes(None)
    
    # Teste 3: ID de usuário inválido
    print("\n----- Teste 3: ID de usuário inválido -----")
    with patch('requests.get', return_value=criar_mock_notificacoes("usuario_invalido")):
        tester.test_obter_notificacoes_usuario_invalido(None)
    
    print("\n===== TESTES FINALIZADOS =====")

if __name__ == "__main__":
    executar_testes()