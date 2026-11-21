"""Gera o PDF e os diagramas vetoriais. Execute a partir de qualquer pasta.
Dependência de autoria: pip install reportlab
"""
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, Ellipse, Line, String, Circle
from reportlab.graphics import renderSVG

HERE = Path(__file__).resolve().parent
INK = colors.HexColor('#182a35')
GREEN = colors.HexColor('#087e70')
GRAY = colors.HexColor('#677882')
LIGHT = colors.HexColor('#edf5f2')
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyBR', fontName='Helvetica', fontSize=10.5, leading=16, alignment=TA_JUSTIFY, spaceAfter=10, textColor=INK))
styles.add(ParagraphStyle(name='TitleBR', fontName='Helvetica-Bold', fontSize=21, leading=26, spaceAfter=18, textColor=GREEN))
styles.add(ParagraphStyle(name='SubBR', fontName='Helvetica-Bold', fontSize=12, leading=17, spaceBefore=12, spaceAfter=8, textColor=INK))
styles.add(ParagraphStyle(name='CellBR', fontName='Helvetica', fontSize=8.5, leading=12, textColor=INK))
styles.add(ParagraphStyle(name='CenterBR', fontName='Helvetica', fontSize=12, leading=20, alignment=TA_CENTER, spaceAfter=14, textColor=INK))
styles.add(ParagraphStyle(name='CaptionBR', fontSize=9, leading=13, textColor=GRAY, spaceBefore=8, spaceAfter=12))


def p(text):
    return Paragraph(text, styles['BodyBR'])


def table(rows, widths):
    data = [[Paragraph(escape(str(c)), styles['CellBR']) for c in row] for row in rows]
    t = Table(data, colWidths=widths, repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), LIGHT), ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 9), ('RIGHTPADDING', (0, 0), (-1, -1), 9), ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 8), ('LINEBELOW', (0, 0), (-1, -1), .4, colors.HexColor('#dde5e8'))]))
    return t


def text(d, x, y, value, size=10, center=False):
    d.add(String(x, y, value, fontName='Helvetica', fontSize=size, fillColor=INK, textAnchor='middle' if center else 'start'))


def usecases():
    d = Drawing(480, 360)
    d.add(Rect(142, 12, 328, 335, strokeColor=GREEN, fillColor=colors.white, rx=8))
    text(d, 306, 324, 'FIXNOW - Gestão de chamados', 12, True)
    d.add(Circle(58, 199, 13, strokeColor=INK, fillColor=colors.white))
    for coords in [(58,186,58,135),(28,169,88,169),(58,135,32,100),(58,135,84,100)]:
        d.add(Line(*coords,strokeColor=INK))
    text(d,58,77,'Operador',11,True)
    labels = ['UC01 - Gerenciar clientes','UC02 - Gerenciar técnicos','UC03 - Abrir chamado','UC04 - Atualizar chamado','UC05 - Consultar chamados']
    for i,label in enumerate(labels):
        cy = 282 - i*55
        d.add(Line(91,169,195,cy,strokeColor=GRAY))
        d.add(Ellipse(323,cy,126,20,strokeColor=GREEN,fillColor=LIGHT))
        text(d,323,cy-3,label,10,True)
    return d


def er():
    d=Drawing(480,370)
    def entity(x,y,w,name,fields):
        h=32+len(fields)*21
        d.add(Rect(x,y-h,w,h,strokeColor=GREEN,fillColor=colors.white,rx=5))
        d.add(Rect(x,y-30,w,30,strokeColor=GREEN,fillColor=LIGHT))
        text(d,x+w/2,y-20,name,11,True)
        for i,f in enumerate(fields): text(d,x+10,y-48-21*i,f,9)
        return y-h
    entity(2,350,190,'CLIENTE',['PK  id : INTEGER','nome : TEXT(100)','email : TEXT(150)','telefone : TEXT(30)'])
    entity(288,350,190,'TÉCNICO',['PK  id : INTEGER','nome : TEXT(100)','email : TEXT(150)','especialidade : TEXT(100)'])
    entity(129,195,222,'CHAMADO',['PK  id : INTEGER','FK  cliente_id : INTEGER','FK  tecnico_id : INTEGER','titulo : TEXT(150)','descricao : TEXT(3000)','status : TEXT','criado_em : TEXT (UTC)','atualizado_em : TEXT (UTC)'])
    # Endpoint annotations express cardinalities without ambiguity.
    for x,end in [(97,176),(383,304)]:
        d.add(Line(x,234,x,215,strokeColor=GREEN))
        d.add(Line(x,215,end,215,strokeColor=GREEN))
        d.add(Line(end,215,end,195,strokeColor=GREEN))
        text(d,x-15,218,'1',9)
        text(d,end+5,199,'0..N',9)
    return d


