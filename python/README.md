# Teste de Back-end Bcredi

Aplicação simples feita puramente com Python que recebe dados de eventos e implementa as regras de negócio [definidas aqui](https://github.com/guimunarolo/teste-backends/blob/master/README.md).


## Requirements

- Python 3.8
- Pipenv


## How to run

Supondo que seu ambiente atenda os requerimentos, basta executar:

```bash
$ pipenv install --dev
```

Após isso você já possuí o necessário para rodar os testes:

```bash
$ pytest
```

Será exibido uma interface com os testes executados e a cobertura de cada modulo.

Agora para fazer um teste com dados reais, você tem 2 opções:

#### Utilizando uma string com os eventos

```bash
$ python main.py "8
c2d06c4f-e1dc-4b2a-af61-ba15bc6d8610,proposal,created,2019-11-11T13:26:04Z,bd6abe95-7c44-41a4-92d0-edf4978c9f4e,684397.0,72
27179730-5a3a-464d-8f1e-a742d00b3dd3,warranty,added,2019-11-11T13:26:04Z,bd6abe95-7c44-41a4-92d0-edf4978c9f4e,6b5fc3f9-bb6b-4145-9891-c7e71aa87ca2,1967835.53,ES
716de46f-9cc0-40be-b665-b0d47841db4c,warranty,added,2019-11-11T13:26:04Z,bd6abe95-7c44-41a4-92d0-edf4978c9f4e,1750dfe8-fac7-4913-b946-ab538dce0977,1608429.56,GO
814695b6-f44e-491b-9921-af806f5bb25c,proposal,created,2019-11-11T13:27:22Z,af6e600b-2622-40d1-89ad-d3e5b6cc2fdf,2908382.0,108
cc08d0d2-e519-495f-b7d6-db6391c21958,warranty,added,2019-11-11T13:27:22Z,af6e600b-2622-40d1-89ad-d3e5b6cc2fdf,37113e50-26ae-48d2-aaf4-4cda8fa76c79,6040545.22,BA
f72d0829-beac-45bb-b235-7fa16b117c43,warranty,added,2019-11-11T13:27:22Z,af6e600b-2622-40d1-89ad-d3e5b6cc2fdf,8ade6e09-cb60-4a97-abbb-b73bf4bd8f76,6688872.79,DF
5d9e1ec6-9304-40a1-947f-ab5ea993d100,proponent,added,2019-11-11T13:27:22Z,af6e600b-2622-40d1-89ad-d3e5b6cc2fdf,2213ea91-4a3c-46a3-b3a7-ff55c2888561,Kathline Ferry,50,168896.38,true
23060b08-32bf-4e53-9866-69f6bcc7fdbd,proponent,added,2019-11-11T13:27:22Z,af6e600b-2622-40d1-89ad-d3e5b6cc2fdf,7526214a-cd5b-4e49-a723-e031bc82dcef,Merle Leuschke,50,143081.9,false"
```

Output:

```bash
af6e600b-2622-40d1-89ad-d3e5b6cc2fdf
```

#### Utilizando um arquivo com os eventos

```bash
$ python main.py -i ../test/input/input000.txt
```

> Note que para utilizar um arquivo é preciso fornecer o paramêtro **-i** e depois o caminho absoluto para o arquivo

Output:

```bash
901557cb-01b5-4747-ad73-5d1e53d16bac,2685c557-f70c-4cd6-8be4-f90b10699963,20906979-43e1-4c1a-9c38-f4538b576cc5
```
