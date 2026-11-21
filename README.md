# FIXNOW - Projeto de Desenvolvimento de Software II

Sistema acadêmico local para gerenciar clientes, técnicos e chamados de assistência técnica.

**Repositório público:** https://github.com/ViniciusGcanovas/fixnow-projeto-ii

**Autor:** Vinicius Guilherme Canovas · **Trabalho:** individual  
**Instituição:** UniFil · **Curso:** Engenharia de Software  
**Professor/tutor informado:** Fernando Nakagawa · **Prazo informado:** 21/11/2026

## Funcionalidades

- CRUD completo de clientes, técnicos e chamados.
- Vínculo obrigatório do chamado a um cliente e a um técnico.
- Estados Aberto, Em andamento e Concluído.
- Filtros combinados por estado, técnico e título/nome do cliente.
- Painel de contagens, detalhes do chamado e datas em UTC.
- Validação no servidor, confirmação visual de exclusão e proteção de vínculos no banco.

Não há login ou perfis de acesso. O ator é o operador; técnicos são registros do cadastro. Escopo limitado ao uso acadêmico local.

## Tecnologias

Python 3.12, Flask 3.1.2, SQLite, Jinja2, HTML, CSS local e JavaScript. Os estilos não dependem de CDN ou Bootstrap.

## Executar no Windows

Instale Python 3.12 com a opção de adicioná-lo ao PATH. Abra `iniciar.bat`, aguarde a instalação e acesse **http://127.0.0.1:5000**. A primeira instalação precisa de internet. Encerre com Ctrl+C no terminal.

Alternativa manual, dentro da pasta do projeto:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python app.py
```

Linux/macOS: use `python3 -m venv .venv` e substitua `.venv\Scripts\python` por `.venv/bin/python`.

O banco é criado automaticamente em `instance/fixnow.db`. A instalação começa vazia: cadastre clientes e técnicos, depois chamados.

## Exemplos opcionais

```powershell
.venv\Scripts\python -m flask --app app demo
```

Adiciona apenas dados fictícios, com e-mails `example.com`, se as três tabelas estiverem vazias. Não altera banco preenchido. Não é necessário apagar dados para executar o sistema.

## Testes

```powershell
.venv\Scripts\python -m unittest discover -s tests -v
```

São 12 testes, com bancos temporários isolados: CRUDs, filtros, validação, vínculos, CSRF, escape de HTML, persistência e carga demo. Os resultados registrados estão em `docs/validacao.txt`.

## Estrutura

```text
app.py                   Rotas, regras, conexão e comando demo
schema.sql               Tabelas, restrições e índices
templates/               Interface HTML
static/                  CSS e JavaScript locais
tests/test_app.py        Testes automatizados
docs/                    PDF, diagramas, imagens e gerador editável
instance/                Banco criado na execução (ignorado pelo Git)
iniciar.bat              Inicializador Windows
requirements.txt         Dependências da aplicação
```

## Documentação

- [Documento acadêmico em PDF](docs/Documentacao_FIXNOW.pdf)
- [Casos de uso](docs/casos-de-uso.svg)
- [DER](docs/der.svg)

O conteúdo do PDF é editável em `docs/build_documentation.py`, e a arte institucional está em `docs/capa-modelo.pdf`. Para regenerar, instale `reportlab`, `Pillow` e `pypdf` e execute `python docs/build_documentation.py`. Essas bibliotecas são necessárias apenas para autoria do PDF.

## Regras e limites

Clientes e técnicos vinculados a chamados não podem ser excluídos. Antes, reatribua ou exclua os respectivos chamados. Exclusões são permanentes. E-mails podem se repetir; o ID identifica cada registro. O estado pode ser alterado livremente entre os três valores permitidos.

As datas são armazenadas e exibidas em UTC. Todas as alterações usam POST com CSRF; consultas usam GET. Os parâmetros de busca não são concatenados ao SQL. O HTML das entradas é escapado pelo Jinja2.

O servidor inicia em `127.0.0.1`, sem depuração. Não é uma implantação pública. A chave de sessão muda a cada reinício; opcionalmente, configure `FIXNOW_SECRET_KEY` para mantê-la estável. Não há promessa de desempenho sob carga ou disponibilidade de produção.

## Autoria e apoio

Projeto individual elaborado com auxílio de IA para implementação, testes e organização documental. A reflexão acadêmica foi baseada no relato do aluno. O aluno deve compreender e revisar a entrega. O vídeo de defesa deve ser gravado pelo próprio aluno, respeitando a proibição de IA e leitores de texto nessa etapa.
