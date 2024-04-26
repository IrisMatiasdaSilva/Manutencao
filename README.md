# Parking

O presente projeto é um cenário fictício para um estacionamento rotativo. O sistema possui três modelos principais Parking, ParkingSpace e Ticket. Para cada modelo foram liberados os endpoints básicos (CRUD), além de um endpoints personalizado para calcular o valor do estacionamento.

## Configuração

Para executar o projeto configure o ambiente virtual Python. 

### Linux

~~~
    python3 -m venv venv
~~~
~~~
    source venv/bin/activate
~~~

### Windows

~~~
    python3 -m venv venv
~~~
~~~
    venv\Scripts\activate.bat
~~~

### Instalando Dependências

Em seguida instale as dependências:

~~~
    pip install -r requirements.txt
~~~

### Branches

O projeto está organizado em 4 branches diferentes:


- **main** - branch principal do projeto.
- **develop** - branch de desenvolvimento com a configuração inicial.
- **feature/basic** - branch com os modelos básicos do projeto.
- **feature/intermediate** - branch com endpoints ativos.
- **feature/advanced** - branch com implementações de endpoints personalizados com tratamento de erros.
- **feature/api_tests** - branch com implementações dos endpoints e testes da API.


### Execução

Para colocar o projeto em execução use o comando:

~~~
    python manage.py runserver
~~~