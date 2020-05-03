# scrapy-user-agent-rotator

Este módulo tem por finalidade permitir rotacionar user-agents no [Scrapy](https://scrapy.org/). 

Suas funcionalidades são:
- Rotacionar user-agent a cada **n** número de requisições feitas, sendo **n** um número escolhido ao acaso entre um mínimo e máximo.
    - Obs.: O valor de **n** será escolhido novamente ao acaso no momento de troca de user-agent. A finalidade disso é dificultar o trabalho de possíveis mecanismos de rastreamento contra crawlers.
- Escolha aleatória ou cíclica de um novo user-agent quando **n** requisições forem feitas. 

**Como usar**:
- Instale este módulo via **pip**:
    ```bash
    pip install scrapy-user-agent-rotator
    ```
- Configure seu projeto Scrapy para que possa usá-lo(**settings.py**):
    ```python
    DOWNLOADER_MIDDLEWARES = {
        ...,
        'user_agent_rotator.middlewares.RotateUserAgentMiddleware': 0,
    }
    ```
- Após isso, habilite-o (**settings.py**):
    ```python
    ROTATE_USER_AGENT_ENABLED = True
    ```
- Passe a lista de user-agents a ser usada (**settings.py**):
    ```python
    USER_AGENTS = [...]
    ```
- Defina o número mínimo e máximo de requisições a serem feitas com um mesmo user-agent. Um número aleatório entre eles (inclusive) será escolhido (**settings.py**):
    ```python
    MIN_USER_AGENT_USAGE = #uso mínimo de user-agent
    MAX_USER_AGENT_USAGE = #uso máximo de user-agent
    ```
- (Opcional) Defina o mecanismo de rotação de user-agents: Cíclico ou aleatório. O padrão é cíclico (**settings.py**):
    ```python
    CHOOSE_USER_AGENT_RANDOMLY = # False = Cíclico, True = Aleatório
    ```
- (Opcional) É possível conferir o user-agent usado no site: https://www.whatismybrowser.com/detect/what-is-my-user-agent 
