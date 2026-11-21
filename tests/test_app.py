import re
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from app import create_app


class FixnowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.temp.name) / 'test.db')
        self.app = create_app({'TESTING': True, 'DATABASE': self.path, 'SECRET_KEY': 'tests-only'})
        self.client = self.app.test_client()
        self.client.get('/')
        with self.client.session_transaction() as session:
            self.csrf = session['csrf']

    def tearDown(self):
        self.temp.cleanup()

    def post(self, path, data=None):
        return self.client.post(path, data={**(data or {}), 'csrf': self.csrf}, follow_redirects=True)

    def rows(self, table):
        with closing(sqlite3.connect(self.path)) as connection:
            connection.row_factory = sqlite3.Row
            return [dict(r) for r in connection.execute(f'SELECT * FROM {table}')]

    def parents(self):
        self.post('/cadastros/clientes/novo', {'nome': 'Cliente teste', 'email': 'cliente@example.com', 'telefone': '43999999999'})
        self.post('/cadastros/tecnicos/novo', {'nome': 'Técnico teste', 'email': 'tecnico@example.com', 'especialidade': 'Redes'})

    def ticket_data(self, **changes):
        return {'titulo': 'Sem conexão', 'descricao': 'Verificar equipamento', 'cliente_id': '1', 'tecnico_id': '1', 'status': 'Aberto', **changes}

    def test_clients_and_technicians_complete_crud(self):
        for entity, extra in [('clientes', {'telefone': '43999999999'}), ('tecnicos', {'especialidade': 'Redes'})]:
            data = {'nome': 'Teste', 'email': 'teste@example.com', **extra}
            self.assertEqual(self.post(f'/cadastros/{entity}/novo', data).status_code, 200)
            self.assertIn('Teste', self.client.get(f'/cadastros/{entity}').get_data(as_text=True))
            self.assertEqual(self.client.get(f'/cadastros/{entity}/1/editar').status_code, 200)
            self.post(f'/cadastros/{entity}/1/editar', {**data, 'nome': 'Alterado'})
            self.assertEqual(self.rows(entity)[0]['nome'], 'Alterado')
            self.post(f'/cadastros/{entity}/1/excluir')
            self.assertEqual(self.rows(entity), [])

    def test_tickets_complete_crud_and_states(self):
        self.parents()
        self.post('/chamados/novo', self.ticket_data())
        self.assertEqual(self.rows('chamados')[0]['status'], 'Aberto')
        self.assertIn('Sem conexão', self.client.get('/chamados/1').get_data(as_text=True))
        for state in ['Em andamento', 'Concluído', 'Aberto']:
            self.post('/chamados/1/editar', self.ticket_data(status=state, titulo='Atualizado'))
            self.assertEqual(self.rows('chamados')[0]['status'], state)
        self.assertEqual(self.client.get('/chamados/1/editar').status_code, 200)
        self.post('/chamados/1/excluir')
        self.assertEqual(self.rows('chamados'), [])

    def test_referenced_parents_cannot_be_deleted(self):
        self.parents()
        self.post('/chamados/novo', self.ticket_data())
        for entity in ['clientes', 'tecnicos']:
            response = self.post(f'/cadastros/{entity}/1/excluir')
            self.assertIn('vinculado', response.get_data(as_text=True))
            self.assertEqual(len(self.rows(entity)), 1)

    def test_required_fields_email_and_limits(self):
        for data in [{}, {'nome': 'x', 'email': 'errado', 'telefone': '1'}, {'nome': 'x' * 101, 'email': 'x@y.com', 'telefone': '1'}]:
            self.assertIn('Confira os dados', self.post('/cadastros/clientes/novo', data).get_data(as_text=True))
        self.assertEqual(self.rows('clientes'), [])

    def test_ticket_rejects_invalid_links_states_and_empty_fields(self):
        self.parents()
        for changes in [{'cliente_id': '999'}, {'tecnico_id': 'abc'}, {'status': 'Inválido'}, {'titulo': ''}, {'descricao': 'x' * 3001}]:
            response = self.post('/chamados/novo', self.ticket_data(**changes))
            self.assertIn('Confira os dados', response.get_data(as_text=True))
        self.assertEqual(self.rows('chamados'), [])

    def test_filters_combined_and_empty_results(self):
        self.parents()
        self.post('/chamados/novo', self.ticket_data())
        self.post('/chamados/novo', self.ticket_data(status='Concluído', titulo='Finalizado'))
        response = self.client.get('/chamados?status=Aberto&tecnico=1&busca=conex').get_data(as_text=True)
        self.assertIn('Sem conexão', response)
        self.assertNotIn('Finalizado', response)
        self.assertIn('Nenhum chamado', self.client.get('/chamados?busca=inexistente').get_data(as_text=True))
        self.assertEqual(self.client.get('/chamados?status=Inválido').status_code, 400)
        self.assertEqual(self.client.get('/chamados?tecnico=abc').status_code, 400)

    def test_csrf_and_delete_methods(self):
        self.assertEqual(self.client.post('/cadastros/clientes/novo', data={'nome': 'X'}).status_code, 400)
        self.assertEqual(self.client.get('/chamados/1/excluir').status_code, 405)

    def test_missing_records_and_unknown_entities(self):
        for path in ['/chamados/999', '/chamados/999/editar', '/cadastros/clientes/999/editar', '/cadastros/users']:
            self.assertEqual(self.client.get(path).status_code, 404)

    def test_html_escaped_and_sql_parameters(self):
        self.parents()
        self.post('/chamados/novo', self.ticket_data(titulo='<script>alert(1)</script>'))
        detail = self.client.get('/chamados/1').get_data(as_text=True)
        self.assertNotIn('<script>alert(1)</script>', detail)
        self.assertIn('&lt;script&gt;', detail)
        self.assertEqual(self.client.get('/chamados?busca=%27%3B%20DROP%20TABLE%20chamados%3B--').status_code, 200)
        self.assertEqual(len(self.rows('chamados')), 1)

    def test_persistence_after_reopening_application(self):
        self.parents()
        another = create_app({'TESTING': True, 'DATABASE': self.path})
        response = another.test_client().get('/cadastros/clientes')
        self.assertIn('Cliente teste', response.get_data(as_text=True))

    def test_dashboard_and_empty_screens(self):
        for path in ['/', '/chamados', '/chamados/novo', '/cadastros/clientes', '/cadastros/tecnicos']:
            self.assertEqual(self.client.get(path).status_code, 200)
        self.assertIn('cadastre pelo menos', self.client.get('/chamados/novo').get_data(as_text=True))

    def test_demo_is_non_destructive(self):
        runner = self.app.test_cli_runner()
        self.assertEqual(runner.invoke(args=['demo']).exit_code, 0)
        self.assertEqual(len(self.rows('chamados')), 3)
        runner.invoke(args=['demo'])
        self.assertEqual(len(self.rows('chamados')), 3)


if __name__ == '__main__':
    unittest.main()
