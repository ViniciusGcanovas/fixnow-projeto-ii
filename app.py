"""FIXNOW: gerenciamento local de chamados técnicos."""
import os
import re
import secrets
import sqlite3
from pathlib import Path

from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for

ROOT = Path(__file__).resolve().parent
STATUS = ('Aberto', 'Em andamento', 'Concluído')
ENTITIES = {
    'clientes': {'title': 'Clientes', 'singular': 'cliente', 'fields': [('nome', 'Nome', 100), ('email', 'E-mail', 150), ('telefone', 'Telefone', 30)]},
    'tecnicos': {'title': 'Técnicos', 'singular': 'técnico', 'fields': [('nome', 'Nome', 100), ('email', 'E-mail', 150), ('especialidade', 'Especialidade', 100)]},
}


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(SECRET_KEY=os.environ.get('FIXNOW_SECRET_KEY') or secrets.token_hex(32),
                      DATABASE=str(ROOT / 'instance' / 'fixnow.db'), MAX_CONTENT_LENGTH=64 * 1024,
                      SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax')
    if config:
        app.config.update(config)
    Path(app.config['DATABASE']).parent.mkdir(parents=True, exist_ok=True)

    def db():
        if 'db' not in g:
            g.db = sqlite3.connect(app.config['DATABASE'])
            g.db.row_factory = sqlite3.Row
            g.db.execute('PRAGMA foreign_keys = ON')
        return g.db

    @app.teardown_appcontext
    def close_db(error=None):
        connection = g.pop('db', None)
        if connection is not None:
            connection.close()

    with app.app_context():
        db().executescript((ROOT / 'schema.sql').read_text(encoding='utf-8'))

    @app.before_request
    def protect_forms():
        session.setdefault('csrf', secrets.token_urlsafe(32))
        if request.method == 'POST' and not secrets.compare_digest(session['csrf'], request.form.get('csrf', '')):
            abort(400, description='Formulário expirado ou inválido. Recarregue a página e tente novamente.')

    @app.context_processor
    def globals_for_templates():
        return dict(statuses=STATUS, entities=ENTITIES)

    def one(table, record_id):
        # Table names come exclusively from internal route allowlists.
        record = db().execute(f'SELECT * FROM {table} WHERE id = ?', (record_id,)).fetchone()
        if record is None:
            abort(404)
        return record

    def entity_info(entity):
        if entity not in ENTITIES:
            abort(404)
        return ENTITIES[entity]

    def fields_data(fields):
        data, errors = {}, []
        for key, label, limit in fields:
            value = request.form.get(key, '').strip()
            data[key] = value
            if not value:
                errors.append(f'{label}: preenchimento obrigatório.')
            elif len(value) > limit:
                errors.append(f'{label}: limite de {limit} caracteres.')
            elif key == 'email' and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', value):
                errors.append('Informe um e-mail válido.')
        return data, errors

    @app.get('/')
    def dashboard():
        counts = {s: db().execute('SELECT COUNT(*) FROM chamados WHERE status = ?', (s,)).fetchone()[0] for s in STATUS}
        recent = db().execute('SELECT c.*, cl.nome AS cliente, t.nome AS tecnico FROM chamados c JOIN clientes cl ON cl.id=c.cliente_id JOIN tecnicos t ON t.id=c.tecnico_id ORDER BY c.id DESC LIMIT 5').fetchall()
        return render_template('dashboard.html', title='Visão geral', counts=counts, recent=recent)

    @app.get('/cadastros/<entity>')
    def records(entity):
        info = entity_info(entity)
        rows = db().execute(f'SELECT * FROM {entity} ORDER BY nome, id').fetchall()
        return render_template('records.html', title=info['title'], entity=entity, info=info, rows=rows)

    @app.route('/cadastros/<entity>/novo', methods=['GET', 'POST'])
    @app.route('/cadastros/<entity>/<int:record_id>/editar', methods=['GET', 'POST'])
    def record_form(entity, record_id=None):
        info = entity_info(entity)
        data = dict(one(entity, record_id)) if record_id is not None else {}
        errors = []
        if request.method == 'POST':
            data, errors = fields_data(info['fields'])
            if not errors:
                keys = list(data)
                with db():
                    if record_id is None:
                        db().execute(f"INSERT INTO {entity} ({','.join(keys)}) VALUES ({','.join('?' for _ in keys)})", list(data.values()))
                    else:
                        db().execute(f"UPDATE {entity} SET {','.join(k+'=?' for k in keys)} WHERE id=?", [*data.values(), record_id])
                flash('Cadastro salvo com sucesso.', 'success')
                return redirect(url_for('records', entity=entity))
        return render_template('record_form.html', title=('Editar ' if record_id else 'Novo ') + info['singular'], info=info, entity=entity, data=data, errors=errors)

    @app.post('/cadastros/<entity>/<int:record_id>/excluir')
    def record_delete(entity, record_id):
        entity_info(entity)
        one(entity, record_id)
        try:
            with db():
                db().execute(f'DELETE FROM {entity} WHERE id=?', (record_id,))
            flash('Cadastro excluído com sucesso.', 'success')
        except sqlite3.IntegrityError:
            flash('Este cadastro está vinculado a um chamado. Exclua ou altere o chamado antes de removê-lo.', 'error')
        return redirect(url_for('records', entity=entity))

    @app.get('/chamados')
    def tickets():
        state = request.args.get('status', '')
        technician = request.args.get('tecnico', '')
        search = request.args.get('busca', '').strip()
        if state and state not in STATUS:
            abort(400, description='Estado de chamado inválido.')
        if technician and not technician.isdecimal():
            abort(400, description='Técnico inválido.')
        clauses, params = [], []
        if state:
            clauses.append('c.status=?'); params.append(state)
        if technician:
            clauses.append('c.tecnico_id=?'); params.append(technician)
        if search:
            clauses.append('(c.titulo LIKE ? OR cl.nome LIKE ?)'); params.extend([f'%{search}%', f'%{search}%'])
        sql = 'SELECT c.*, cl.nome AS cliente, t.nome AS tecnico FROM chamados c JOIN clientes cl ON cl.id=c.cliente_id JOIN tecnicos t ON t.id=c.tecnico_id'
        if clauses:
            sql += ' WHERE ' + ' AND '.join(clauses)
        rows = db().execute(sql + ' ORDER BY c.id DESC', params).fetchall()
        technicians = db().execute('SELECT * FROM tecnicos ORDER BY nome').fetchall()
        return render_template('tickets.html', title='Chamados', rows=rows, technicians=technicians, state=state, technician=technician, search=search)

    @app.route('/chamados/novo', methods=['GET', 'POST'])
    @app.route('/chamados/<int:record_id>/editar', methods=['GET', 'POST'])
    def ticket_form(record_id=None):
        data = dict(one('chamados', record_id)) if record_id is not None else {'status': 'Aberto'}
        errors = []
        clients = db().execute('SELECT * FROM clientes ORDER BY nome').fetchall()
        technicians = db().execute('SELECT * FROM tecnicos ORDER BY nome').fetchall()
        if request.method == 'POST':
            data, errors = fields_data([('titulo', 'Título', 150), ('descricao', 'Descrição', 3000)])
            data['status'] = request.form.get('status', '')
            if data['status'] not in STATUS:
                errors.append('Selecione um estado válido.')
            for key, table in [('cliente_id', 'clientes'), ('tecnico_id', 'tecnicos')]:
                value = request.form.get(key, '')
                data[key] = value
                if not value.isdecimal() or not db().execute(f'SELECT id FROM {table} WHERE id=?', (value,)).fetchone():
                    errors.append('Selecione um cliente e um técnico existentes.')
            if not errors:
                with db():
                    if record_id is None:
                        cursor = db().execute('INSERT INTO chamados (titulo,descricao,status,cliente_id,tecnico_id) VALUES (:titulo,:descricao,:status,:cliente_id,:tecnico_id)', data)
                        record_id = cursor.lastrowid
                    else:
                        db().execute("UPDATE chamados SET titulo=:titulo,descricao=:descricao,status=:status,cliente_id=:cliente_id,tecnico_id=:tecnico_id, atualizado_em=strftime('%Y-%m-%d %H:%M:%S','now') WHERE id=:id", {**data, 'id': record_id})
                flash('Chamado salvo com sucesso.', 'success')
                return redirect(url_for('ticket_detail', record_id=record_id))
        return render_template('ticket_form.html', title='Editar chamado' if record_id else 'Novo chamado', data=data, errors=errors, clients=clients, technicians=technicians)

    @app.get('/chamados/<int:record_id>')
    def ticket_detail(record_id):
        ticket = one('chamados', record_id)
        return render_template('ticket_detail.html', title=f'Chamado #{record_id:04d}', ticket=ticket, client=one('clientes', ticket['cliente_id']), technician=one('tecnicos', ticket['tecnico_id']))

    @app.post('/chamados/<int:record_id>/excluir')
    def ticket_delete(record_id):
        one('chamados', record_id)
        with db():
            db().execute('DELETE FROM chamados WHERE id=?', (record_id,))
        flash('Chamado excluído com sucesso.', 'success')
        return redirect(url_for('tickets'))

    @app.errorhandler(400)
    @app.errorhandler(404)
    @app.errorhandler(413)
    def error_page(error):
        return render_template('error.html', title=f'Erro {error.code}', error=error), error.code

    @app.cli.command('demo')
    def demo():
        """Adiciona dados fictícios somente quando o banco está vazio."""
        if any(db().execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in ('clientes', 'tecnicos', 'chamados')):
            print('Banco não vazio: nenhum dado foi alterado.'); return
        with db():
            db().executemany('INSERT INTO clientes (nome,email,telefone) VALUES (?,?,?)', [('Ana Lima (exemplo)', 'ana@example.com', '(43) 99999-0101'), ('Mercado Central (exemplo)', 'mercado@example.com', '(43) 3333-0102')])
            db().executemany('INSERT INTO tecnicos (nome,email,especialidade) VALUES (?,?,?)', [('Bruno Alves (exemplo)', 'bruno@example.com', 'Redes'), ('Carla Souza (exemplo)', 'carla@example.com', 'Computadores')])
            db().executemany('INSERT INTO chamados (titulo,descricao,status,cliente_id,tecnico_id) VALUES (?,?,?,?,?)', [('Conexão instável', 'Verificar sinal de rede e conexões do roteador.', 'Aberto', 1, 1), ('Computador não inicia', 'Realizar diagnóstico do equipamento do caixa.', 'Em andamento', 2, 2), ('Configurar rede sem fio', 'Configuração concluída e conexão verificada.', 'Concluído', 1, 1)])
        print('Dados fictícios adicionados.')

    return app


if __name__ == '__main__':
    create_app().run(host='127.0.0.1', port=5000, debug=False)