def page_header(canvas,doc):
    canvas.saveState()
    if doc.page>1:
        canvas.setStrokeColor(colors.HexColor('#d9e5e1')); canvas.line(52,795,543,795)
        canvas.setFillColor(GRAY); canvas.setFont('Helvetica',8)
        canvas.drawString(52,805,'FIXNOW | Projeto de Desenvolvimento de Software II')
        canvas.drawRightString(543,805,'Vinicius Guilherme Canovas')
        canvas.drawString(52,32,'UniFil | Engenharia de Software | 2026')
        canvas.drawRightString(543,32,str(doc.page))
    canvas.restoreState()


def build():
    story=[]
    def title(s): story.append(Paragraph(s,styles['TitleBR']))
    def sub(s): story.append(Paragraph(s,styles['SubBR']))
    def body(s): story.append(p(s))
    def new(): story.append(PageBreak())
    def tab(rows,widths): story.append(table(rows,widths))

    story += [Spacer(1,48),Paragraph('CENTRO UNIVERSITÁRIO FILADÉLFIA - UNIFIL',styles['CenterBR']),Paragraph('BACHARELADO EM ENGENHARIA DE SOFTWARE',styles['CenterBR']),Spacer(1,70),Paragraph('VINICIUS GUILHERME CANOVAS',styles['CenterBR']),Spacer(1,70),Paragraph('FIXNOW',ParagraphStyle('CoverTitle',parent=styles['CenterBR'],fontName='Helvetica-Bold',fontSize=32,leading=38,textColor=GREEN)),Paragraph('Sistema de gerenciamento de chamados técnicos',styles['CenterBR']),Spacer(1,50),Paragraph('Projeto de Desenvolvimento de Software II<br/>Trabalho individual<br/>Professor/tutor: Fernando Nakagawa',styles['CenterBR']),Spacer(1,70),Paragraph('2026',styles['CenterBR'])]
    new(); title('Sumário')
    contents=[('1. Introdução',3),('2. Requisitos funcionais',4),('3. Requisitos não funcionais e regras',5),('4. Diagrama de casos de uso',6),('5. Especificação dos casos de uso',7),('6. Diagrama entidade-relacionamento',8),('7. Dicionário de dados',9),('8. Implementação e execução',10),('9. Evidências da interface',11),('10. Validação e resultados',12),('11. Conclusão',13),('Referências',14)]
    tab([['SEÇÃO','PÁGINA'],*contents],[430,55])
    body('Documento da implementação acadêmica simplificada, versão 1.0. O escopo desta entrega é independente do projeto anterior em Laravel. Os diagramas correspondem ao esquema e às funcionalidades desta versão em Python.')
    new();title('1. Introdução')
    body('O acompanhamento de atendimentos técnicos exige organizar informações de clientes, responsáveis e problemas relatados. Quando esses registros ficam dispersos, torna-se mais difícil localizar uma solicitação e identificar seu estado atual. O FIXNOW foi desenvolvido como uma aplicação web local para centralizar esses registros em uma interface simples.')
    sub('1.1 Objetivo geral')
    body('Implementar um sistema com persistência em banco de dados e operações de cadastro, consulta, atualização e exclusão (CRUD), permitindo gerenciar clientes, técnicos e chamados de assistência técnica.')
    sub('1.2 Escopo')
    body('O sistema permite cadastrar os participantes do atendimento, abrir chamados vinculados a um cliente e a um técnico, atualizar seus dados e estado, consultar registros com filtros e excluir informações respeitando seus relacionamentos. Um painel apresenta a quantidade de chamados por estado e os cinco registros mais recentes.')
    body('O ator da aplicação é o operador, pessoa que realiza a gestão dos registros. Técnico é uma entidade cadastrada e não um perfil de acesso. Esta versão não possui autenticação ou distinção de permissões; sua execução é local, em ambiente acadêmico. Não inclui estoque, notificações, assinatura digital, distribuição automática ou hospedagem pública.')
    sub('1.3 Tecnologias utilizadas')
    tab([['CAMADA','TECNOLOGIA / FINALIDADE'],['Backend','Python 3.12 e Flask 3.1.2: rotas HTTP, validação e processamento.'],['Frontend','HTML5, templates Jinja2, CSS local e JavaScript para confirmação de exclusões.'],['Persistência','SQLite, acessado pelo módulo sqlite3, com consultas parametrizadas e chaves estrangeiras.'],['Validação','unittest e cliente HTTP de teste do Flask; conferência visual em navegador.']],[95,390])
    new(); title('2. Requisitos funcionais')
    body('Os requisitos abaixo descrevem o comportamento implementado. Todos pertencem ao escopo da versão 1.0.')
    tab([['ID','REQUISITO','CASO'],['RF01','Cadastrar, listar, editar e excluir clientes, informando nome, e-mail e telefone.','UC01'],['RF02','Cadastrar, listar, editar e excluir técnicos, informando nome, e-mail e especialidade.','UC02'],['RF03','Abrir chamado com título, descrição, cliente, técnico responsável e estado.','UC03'],['RF04','Consultar os detalhes de um chamado, incluindo os dados vinculados e datas de criação e atualização.','UC05'],['RF05','Editar título, descrição, cliente, técnico e estado de um chamado.','UC04'],['RF06','Permitir os estados Aberto, Em andamento e Concluído.','UC03/04'],['RF07','Listar chamados e combinar filtros por estado, técnico e busca por título ou nome do cliente.','UC05'],['RF08','Excluir chamados mediante envio de formulário; apresentar confirmação na interface.','UC04'],['RF09','Impedir exclusão de cliente ou técnico vinculado a um chamado.','UC01/02'],['RF10','Exibir no painel contagens por estado e os cinco chamados mais recentes.','UC05'],['RF11','Informar erros de validação e preservar os campos enviados para correção.','UC01-04']],[43,386,56])
    sub('Dados de demonstração')
    body('Um comando opcional adiciona clientes, técnicos e chamados fictícios somente se o banco estiver completamente vazio. O sistema também funciona sem esses exemplos, com os cadastros realizados manualmente.')
    new();title('3. Requisitos não funcionais e regras')
    tab([['ID','REQUISITO / CRITÉRIO DE VERIFICAÇÃO'],['RNF01','Persistência: os registros devem continuar disponíveis após recriar a aplicação utilizando o mesmo arquivo SQLite.'],['RNF02','Integridade: todo chamado deve referenciar cliente e técnico existentes; o banco deve rejeitar a exclusão de registros vinculados.'],['RNF03','Validação: campos obrigatórios, limites de tamanho, formato de e-mail, vínculos e estados devem ser conferidos no servidor.'],['RNF04','Proteção das entradas: usar parâmetros SQL, escape de HTML e token CSRF nos formulários de alteração.'],['RNF05','Usabilidade: interface em português, rótulos nos campos, mensagens de resultado e navegação entre os três cadastros.'],['RNF06','Adaptação visual: menus e formulários devem se adaptar a telas estreitas; tabelas podem usar rolagem horizontal.'],['RNF07','Execução local: após instalar as dependências, o sistema deve funcionar sem recursos visuais externos ou conexão com serviços de terceiros.'],['RNF08','Manutenção: separar regras e rotas, esquema SQL, templates, recursos estáticos, testes e documentação.']],[47,438])
    sub('Regras de negócio')
    body('<b>RB01.</b> Cada chamado pertence a exatamente um cliente e possui exatamente um técnico responsável. Um cliente ou técnico pode ter nenhum ou vários chamados.')
    body('<b>RB02.</b> Os três estados podem ser escolhidos na criação e na edição, inclusive para reabrir um atendimento. Não existe bloqueio de transição nesta versão.')
    body('<b>RB03.</b> Para excluir cliente ou técnico vinculado, é necessário antes reatribuir ou excluir os chamados associados. Exclusões são permanentes; a interface solicita confirmação.')
    body('<b>RB04.</b> Datas são registradas automaticamente em UTC e identificadas como UTC na tela de detalhes. Nomes e e-mails não são identificadores exclusivos; o identificador de cada registro é seu ID.')
    new();title('4. Diagrama de casos de uso')
    body('O operador interage com cinco casos de uso dentro da fronteira do sistema. As associações são representadas por linhas simples. Não foram usadas relações include ou extend porque os cinco objetivos podem ser representados diretamente.')
    story.append(usecases()); story.append(Paragraph('Figura 1 - Casos de uso do FIXNOW. Fonte: elaboração para esta implementação.',styles['CaptionBR']))
    body('<b>Operador:</b> usuário que cadastra clientes e técnicos e gerencia os atendimentos. O sistema não exige login no escopo acadêmico local.')
    body('UC01 e UC02 agrupam os respectivos CRUDs. UC03 representa a criação do chamado, UC04 sua manutenção e exclusão, e UC05 a consulta dos detalhes, dos filtros e do painel.')
    new();title('5. Especificação dos casos de uso')
    for heading,description in [
        ('UC01 - Gerenciar clientes','Pré-condição: aplicação disponível. Fluxo: acessar Clientes, cadastrar os dados, salvar, consultar a lista e editar ou excluir o cadastro. Alternativas: dados inválidos mantêm o formulário; cliente vinculado não pode ser excluído. Resultado: cadastro persistido, alterado ou removido.'),
        ('UC02 - Gerenciar técnicos','Pré-condição: aplicação disponível. Fluxo: acessar Técnicos, informar nome, e-mail e especialidade, salvar e consultar a lista. O operador pode editar ou excluir. Alternativas: campos inválidos geram mensagens; técnico vinculado não pode ser excluído. Resultado: cadastro atualizado no banco.'),
        ('UC03 - Abrir chamado','Pré-condição: pelo menos um cliente e um técnico cadastrados. Fluxo: acessar Novo chamado, informar título e descrição, selecionar cliente, técnico e estado, salvar. Alternativas: ausência de cadastros mostra orientação; referências ou campos inválidos impedem a gravação. Resultado: chamado criado e exibido nos detalhes.'),
        ('UC04 - Atualizar chamado','Pré-condição: chamado existente. Fluxo: acessar os detalhes, selecionar Editar chamado, alterar os dados e salvar. Alternativa: solicitar exclusão, confirmar e retornar à lista; cancelar a confirmação mantém o registro. Dados inválidos não são gravados. Resultado: chamado alterado ou excluído.'),
        ('UC05 - Consultar chamados','Pré-condição: aplicação disponível. Fluxo: acessar Chamados, combinar os filtros e abrir os detalhes. O painel permite consultar contagens e os últimos registros. Alternativas: busca sem resultados apresenta mensagem; ID inexistente retorna página 404. Resultado: informações exibidas sem alteração dos registros.')]:
        sub(heading);body(description)
    new();title('6. Diagrama entidade-relacionamento')
    body('O modelo possui três entidades. As chaves estrangeiras de Chamado são obrigatórias e referenciam os IDs de Cliente e Técnico. As cardinalidades abaixo representam um registro principal para zero ou vários chamados.')
    story.append(er()); story.append(Paragraph('Figura 2 - DER lógico do FIXNOW. PK: chave primária. FK: chave estrangeira. Fonte: esquema schema.sql da implementação.',styles['CaptionBR']))
    body('Cada chamado tem exatamente um cliente e um técnico. O banco usa ON DELETE RESTRICT, com chaves estrangeiras ativadas em cada conexão. Os limites indicados para campos TEXT são implementados por validação e restrições CHECK; não representam tipos VARCHAR nativos do SQLite.')
    new();title('7. Dicionário de dados')
    tab([['ENTIDADE / CAMPO','TIPO','REGRA'],['clientes.id / tecnicos.id','INTEGER','Chave primária autoincremental.'],['clientes.nome / tecnicos.nome','TEXT','Obrigatório, de 1 a 100 caracteres após remoção dos espaços nas pontas.'],['clientes.email / tecnicos.email','TEXT','Obrigatório, até 150 caracteres; formato validado na aplicação.'],['clientes.telefone','TEXT','Obrigatório, até 30 caracteres; formato livre.'],['tecnicos.especialidade','TEXT','Obrigatório, até 100 caracteres.'],['chamados.id','INTEGER','Chave primária autoincremental.'],['chamados.cliente_id','INTEGER','Chave estrangeira obrigatória para clientes.id.'],['chamados.tecnico_id','INTEGER','Chave estrangeira obrigatória para tecnicos.id.'],['chamados.titulo','TEXT','Obrigatório, até 150 caracteres.'],['chamados.descricao','TEXT','Obrigatório, até 3.000 caracteres.'],['chamados.status','TEXT','Aberto, Em andamento ou Concluído. Padrão: Aberto.'],['chamados.criado_em','TEXT','Data e hora UTC definidas na inserção.'],['chamados.atualizado_em','TEXT','Data e hora UTC atualizadas no salvamento.']],[192,57,236])
    body('Índices auxiliam as consultas por cliente e por técnico/estado. As mensagens da aplicação explicam o bloqueio de exclusão quando há dependência entre registros.')
    new();title('8. Implementação e execução')
    body('O navegador envia requisições ao Flask. As rotas processam os dados e usam sqlite3 para consultar ou alterar o banco. O Jinja2 combina os resultados com os templates HTML; o navegador apresenta a interface usando CSS e JavaScript locais.')
    tab([['ARQUIVO / PASTA','RESPONSABILIDADE'],['app.py','Fábrica da aplicação, rotas, conexão, validações e comando demo.'],['schema.sql','Criação das tabelas, restrições e índices.'],['templates/ e static/','Páginas HTML, estilos e confirmação de exclusão.'],['tests/test_app.py','Testes automatizados com banco temporário.'],['instance/fixnow.db','Banco local criado automaticamente; ignorado pelo Git.'],['requirements.txt','Versões das dependências da aplicação.']],[160,325])
    sub('Instalação e uso')
    body('Requisito: Python 3.12 e acesso à internet apenas para instalar as dependências. Na pasta do projeto, execute os comandos abaixo. No Windows, iniciar.bat automatiza a preparação do ambiente e a execução.')
    for cmd in ['python -m venv .venv', '.venv\\Scripts\\python -m pip install -r requirements.txt', '.venv\\Scripts\\python app.py']:
        body('<font face="Courier" size="9">'+escape(cmd)+'</font>')
    body('Acesse <b>http://127.0.0.1:5000</b>. Cadastre um cliente e um técnico antes de criar um chamado. Para adicionar exemplos fictícios, use o Python do ambiente com <font face="Courier" size="9">-m flask --app app demo</font>. Para encerrar, pressione Ctrl+C no terminal.')
    body('O servidor inicia apenas no endereço local e sem modo de depuração. O projeto foi delimitado à demonstração acadêmica; publicação do código no GitHub não significa hospedagem da aplicação. A chave da sessão pode ser definida pela variável FIXNOW_SECRET_KEY; sem ela, muda a cada reinicialização.')
    new();title('9. Evidências da interface')
    body('As imagens abaixo foram capturadas durante a execução local com dados fictícios. O painel exibe contagens por estado e a tela de detalhes mostra os relacionamentos do atendimento.')
    from PIL import Image as PILImage
    for filename,caption in [('painel.png','Figura 3 - Painel de acompanhamento.'),('chamado.png','Figura 4 - Detalhes de chamado criado no navegador.')]:
        path=HERE/'imagens'/filename
        if path.exists():
            with PILImage.open(path) as source: w,h=source.size
            factor=min(480/w,250/h)
            story.append(Image(str(path),width=w*factor,height=h*factor))
            story.append(Paragraph(caption+' Fonte: captura da aplicação local, 05 nov. 2026.',styles['CaptionBR']))
    new();title('10. Validação e resultados')
    body('A suíte automatizada utiliza unittest, o cliente de teste do Flask e um arquivo SQLite temporário por teste, isolado do banco usado na demonstração. Execução realizada em 05 de novembro de 2026: <b>12 testes aprovados</b>.')
    tab([['TESTE','CENÁRIO VERIFICADO','RESULTADO'],['T01','CRUD completo de clientes e técnicos.','Aprovado'],['T02','Criação, consulta, edição, estados e exclusão de chamado.','Aprovado'],['T03','Bloqueio de exclusão de cliente/técnico vinculado.','Aprovado'],['T04','Campos obrigatórios, formato de e-mail e limites.','Aprovado'],['T05','Rejeição de vínculos, estado e descrição inválidos.','Aprovado'],['T06','Filtros combinados, resultado vazio e filtros inválidos.','Aprovado'],['T07','Rejeição de POST sem CSRF e de exclusão por GET.','Aprovado'],['T08','Retorno 404 para entidades e registros inexistentes.','Aprovado'],['T09','Escape de HTML e entradas SQL tratadas como dados.','Aprovado'],['T10','Persistência ao recriar a aplicação com o mesmo banco.','Aprovado'],['T11','Telas vazias e orientação sobre cadastros necessários.','Aprovado'],['T12','Carga demo sem duplicação ou alteração de banco preenchido.','Aprovado']],[43,374,68])
    body('Para reproduzir: <font face="Courier" size="9">python -m unittest discover -s tests -v</font>, após instalar as dependências. Também foram conferidos o painel, o formulário e a criação de um chamado pelo navegador, além da adaptação visual em tela estreita.')
    body('Limites da validação: não foram realizados testes de carga, avaliação formal de usabilidade ou medição de disponibilidade. Não se atribuem ao projeto garantias de produção ou desempenho que não tenham sido medidas.')
    new();title('11. Conclusão')
    body('O desenvolvimento do FIXNOW permitiu aplicar a comunicação entre frontend, backend e banco de dados em um fluxo completo. A interface recebe as informações dos formulários, o backend valida e processa essas entradas, e o banco armazena os registros e seus relacionamentos para consultas posteriores.')
    body('Conforme meu relato de aprendizado, compreendi melhor como essas três partes precisam se comunicar para que o sistema apresente um funcionamento adequado. A integração deixa de ser uma ideia isolada quando um cliente e um técnico cadastrados passam a ser utilizados em um chamado e as alterações aparecem novamente na interface.')
    body('A versão entregue mantém um escopo reduzido, com três CRUDs e cinco casos de uso. A implementação e a documentação foram alinhadas para que as funcionalidades descritas correspondam às disponíveis no sistema. Os testes realizados verificaram os fluxos centrais, a persistência e as principais regras de validação.')
    body('Como possíveis evoluções, podem ser considerados autenticação, permissões por perfil e histórico de alterações. Esses recursos não fazem parte desta versão. A avaliação de desempenho sob múltiplos acessos também dependeria de testes específicos.')
    sub('Autoria e processo de elaboração')
    body('Trabalho individual de Vinicius Guilherme Canovas. A implementação e a organização documental foram elaboradas com auxílio de IA nesta colaboração. O conteúdo da reflexão acima foi desenvolvido a partir do relato do aluno sobre integrar backend, frontend e banco de dados. A defesa deve ser realizada pessoalmente pelo aluno, seguindo a regra da disciplina sobre não utilizar IA ou leitores de texto na confecção do vídeo.')
    new();title('Referências')
    refs=[
        ('PALLETS PROJECTS. Flask Documentation: Quickstart.','https://flask.palletsprojects.com/en/stable/quickstart/'),
        ('PYTHON SOFTWARE FOUNDATION. sqlite3 - DB-API 2.0 interface for SQLite databases.','https://docs.python.org/3/library/sqlite3.html'),
        ('PYTHON SOFTWARE FOUNDATION. unittest - Unit testing framework.','https://docs.python.org/3/library/unittest.html'),
        ('SQLITE. Foreign Key Support.','https://www.sqlite.org/foreignkeys.html'),
        ('PALLETS PROJECTS. Jinja Documentation.','https://jinja.palletsprojects.com/en/stable/'),
        ('GITHUB. Creating a new repository.','https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository')]
    for label,url in refs:
        body(escape(label)+' Disponível em: <link href="'+url+'" color="#087e70">'+escape(url)+'</link>. Acesso em: 5 nov. 2026.')
    body('UNIFIL. Enunciado de Projeto de Desenvolvimento de Software II. Orientações de atividade fornecidas pelo aluno nesta colaboração, consultadas em 5 nov. 2026.')
    body('Os diagramas, o esquema de dados e as capturas de tela desta documentação foram produzidos para a implementação acadêmica em Python apresentada neste trabalho.')
    pdf=HERE/'Documentacao_FIXNOW.pdf'
    doc=SimpleDocTemplate(str(pdf),pagesize=(595.28,841.89),rightMargin=52,leftMargin=52,topMargin=65,bottomMargin=53,title='FIXNOW - Projeto de Desenvolvimento de Software II',author='Vinicius Guilherme Canovas')
    doc.build(story,onFirstPage=page_header,onLaterPages=page_header)
    renderSVG.drawToFile(usecases(),str(HERE/'casos-de-uso.svg'))
    renderSVG.drawToFile(er(),str(HERE/'der.svg'))
    print(pdf)


if __name__=='__main__':
    build()
