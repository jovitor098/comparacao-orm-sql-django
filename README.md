# Projeto: Comparação ORM vs SQL com Django e Uvicorn

Este projeto foi desenvolvido para demonstrar e comparar o desempenho de consultas realizadas com Django ORM e SQL direto, utilizando o banco de dados de exemplo "employees".

## Fonte do Banco de Dados

O banco de dados utilizado neste projeto é baseado no schema disponível no repositório:  
[https://github.com/h8/employees-database/tree/master](https://github.com/h8/employees-database/tree/master)

O dump do banco deve ser restaurado em um banco PostgreSQL para que o projeto funcione corretamente.

---

## Requisitos

- **Python**: 3.9 ou superior
- **PostgreSQL**: com o dump do banco de exemplo restaurado

---

## Instalação

1. Clone este repositório:
   ```bash
   git clone https://github.com/jovitor098/comparacao-orm-sql-django.git
   cd comparacao-orm-sql-django
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Instale as dependencias
    ```bash
    uv sync
    ```


---

## Executando o Projeto

O projeto utiliza o **Uvicorn** como servidor ASGI. Para iniciar o servidor, execute:

```bash
cd employee
uvicorn employee.asgi:application --reload --port 8000
```

O servidor estará disponível em: [http://localhost:8000](http://localhost:8000)

---

## Endpoints Disponíveis

Os endpoints estão organizados em `/api/` e são divididos em categorias:

### 1. **Consultas Simples**
- ORM: `GET /api/avg/simple/orm/`
- SQL: `GET /api/avg/simple/sql/`

### 2. **Consultas Complexas**
- ORM: `GET /api/avg/complex/orm/`
- SQL: `GET /api/avg/complex/sql/`

### 3. **Consultas com Grandes Volumes**
- ORM: `GET /api/avg/large/orm/`
- SQL: `GET /api/avg/large/sql/`

### 4. **Exemplo de N+1 Problem**
- ORM (sem otimização): `GET /api/nplus1/orm/bad/`
- ORM (otimizado): `GET /api/nplus1/orm/fixed/`
- SQL (referência): `GET /api/nplus1/sql/reference/`

---

## Testando os Endpoints

Para testar os endpoints, você pode usar o arquivo `requisicoes.http` com o REST Client do VSCode ou ferramentas como `curl`:

```bash
curl -X GET http://localhost:8000/api/avg/simple/orm/
```

---

## Observações

- **Banco de Dados**: O projeto utiliza o PostgreSQL e espera que o schema `employees` esteja configurado. Certifique-se de restaurar o dump do banco antes de executar o projeto.
- **Desempenho**: Alguns endpoints retornam grandes volumes de dados. Para produção, recomenda-se implementar paginação ou streaming.
- **N+1 Problem**: O projeto inclui exemplos de consultas com e sem otimização para demonstrar o impacto do problema N+1.

---

## Licença

O schema do banco de dados foi retirado do repositório [h8/employees-database](https://github.com/h8/employees-database/tree/master). Este projeto foi desenvolvido para fins educacionais e de demonstração.