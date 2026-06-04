# SysOps
Um sistema de monitoramento e backup com virtualização no VirtualBox permite acompanhar o desempenho de máquinas virtuais e proteger dados por meio de cópias de segurança. Essa solução facilita testes, aumenta a segurança e possibilita a recuperação rápida do sistema em caso de falhas ou perda de informações.

### Descrição Completa do Sistema de Monitoramento e Backup com Virtualização no VirtualBox

O Sistema Integrado de Monitoramento e Backup com Virtualização no VirtualBox é uma solução desenvolvida para acompanhar o desempenho de computadores e servidores, proteger dados importantes e garantir a continuidade das operações em ambientes virtuais. O projeto utiliza máquinas virtuais criadas no VirtualBox, permitindo a execução segura de sistemas e aplicações sem interferir no sistema operacional principal.

O módulo de monitoramento coleta informações em tempo real sobre o uso de CPU, memória RAM, armazenamento em disco e tráfego de rede. Além disso, o sistema pode exibir dados como quantidade de núcleos e threads do processador, frequência de operação, temperatura da CPU, utilização da memória virtual (swap), estatísticas de leitura e escrita dos discos e status das interfaces de rede. Essas informações são disponibilizadas por meio de uma API desenvolvida em Python com Flask e Psutil, permitindo integração com interfaces web modernas.

O módulo de backup realiza cópias de segurança de arquivos e diretórios em formatos ZIP ou TAR.GZ, garantindo a preservação dos dados. O sistema aplica a estratégia de backup 3-2-1, mantendo três cópias dos dados em locais diferentes: armazenamento principal, armazenamento secundário e backup externo (offsite). Também é realizada a verificação de integridade dos arquivos por meio de hash SHA-256, assegurando que os backups não foram corrompidos.

Além da criação de backups, o sistema oferece recursos de listagem, restauração e exclusão de cópias de segurança, facilitando o gerenciamento dos dados. Todas as operações são registradas em um manifesto contendo informações como data de criação, tamanho dos arquivos, formato utilizado, localização das cópias e código de verificação.

A utilização do VirtualBox permite criar um ambiente isolado para testes, simulações e validações do sistema, reduzindo riscos e aumentando a segurança. Dessa forma, o projeto combina monitoramento contínuo, proteção de dados, recuperação de informações e virtualização, proporcionando maior confiabilidade, disponibilidade e eficiência na administração de recursos computacionais.

### Linguagens e Tecnologias Utilizadas

O sistema foi desenvolvido utilizando a linguagem **Python** no back-end, responsável pelo monitoramento do computador, gerenciamento dos backups e comunicação com a interface do usuário. Para a criação da API foi utilizado o framework **Flask**, que permite disponibilizar os dados do sistema através de requisições HTTP. Já a biblioteca **Psutil** foi utilizada para coletar informações de hardware e desempenho, como uso de CPU, memória RAM, discos e rede.

No armazenamento e gerenciamento dos backups, foram utilizadas bibliotecas nativas do Python, como **ZipFile**, **TarFile**, **Shutil**, **Hashlib** e **Pathlib**, responsáveis pela compactação, cópia, restauração e verificação de integridade dos arquivos.

### Front-end

O front-end foi desenvolvido com as tecnologias **HTML5**, **CSS3** e **JavaScript**, responsáveis pela criação da interface gráfica do sistema. O HTML estrutura os elementos da página, o CSS define o layout, as cores e o design visual, enquanto o JavaScript realiza a comunicação com a API em tempo real, atualizando os dados de monitoramento sem a necessidade de recarregar a página.

A interface foi projetada para ser intuitiva e moderna, apresentando gráficos, indicadores e painéis que permitem visualizar rapidamente o desempenho do sistema e o status dos backups. Dessa forma, o usuário consegue monitorar recursos computacionais, criar backups e restaurar arquivos por meio de uma experiência simples e organizada.

### Virtualização

Para os testes e a execução do projeto foi utilizado o **VirtualBox**, uma plataforma de virtualização que permite criar máquinas virtuais isoladas do sistema principal. Isso possibilita realizar simulações, testes de segurança, recuperação de backups e monitoramento de recursos em um ambiente controlado, reduzindo riscos e aumentando a confiabilidade do sistema.
