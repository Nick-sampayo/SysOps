# SysOps
Um sistema de monitoramento e backup com virtualização no VirtualBox permite acompanhar o desempenho de máquinas virtuais e proteger dados por meio de cópias de segurança. Essa solução facilita testes, aumenta a segurança e possibilita a recuperação rápida do sistema em caso de falhas ou perda de informações.
### Linguagens e Tecnologias Utilizadas

O sistema foi desenvolvido utilizando a linguagem **Python** no back-end, responsável pelo monitoramento do computador, gerenciamento dos backups e comunicação com a interface do usuário. Para a criação da API foi utilizado o framework **Flask**, que permite disponibilizar os dados do sistema através de requisições HTTP. Já a biblioteca **Psutil** foi utilizada para coletar informações de hardware e desempenho, como uso de CPU, memória RAM, discos e rede.

No armazenamento e gerenciamento dos backups, foram utilizadas bibliotecas nativas do Python, como **ZipFile**, **TarFile**, **Shutil**, **Hashlib** e **Pathlib**, responsáveis pela compactação, cópia, restauração e verificação de integridade dos arquivos.

### Front-end

O front-end foi desenvolvido com as tecnologias **HTML5**, **CSS3** e **JavaScript**, responsáveis pela criação da interface gráfica do sistema. O HTML estrutura os elementos da página, o CSS define o layout, as cores e o design visual, enquanto o JavaScript realiza a comunicação com a API em tempo real, atualizando os dados de monitoramento sem a necessidade de recarregar a página.

A interface foi projetada para ser intuitiva e moderna, apresentando gráficos, indicadores e painéis que permitem visualizar rapidamente o desempenho do sistema e o status dos backups. Dessa forma, o usuário consegue monitorar recursos computacionais, criar backups e restaurar arquivos por meio de uma experiência simples e organizada.

### Virtualização

Para os testes e a execução do projeto foi utilizado o **VirtualBox**, uma plataforma de virtualização que permite criar máquinas virtuais isoladas do sistema principal. Isso possibilita realizar simulações, testes de segurança, recuperação de backups e monitoramento de recursos em um ambiente controlado, reduzindo riscos e aumentando a confiabilidade do sistema.
