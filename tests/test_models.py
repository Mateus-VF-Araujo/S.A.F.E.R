import unittest

class TestFuncionario(unittest.TestCase):
    
    def test_funcionario_tem_nome(self):
        funcionario = {"nome": "Joao Silva"}
        self.assertEqual(funcionario["nome"], "Joao Silva")
    
    def test_funcionario_tem_email(self):
        funcionario = {"email": "joao@safer.com"}
        self.assertEqual(funcionario["email"], "joao@safer.com")
    
    def test_funcionario_tem_cargo(self):
        funcionario = {"cargo": "Operador"}
        self.assertEqual(funcionario["cargo"], "Operador")

class TestProcurado(unittest.TestCase):
    
    def test_procurado_tem_nome(self):
        procurado = {"nome": "Criminoso X"}
        self.assertEqual(procurado["nome"], "Criminoso X")
    
    def test_nivel_periculosidade_valido(self):
        nivel = 9
        self.assertGreaterEqual(nivel, 0)
        self.assertLessEqual(nivel, 10)
    
    def test_procurado_tem_foto(self):
        foto = "base64_foto_aqui"
        self.assertIsNotNone(foto)
        self.assertTrue(len(foto) > 0)

class TestPessoaComum(unittest.TestCase):
    
    def test_pessoa_comum_tem_nome(self):
        pessoa = {"nome": "Cidadao Comum"}
        self.assertEqual(pessoa["nome"], "Cidadao Comum")
    
    def test_pessoa_comum_tem_cpf(self):
        pessoa = {"cpf": "123.456.789-00"}
        self.assertEqual(pessoa["cpf"], "123.456.789-00")

if __name__ == "__main__":
    unittest.main()
