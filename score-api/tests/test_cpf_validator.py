import unittest
from app.utils.cpf_validator import validate_cpf

class TestCPFValidator(unittest.TestCase):
    def test_valid_cpf(self):
        # CPFs válidos com e sem formatação
        valid_cpfs = [
            "529.982.247-25",
            "52998224725",
            "111.444.777-35",
            "11144477735"
        ]
        
        for cpf in valid_cpfs:
            with self.subTest(cpf=cpf):
                self.assertTrue(validate_cpf(cpf))
    
    def test_invalid_cpf(self):
        # CPFs inválidos
        invalid_cpfs = [
            # Muito curto
            "1234567890",
            # Muito longo
            "123456789012",
            # Inválido (dígito verificador errado)
            "12345678900",
            # Todos os dígitos iguais
            "11111111111",
            "00000000000",
            # Formato inválido
            "abc.def.ghi-jk",
            # CPF com dígito verificador incorreto
            "529.982.247-26",
            # Vazio
            ""
        ]
        
        for cpf in invalid_cpfs:
            with self.subTest(cpf=cpf):
                self.assertFalse(validate_cpf(cpf))
    
    def test_cpf_edge_cases(self):
        # Testes com caracteres especiais que devem ser removidos
        self.assertTrue(validate_cpf("529-982-247/25"))
        self.assertTrue(validate_cpf("529 982 247 25"))
        
        # Casos onde o CPF é None ou não-string
        self.assertFalse(validate_cpf(None))
        self.assertFalse(validate_cpf(12345678901))

if __name__ == "__main__":
    unittest.main()