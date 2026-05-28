import unittest

class TestFuncionario(unittest.TestCase):
    
    def test_funcionario_tem_nome(self):
        funcionario = {"nome": "Joao Silva"}
        self.assertEqual(funcionario["nome"], "Joao Silva")
    
    def test_funcionario_tem_email(self):
        funcionario = {"email": "joao@safer.com"}
        self.assertEqual(funcionario["email"], "joao@safer.com")

class TestProcurado(unittest.TestCase):
    
    def test_procurado_tem_nome(self):
        procurado = {"nome": "Criminoso X"}
        self.assertEqual(procurado["nome"], "Criminoso X")
    
    def test_nivel_periculosidade_valido(self):
        nivel = 9
        self.assertGreaterEqual(nivel, 0)
        self.assertLessEqual(nivel, 10)

if __name__ == "__main__":
    unittest.main()
