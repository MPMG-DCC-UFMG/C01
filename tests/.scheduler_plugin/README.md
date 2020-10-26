# Teste para plugin de agendamento de coletas do SC

Para realização dos testes, uma versão diferente do plugin foi necessária. A principal diferença está no tempo tempo corrente, que passa virtualmente mais rápido, viabilizando os testes.

> Instale os requerimentos na pasta de teste antes de executá-los.

Obs.: É necessário que o Redis e Kafka estejam executando e suas configurações (como senha e hosts) estejam devidamente definidas em SETTINGS de `m_scheduler.py` e `test_scheduler.py`