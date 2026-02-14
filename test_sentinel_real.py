import unittest
from unittest.mock import patch, MagicMock
import os
import sentinel_real

class TestDiegoElite(unittest.TestCase):
    def test_memory_load(self):
        mem = sentinel_real.load_memory()
        self.assertIn("current_mission", mem)

    @patch('sentinel_real.Groq')
    def test_groq_diego_logic(self, mock_groq_class):
        # Configurar o mock do cliente e da resposta
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()

        mock_groq_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = mock_completion
        mock_completion.choices = [mock_choice]
        mock_choice.message = mock_message
        mock_message.content = "Diego Proposal"

        # Definir uma chave de API dummy para o teste
        with patch.dict(os.environ, {"GROQ_API_KEY": "dummy_key"}):
            # Recarregar as variaveis de ambiente no modulo se necessario ou injetar direto na funcao
            # Como a funcao le de os.environ.get na inicializacao global, precisamos garantir que o valor seja pego
            # Mas na funcao gerar_proposta_diego ele le GROQ_API_KEY do modulo.
            # Vamos patchar a variavel global do modulo
            with patch('sentinel_real.GROQ_API_KEY', 'dummy_key'):
                res = sentinel_real.gerar_proposta_diego("Test", "Desc")
                self.assertIn("Diego", res)

if __name__ == "__main__":
    unittest.main()
